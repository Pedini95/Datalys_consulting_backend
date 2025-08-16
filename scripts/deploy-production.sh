#!/bin/bash
set -e

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

cd /opt/Datalys_consulting_backend

echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

echo "🔨 Build de la nouvelle image..."
docker-compose build --no-cache --pull

echo "🔄 Redémarrage..."
docker-compose down
docker-compose up -d

echo "🧹 Nettoyage..."
docker image prune -f

echo "✅ Déploiement terminé" 