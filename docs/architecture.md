# MedShield ZeroTrust Architecture (Logical)

## Design Goals
- Assume breach: no implicit trust between users, devices, apps, or networks.
- Enforce strong identity with MFA and least privilege RBAC.
- Detect quickly and recover safely from ransomware and operational outages.
- Keep operating cost low using open-source tooling.

## Logical Network Segmentation
- `VLAN10 Staff`: clinician/admin endpoints.
- `VLAN20 Servers`: EHR, file, application, and authentication servers.
- `VLAN30 Medical`: imaging, IoT medical devices, analyzers.
- `VLAN40 Guest`: internet-only patient/visitor WiFi.
- `VLAN50 Management/SOC`: SIEM, scanner, backup orchestration.

Traffic policy baseline:
- Deny any-to-any by default.
- Allow only required app flows (documented per asset).
- No direct `VLAN10 -> VLAN30` unless explicit medical workflow requires it.
- `VLAN40` blocked from all internal VLANs.
- Administration to infrastructure only from `VLAN50` with MFA.

## Layered Controls
1. Perimeter and segmentation:
- pfSense/OPNsense handles WAN edge, VLAN routing, ACLs, IDS integration, and VPN termination fallback.

2. Identity and access:
- Central IdP + MFA for all users.
- RBAC roles (Clinician, Nurse, Billing, IT Admin, Security Analyst, Vendor).
- Privileged access via dedicated admin accounts, never shared.

3. Endpoint protection:
- Wazuh agents on Windows/Linux/Mac endpoints and servers.
- Full-disk encryption required (BitLocker, FileVault, LUKS).
- Automated OS and third-party patching.

4. Detection and monitoring:
- Suricata NIDS sensor from mirrored traffic.
- Wazuh SIEM for logs, FIM, vuln detection, and alerting.
- OpenVAS for scheduled authenticated and unauthenticated scans.

5. Data resilience:
- Restic encrypted backups following 3-2-1 (local + offsite + offline/immutable).
- Monthly restore drills and evidence capture.

## Containerized Security Plane
`docker-compose.yml` deploys:
- Wazuh indexer, manager, dashboard
- Suricata sensor
- OpenVAS scanner
- WireGuard VPN
- Restic backup runner

Note: firewall/VLAN enforcement remains on dedicated network infrastructure, not in Docker.
