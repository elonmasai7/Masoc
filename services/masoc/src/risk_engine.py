import hashlib
import json
import os
import time
from collections import defaultdict, deque

from .common import kafka_consumer, kafka_producer, load_yaml, utc_now


def extract_ioc_values(event: dict) -> set[str]:
    values = set()
    for key in ("entity", "src_ip", "user", "host", "domain", "hash"):
        value = event.get(key)
        if isinstance(value, str) and value:
            values.add(value)

    details = event.get("details", {}) if isinstance(event.get("details"), dict) else {}
    for key in ("src_ip", "user", "host", "domain", "hash"):
        value = details.get(key)
        if isinstance(value, str) and value:
            values.add(value)

    source_event = event.get("source_event", {}) if isinstance(event.get("source_event"), dict) else {}
    for key in ("src_ip", "user", "host"):
        value = source_event.get(key)
        if isinstance(value, str) and value:
            values.add(value)

    metadata = source_event.get("metadata", {}) if isinstance(source_event.get("metadata"), dict) else {}
    for key in ("domain", "hash", "sha256"):
        value = metadata.get(key)
        if isinstance(value, str) and value:
            values.add(value)
    return values


def main() -> None:
    ml_topic = os.getenv("ML_TOPIC", "detections.ml")
    rules_topic = os.getenv("RULES_TOPIC", "detections.rules")
    intel_topic = os.getenv("INTEL_TOPIC", "threat.intel")
    incident_topic = os.getenv("INCIDENT_TOPIC", "incidents.risk")

    asset_cfg_path = os.getenv("ASSET_CRITICALITY_PATH", "/app/config/asset_criticality.yaml")
    cfg = load_yaml(asset_cfg_path, default={"criticality": {}})
    criticality = cfg.get("criticality", {})

    consumer = kafka_consumer([ml_topic, rules_topic, intel_topic], group_id="masoc-risk-engine")
    producer = kafka_producer()

    recent = defaultdict(deque)
    dedup = {}
    ioc_set = set()
    dedup_window = int(os.getenv("RISK_DEDUP_SECONDS", "300"))

    for message in consumer:
        event = message.value

        if message.topic == intel_topic:
            ioc_value = str(event.get("value", "")).strip()
            if ioc_value:
                ioc_set.add(ioc_value)
                print(json.dumps({"ioc_loaded": ioc_value, "count": len(ioc_set)}))
            continue

        entity = event.get("entity", "unknown")
        category = event.get("category", event.get("threat_category", "unknown"))

        base = int(event.get("risk_score", event.get("score", 50)))
        confidence = float(event.get("confidence", 0.7))

        multiplier = float(criticality.get(entity, criticality.get("default", 1.0)))
        now = time.time()
        recent[entity].append(now)
        while recent[entity] and now - recent[entity][0] > 600:
            recent[entity].popleft()

        repeat_bonus = min(20, len(recent[entity]) * 2)

        hits = [value for value in extract_ioc_values(event) if value in ioc_set]
        ioc_bonus = 25 if hits else 0

        unified = int(min(100, base * multiplier + repeat_bonus + ioc_bonus))

        fingerprint = hashlib.sha256(f"{entity}:{category}:{base//10}".encode("utf-8")).hexdigest()
        if fingerprint in dedup and now - dedup[fingerprint] < dedup_window:
            continue
        dedup[fingerprint] = now

        incident = {
            "incident_id": f"inc-{int(now * 1000)}",
            "timestamp": utc_now(),
            "entity": entity,
            "category": category,
            "risk_score": unified,
            "confidence": round(confidence, 2),
            "recommended_action": event.get("recommended_action", "investigate"),
            "source": "risk-engine",
            "ioc_hits": hits,
            "details": event,
        }

        producer.send(incident_topic, incident)
        print(json.dumps({"incident_id": incident["incident_id"], "score": unified, "ioc_hits": len(hits)}))


if __name__ == "__main__":
    main()
