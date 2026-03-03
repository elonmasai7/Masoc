#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID}" -ne 0 ]; then
  echo "Run as root (sudo)."
  exit 1
fi

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <manager_ip> <agent_group>"
  exit 1
fi

MANAGER_IP="$1"
AGENT_GROUP="$2"

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y curl gnupg lsb-release
  curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --dearmor >/usr/share/keyrings/wazuh.gpg
  echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" >/etc/apt/sources.list.d/wazuh.list
  apt-get update
  WAZUH_MANAGER="$MANAGER_IP" apt-get install -y wazuh-agent
elif command -v yum >/dev/null 2>&1; then
  rpm --import https://packages.wazuh.com/key/GPG-KEY-WAZUH
  cat >/etc/yum.repos.d/wazuh.repo <<REPO
[wazuh]
gpgcheck=1
gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH
enabled=1
name=EL-
baseurl=https://packages.wazuh.com/4.x/yum/
protect=1
REPO
  WAZUH_MANAGER="$MANAGER_IP" yum install -y wazuh-agent
else
  echo "Unsupported package manager. Install wazuh-agent manually."
  exit 1
fi

sed -i "s|<address>.*</address>|<address>${MANAGER_IP}</address>|" /var/ossec/etc/ossec.conf

/var/ossec/bin/agent-auth -m "$MANAGER_IP" -A "$(hostname)" || true
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl restart wazuh-agent

if [ -x /var/ossec/bin/agent_groups ]; then
  /var/ossec/bin/agent_groups -a -g "$AGENT_GROUP" -q || true
fi

echo "Wazuh agent onboarded to manager ${MANAGER_IP}."
