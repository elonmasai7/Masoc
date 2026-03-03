# MASOC Connector Stubs

The `connector-hub` service provides two integration modes so external security tools land in MASOC automatically:

1. Pull mode
- Scheduled HTTP pulls from configured vendor APIs.
- Connectors defined in `configs/masoc/connectors.yaml`.
- Output:
  - Identity/EDR/Email events -> `telemetry.raw`
  - STIX/TAXII indicators -> `threat.intel`

2. Webhook mode
- POST vendor payloads to `http://localhost:8092/webhook/{connector_name}`.
- Useful when vendor tool supports push/webhook delivery.

## Included Connector Stubs
- `entra` (Microsoft Entra ID)
- `okta`
- `crowdstrike`
- `sentinelone`
- `proofpoint`
- `mimecast`
- `taxii`

## Enable a Connector
1. Set endpoint/token values in `.env`.
2. In `configs/masoc/connectors.yaml`, set `enabled: true` for the connector.
3. Restart connector hub:
```bash
docker compose -f docker-compose.masoc.yml restart connector-hub
```
4. Check status:
```bash
curl -s http://localhost:8092/status
```

## Quick Stub Test
Send sample events to each webhook:
```bash
./scripts/masoc-test-connectors.sh
```
