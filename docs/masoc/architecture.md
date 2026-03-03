# MASOC Architecture

## Pipeline
Telemetry Sources -> Ingest API -> Kafka Bus -> Stream Processing -> ML Detection -> Risk Correlation -> SOAR -> Dashboard/API

## Components
1. Telemetry Ingestor
- Accepts endpoint/server/network/auth events through REST.
- Publishes raw events to `telemetry.raw`.

2. Stream Processor
- Normalizes raw telemetry.
- Extracts security features.
- Emits normalized events to `telemetry.normalized`.
- Triggers rule detections (`detections.rules`) for known attack patterns.

3. ML Engine
- Consumes normalized events.
- Uses IsolationForest + behavioral heuristics.
- Produces per-event risk outputs on `detections.ml`.

4. Risk Engine
- Correlates rule + ML outputs.
- Applies asset criticality weighting.
- Deduplicates alert storms.
- Emits prioritized incidents to `incidents.risk`.

5. SOAR Engine
- Executes approved low-latency responses.
- Defers high-impact actions for human approval unless break-glass threshold is met.
- Persists incidents, actions, and approvals to audit datastore.

6. SOC Dashboard
- Displays incident timeline and response actions.
- Provides summary API for reporting and health checks.
