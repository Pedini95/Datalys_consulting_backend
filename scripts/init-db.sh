#!/bin/bash
set -euo pipefail

# This script initializes the database (creates DB if missing, then tables)
# Usage examples:
#   ./scripts/init-db.sh                      # if running inside the repo host with docker installed
#   ENV_FILE=.env.production IMAGE=datalys-consulting-backend:latest ./scripts/init-db.sh

ENV_FILE=${ENV_FILE:-.env.production}
IMAGE=${IMAGE:-datalys-consulting-backend:latest}

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Fichier d'environnement introuvable: $ENV_FILE"
  echo "Astuce: cp src/env.production.template .env.production && éditez les valeurs."
  exit 1
fi

# Run a one-off container to execute init_db.py
# We mount only what is needed and reuse the same image to access dependencies
exec docker run --rm \
  --env-file "$ENV_FILE" \
  -v "$(pwd)/src:/app/src" \
  -w /app/src \
  "$IMAGE" \
  /opt/venv/bin/python init_db.py 