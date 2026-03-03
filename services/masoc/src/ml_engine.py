import json
import os
from collections import deque

import numpy as np
from sklearn.ensemble import IsolationForest

from .common import kafka_consumer, kafka_producer, utc_now


def category_from_features(features: dict) -> str:
    if features.get("file_mod_rate", 0) > 80:
        return "ransomware_precursor"
    if features.get("failed_login", 0) == 1:
        return "credential_attack"
    if features.get("process_spawn_rate", 0) > 12:
        return "lateral_movement"
    return "anomalous_behavior"


def recommended_action(category: str) -> str:
    mapping = {
        "ransomware_precursor": "isolate_endpoint",
        "credential_attack": "disable_account",
        "lateral_movement": "block_ip",
        "anomalous_behavior": "investigate",
    }
    return mapping.get(category, "investigate")


def main() -> None:
    normalized_topic = os.getenv("NORMALIZED_TOPIC", "telemetry.normalized")
    ml_topic = os.getenv("ML_TOPIC", "detections.ml")

    consumer = kafka_consumer([normalized_topic], group_id="masoc-ml-engine")
    producer = kafka_producer()

    min_train = int(os.getenv("ML_MIN_TRAIN_SAMPLES", "50"))
    history = deque(maxlen=int(os.getenv("ML_HISTORY_SIZE", "500")))
    model = None

    for message in consumer:
        event = message.value
        features = event.get("features", {})
        vector = np.array(
            [
                features.get("failed_login", 0),
                features.get("file_mod_rate", 0),
                features.get("process_spawn_rate", 0),
                features.get("off_hours", 0),
            ],
            dtype=float,
        )

        history.append(vector)

        if len(history) >= min_train and model is None:
            model = IsolationForest(contamination=0.05, random_state=42)
            model.fit(np.array(history))

        if model is not None and len(history) % 100 == 0:
            model.fit(np.array(history))

        if model is None:
            risk = min(100, int(vector[1] * 0.6 + vector[2] * 2 + vector[0] * 20))
            confidence = 0.65
        else:
            score = float(model.decision_function([vector])[0])
            # Lower decision function => more anomalous
            risk = int(max(0, min(100, (0.2 - score) * 180)))
            confidence = round(max(0.55, min(0.99, abs(score) + 0.6)), 2)

        category = category_from_features(features)
        detection = {
            "timestamp": utc_now(),
            "entity": event.get("user") if category == "credential_attack" else event.get("host"),
            "category": category,
            "risk_score": risk,
            "confidence": confidence,
            "recommended_action": recommended_action(category),
            "source_event": event,
            "threat_category": category,
        }

        producer.send(ml_topic, detection)
        print(json.dumps({"ml_sent": True, "category": category, "risk": risk}))


if __name__ == "__main__":
    main()
