# Wazuh Agent Onboarding

## Manager Address
- Wazuh manager: `10.10.50.10`
- Agent registration port: `1515/tcp`
- Event port: `1514/udp`

## Linux Endpoint Onboarding
Run:
```bash
sudo ./scripts/onboard-wazuh-agent-linux.sh <manager_ip> <agent_group>
```
Example:
```bash
sudo ./scripts/onboard-wazuh-agent-linux.sh 10.10.50.10 linux-workstations
```

## Windows Endpoint Onboarding (PowerShell as Admin)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\scripts\onboard-wazuh-agent-windows.ps1 -ManagerIP 10.10.50.10 -AgentGroup windows-workstations
```

## Post-Onboarding Validation
1. Check agent appears in Wazuh dashboard and status is `Active`.
2. Trigger a safe test event (failed login or EICAR in isolated test endpoint).
3. Confirm alert ingestion and correlation.
