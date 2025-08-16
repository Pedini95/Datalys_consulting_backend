#!/bin/bash
set -e

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

cd /opt/Datalys_consulting_backend

echo "⬇️ Pull de la dernière image..."
docker-compose pull

echo "🔄 Redémarrage..."
docker-compose up -d

docker image prune -f

echo "✅ Déploiement terminé" 