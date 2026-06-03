#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".env.remote.example" ]]; then
  echo "Missing .env.remote.example"
  exit 1
fi

cp .env.remote.example .env
echo "Wrote .env using remote profile defaults."
echo "Review credentials and then start services."
