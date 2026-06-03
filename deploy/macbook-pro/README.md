# MacBook Pro Ollama Host

This host runs native Ollama and serves Sage AI models over Tailscale.

## Recommended model set

- `mistral` as the preferred chat model
- `nomic-embed-text` for embeddings

## Usage

Run Ollama locally and expose the API to the Tailnet. Point Sage AI to the Tailscale address via `OLLAMA_BASE_URL_REMOTE`.
