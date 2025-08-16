#!/bin/bash
set -e

APP_DIR="/opt/Datalys_consulting_backend"

echo "🚀 Déploiement en cours..."
cd "$APP_DIR"

echo "📥 Pull du dernier docker-compose.yml..."
git fetch --all
# Utiliser la branche develop (ou main si elle existe)
if git show-ref --verify --quiet refs/remotes/origin/main; then
    git reset --hard origin/main
else
    git reset --hard origin/develop
fi

echo "⬇️ Pull de la dernière image..."
docker-compose pull

echo "🔄 Redémarrage des services..."
docker-compose up -d

echo "⏳ Attente du démarrage..."
sleep 30

echo "🔍 Vérification de la santé..."
if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health; then
    echo "✅ Déploiement terminé avec succès !"
else
    echo "❌ Health check échoué"
    docker-compose logs --tail=20 datalys-api
    exit 1
fi

echo "🧹 Nettoyage des anciennes images..."
docker image prune -f 