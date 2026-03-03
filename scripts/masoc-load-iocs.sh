#!/usr/bin/env sh
set -eu

INTEL_URL=${INTEL_URL:-http://localhost:8089}

curl -fsS -X POST "${INTEL_URL}/ioc/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "indicators": [
      {"indicator_type":"ip","value":"185.220.101.1","source":"otx","confidence":0.92,"tags":["c2","ransomware"]},
      {"indicator_type":"domain","value":"malicious-ehr-sync.example","source":"stix-taxii","confidence":0.85,"tags":["phishing"]},
      {"indicator_type":"user","value":"domain-admin","source":"internal","confidence":0.8,"tags":["privileged_risk"]}
    ]
  }'

echo "IOC batch loaded"
