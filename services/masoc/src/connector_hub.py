import os
import threading
import time
from typing import Any

import requests
import uvicorn
from fastapi import Body, FastAPI, HTTPException

from .common import kafka_producer, load_yaml, utc_now


def as_list(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "events", "indicators", "objects"):
            if isinstance(payload.get(key), list):
                return [item for item in payload[key] if isinstance(item, dict)]
        return [payload]
    return []


def expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    return value


class ConnectorHub:
    def __init__(self) -> None:
        self.config_path = os.getenv("CONNECTOR_CONFIG_PATH", "/app/config/connectors.yaml")
        self.raw_topic = os.getenv("RAW_TOPIC", "telemetry.raw")
        self.intel_topic = os.getenv("INTEL_TOPIC", "threat.intel")
        self.producer = kafka_producer()
        self.status: dict[str, dict] = {}
        self.connectors: list[dict] = []
        self.reload_config()

    def reload_config(self) -> None:
        cfg = load_yaml(self.config_path, default={"connectors": []})
        self.connectors = [expand_env(c) for c in cfg.get("connectors", []) if isinstance(c, dict)]
        for c in self.connectors:
            name = c.get("name", "unknown")
            self.status.setdefault(name, {"last_success": "", "last_error": "", "published": 0})

    def _headers(self, connector: dict) -> dict:
        headers = {"Accept": "application/json"}
        auth = connector.get("auth", {})
        if auth.get("type") == "bearer":
            token = os.getenv(auth.get("token_env", ""), "").strip()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        if auth.get("type") == "apikey":
            key_name = auth.get("key_name", "X-API-Key")
            key_val = os.getenv(auth.get("key_env", ""), "").strip()
            if key_val:
                headers[key_name] = key_val
        return headers

    def _normalize_telemetry(self, source: str, event_type: str, item: dict, metadata: dict | None = None) -> dict:
        return {
            "source": source,
            "event_type": event_type,
            "user": str(item.get("user") or item.get("username") or item.get("actor") or "unknown"),
            "host": str(item.get("host") or item.get("device") or item.get("endpoint") or "unknown"),
            "src_ip": str(item.get("src_ip") or item.get("ip") or item.get("source_ip") or "0.0.0.0"),
            "action": str(item.get("action") or item.get("event") or "observed"),
            "result": str(item.get("result") or item.get("status") or "unknown"),
            "file_mod_count": int(item.get("file_mod_count", 0) or 0),
            "process_spawn_count": int(item.get("process_spawn_count", 0) or 0),
            "metadata": {"connector_time": utc_now(), **(metadata or {}), "raw": item},
            "ingested_at": utc_now(),
        }

    def _records_from_payload(self, ctype: str, cname: str, payload: Any) -> tuple[list[dict], str]:
        items = as_list(payload)
        if ctype in ("entra", "okta", "identity"):
            return [self._normalize_telemetry(f"identity.{cname}", "auth", i) for i in items], self.raw_topic
        if ctype in ("crowdstrike", "sentinelone", "edr"):
            return [self._normalize_telemetry(f"edr.{cname}", "edr_alert", i) for i in items], self.raw_topic
        if ctype in ("proofpoint", "mimecast", "email"):
            return [self._normalize_telemetry(f"email.{cname}", "email_threat", i) for i in items], self.raw_topic
        if ctype in ("taxii", "stix", "threat_intel"):
            iocs = []
            for i in items:
                value = str(i.get("value") or i.get("indicator") or i.get("pattern") or "").strip()
                if not value:
                    continue
                iocs.append(
                    {
                        "indicator_type": str(i.get("indicator_type") or i.get("type") or "unknown"),
                        "value": value,
                        "source": cname,
                        "confidence": float(i.get("confidence", 0.8)),
                        "tags": i.get("tags", []),
                        "timestamp": utc_now(),
                    }
                )
            return iocs, self.intel_topic
        return [self._normalize_telemetry(f"generic.{cname}", "security_event", i) for i in items], self.raw_topic

    def _publish(self, connector: dict, payload: Any) -> int:
        cname = connector.get("name", "unknown")
        ctype = connector.get("type", "generic")
        records, topic = self._records_from_payload(ctype, cname, payload)
        for r in records:
            self.producer.send(topic, r)
        self.status[cname]["published"] = self.status[cname].get("published", 0) + len(records)
        self.status[cname]["last_success"] = utc_now()
        self.status[cname]["last_error"] = ""
        return len(records)

    def _pull_once(self, connector: dict) -> None:
        cname = connector.get("name", "unknown")
        url = connector.get("url", "").strip()
        if not url:
            self.status[cname]["last_error"] = "missing_url"
            return
        try:
            resp = requests.get(url, headers=self._headers(connector), timeout=20)
            if resp.status_code >= 400:
                raise RuntimeError(f"http_{resp.status_code}")
            data = resp.json()
            self._publish(connector, data)
        except Exception as exc:
            self.status[cname]["last_error"] = str(exc)

    def run_loop(self, connector: dict) -> None:
        cname = connector.get("name", "unknown")
        interval = int(connector.get("interval_seconds", 300))
        while True:
            self._pull_once(connector)
            time.sleep(interval)

    def start_pull_threads(self) -> None:
        for connector in self.connectors:
            if not connector.get("enabled", False):
                continue
            if connector.get("mode", "pull") != "pull":
                continue
            t = threading.Thread(target=self.run_loop, args=(connector,), daemon=True, name=f"pull-{connector.get('name')}")
            t.start()


hub = ConnectorHub()
app = FastAPI(title="MASOC Connector Hub")


@app.on_event("startup")
def startup() -> None:
    hub.start_pull_threads()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "connector-hub", "connectors": len(hub.connectors)}


@app.get("/status")
def status() -> dict:
    return {"status": hub.status}


@app.post("/reload")
def reload_config() -> dict:
    hub.reload_config()
    return {"reloaded": True, "connectors": len(hub.connectors)}


@app.post("/webhook/{connector_name}")
def webhook(connector_name: str, payload: dict | list = Body(...)) -> dict:
    connector = next((c for c in hub.connectors if c.get("name") == connector_name), None)
    if not connector:
        raise HTTPException(status_code=404, detail="connector_not_found")
    count = hub._publish(connector, payload)
    return {"accepted": count, "connector": connector_name}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8092)
