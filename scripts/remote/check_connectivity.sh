#!/usr/bin/env bash
set -euo pipefail

UBUNTU2_HOST="${1:-100.98.104.84}"
LLM_HOST="${2:-100.70.5.76}"

echo "Checking Ubuntu2 Postgres port on ${UBUNTU2_HOST}:5432"
nc -zv "$UBUNTU2_HOST" 5432 || true

echo "Checking Ubuntu2 Qdrant port on ${UBUNTU2_HOST}:6333"
nc -zv "$UBUNTU2_HOST" 6333 || true

echo "Checking remote Ollama API on ${LLM_HOST}:11434"
curl -sS --max-time 10 "http://${LLM_HOST}:11434/api/tags" | head -c 800 || true
echo
