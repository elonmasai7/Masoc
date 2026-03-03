# pfSense/OPNsense Alias Definitions

Create these aliases in Firewall -> Aliases:

- `RFC1918_NETS`
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`

- `MGMT_HOSTS`
  - `10.10.50.10` (Wazuh)
  - `10.10.50.11` (OpenVAS)
  - `10.10.50.12` (Backup host)

- `CRITICAL_SERVERS`
  - `10.10.20.20` (EHR app)
  - `10.10.20.21` (DB)
  - `10.10.20.22` (AD/IdP)

- `EHR_SERVERS`
  - `10.10.20.20`
  - `10.10.20.21`
