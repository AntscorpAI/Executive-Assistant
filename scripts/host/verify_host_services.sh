#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${LOG_FILE:-/var/log/sage-host-healthcheck.log}"
SAGE_HEALTH_URL="${SAGE_HEALTH_URL:-http://127.0.0.1:8000/api/health}"
OPENCLAW_HOST="${OPENCLAW_HOST:-127.0.0.1}"
OPENCLAW_PORT="${OPENCLAW_PORT:-19001}"
SSH_HOST="${SSH_HOST:-127.0.0.1}"
SSH_PORT="${SSH_PORT:-22}"

mkdir -p "$(dirname "$LOG_FILE")"

timestamp() {
  date '+%Y-%m-%d %H:%M:%S %z'
}

log() {
  local level="$1"
  local message="$2"
  echo "$(timestamp) [$level] $message" | tee -a "$LOG_FILE"
}

check_port() {
  local host="$1"
  local port="$2"
  local name="$3"

  if nc -z "$host" "$port" >/dev/null 2>&1; then
    log "OK" "$name is reachable on $host:$port"
    return 0
  fi

  log "WARN" "$name is NOT reachable on $host:$port"
  return 1
}

check_http() {
  local url="$1"
  local name="$2"

  if curl -fsS --max-time 8 "$url" >/dev/null 2>&1; then
    log "OK" "$name responded at $url"
    return 0
  fi

  log "WARN" "$name did NOT respond at $url"
  return 1
}

ensure_ssh() {
  if check_port "$SSH_HOST" "$SSH_PORT" "SSH"; then
    return 0
  fi

  log "INFO" "Attempting to enable/start SSH service"
  /bin/launchctl load -w /System/Library/LaunchDaemons/ssh.plist >/dev/null 2>&1 || true
  sleep 1

  if check_port "$SSH_HOST" "$SSH_PORT" "SSH"; then
    log "OK" "SSH recovered successfully"
  else
    log "ERROR" "SSH is still unavailable after recovery attempt"
  fi
}

main() {
  log "INFO" "Sage host boot health check started"

  ensure_ssh
  check_port "$OPENCLAW_HOST" "$OPENCLAW_PORT" "OpenClaw gateway" || true
  check_http "$SAGE_HEALTH_URL" "Sage API health" || true

  log "INFO" "Sage host boot health check finished"
}

main
