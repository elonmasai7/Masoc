import os
import random
import time

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .common import kafka_producer, utc_now


class TelemetryEvent(BaseModel):
    source: str = Field(default="endpoint")
    event_type: str
    user: str = Field(default="unknown")
    host: str
    src_ip: str = Field(default="0.0.0.0")
    action: str = Field(default="observed")
    result: str = Field(default="unknown")
    file_mod_count: int = Field(default=0)
    process_spawn_count: int = Field(default=0)
    metadata: dict = Field(default_factory=dict)


app = FastAPI(title="MASOC Telemetry Ingestor")
producer = kafka_producer()
raw_topic = os.getenv("RAW_TOPIC", "telemetry.raw")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "telemetry-ingestor"}


@app.post("/events")
def ingest(event: TelemetryEvent) -> dict:
    payload = event.model_dump()
    payload["ingested_at"] = utc_now()
    producer.send(raw_topic, payload)
    return {"accepted": True, "topic": raw_topic}


@app.post("/simulate/ransomware")
def simulate_ransomware(host: str = "nurse-station-03", user: str = "nurse.demo") -> dict:
    for i in range(30):
        payload = {
            "source": "endpoint",
            "event_type": "file_write",
            "user": user,
            "host": host,
            "src_ip": "10.10.10.33",
            "action": "modify",
            "result": "success",
            "file_mod_count": random.randint(70, 200),
            "process_spawn_count": random.randint(8, 20),
            "metadata": {"burst_id": f"sim-{int(time.time())}", "sequence": i},
            "ingested_at": utc_now(),
        }
        producer.send(raw_topic, payload)
    return {"sent": 30, "scenario": "ransomware_precursor", "topic": raw_topic}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
