#!/usr/bin/env sh
set -eu

fail=0

check() {
  name="$1"
  cmd="$2"
  if sh -c "$cmd" >/dev/null 2>&1; then
    echo "[PASS] $name"
  else
    echo "[FAIL] $name"
    fail=1
  fi
}

check "masoc compose syntax" "docker compose -f docker-compose.masoc.yml config"
check "redpanda running" "docker compose -f docker-compose.masoc.yml ps redpanda | grep -q running"
check "telemetry-ingestor running" "docker compose -f docker-compose.masoc.yml ps telemetry-ingestor | grep -q running"
check "intel-ingestor running" "docker compose -f docker-compose.masoc.yml ps intel-ingestor | grep -q running"
check "connector-hub running" "docker compose -f docker-compose.masoc.yml ps connector-hub | grep -q running"
check "stream-processor running" "docker compose -f docker-compose.masoc.yml ps stream-processor | grep -q running"
check "ml-engine running" "docker compose -f docker-compose.masoc.yml ps ml-engine | grep -q running"
check "risk-engine running" "docker compose -f docker-compose.masoc.yml ps risk-engine | grep -q running"
check "soar-engine running" "docker compose -f docker-compose.masoc.yml ps soar-engine | grep -q running"
check "soc-dashboard running" "docker compose -f docker-compose.masoc.yml ps soc-dashboard | grep -q running"
check "ingestor health" "curl -fsS http://localhost:8088/health"
check "intel health" "curl -fsS http://localhost:8089/health"
check "connector health" "curl -fsS http://localhost:8092/health"
check "soar health" "curl -fsS http://localhost:8090/health"
check "dashboard health" "curl -fsS http://localhost:8091/health"

if [ "$fail" -ne 0 ]; then
  echo "MASOC validation failed"
  exit 1
fi

echo "MASOC validation passed"
