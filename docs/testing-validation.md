# Testing and Validation Procedures

## Baseline Availability Tests
1. `docker compose ps` shows all services healthy/running.
2. Wazuh dashboard login succeeds from management network.
3. OpenVAS UI is reachable on configured port.
4. WireGuard handshake succeeds for a test user.

## Security Control Tests
1. Failed login test:
- Trigger repeated failed logins on a test endpoint.
- Verify Wazuh alert generated and notified.

2. Malware simulation:
- Use EICAR test file on isolated test endpoint.
- Confirm endpoint alert in Wazuh.

3. Network IDS detection:
- Send controlled scan traffic from test host.
- Validate Suricata alert appears in SIEM.

4. Vulnerability detection:
- Run OpenVAS scan against known vulnerable lab target.
- Ensure findings include CVE references and severity.

## Backup and Recovery Tests
1. Run on-demand backup:
- `docker compose exec restic-runner /opt/backup.sh`
2. Restore sample dataset to alternate path.
3. Validate file hashes and application readability.
4. Record RTO/RPO metrics in `checks/restore-evidence.md`.

## Audit Evidence
Capture and retain:
- Screenshots of alerts and remediation tickets.
- Backup job logs and restore logs.
- Change records for firewall rules and RBAC updates.
