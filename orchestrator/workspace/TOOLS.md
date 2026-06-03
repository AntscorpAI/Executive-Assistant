# TOOLS.md - Sage Local Notes

## Core Services

- Sage API base: http://127.0.0.1:8000/api
- OpenClaw gateway: ws://127.0.0.1:19001
- OpenClaw dashboard: http://127.0.0.1:19001/
- Remote Ollama: http://100.70.5.76:11434
- Default model: ollama-remote/mistral-nemo

## MCP Bridge

- MCP server name: sage-api
- Command: node /Users/aibot/Documents/Executive Assistant/orchestrator/sage-mcp-server.mjs
- Env:
	SAGE_API_BASE=http://127.0.0.1:8000/api
	SAGE_TOKEN or SAGE_EMAIL + SAGE_PASSWORD required for authenticated routes

## High-Value Endpoints

- GET /health
- POST /integrations/meetings/command
- GET /tasks/
- POST /tasks/
- PATCH /tasks/{task_id}/status
- POST /integrations/whatsapp/test
- POST /integrations/teams/test
- POST /integrations/microsoft-graph/sync
- GET /integrations/microsoft-graph/preview

## Channel State

- WhatsApp account: default (plugin installed, not linked)
- Teams account: default (plugin installed, not configured)
