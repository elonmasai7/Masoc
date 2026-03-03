# MedShield ZeroTrust + MASOC

This repository contains two deployable security planes for healthcare clinics:

- `MedShield ZeroTrust`: foundational controls (Wazuh, Suricata, OpenVAS, WireGuard, Restic)
- `MedShield Autonomous SOC (MASOC)`: real-time telemetry pipeline, ML detection, risk correlation, SOAR automation with human approval

## 1. ZeroTrust Stack

Main compose file: `docker-compose.yml`

1. Bootstrap:
   ```bash
   ./scripts/bootstrap.sh
   ```
2. Update secrets in `.env` and `configs/restic/restic.env`.
3. Start:
   ```bash
   docker compose --env-file .env up -d
   ```
4. Validate:
   ```bash
   ./scripts/validate.sh
   ```

## 2. MASOC Stack

MASOC compose file: `docker-compose.masoc.yml`

Services:
- `redpanda` (Kafka API)
- `telemetry-ingestor` (real-time event intake)
- `intel-ingestor` (IOC ingestion API)
- `connector-hub` (vendor connector pull/webhook stubs)
- `stream-processor` (normalization + rule signals)
- `ml-engine` (IsolationForest anomaly scoring)
- `risk-engine` (correlation + unified risk + IOC matches)
- `soar-engine` (response automation + approvals)
- `soc-dashboard` (incident/action visibility)

Start MASOC:
```bash
docker compose -f docker-compose.masoc.yml up -d --build
```

Validate MASOC:
```bash
./scripts/validate-masoc.sh
```

Load IOC sample feed:
```bash
./scripts/masoc-load-iocs.sh
```

Generate test telemetry:
```bash
./scripts/masoc-simulate.sh
```

Test connector webhook stubs:
```bash
./scripts/masoc-test-connectors.sh
```

Key endpoints:
- Telemetry ingest API: `http://localhost:8088`
- Threat intel API: `http://localhost:8089`
- Connector hub API: `http://localhost:8092`
- SOAR API: `http://localhost:8090`
- SOC dashboard: `http://localhost:8091`

## Governance and Safety

- High-impact SOAR actions require approval by policy in `configs/masoc/soar_policy.yaml`.
- SOC access should be protected with MFA and RBAC.
- Automated actions and analyst approvals are audit logged in MASOC SQLite state.

## Important Deployment Notes

- pfSense/OPNsense must run as dedicated gateway appliance/VM.
- Medical networks should remain physically/virtually segmented outside Docker.
- Enable immutable/offline backup strategy in addition to object storage.
- Apply TLS and reverse-proxy hardening for all management APIs in production.

## Documentation Map

- ZeroTrust architecture: `docs/architecture.md`
- ZeroTrust deployment: `docs/deployment-plan.md`
- pfSense/OPNsense integration: `docs/pfsense-opnsense-integration.md`
- Wazuh onboarding: `onboarding/wazuh-agents.md`
- MASOC architecture: `docs/masoc/architecture.md`
- MASOC deployment: `docs/masoc/deployment.md`
- MASOC governance: `docs/masoc/governance.md`
- MASOC enterprise expansion: `docs/masoc/enterprise-expansion.md`
- MASOC connectors: `docs/masoc/connectors.md`
