# pfSense/OPNsense VLAN Integration Guide

## VLAN Design
- VLAN10 `STAFF` - `10.10.10.0/24`
- VLAN20 `SERVERS` - `10.10.20.0/24`
- VLAN30 `MEDICAL` - `10.10.30.0/24`
- VLAN40 `GUEST` - `10.10.40.0/24`
- VLAN50 `MGMT` - `10.10.50.0/24`

## 1. Create VLAN Interfaces
1. In pfSense/OPNsense, create VLANs 10/20/30/40/50 on the LAN trunk interface.
2. Assign each VLAN to an interface.
3. Configure static interface IPs:
- STAFF `10.10.10.1/24`
- SERVERS `10.10.20.1/24`
- MEDICAL `10.10.30.1/24`
- GUEST `10.10.40.1/24`
- MGMT `10.10.50.1/24`

## 2. DHCP Scopes
- Enable DHCP per VLAN except where static-only is required (for servers/medical assets if policy requires).
- Reserve static mappings for SIEM host, backup host, scanners, and medical devices.

## 3. Firewall Aliases
Create aliases from `configs/pfsense/aliases.md`:
- `RFC1918_NETS`
- `MGMT_HOSTS`
- `CRITICAL_SERVERS`
- `EHR_SERVERS`

## 4. Baseline Firewall Rules
Apply rules from `configs/pfsense/ruleset.md`:
- Default deny all inter-VLAN traffic.
- Allow MGMT to all internal VLANs on admin ports only.
- Allow STAFF to required EHR/application ports in SERVERS.
- Deny STAFF to MEDICAL by default.
- Deny GUEST to any RFC1918 destination.
- Allow MEDICAL only to required server destinations.

## 5. IDS/IPS Integration
1. Enable Suricata package on pfSense/OPNsense OR mirror trunk traffic to the Docker Suricata host.
2. For SPAN/mirror mode, send mirrored packets to the host NIC used by `suricata` container.
3. Forward Suricata eve logs to Wazuh manager using Filebeat/syslog.

## 6. VPN Integration
- Keep WireGuard UDP `51820` open from WAN to VPN host.
- Set WireGuard peer allowed networks to STAFF and SERVERS only unless explicitly approved.
- Require MFA in upstream identity provider for VPN portal/workflow.

## 7. Logging and Audit
- Forward firewall and VPN logs to Wazuh.
- Retain at least 12 months of access and admin-change logs.
