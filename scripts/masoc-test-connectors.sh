#!/usr/bin/env sh
set -eu

HUB_URL=${HUB_URL:-http://localhost:8092}

curl -fsS -X POST "${HUB_URL}/webhook/entra" -H "Content-Type: application/json" -d '{"user":"alice.clinic","host":"laptop-22","ip":"10.10.10.22","action":"login","status":"failed"}'
curl -fsS -X POST "${HUB_URL}/webhook/crowdstrike" -H "Content-Type: application/json" -d '{"user":"alice.clinic","host":"laptop-22","ip":"10.10.10.22","event":"malware_blocked","status":"blocked","process_spawn_count":5}'
curl -fsS -X POST "${HUB_URL}/webhook/proofpoint" -H "Content-Type: application/json" -d '{"user":"nurse.demo","host":"nurse-station-03","source_ip":"198.51.100.44","event":"phish_click","status":"clicked","domain":"malicious-ehr-sync.example"}'
curl -fsS -X POST "${HUB_URL}/webhook/taxii" -H "Content-Type: application/json" -d '{"indicator_type":"domain","value":"malicious-ehr-sync.example","confidence":0.9,"tags":["phishing"]}'

echo "Connector webhook stubs sent"
