import json
import os
import sqlite3
import time
from contextlib import contextmanager

import yaml
from kafka import KafkaConsumer, KafkaProducer


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def kafka_producer() -> KafkaProducer:
    brokers = env("KAFKA_BROKERS", "redpanda:9092")
    return KafkaProducer(
        bootstrap_servers=brokers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
        linger_ms=20,
    )


def kafka_consumer(topics: list[str], group_id: str) -> KafkaConsumer:
    brokers = env("KAFKA_BROKERS", "redpanda:9092")
    return KafkaConsumer(
        *topics,
        bootstrap_servers=brokers,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        max_poll_records=100,
    )


def load_yaml(path: str, default: dict) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else default
    except FileNotFoundError:
        return default


@contextmanager
def db_conn() -> sqlite3.Connection:
    db_path = env("MASOC_DB_PATH", "/data/masoc.db")
    conn = sqlite3.connect(db_path, timeout=30)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with db_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              incident_id TEXT UNIQUE,
              created_at TEXT,
              entity TEXT,
              category TEXT,
              score INTEGER,
              confidence REAL,
              status TEXT,
              payload TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              incident_id TEXT,
              action TEXT,
              decision TEXT,
              reason TEXT,
              actor TEXT,
              created_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS approvals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              incident_id TEXT,
              action TEXT,
              reason TEXT,
              status TEXT,
              requested_at TEXT,
              decided_at TEXT,
              decided_by TEXT
            )
            """
        )
        conn.commit()


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
