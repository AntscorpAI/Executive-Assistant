# Sage AI

Sage AI is a self-hosted executive assistant for ISO auditing firms. It centralizes audit schedules, reminders, client documentation checklists, meeting support, task follow-up, and document retrieval while keeping data local and auditable.

## Architecture

Sage AI uses a small, service-oriented monorepo designed to run on a dedicated Mac host or other always-on machine:

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

## Setup on the Primary Host

### Ollama

Install Ollama and pull a compact model that fits the hardware first.

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

If you have room and need better quality, you can later switch to a larger quantized model. For a laptop host, start small and monitor memory pressure before moving up to larger models.

### Tailscale-connected hosts

Sage AI can point to services on other machines over Tailscale.

- Remote data host: run PostgreSQL and Qdrant where you want persistent data to live.
- Remote Ollama host: run native Ollama and expose the HTTP API over the Tailnet.

Recommended environment settings:

- `DATABASE_URL_REMOTE`: PostgreSQL connection string using the remote database host name or IP
- `OLLAMA_URL`: primary HTTP endpoint (CB-Portal style)
- `OLLAMA_BASE_URL_REMOTE`: Ollama base URL on the remote Ollama host
- `OLLAMA_CHAT_MODEL_REMOTE`: the Ollama model to prefer remotely, such as `mistral`
- `DEFAULT_LLM_PROVIDER`: keep `ollama` during local development, switch to a remote profile when needed

If you want Sage AI to use the remote stack by default, I can add a profile switch so the backend reads the remote URLs automatically.

### HTTP-only via Tailscale for Ollama

This project now supports the hostname-based HTTP-only pattern:

- Ollama endpoint: `http://sage-llm-host:11434`
- Docker backend can map `OLLAMA_REMOTE_HOST_ALIAS -> OLLAMA_REMOTE_HOST_IP` for container-to-host access

To configure native Ollama on a remote macOS host for HTTP over Tailnet:

```bash
bash scripts/remote/configure_macos_ollama_http.sh sage-llm-host
```

If the alias user is wrong, pass the explicit macOS short username:

```bash
bash scripts/remote/configure_macos_ollama_http.sh sage-llm-host <mac-short-username> <tailscale-ip-or-name>
```

Important: the Tailscale device name is not always the SSH username. On the macOS Ollama host, run `id -un` to get the correct short username.

This uses a launchd agent (`com.ollama.server.plist`) with `OLLAMA_HOST=0.0.0.0:11434` so the HTTP endpoint survives reboot.

To verify endpoint and model response:

```bash
bash scripts/remote/verify_llm_http.sh <tailscale-ip-or-name>
```

Sage API health now reports Ollama status, pulled models, and whether the configured chat model is available.

### Remote profile quick start

1. Prepare the remote profile:

```bash
cp .env.remote.example .env
```

2. Deploy the remote data containers once SSH trust is configured:

```bash
bash scripts/remote/deploy_ubuntu2_stack.sh <db-host-or-ip> <ssh-user>
```

This creates a new isolated Docker project (`sage_ai_new`) with new containers and a fresh PostgreSQL database (`sage_new`) instead of reusing existing containers.

3. Check end-to-end connectivity:

```bash
bash scripts/remote/check_connectivity.sh <db-host-or-ip> <ollama-host-or-ip>
```

### Stop repeated password prompts

1. Set up SSH client config and multiplexing aliases:

```bash
DB_HOST_NAME=<db-host-or-ip> DB_HOST_USER=<ssh-user> LLM_HOST_NAME=<ollama-host-or-ip> LLM_USER=<mac-short-username> bash scripts/remote/setup_ssh_config.sh
```

2. Install your local public key to the remote data host (one password prompt expected):

```bash
bash scripts/remote/setup_passwordless_ssh.sh <db-host-or-ip> <ssh-user>
```

3. Optional: install the key on the remote macOS Ollama host as well after sharing the SSH username:

```bash
bash scripts/remote/setup_passwordless_ssh.sh <ollama-host-or-ip> <mac-ssh-username>
```

If your SSH alias is configured as `sage-llm-host`, use:

```bash
ssh sage-llm-host
```

After this, deployment commands should stop asking for passwords repeatedly.

4. Start Sage AI locally using remote services:

```bash
docker compose up --build
```

### Notes for remote Ollama models

Set `OLLAMA_CHAT_MODEL_REMOTE` to one of your installed models on the remote Ollama host, for example:

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

## Always-On Host

This laptop is configured to stay awake on AC power with sleep disabled.

To start the assistant stack automatically on login or reboot, load the launch agent in [launchd/com.sage.ai.stack.plist](launchd/com.sage.ai.stack.plist).

Current macOS power state is already set to `sleep 0` for AC and battery, with `displaysleep` left enabled so the screen can turn off while the machine stays awake.

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

## Current Migration Snapshot

The live Mac mini deployment that is being retired currently runs:

- `nginx` as the single public entry point on port 80
- `backend` as the FastAPI API service
- `frontend` as the Vite dashboard service
- `postgres` for application data
- `qdrant` for document retrieval
- `waha` for the WhatsApp gateway
- Ollama on a separate Tailnet host at `llm-server`

The Mac mini itself is reachable over Tailscale as `vishnus-mac-mini`, and passwordless SSH from this laptop is already configured.

The migration artifacts from the Mac mini are stored under [migration/mac-mini](migration/mac-mini).

