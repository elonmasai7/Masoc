import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .common import db_conn, init_db

app = FastAPI(title="MASOC Dashboard")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "soc-dashboard"}


@app.get("/api/summary")
def summary() -> dict:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM incidents")
        incidents = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM incidents WHERE status = 'pending_approval'")
        pending = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM actions WHERE decision LIKE 'auto_%'")
        auto_actions = cur.fetchone()[0]
    return {"incidents": incidents, "pending_approvals": pending, "auto_actions": auto_actions}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT incident_id, created_at, entity, category, score, status FROM incidents ORDER BY id DESC LIMIT 30"
        )
        incidents = cur.fetchall()
        cur.execute(
            "SELECT incident_id, action, decision, actor, created_at FROM actions ORDER BY id DESC LIMIT 30"
        )
        actions = cur.fetchall()

    incident_rows = "".join(
        [
            f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"
            for r in incidents
        ]
    )
    action_rows = "".join(
        [f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>" for r in actions]
    )

    return f"""
    <html>
    <head>
      <title>MedShield Autonomous SOC</title>
      <style>
        body {{ font-family: "IBM Plex Sans", sans-serif; margin: 2rem; background: #f4f7f3; color: #102a43; }}
        h1 {{ margin-bottom: 0.2rem; }}
        .panel {{ background: #ffffff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border-bottom: 1px solid #d9e2ec; text-align: left; padding: 0.5rem; font-size: 0.9rem; }}
        th {{ background: #e6f4ea; }}
      </style>
    </head>
    <body>
      <h1>MedShield Autonomous SOC (MASOC)</h1>
      <p>Real-time incidents, AI correlation, and governed response actions.</p>
      <div class="panel">
        <h2>Active Incidents</h2>
        <table>
          <thead><tr><th>ID</th><th>Time</th><th>Entity</th><th>Category</th><th>Score</th><th>Status</th></tr></thead>
          <tbody>{incident_rows}</tbody>
        </table>
      </div>
      <div class="panel">
        <h2>SOAR Actions</h2>
        <table>
          <thead><tr><th>Incident</th><th>Action</th><th>Decision</th><th>Actor</th><th>Time</th></tr></thead>
          <tbody>{action_rows}</tbody>
        </table>
      </div>
    </body>
    </html>
    """


def start() -> None:
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8091)


if __name__ == "__main__":
    start()
