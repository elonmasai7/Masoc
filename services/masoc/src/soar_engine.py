import json
import os
import threading

import uvicorn
from fastapi import FastAPI, HTTPException

from .common import db_conn, init_db, kafka_consumer, load_yaml, utc_now

app = FastAPI(title="MASOC SOAR")

POLICY_PATH = os.getenv("SOAR_POLICY_PATH", "/app/config/soar_policy.yaml")
POLICY = load_yaml(
    POLICY_PATH,
    default={
        "auto_action_min_score": 70,
        "high_impact_actions": ["disable_account", "network_wide_isolation", "shutdown_critical_system"],
        "break_glass_score": 95,
    },
)


def record_incident(incident: dict) -> None:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO incidents (incident_id, created_at, entity, category, score, confidence, status, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident["incident_id"],
                incident["timestamp"],
                incident["entity"],
                incident["category"],
                int(incident["risk_score"]),
                float(incident.get("confidence", 0.7)),
                "new",
                json.dumps(incident),
            ),
        )
        conn.commit()


def record_action(incident_id: str, action: str, decision: str, reason: str, actor: str) -> None:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO actions (incident_id, action, decision, reason, actor, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (incident_id, action, decision, reason, actor, utc_now()),
        )
        cur.execute("UPDATE incidents SET status = ? WHERE incident_id = ?", (decision, incident_id))
        conn.commit()


def request_approval(incident_id: str, action: str, reason: str) -> None:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO approvals (incident_id, action, reason, status, requested_at, decided_at, decided_by)
            VALUES (?, ?, ?, 'pending', ?, '', '')
            """,
            (incident_id, action, reason, utc_now()),
        )
        cur.execute("UPDATE incidents SET status = 'pending_approval' WHERE incident_id = ?", (incident_id,))
        conn.commit()


def process_incident(incident: dict) -> None:
    auto_min = int(POLICY.get("auto_action_min_score", 70))
    break_glass = int(POLICY.get("break_glass_score", 95))
    high_impact = set(POLICY.get("high_impact_actions", []))

    incident_id = incident["incident_id"]
    action = incident.get("recommended_action", "investigate")
    score = int(incident.get("risk_score", 0))

    record_incident(incident)

    if action in high_impact and score < break_glass:
        request_approval(incident_id, action, "High-impact action requires human approval")
        return

    if score >= auto_min:
        record_action(incident_id, action, "auto_executed", "Risk threshold exceeded", "masoc-soar")
    else:
        record_action(incident_id, "investigate", "manual_review", "Below automation threshold", "masoc-soar")


def consumer_loop() -> None:
    topic = os.getenv("INCIDENT_TOPIC", "incidents.risk")
    consumer = kafka_consumer([topic], group_id="masoc-soar")
    for message in consumer:
        process_incident(message.value)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "soar-engine"}


@app.get("/incidents")
def incidents(limit: int = 100) -> list[dict]:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT incident_id, created_at, entity, category, score, confidence, status FROM incidents ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "incident_id": r[0],
            "created_at": r[1],
            "entity": r[2],
            "category": r[3],
            "score": r[4],
            "confidence": r[5],
            "status": r[6],
        }
        for r in rows
    ]


@app.get("/actions")
def actions(limit: int = 100) -> list[dict]:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT incident_id, action, decision, reason, actor, created_at FROM actions ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "incident_id": r[0],
            "action": r[1],
            "decision": r[2],
            "reason": r[3],
            "actor": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]


@app.get("/approvals/pending")
def pending_approvals() -> list[dict]:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, incident_id, action, reason, requested_at FROM approvals WHERE status = 'pending' ORDER BY id DESC"
        )
        rows = cur.fetchall()
    return [
        {"id": r[0], "incident_id": r[1], "action": r[2], "reason": r[3], "requested_at": r[4]} for r in rows
    ]


@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: int, actor: str = "soc-analyst") -> dict:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT incident_id, action, status FROM approvals WHERE id = ?", (approval_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Approval request not found")
        if row[2] != "pending":
            raise HTTPException(status_code=409, detail="Approval request already decided")
        incident_id, action, _ = row
        cur.execute(
            "UPDATE approvals SET status='approved', decided_at=?, decided_by=? WHERE id = ?",
            (utc_now(), actor, approval_id),
        )
        conn.commit()
    record_action(incident_id, action, "approved_executed", "Approved by analyst", actor)
    return {"approval_id": approval_id, "status": "approved"}


@app.post("/approvals/{approval_id}/reject")
def reject(approval_id: int, actor: str = "soc-analyst") -> dict:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT incident_id, status FROM approvals WHERE id = ?", (approval_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Approval request not found")
        if row[1] != "pending":
            raise HTTPException(status_code=409, detail="Approval request already decided")
        incident_id = row[0]
        cur.execute(
            "UPDATE approvals SET status='rejected', decided_at=?, decided_by=? WHERE id = ?",
            (utc_now(), actor, approval_id),
        )
        conn.commit()
    record_action(incident_id, "none", "rejected", "Analyst rejected automated action", actor)
    return {"approval_id": approval_id, "status": "rejected"}


def start() -> None:
    init_db()
    threading.Thread(target=consumer_loop, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8090)


if __name__ == "__main__":
    start()
