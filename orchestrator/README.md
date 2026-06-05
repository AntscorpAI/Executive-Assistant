# Sage OpenClaw Orchestrator

This folder runs OpenClaw as the orchestration layer for Sage.

## Current Profile

- Profile: `sage`
- Gateway: `ws://127.0.0.1:19001`
- Dashboard: `http://127.0.0.1:19001/`
- Default model: `ollama/llama3.1:8b` locally, or your configured remote Ollama model
- Ollama endpoint: `http://127.0.0.1:11434` locally, or your configured remote Ollama host

## Start and Verify

```bash
npx openclaw --profile sage status --deep
npx openclaw --profile sage gateway status
npx openclaw --profile sage models status --plain
```

## MCP Bridge to Sage API

The MCP server is `sage-mcp-server.mjs` and is registered as `sage-api`.

### Environment options

- `SAGE_API_BASE` (default: `http://127.0.0.1:8000/api`)
- `SAGE_TOKEN` (preferred)
- or `SAGE_EMAIL` + `SAGE_PASSWORD`

### Tool coverage

- Health: `GET /health`
- Meeting commands: `POST /integrations/meetings/command`
- Tasks: list/create/update status
- Messaging tests: WhatsApp and Teams
- Outlook preview/sync

## Channel setup status

- WhatsApp plugin installed, account added, still needs linking.
- Teams plugin installed, account added, still needs channel credentials/config.

## Link channels

```bash
npx openclaw --profile sage channels login --channel whatsapp
npx openclaw --profile sage channels add --channel msteams --name default
npx openclaw --profile sage channels status --deep
```

## Useful commands

```bash
npx openclaw --profile sage mcp list
npx openclaw --profile sage mcp show sage-api
npx openclaw --profile sage logs --follow
```
