import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .common import kafka_producer, utc_now


class IOC(BaseModel):
    indicator_type: str = Field(description="ip|domain|hash|user")
    value: str
    source: str = Field(default="manual")
    confidence: float = Field(default=0.8)
    tags: list[str] = Field(default_factory=list)


class IOCBatch(BaseModel):
    indicators: list[IOC]


app = FastAPI(title="MASOC Threat Intel Ingestor")
producer = kafka_producer()
intel_topic = os.getenv("INTEL_TOPIC", "threat.intel")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "intel-ingestor"}


@app.post("/ioc")
def push_ioc(ioc: IOC) -> dict:
    payload = ioc.model_dump()
    payload["timestamp"] = utc_now()
    producer.send(intel_topic, payload)
    return {"accepted": True, "topic": intel_topic}


@app.post("/ioc/bulk")
def push_ioc_bulk(batch: IOCBatch) -> dict:
    for ioc in batch.indicators:
        payload = ioc.model_dump()
        payload["timestamp"] = utc_now()
        producer.send(intel_topic, payload)
    return {"accepted": len(batch.indicators), "topic": intel_topic}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8089)
