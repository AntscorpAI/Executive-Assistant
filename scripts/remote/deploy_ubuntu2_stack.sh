#!/usr/bin/env bash
set -euo pipefail

UBUNTU2_HOST="${1:-100.98.104.84}"
UBUNTU2_USER="${2:-vishnu}"
REMOTE_DIR="${3:-~/sage-remote}"
PROJECT_NAME="${4:-sage_ai_new}"
POSTGRES_DB="${POSTGRES_DB:-sage_new}"
POSTGRES_USER="${POSTGRES_USER:-sage_user_new}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-change-me-sage-db}"

echo "Preparing host key for ${UBUNTU2_HOST}"
mkdir -p "$HOME/.ssh"
ssh-keyscan -H "$UBUNTU2_HOST" >> "$HOME/.ssh/known_hosts"

echo "Copying compose files to ${UBUNTU2_USER}@${UBUNTU2_HOST}:${REMOTE_DIR}"
ssh "${UBUNTU2_USER}@${UBUNTU2_HOST}" "mkdir -p ${REMOTE_DIR}/deploy/ubuntu2"
scp "deploy/ubuntu2/docker-compose.yml" "${UBUNTU2_USER}@${UBUNTU2_HOST}:${REMOTE_DIR}/deploy/ubuntu2/docker-compose.yml"

echo "Writing remote .env for new stack ${PROJECT_NAME}"
ssh "${UBUNTU2_USER}@${UBUNTU2_HOST}" "cat > ${REMOTE_DIR}/deploy/ubuntu2/.env <<EOF
COMPOSE_PROJECT_NAME=${PROJECT_NAME}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF"

echo "Starting containers on Ubuntu2"
ssh "${UBUNTU2_USER}@${UBUNTU2_HOST}" "cd ${REMOTE_DIR}/deploy/ubuntu2 && docker compose --env-file .env -f docker-compose.yml up -d"

echo "Done. Verify with: ssh ${UBUNTU2_USER}@${UBUNTU2_HOST} 'docker ps --format \"table {{.Names}}\\t{{.Status}}\"'"
