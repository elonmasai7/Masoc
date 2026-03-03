# MASOC Enterprise Expansion (Healthcare-Focused)

## Added Integration Surfaces
1. Identity and access security
- Okta / Microsoft Entra ID integration for adaptive MFA and conditional access signals.
- PAM/JIT hooks: privileged account events can be ingested and correlated at higher risk.

2. Advanced endpoint security
- CrowdStrike/SentinelOne detections can be forwarded into telemetry ingestion API.
- MASOC correlation can combine EDR severity with user/device behavioral anomalies.

3. NDR and medical device visibility
- Darktrace/ExtraHop outputs can be posted as telemetry events for east-west anomaly scoring.
- Supports agentless monitoring use cases for clinical IoT and legacy medical devices.

4. Cloud and container security
- Wiz/Prisma Cloud findings can be ingested as events and tied to incident priorities.

5. Email security
- Proofpoint/Mimecast verdicts can be posted as `email_gateway` events to catch phishing-to-endpoint kill chains.

6. Threat intelligence
- New `intel-ingestor` service accepts IOC feeds and pushes to `threat.intel`.
- Risk engine now raises incident scores automatically on IOC matches.

7. DLP and data exfiltration
- Varonis/Forcepoint alerts can be ingested and mapped to `data_exfiltration` categories.

## Expansion Phases
Phase 1:
- NDR integration
- Email security integration
- PAM/JIT signals

Phase 2:
- Deception signals
- DLP incidents
- Automated IOC feed ingestion (STIX/TAXII)

Phase 3:
- Graph attack-path analytics
- Breach simulation feedback loop
- AI-assisted exposure scoring and drift monitoring

## Governance Guardrails
- Human approval required for high-impact SOAR actions.
- Explainability retained via incident payloads and action logs.
- Quarterly red-team validation required before wider automation scope.
