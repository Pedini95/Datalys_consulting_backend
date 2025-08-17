#!/bin/bash
set -e

# 🚀 DÉPLOIEMENT SIMPLE - DOCKER COMPOSE UNIFIÉ
# ==============================================

echo "🚀 DÉPLOIEMENT SIMPLE - $(date)"

# Variables
export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
export COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
export IMAGE_TAG=${IMAGE_TAG:-latest}
export ENVIRONMENT="production"

echo "📦 Version: $IMAGE_TAG"
echo "🔨 Build Date: $BUILD_DATE"
echo "📝 Commit: $COMMIT_SHA"

# Vérification et configuration MySQL si nécessaire
echo "🔍 Vérification de la configuration MySQL..."
if netstat -tlnp | grep -q "127.0.0.1:3306"; then
    echo "⚠️  MySQL écoute sur localhost - Reconfiguration..."
    ./scripts/configure-mysql.sh
elif netstat -tlnp | grep -q "82.112.253.137:3306"; then
    echo "✅ MySQL déjà configuré sur l'IP publique"
else
    echo "❌ MySQL non détecté - Veuillez le configurer manuellement"
fi

# Arrêt propre
echo "🛑 Arrêt des services..."
docker-compose --profile production down || true

# Reconstruction et démarrage
echo "🔨 Reconstruction et démarrage..."
docker-compose --profile production up -d --build

# Health check simple
echo "🔍 Vérification de la santé..."
sleep 15

if curl -f http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Déploiement réussi !"
    echo "🔗 Application: http://$(hostname -I | awk '{print $1}'):8082"
else
    echo "⚠️  Service en cours de démarrage..."
    echo "📋 Logs récents:"
    docker-compose logs --tail=10 datalys-api
fi

echo "✨ Déploiement simple terminé !" 