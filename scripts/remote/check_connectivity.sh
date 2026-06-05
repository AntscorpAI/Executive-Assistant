#!/usr/bin/env bash
set -euo pipefail

DB_HOST="${1:-remote-db-host}"
LLM_HOST="${2:-remote-ollama-host}"

echo "Checking remote Postgres port on ${DB_HOST}:5432"
nc -zv "$DB_HOST" 5432 || true

echo "Checking remote Qdrant port on ${DB_HOST}:6333"
nc -zv "$DB_HOST" 6333 || true

echo "Checking remote Ollama API on ${LLM_HOST}:11434"
curl -sS --max-time 10 "http://${LLM_HOST}:11434/api/tags" | head -c 800 || true
echo
