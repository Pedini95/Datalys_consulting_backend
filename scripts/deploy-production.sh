#!/bin/bash
set -e

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

cd /opt/Datalys_consulting_backend

echo "🔨 Build de la nouvelle image..."
docker-compose build --no-cache

echo "🔄 Redémarrage..."
docker-compose up -d

docker image prune -f

echo "✅ Déploiement terminé" 