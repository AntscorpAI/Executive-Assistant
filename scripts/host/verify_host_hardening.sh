#!/usr/bin/env bash
set -euo pipefail

echo "== launch agents =="
launchctl print gui/"$(id -u)"/com.sage.ai.stack | grep -E "state =|last exit code"
launchctl print gui/"$(id -u)"/com.sage.ai.keepawake | grep -E "state =|pid =|last exit code"
launchctl print gui/"$(id -u)"/com.sage.ai.watchdog | grep -E "state =|last exit code"

echo
echo "== caffeinate =="
pgrep -fl caffeinate || true

echo
echo "== assertions =="
pmset -g assertions | sed -n '1,80p'

echo
echo "== api health =="
curl -sS http://localhost/api/health
echo