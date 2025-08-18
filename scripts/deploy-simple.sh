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
if docker ps | grep -q "mysql.*82.112.253.137:3306"; then
    echo "✅ MySQL container actif sur l'IP publique"
elif docker ps | grep -q "mysql"; then
    echo "⚠️  MySQL container détecté mais configuration à vérifier"
elif netstat -tlnp | grep -q "127.0.0.1:3306"; then
    echo "⚠️  MySQL écoute sur localhost - Reconfiguration..."
    ./scripts/configure-mysql.sh
elif netstat -tlnp | grep -q "82.112.253.137:3306"; then
    echo "✅ MySQL déjà configuré sur l'IP publique"
else
    echo "⚠️  MySQL non détecté - vérification manuelle recommandée"
fi

# Arrêt propre
echo "🛑 Arrêt des services..."
docker-compose --profile production down || true

# Préservation des permissions des fichiers d'upload
echo "🔐 Configuration des permissions pour les uploads..."
mkdir -p ./src/static/files/logos ./src/static/files/files ./src/static/files/projects
chown -R 1000:1000 ./src/static/files/ 2>/dev/null || true
chmod -R 775 ./src/static/files/ 2>/dev/null || true

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