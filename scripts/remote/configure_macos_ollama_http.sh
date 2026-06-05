#!/usr/bin/env bash
set -euo pipefail

LLM_HOST_ALIAS="${1:-sage-llm-host}"
LLM_SSH_USER="${2:-}"
LLM_HOST_IP="${3:-127.0.0.1}"

SSH_TARGET="$LLM_HOST_ALIAS"
if [[ -n "$LLM_SSH_USER" ]]; then
  SSH_TARGET="${LLM_SSH_USER}@${LLM_HOST_ALIAS}"
fi

echo "Configuring Ollama HTTP listener on ${SSH_TARGET}"
ssh "$SSH_TARGET" "
  set -euo pipefail
  mkdir -p ~/.sage-llm
  OLLAMA_BIN=\"\$(command -v ollama || true)\"
  if [[ -z \"\$OLLAMA_BIN\" ]]; then
    if [[ -x /opt/homebrew/bin/ollama ]]; then
      OLLAMA_BIN=/opt/homebrew/bin/ollama
    elif [[ -x /usr/local/bin/ollama ]]; then
      OLLAMA_BIN=/usr/local/bin/ollama
    elif [[ -x /Applications/Ollama.app/Contents/Resources/ollama ]]; then
      OLLAMA_BIN=/Applications/Ollama.app/Contents/Resources/ollama
    else
      echo 'ERROR: ollama binary not found on the remote macOS host'
      exit 1
    fi
  fi
  cat > ~/Library/LaunchAgents/com.ollama.server.plist <<'PLIST'
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
  <key>Label</key>
  <string>com.ollama.server</string>
  <key>ProgramArguments</key>
  <array>
    <string>__OLLAMA_BIN__</string>
    <string>serve</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>OLLAMA_HOST</key>
    <string>0.0.0.0:11434</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/ollama.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/ollama.error.log</string>
</dict>
</plist>
PLIST
  sed -i.bak \"s#__OLLAMA_BIN__#\$OLLAMA_BIN#g\" ~/Library/LaunchAgents/com.ollama.server.plist
  launchctl unload ~/Library/LaunchAgents/com.ollama.server.plist >/dev/null 2>&1 || true
  launchctl load -w ~/Library/LaunchAgents/com.ollama.server.plist
  launchctl setenv OLLAMA_HOST 0.0.0.0:11434 || true
  sleep 2
  curl -sS --max-time 8 http://127.0.0.1:11434/api/tags | head -c 800
  echo
"

echo "Validating remote HTTP from local machine"
curl -sS --max-time 8 http://${LLM_HOST_IP}:11434/api/tags | head -c 800
echo
