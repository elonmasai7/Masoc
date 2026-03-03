#!/usr/bin/env sh
set -eu

API_URL=${API_URL:-http://localhost:8088}

curl -fsS -X POST "${API_URL}/events" \
  -H "Content-Type: application/json" \
  -d '{
    "source":"endpoint",
    "event_type":"auth",
    "user":"domain-admin",
    "host":"admin-jump-01",
    "src_ip":"185.220.101.1",
    "action":"login",
    "result":"failed",
    "file_mod_count":0,
    "process_spawn_count":2,
    "metadata":{"reason":"bad_password"}
  }'

curl -fsS -X POST "${API_URL}/events" \
  -H "Content-Type: application/json" \
  -d '{
    "source":"email_gateway",
    "event_type":"email_click",
    "user":"nurse.demo",
    "host":"nurse-station-03",
    "src_ip":"10.10.10.33",
    "action":"clicked",
    "result":"success",
    "file_mod_count":0,
    "process_spawn_count":1,
    "metadata":{"domain":"malicious-ehr-sync.example"}
  }'

curl -fsS -X POST "${API_URL}/simulate/ransomware" -H "Content-Type: application/json"

echo "Simulation events sent"
