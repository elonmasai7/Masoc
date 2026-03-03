# Incident Response Playbook

## Scope
Applies to malware, ransomware, unauthorized access, data exfiltration, and service outages.

## Phase 1: Detect
- Trigger sources: Wazuh, Suricata, OpenVAS, staff report.
- Triage severity and identify impacted systems/accounts.

## Phase 2: Contain
- Isolate affected endpoint/server from network.
- Disable or reset compromised accounts.
- Block indicators (IP, domain, hash) at firewall and endpoint controls.

## Phase 3: Eradicate
- Remove malware/persistence artifacts.
- Patch exploited vulnerabilities.
- Rotate credentials and revoke stale sessions/tokens.

## Phase 4: Recover
- Restore from verified clean backup.
- Rejoin systems to network after validation.
- Increase monitoring for 72 hours post-recovery.

## Phase 5: Report and Improve
- Document timeline, root cause, impact, and actions.
- Notify stakeholders and regulators where required.
- Update detections, controls, and playbooks.

## Ransomware-Specific Procedure
1. Immediately isolate infected hosts and shared storage.
2. Disable SMB shares and remote admin protocols where needed.
3. Preserve forensic artifacts before reimaging.
4. Recover from immutable/offline backup only.
5. Validate no reinfection indicators before business resumption.
