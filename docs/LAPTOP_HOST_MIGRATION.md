# Laptop Host Migration Runbook

This runbook moves Sage AI from the current Mac mini to a laptop that will become the new always-on primary host.

## Target State

- Sage AI runs from this laptop as the primary host.
- The Mac mini is retired only after the laptop passes validation.
- Remote services remain optional and can stay in service if you want to keep PostgreSQL, Qdrant, or Ollama on separate machines.

## Before Cutover

Collect these items from the current production setup:

1. Current `.env` file and any secrets stored outside it.
2. Docker Compose overrides, launchd jobs, cron jobs, or shell scripts used to keep Sage AI running.
3. PostgreSQL data location or database host details.
4. Qdrant storage location or remote endpoint details.
5. Ollama model list and whether Ollama runs locally or on another host.
6. Tailscale names or IPs for any machine that will remain in service.
7. Webhook endpoints and credentials for WhatsApp, Teams, Microsoft Graph, and Claude if used.

Do not retire the Mac mini until all of the above are confirmed and the laptop has passed the validation steps below.

## Laptop Preparation

1. Install or start Docker Desktop.
2. Confirm Ollama is installed if the laptop will host models locally.
3. Confirm Tailscale is installed if remote services or private network access are required.
4. Copy `.env.example` to `.env` and replace placeholder values with production values.
5. Decide whether the laptop will host everything locally or use remote data and LLM services.

### Local-first profile

Use this when the laptop will host PostgreSQL, Qdrant, backend, frontend, and optionally Ollama.

- `USE_REMOTE_STACK=false`
- `DATABASE_URL=postgresql+psycopg://sage:sage@postgres:5432/sage`
- `QDRANT_URL=http://qdrant:6333`
- `OLLAMA_BASE_URL=http://ollama:11434` if using the containerized Ollama service
- `OLLAMA_BASE_URL=http://host.docker.internal:11434` if using native Ollama on the laptop

### Remote-service profile

Use this when PostgreSQL, Qdrant, or Ollama stay on another host.

- `USE_REMOTE_STACK=true`
- Set `DATABASE_URL_REMOTE`, `QDRANT_URL_REMOTE`, and `OLLAMA_BASE_URL_REMOTE`
- If the backend container must resolve a non-public Ollama hostname, set:
  - `OLLAMA_REMOTE_HOST_ALIAS`
  - `OLLAMA_REMOTE_HOST_IP`

## Validation on the Laptop

Run these checks before cutover:

1. `docker-compose config`
2. `docker-compose up --build -d`
3. `curl http://localhost:8000/health`
4. `curl http://localhost:8000/docs`
5. Open `http://localhost:5173`
6. Confirm the backend reports the expected Ollama URL and chat model.
7. Confirm the admin user can authenticate with the production or migration admin credentials.
8. Run one outbound test for each configured integration:
   - Microsoft Graph preview or sync
   - WhatsApp test endpoint
   - Teams test endpoint

## Data Migration

Choose one of these approaches:

### Clean cutover

Use the laptop with fresh PostgreSQL and Qdrant data.

This is faster, but historical tasks, reminders, messages, and vector data will not carry over.

### Full migration

Copy production data from the Mac mini or current remote hosts.

Minimum items to migrate:

- PostgreSQL database
- Qdrant collections and storage
- Uploaded files or document directories mounted into the app
- `.env` values and integration secrets
- Ollama models if the laptop will host them locally

## Cutover Sequence

1. Freeze changes on the Mac mini.
2. Export or snapshot the current PostgreSQL and Qdrant data.
3. Copy the production `.env` and any integration credentials.
4. Start Sage AI on the laptop.
5. Run the validation steps above.
6. Update any webhook senders, Graph callbacks, Tailscale aliases, or reverse proxies to point at the laptop.
7. Monitor health, logs, and integration traffic from the laptop.
8. Retire the Mac mini only after the laptop has remained healthy through at least one complete reminder and sync cycle.

## Retirement Checklist for the Mac mini

1. Confirm there are no remaining inbound webhooks or cron jobs targeting the Mac mini.
2. Confirm no users or services still depend on the Mac mini IP, hostname, or Tailscale name.
3. Stop Sage AI services on the Mac mini.
4. Keep a backup of the Mac mini data and `.env` before decommissioning.
5. Remove or archive old launch agents, SSH aliases, and Tailscale advertisements if they are no longer needed.

## Current Blockers on This Laptop

At the time this runbook was added, the laptop had:

- `ollama` installed
- `tailscale` installed
- Node.js and npm installed
- Docker Compose installed

The remaining host validation blocker was the local Docker client and daemon path not yet starting the stack cleanly. Resolve Docker first, then continue with `docker-compose up --build -d`.

## Keep-Alive Hardening (Implemented)

- Keep-awake launch agent: `launchd/com.sage.ai.keepawake.plist`
- Keep-awake script: `/Users/Assistant/Library/Application Support/Executive-Assistant/keep_awake.sh`
- Runtime behavior: runs `caffeinate -dimsu` continuously to prevent idle system sleep, display sleep, disk sleep, and sleep on AC power.
- Important laptop caveat: lid close (clamshell) can still sleep a laptop. Keep the lid open for 24/7 hosting unless you have a validated external-display clamshell setup that remains awake.

## Watchdog Hardening (Implemented)

- Watchdog launch agent: `launchd/com.sage.ai.watchdog.plist`
- Watchdog script: `/Users/Assistant/Library/Application Support/Executive-Assistant/watchdog_assistant_stack.sh`
- Runs every 300 seconds and checks `http://localhost/api/health`.
- If health is not `ok`, it runs `docker-compose up -d --remove-orphans` for automatic recovery.
- Watchdog log: `/Users/Assistant/Library/Logs/Executive-Assistant/watchdog.log`

## Pre-Login Startup Note

With Docker Desktop, full pre-login startup as a root LaunchDaemon is limited because Docker availability is tied to the user session and Desktop app lifecycle. The current hardening runs immediately after user login via launchd and keeps the host awake continuously while on AC power.