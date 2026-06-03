#!/usr/bin/env bash
set -euo pipefail

PLIST_SRC="/Users/aibot/Documents/Executive Assistant/deploy/macbook-pro/com.sage.host-healthcheck.plist"
PLIST_DST="/Library/LaunchDaemons/com.sage.host-healthcheck.plist"
SCRIPT_PATH="/Users/aibot/Documents/Executive Assistant/scripts/host/verify_host_services.sh"
SCRIPT_DST="/usr/local/libexec/sage-host-healthcheck.sh"

if [[ ! -f "$PLIST_SRC" ]]; then
  echo "Missing plist: $PLIST_SRC"
  exit 1
fi

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "Missing script: $SCRIPT_PATH"
  exit 1
fi

chmod +x "$SCRIPT_PATH"

sudo mkdir -p /usr/local/libexec
sudo cp "$SCRIPT_PATH" "$SCRIPT_DST"
sudo chown root:wheel "$SCRIPT_DST"
sudo chmod 755 "$SCRIPT_DST"

sudo cp "$PLIST_SRC" "$PLIST_DST"
sudo chown root:wheel "$PLIST_DST"
sudo chmod 644 "$PLIST_DST"

sudo launchctl bootout system/com.sage.host-healthcheck >/dev/null 2>&1 || true
sudo launchctl bootstrap system "$PLIST_DST"
sudo launchctl enable system/com.sage.host-healthcheck

echo "Installed and enabled: $PLIST_DST"
