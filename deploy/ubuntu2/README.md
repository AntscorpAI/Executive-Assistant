# Ubuntu2 Database Host

This folder contains the Docker Compose stack for the Ubuntu2 host that will be reachable over Tailscale.

## Services

- PostgreSQL for Sage AI application data
- Qdrant for document retrieval
- Redis for jobs, queueing, or transient assistant state

## Usage

```bash
docker compose -f deploy/ubuntu2/docker-compose.yml up -d
```

## Tailscale Notes

- Install Tailscale on Ubuntu2 and join the Tailnet.
- Use the Tailscale IP or MagicDNS name in the Sage AI `.env` file.
- Keep the container ports only reachable from the Tailnet or local host firewall rules.
