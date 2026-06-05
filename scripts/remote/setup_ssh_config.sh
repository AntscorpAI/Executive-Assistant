#!/usr/bin/env bash
set -euo pipefail

DB_HOST_ALIAS="${DB_HOST_ALIAS:-sage-db-host}"
DB_HOST_NAME="${DB_HOST_NAME:-remote-db-host}"
DB_HOST_USER="${DB_HOST_USER:-sage}"
LLM_HOST_ALIAS="${LLM_HOST_ALIAS:-sage-llm-host}"
LLM_HOST_NAME="${LLM_HOST_NAME:-remote-ollama-host}"
LLM_USER="${LLM_USER:-$USER}"

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

ensure_block "$DB_HOST_ALIAS" "$DB_HOST_NAME" "$DB_HOST_USER"
ensure_block "$LLM_HOST_ALIAS" "$LLM_HOST_NAME" "$LLM_USER"

echo "SSH config updated at $CONFIG_FILE"
echo "Use aliases: ssh ${DB_HOST_ALIAS}, ssh ${LLM_HOST_ALIAS}"
