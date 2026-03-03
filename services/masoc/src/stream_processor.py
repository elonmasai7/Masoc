import json
import os
import time
from collections import defaultdict, deque

from .common import kafka_consumer, kafka_producer, utc_now


def off_hours() -> int:
    hour = time.gmtime().tm_hour
    return 1 if hour < 5 or hour > 20 else 0


def normalize(event: dict) -> dict:
    return {
        "event_id": f"evt-{int(time.time() * 1000)}",
        "timestamp": event.get("ingested_at", utc_now()),
        "source": event.get("source", "unknown"),
        "event_type": event.get("event_type", "unknown"),
        "user": event.get("user", "unknown"),
        "host": event.get("host", "unknown"),
        "src_ip": event.get("src_ip", "0.0.0.0"),
        "result": event.get("result", "unknown"),
        "file_mod_count": int(event.get("file_mod_count", 0)),
        "process_spawn_count": int(event.get("process_spawn_count", 0)),
        "metadata": event.get("metadata", {}),
    }


def extract_features(event: dict) -> dict:
    failed_login = 1 if event["event_type"] == "auth" and event["result"] == "failed" else 0
    return {
        **event,
        "features": {
            "failed_login": failed_login,
            "file_mod_rate": event["file_mod_count"],
            "process_spawn_rate": event["process_spawn_count"],
            "off_hours": off_hours(),
        },
    }


def main() -> None:
    raw_topic = os.getenv("RAW_TOPIC", "telemetry.raw")
    normalized_topic = os.getenv("NORMALIZED_TOPIC", "telemetry.normalized")
    rules_topic = os.getenv("RULES_TOPIC", "detections.rules")

    producer = kafka_producer()
    consumer = kafka_consumer([raw_topic], group_id="masoc-stream-processor")

    failed_logins = defaultdict(deque)
    burst_window_s = int(os.getenv("FAILED_LOGIN_WINDOW_SEC", "300"))
    burst_threshold = int(os.getenv("FAILED_LOGIN_THRESHOLD", "6"))

    for message in consumer:
        raw = message.value
        normalized = extract_features(normalize(raw))
        producer.send(normalized_topic, normalized)

        if normalized["features"]["failed_login"]:
            user = normalized["user"]
            now = time.time()
            failed_logins[user].append(now)
            while failed_logins[user] and now - failed_logins[user][0] > burst_window_s:
                failed_logins[user].popleft()
            if len(failed_logins[user]) >= burst_threshold:
                rule_hit = {
                    "timestamp": utc_now(),
                    "rule_id": "R-FAILED-LOGIN-BURST",
                    "entity": user,
                    "category": "credential_attack",
                    "score": 65,
                    "confidence": 0.91,
                    "details": {
                        "window_sec": burst_window_s,
                        "failed_count": len(failed_logins[user]),
                    },
                }
                producer.send(rules_topic, rule_hit)

        # Burst file-write heuristic for ransomware precursor
        if normalized["file_mod_count"] > 80:
            producer.send(
                rules_topic,
                {
                    "timestamp": utc_now(),
                    "rule_id": "R-FILE-BURST",
                    "entity": normalized["host"],
                    "category": "ransomware_precursor",
                    "score": 80,
                    "confidence": 0.88,
                    "details": {
                        "host": normalized["host"],
                        "file_mod_count": normalized["file_mod_count"],
                    },
                },
            )

        print(json.dumps({"status": "processed", "event_id": normalized["event_id"]}))


if __name__ == "__main__":
    main()
