# Configuration Checklist

## Zero Trust and IAM
- [ ] MFA enforced for all user logins (no exceptions).
- [ ] RBAC implemented per `policies/rbac-matrix.md`.
- [ ] Shared accounts eliminated.
- [ ] Privileged access separated from standard user accounts.

## Network and Remote Access
- [ ] VLAN segmentation configured and verified.
- [ ] Default deny inter-VLAN policies enabled.
- [ ] WireGuard profiles issued only to approved staff.
- [ ] Guest WiFi isolated from internal systems.

## Endpoint and Server Security
- [ ] Wazuh agent installed on all assets.
- [ ] Full disk encryption enabled everywhere.
- [ ] Patch automation enabled and monitored.
- [ ] Local host firewall enabled on all endpoints.

## Detection and Monitoring
- [ ] Suricata receiving mirrored traffic.
- [ ] Wazuh alerts mapped to severity and on-call routing.
- [ ] File integrity monitoring enabled for critical systems.
- [ ] Failed login, privilege escalation, and malware alerts tested.

## Data Protection and Backup
- [ ] Restic repository encrypted and tested.
- [ ] 3-2-1 backup policy documented.
- [ ] Offline or immutable copy validated.
- [ ] Monthly restore drill completed and recorded.

## Email Security
- [ ] SPF configured for all sending domains.
- [ ] DKIM signing enabled.
- [ ] DMARC policy set to quarantine/reject with reporting.

## Governance and Compliance
- [ ] Audit logs retained for required period.
- [ ] Security awareness training scheduled monthly.
- [ ] Incident response contacts validated quarterly.
