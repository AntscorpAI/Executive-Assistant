#!/usr/bin/env bash
set -euo pipefail

LLM_HOST="${1:-100.70.5.76}"
CHAT_MODEL="${2:-mistral-nemo}"

echo "Checking Ollama tags endpoint on ${LLM_HOST}"
curl -sS --max-time 10 "http://${LLM_HOST}:11434/api/tags" | head -c 1200
echo

echo "Running lightweight chat probe with mistral-small"
echo "Running lightweight chat probe with ${CHAT_MODEL}"
curl -sS --max-time 30 -X POST "http://${LLM_HOST}:11434/api/chat" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${CHAT_MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with ok\"}],\"stream\":false}" | head -c 1200
echo
