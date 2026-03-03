# MASOC Governance

## Human-in-the-Loop Controls
- Actions in `high_impact_actions` always require SOC analyst approval.
- Break-glass automation only allowed for extreme risk (`break_glass_score`).
- Approvals and rejections must record actor identity.

## Explainability
- Incident payload stores category, risk score, confidence, source details, and recommended action.
- Analysts should review model outputs against raw telemetry before policy changes.

## Security Controls
- Enforce MFA and RBAC on SOC interfaces.
- Enable audit retention for incident and approval records.
- Restrict SOAR API access to management subnet.
- Version-control model/policy changes and require peer review.

## Validation Cadence
- Weekly: review false positives and threshold tuning.
- Monthly: replay known attack scenarios (ransomware/auth abuse/lateral movement).
- Quarterly: red-team exercise to test automation boundaries and fail-safe behavior.
