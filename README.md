# Sage AI

Sage AI is a self-hosted executive assistant for ISO auditing firms. It centralizes audit schedules, reminders, client documentation checklists, meeting support, task follow-up, and document retrieval while keeping data local and auditable.

## Architecture

Sage AI uses a small, service-oriented monorepo designed to run on a Mac mini with 16 GB RAM:

- Backend API: FastAPI + SQLAlchemy + PostgreSQL
- AI orchestration: LangGraph-ready service layer with Ollama first and Claude fallback
- RAG store: Qdrant for semantic retrieval over ISO standards, reports, and templates
- Scheduling: APScheduler jobs for daily reminders, Friday digests, and overdue task follow-up
- Notifications: WhatsApp gateway adapter, Email, and Microsoft Teams adapters
- Calendar sync: Microsoft Graph API for Outlook calendars
- Meeting assistant: transcription and action-item extraction pipeline
- Frontend: React + Vite admin dashboard

### Core Flow

1. Audit schedules are ingested from Outlook and the local audit system.
2. Conflict checks run before reminders are sent.
3. Friday and daily notifications are generated per auditor and per client.
4. ISO document checklists are fetched from the rules catalog and sent automatically.
5. Meeting actions and user tasks are captured into the task ledger.
6. Conversations, reminders, and document lookups are retained in local storage.

## Repository Layout

- `backend/`: FastAPI application, workers, services, and integrations
- `frontend/`: React admin dashboard
- `config/`: audit-type and reminder configuration
- `data/`: local persistent data mounted into containers

## Quick Start

### 1. Prerequisites

- Docker Desktop or Docker Engine
- Python 3.12+ if running the backend outside Docker
- Node.js 20+ if running the frontend outside Docker
- Ollama installed locally or reachable on the network
- Microsoft Graph app registration for Outlook integration
- WhatsApp gateway such as Evolution API, Baileys-based gateway, or a compatible webhook service

### 2. Configure environment

Copy the example environment file and edit the values for your environment.

```bash
cp .env.example .env
```

Important values:

- `DATABASE_URL`: PostgreSQL connection string
- `OLLAMA_BASE_URL`: Ollama host, usually `http://ollama:11434`
- `DEFAULT_LLM_PROVIDER`: `ollama` or `claude`
- `ANTHROPIC_API_KEY`: optional Claude fallback key
- `MS_GRAPH_*`: Microsoft Graph credentials
- `WHATSAPP_GATEWAY_URL`: your WhatsApp gateway endpoint

### 3. Start the stack

```bash
docker compose up --build
```

### 4. Open the apps

- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Admin dashboard: `http://localhost:5173`

## Setup on Mac mini

### Ollama

Install Ollama and pull a compact model that fits the hardware first.

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

If you have room and need better quality, you can later switch to a larger quantized model. For a 16 GB Mac mini, start small and monitor memory pressure.

### Tailscale-connected hosts

Sage AI can point to services on other machines over Tailscale.

- Ubuntu2: run the database stack in Docker and expose only the service ports over the Tailnet.
- MacBook Pro: run native Ollama and expose the Ollama HTTP API over the Tailnet.

Recommended environment settings:

- `DATABASE_URL_REMOTE`: PostgreSQL connection string using the Ubuntu2 Tailscale IP or MagicDNS name
- `OLLAMA_URL`: primary HTTP endpoint (CB-Portal style)
- `OLLAMA_BASE_URL_REMOTE`: Ollama base URL on the MacBook Pro
- `OLLAMA_CHAT_MODEL_REMOTE`: the Ollama model to prefer remotely, such as `mistral`
- `DEFAULT_LLM_PROVIDER`: keep `ollama` during local development, switch to a remote profile when needed

If you want Sage AI to use the remote stack by default, I can add a profile switch so the backend reads the remote URLs automatically.

Current assigned hosts:

- Ubuntu2: `100.98.104.84`
- MacBook Pro Ollama: `100.70.5.76`

### HTTP-only via Tailscale for Ollama

This project now supports the hostname-based HTTP-only pattern:

- Ollama endpoint: `http://llm-server-macbook-pro:11434`
- Docker backend includes a host mapping for `llm-server-macbook-pro -> 100.70.5.76`

To configure native Ollama on the MacBook for HTTP over Tailnet:

```bash
bash scripts/remote/configure_macos_ollama_http.sh llm-server-macbook-pro
```

If the alias user is wrong, pass the explicit macOS short username:

```bash
bash scripts/remote/configure_macos_ollama_http.sh llm-server-macbook-pro <mac-short-username> 100.70.5.76
```

Important: the Tailscale device name is not always the SSH username. On the MacBook, run `id -un` to get the correct short username.

This uses a launchd agent (`com.ollama.server.plist`) with `OLLAMA_HOST=0.0.0.0:11434` so the HTTP endpoint survives reboot.

To verify endpoint and model response:

```bash
bash scripts/remote/verify_llm_http.sh 100.70.5.76
```

Sage API health now reports Ollama status, pulled models, and whether the configured chat model is available.

### Remote profile quick start

1. Prepare the remote profile:

```bash
cp .env.remote.example .env
```

2. Deploy the Ubuntu2 containers once SSH trust is configured:

```bash
bash scripts/remote/deploy_ubuntu2_stack.sh 100.98.104.84 vishnu
```

This creates a new isolated Docker project (`sage_ai_new`) with new containers and a fresh PostgreSQL database (`sage_new`) instead of reusing existing containers.

3. Check end-to-end connectivity:

```bash
bash scripts/remote/check_connectivity.sh 100.98.104.84 100.70.5.76
```

### Stop repeated password prompts

1. Set up SSH client config and multiplexing aliases:

```bash
LLM_USER=<mac-short-username> bash scripts/remote/setup_ssh_config.sh
```

2. Install your local public key to Ubuntu2 (one password prompt expected):

```bash
bash scripts/remote/setup_passwordless_ssh.sh 100.98.104.84 vishnu
```

3. Optional: install key on MacBook Pro as well after sharing the SSH username:

```bash
bash scripts/remote/setup_passwordless_ssh.sh 100.70.5.76 <macbook-ssh-username>
```

If your SSH alias is configured as `llm-server-macbook-pro`, use:

```bash
ssh llm-server-macbook-pro
```

After this, deployment commands should stop asking for passwords repeatedly.

4. Start Sage AI locally using remote services:

```bash
docker compose up --build
```

### Notes for remote Ollama models

Set `OLLAMA_CHAT_MODEL_REMOTE` to one of your installed models on the MacBook Pro, for example:

- `mistral-small`
- `mistral-nemo`

The remote profile defaults to `mistral-nemo` and can be changed in `.env`.

### Microsoft Outlook sync

Register an Azure app with Microsoft Graph permissions for calendars, mail, and Teams as needed. Use the client credentials or delegated flow that best fits your tenant policy.

### WhatsApp

Use a self-hosted gateway or a compliant business integration. Sage AI treats WhatsApp as an adapter so the transport can be swapped without changing the core app.

## Configuration

Edit `config/audit_types.yaml` to define the document checklist and reminder template for each audit type.

For full Outlook, WhatsApp, Teams, and meeting-command setup, use [docs/INTEGRATIONS_RUNBOOK.md](docs/INTEGRATIONS_RUNBOOK.md).

Example:

```yaml
iso_9001:
  title: ISO 9001 Quality Management System
  required_documents:
    - Quality manual
    - Process map
    - Management review minutes
  client_message: Please prepare the ISO 9001 documents listed in the checklist.
```

## Security

- All data is stored locally by default.
- Authentication uses JWT with role-based access control.
- Sensitive data is isolated in PostgreSQL and Qdrant.
- Actions are written to an audit log.
- External providers are optional and adapter-based.

## First Milestone

The initial production slice includes:

- Audit schedule ingestion
- Friday and daily reminders
- Client documentation reminders by ISO type
- Conflict-of-interest checks
- Task capture and overdue follow-up
- Search over document templates and audit artifacts
- Admin dashboard for operations visibility

## Next Steps

After the bootstrap is running, the next hardening pass is usually:

1. Connect the local audit app to the sync adapter.
2. Configure Microsoft Graph permissions and mail templates.
3. Wire the WhatsApp gateway and message templates.
4. Load ISO document sets into the vector index.
5. Tune reminder schedules and escalation rules.

## What I Need From You

To finish the Ubuntu2 and MacBook Pro wiring, send me:

1. The Tailscale names or IPs for Ubuntu2 and the MacBook Pro.
2. Whether Ubuntu2 should host PostgreSQL only, or PostgreSQL plus Qdrant and any other services.
3. The database names, usernames, and passwords you want used in the new Docker container.
4. Whether the MacBook Pro should expose only Ollama, or also embeddings and any local file paths.
5. The preferred Ollama model names to install on the MacBook Pro beyond `mistral`.
6. Whether you want the app to default to the remote stack or keep local-first with a manual switch.

