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

check "docker compose file syntax" "docker compose config"
check "wazuh-manager running" "docker compose ps wazuh-manager | grep -q running"
check "wazuh-dashboard running" "docker compose ps wazuh-dashboard | grep -q running"
check "suricata running" "docker compose ps suricata | grep -q running"
check "openvas running" "docker compose ps openvas | grep -q running"
check "wireguard running" "docker compose ps wireguard | grep -q running"
check "restic-runner running" "docker compose ps restic-runner | grep -q running"

if [ "$fail" -ne 0 ]; then
  echo "Validation failed. Review docker compose logs and docs/testing-validation.md"
  exit 1
fi

echo "All checks passed."
