# Tool Deployment Plan

## 1. Prerequisites
- Linux host (8+ vCPU, 16+ GB RAM, 250+ GB SSD recommended).
- Docker Engine and Docker Compose plugin.
- Dedicated pfSense/OPNsense gateway with VLAN-capable switches/APs.
- Internal PKI or trusted certificates for management endpoints.

## 2. Prepare Environment
1. Run `./scripts/bootstrap.sh`.
2. Set strong secrets in `.env` and `configs/restic/restic.env`.
3. Create DNS records (for example `siem.medshield.local`, `vpn.medshield.local`).
4. Restrict host firewall to management subnet.

## 3. Deploy Security Stack
1. Pull images: `docker compose pull`.
2. Start stack: `docker compose up -d`.
3. Confirm service status: `docker compose ps`.
4. Run validation: `./scripts/validate.sh`.

## 4. Integrate with Clinic Environment
1. Install Wazuh agents on all endpoints/servers.
2. Forward firewall, VPN, and server logs into Wazuh.
3. Configure SPAN/mirror port to Suricata container host NIC.
4. Import asset list in OpenVAS and schedule weekly scans.
5. Provision WireGuard peer profiles for remote staff only.

## 5. Production Hardening
1. Replace default certificates and enforce TLS 1.2+.
2. Restrict admin interfaces to `VLAN50`.
3. Set alert routing (email, webhook, ticketing).
4. Configure immutable/offline backup target.
5. Enable audit retention policy (minimum 1 year).
