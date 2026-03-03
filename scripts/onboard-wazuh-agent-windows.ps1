param(
  [Parameter(Mandatory=$true)][string]$ManagerIP,
  [Parameter(Mandatory=$true)][string]$AgentGroup
)

$ErrorActionPreference = "Stop"
$installer = "$env:TEMP\wazuh-agent.msi"
$download = "https://packages.wazuh.com/4.x/windows/wazuh-agent-4.8.2-1.msi"

Invoke-WebRequest -Uri $download -OutFile $installer
Start-Process msiexec.exe -Wait -ArgumentList "/i `"$installer`" /qn WAZUH_MANAGER=$ManagerIP"

$cfg = "C:\Program Files (x86)\ossec-agent\ossec.conf"
(Get-Content $cfg) -replace "<address>.*</address>","<address>$ManagerIP</address>" | Set-Content $cfg

$auth = "C:\Program Files (x86)\ossec-agent\agent-auth.exe"
& $auth -m $ManagerIP -A $env:COMPUTERNAME

Restart-Service -Name WazuhSvc
Set-Service -Name WazuhSvc -StartupType Automatic

Write-Host "Wazuh agent onboarded to manager $ManagerIP. Group assignment ($AgentGroup) can be done from Wazuh manager UI/API."
