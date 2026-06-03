# Sage AI Integrations Runbook

This runbook shows how to configure Outlook Calendar, WhatsApp, Teams notifications, and meeting command handling that opens documents and shares context.

## 1. Outlook Calendar (Microsoft Graph)

### Azure setup

1. Register an app in Azure Entra ID.
2. Add application permissions:
   - `Calendars.Read`
   - `User.Read.All`
3. Grant admin consent.
4. Create a client secret and copy values:
   - `MS_GRAPH_TENANT_ID`
   - `MS_GRAPH_CLIENT_ID`
   - `MS_GRAPH_CLIENT_SECRET`
   - `MS_GRAPH_USER_ID` (mailbox or user object id)

### Sage setup

1. Update `.env` with the four `MS_GRAPH_*` values.
2. Restart backend.
3. Test preview:

```bash
curl -s http://localhost:8000/api/integrations/microsoft-graph/preview \
  -H "Authorization: Bearer <token>"
```

4. Sync into Sage audits:

```bash
curl -s -X POST http://localhost:8000/api/integrations/microsoft-graph/sync \
  -H "Authorization: Bearer <token>"
```

## 2. WhatsApp Notifications

Sage expects a gateway endpoint with a POST `/messages` API.

### Required env

- `WHATSAPP_GATEWAY_URL`
- `WHATSAPP_GATEWAY_TOKEN` (optional depending on provider)

### Test from Sage

```bash
curl -s -X POST http://localhost:8000/api/integrations/whatsapp/test \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "+1XXXXXXXXXX",
    "subject": "Sage Test",
    "body": "Sage WhatsApp integration is active"
  }'
```

If status is `sent`, Friday and morning reminder jobs can use the same channel.

## 3. Teams Notifications

For MVP, configure an Incoming Webhook URL in Teams.

### Required env

- `MS_TEAMS_WEBHOOK_URL`

### Test from Sage

```bash
curl -s -X POST http://localhost:8000/api/integrations/teams/test \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "audit-team",
    "subject": "Sage Teams Test",
    "body": "Teams webhook from Sage is working"
  }'
```

## 4. Teams Meetings + Commands + Document Context

Sage currently provides a meeting command API that can be called by a meeting bot/transcription bridge.

### Supported command styles

- "show me the audit schedule for next week"
- "open the ISO 27001 checklist"
- "show section 7.2 of the audit report"

### Command endpoint

```bash
curl -s -X POST http://localhost:8000/api/integrations/meetings/command \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Hey Sage, show me section 7.2 of the ISO 27001 checklist",
    "top_k": 3
  }'
```

The response includes:

- Detected intent (`show_schedule`, `open_checklist`, `show_section`)
- Action items
- Matching document chunks from RAG
- Optional section extract line if found

## 5. Document Opening and Context

To make "open document" and "share context" useful:

1. Load checklists/templates into `document_templates`.
2. Index templates into Qdrant:

```bash
curl -s -X POST http://localhost:8000/api/rag/index \
  -H "Authorization: Bearer <token>"
```

3. Verify search:

```bash
curl -s -X POST http://localhost:8000/api/rag/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query":"ISO 27001 section 7.2", "top_k":5}'
```

## 6. Suggested Production Path

1. Keep reminder delivery in WhatsApp + Teams webhook as currently implemented.
2. Add Teams bot for auto-join commands (Graph communications APIs or bot framework) and forward transcript snippets to `/api/integrations/meetings/command`.
3. Keep final document retrieval in Sage RAG so meeting assistants show controlled context from your local data.
