#!/usr/bin/env bash
set -euo pipefail

UBUNTU2_USER="${UBUNTU2_USER:-vishnu}"
LLM_USER="${LLM_USER:-sanjay}"

mkdir -p "$HOME/.ssh/controlmasters"
mkdir -p "$HOME/.ssh"

CONFIG_FILE="$HOME/.ssh/config"

ensure_block() {
  local host_alias="$1"
  local host_name="$2"
  local user_name="$3"

  if grep -q "^Host ${host_alias}$" "$CONFIG_FILE" 2>/dev/null; then
    return
  fi

  cat >> "$CONFIG_FILE" <<EOF

Host ${host_alias}
  HostName ${host_name}
  User ${user_name}
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
  ControlMaster auto
  ControlPath ~/.ssh/controlmasters/%r@%h:%p
  ControlPersist 10m
EOF
}

touch "$CONFIG_FILE"
chmod 600 "$CONFIG_FILE"

ensure_block "ubuntu2" "100.98.104.84" "$UBUNTU2_USER"
ensure_block "llm-mbp" "100.70.5.76" "$LLM_USER"
ensure_block "llm-server-macbook-pro" "100.70.5.76" "$LLM_USER"

echo "SSH config updated at $CONFIG_FILE"
echo "Use aliases: ssh ubuntu2, ssh llm-mbp, ssh llm-server-macbook-pro"
