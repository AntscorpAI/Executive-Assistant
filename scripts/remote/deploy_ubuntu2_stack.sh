#!/usr/bin/env bash
set -euo pipefail

DATA_HOST="${1:-remote-db-host}"
DATA_HOST_USER="${2:-sage}"
REMOTE_DIR="${3:-~/sage-remote}"
PROJECT_NAME="${4:-sage_ai_new}"
POSTGRES_DB="${POSTGRES_DB:-sage_new}"
POSTGRES_USER="${POSTGRES_USER:-sage_user_new}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change-me-sage-db}"

echo "Preparing host key for ${DATA_HOST}"
mkdir -p "$HOME/.ssh"
ssh-keyscan -H "$DATA_HOST" >> "$HOME/.ssh/known_hosts"

echo "Copying compose files to ${DATA_HOST_USER}@${DATA_HOST}:${REMOTE_DIR}"
ssh "${DATA_HOST_USER}@${DATA_HOST}" "mkdir -p ${REMOTE_DIR}/deploy/ubuntu2"
scp "deploy/ubuntu2/docker-compose.yml" "${DATA_HOST_USER}@${DATA_HOST}:${REMOTE_DIR}/deploy/ubuntu2/docker-compose.yml"

echo "Writing remote .env for new stack ${PROJECT_NAME}"
ssh "${DATA_HOST_USER}@${DATA_HOST}" "cat > ${REMOTE_DIR}/deploy/ubuntu2/.env <<EOF
COMPOSE_PROJECT_NAME=${PROJECT_NAME}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF"

echo "Starting containers on the remote data host"
ssh "${DATA_HOST_USER}@${DATA_HOST}" "cd ${REMOTE_DIR}/deploy/ubuntu2 && docker compose --env-file .env -f docker-compose.yml up -d"

echo "Done. Verify with: ssh ${DATA_HOST_USER}@${DATA_HOST} 'docker ps --format \"table {{.Names}}\\t{{.Status}}\"'"
