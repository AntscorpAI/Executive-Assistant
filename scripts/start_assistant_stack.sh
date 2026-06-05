#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/Users/Assistant/Documents/AntscorpAI/Executive-Assistant"
DOCKER_BIN="/usr/local/bin/docker"
DOCKER_COMPOSE_BIN="/usr/local/bin/docker-compose"
OPEN_BIN="/usr/bin/open"
export DOCKER_HOST="unix://${HOME}/.docker/run/docker.sock"

cd "$WORKSPACE"

"$OPEN_BIN" -g -a Docker || true

for _ in 1 2 3 4 5 6 7 8 9 10; do
  if "$DOCKER_BIN" info >/dev/null 2>&1; then
    break
  fi
  /bin/sleep 5
done

"$DOCKER_COMPOSE_BIN" up -d --remove-orphans