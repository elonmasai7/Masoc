# MASOC Deployment

## Prerequisites
- Docker Engine + Compose plugin
- 4+ vCPU, 8+ GB RAM for MASOC stack alone
- `.env` configured with thresholds and clinic network assumptions

## Deploy
1. Build and start services:
```bash
docker compose -f docker-compose.masoc.yml up -d --build
```
2. Validate service health:
```bash
./scripts/validate-masoc.sh
```
3. Load sample IOCs:
```bash
./scripts/masoc-load-iocs.sh
```
4. Generate synthetic threat flow:
```bash
./scripts/masoc-simulate.sh
```
5. Inspect:
- `http://localhost:8091` for dashboard
- `http://localhost:8090/incidents` for incident feed
- `http://localhost:8090/approvals/pending` for queued approvals

## Production Hardening
- Place ingestor/SOAR/dashboard behind reverse proxy with TLS.
- Integrate SSO + MFA for SOC users.
- Move SQLite to managed PostgreSQL for multi-node scale.
- Replace simulated SOAR actions with firewall/IdP/EDR API integrations.
- Wire STIX/TAXII feed puller into `intel-ingestor`.
