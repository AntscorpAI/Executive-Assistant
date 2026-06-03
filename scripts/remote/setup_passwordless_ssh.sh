#!/usr/bin/env bash
set -euo pipefail

HOST="${1:?Host IP or DNS required}"
USER_NAME="${2:?SSH username required}"
KEY_PATH="${3:-$HOME/.ssh/id_ed25519.pub}"

if [[ ! -f "$KEY_PATH" ]]; then
  echo "Public key not found at $KEY_PATH"
  exit 1
fi

mkdir -p "$HOME/.ssh"
ssh-keyscan -H "$HOST" >> "$HOME/.ssh/known_hosts" 2>/dev/null || true

echo "Installing public key on ${USER_NAME}@${HOST}."
echo "You may be prompted once for the SSH password."

PUB_KEY_CONTENT="$(cat "$KEY_PATH")"
ssh "${USER_NAME}@${HOST}" "mkdir -p ~/.ssh && chmod 700 ~/.ssh && grep -qxF '$PUB_KEY_CONTENT' ~/.ssh/authorized_keys || echo '$PUB_KEY_CONTENT' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

echo "Key installed. Testing passwordless login..."
ssh -o BatchMode=yes "${USER_NAME}@${HOST}" "echo Passwordless SSH is configured for \\$(hostname)"
