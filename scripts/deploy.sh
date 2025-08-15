#!/bin/bash
set -e

echo "🚀 Déploiement ultra-rapide - Datalys Consulting Backend"
echo "⏰ $(date)"
echo "=================================================="

# Variables
REGISTRY="localhost:8081"
IMAGE_NAME="datalys/api"
PROJECT_DIR="/opt/Datalys_consulting_backend"
CONTAINER_NAME="datalys-api"

# Activer BuildKit pour des performances maximales
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 1. Vérifier les services Docker
echo "🔧 Vérification des services Docker..."
docker start redis-db mysql-db registry || true

# 2. Aller dans le répertoire du projet
cd $PROJECT_DIR
echo "📁 Répertoire de travail: $(pwd)"

# 3. Mettre à jour le code
echo "📦 Mise à jour du code..."
git fetch origin
git reset --hard origin/develop

# 4. Vérifier l'espace disque
echo "💾 Vérification de l'espace disque..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️ Espace disque faible ($DISK_USAGE%), nettoyage..."
    docker system prune -f
    docker image prune -f
fi

# 5. Construction ultra-rapide avec cache
echo "⚡ Construction ultra-rapide avec cache..."
CURRENT_HASH=$(git rev-parse HEAD)
CACHED_IMAGE="$REGISTRY/$IMAGE_NAME:$CURRENT_HASH"

# Construction avec cache optimisé (sans BuildKit)
echo "🔨 Construction avec cache Docker classique..."
docker build \
    --cache-from $REGISTRY/$IMAGE_NAME:latest \
    --tag $REGISTRY/$IMAGE_NAME:latest \
    --tag $CACHED_IMAGE \
    --tag $REGISTRY/$IMAGE_NAME:buildcache \
    -f src/Dockerfile .

# 6. Arrêt rapide de l'ancien conteneur
echo "🔄 Arrêt de l'ancien conteneur..."
docker stop $CONTAINER_NAME --time=10 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 7. Démarrage du nouveau conteneur
echo "🚀 Démarrage du nouveau conteneur..."
docker run -d \
    --name $CONTAINER_NAME \
    --network host \
    --restart unless-stopped \
    --health-cmd="curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1" \
    --health-interval=60s \
    --health-timeout=30s \
    --health-retries=5 \
    --health-start-period=60s \
    --memory=1g \
    --cpus=1.0 \
    $REGISTRY/$IMAGE_NAME:latest

# 8. Attente rapide du démarrage
echo "⏳ Attente du démarrage..."
for i in {1..30}; do
    if docker ps | grep -q $CONTAINER_NAME; then
        if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health > /dev/null 2>&1; then
            echo "✅ Application en ligne après $i secondes"
            break
        fi
    fi
    sleep 2
    echo -n "."
done

# 9. Test de santé final
echo "🏥 Test de santé final..."
if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Application en ligne et fonctionnelle"
else
    echo "❌ L'application ne répond pas"
    docker logs $CONTAINER_NAME --tail=20
    exit 1
fi

# 10. Nettoyage intelligent
echo "🧹 Nettoyage intelligent..."
# Garder seulement les 3 dernières images
docker images $REGISTRY/$IMAGE_NAME --format "table {{.Tag}}\t{{.CreatedAt}}" | \
    grep -v "latest" | grep -v "buildcache" | tail -n +4 | \
    awk '{print $1}' | while read tag; do
        if [ -n "$tag" ] && [ "$tag" != "<none>" ]; then
            docker rmi "$tag" 2>/dev/null || true
        fi
    done

# Nettoyage des conteneurs arrêtés
docker container prune -f

echo "🎉 Déploiement ultra-rapide terminé !"
echo "⚡ Temps total: $(($(date +%s) - $(date -d "$(date)" +%s))) secondes"
echo "🌐 URL: http://***:8082"
echo "⏰ $(date)" 