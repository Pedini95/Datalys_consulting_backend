#!/bin/bash

echo "🚀 Déploiement avec informations de cache - Datalys Consulting Backend"
echo "⏰ $(date)"
echo "=================================================="

# Variables
REGISTRY="localhost:8081"
IMAGE_NAME="datalys/api"
PROJECT_DIR="/opt/Datalys_consulting_backend"
CONTAINER_NAME="datalys-api"

# 1. Vérifier les services Docker
echo "🔧 Vérification des services Docker..."
docker start redis-db mysql-db registry || true

# 2. Aller dans le répertoire du projet
cd $PROJECT_DIR
echo "📁 Répertoire de travail: $(pwd)"

# 3. Mettre à jour le code depuis Git
echo "📦 Mise à jour du code..."
git fetch origin
git reset --hard origin/develop

# 4. Vérifier l'espace disque
echo "💾 Vérification de l'espace disque..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "⚠️ Espace disque faible ($DISK_USAGE%), nettoyage..."
    docker system prune -f
    docker image prune -f
fi

# 5. Afficher les images existantes
echo "🐳 Images Docker existantes:"
docker images $REGISTRY/$IMAGE_NAME --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"

# 6. Construction avec informations de cache
echo "🔨 Construction de l'image avec cache..."
CURRENT_HASH=$(git rev-parse HEAD)
CACHED_IMAGE="$REGISTRY/$IMAGE_NAME:$CURRENT_HASH"

# Utiliser BuildKit pour de meilleures informations de cache
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

echo "📊 Début de la construction (BuildKit activé)..."
docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from $REGISTRY/$IMAGE_NAME:latest \
    --cache-from $REGISTRY/$IMAGE_NAME:buildcache \
    --tag $REGISTRY/$IMAGE_NAME:latest \
    --tag $CACHED_IMAGE \
    --tag $REGISTRY/$IMAGE_NAME:buildcache \
    --progress=plain \
    -f src/Dockerfile.optimized . 2>&1 | tee build.log

# 7. Analyser les logs de construction
echo ""
echo "📋 Analyse des logs de construction:"
echo "-----------------------------------"
CACHE_HITS=$(grep -c "CACHED" build.log || echo "0")
CACHE_MISSES=$(grep -c "RUN" build.log | head -1 || echo "0")
TOTAL_STEPS=$(grep -c "Step" build.log || echo "0")

echo "✅ Couches en cache: $CACHE_HITS"
echo "🔄 Couches reconstruites: $CACHE_MISSES"
echo "📊 Total des étapes: $TOTAL_STEPS"

if [ $CACHE_HITS -gt 0 ]; then
    CACHE_PERCENTAGE=$((CACHE_HITS * 100 / TOTAL_STEPS))
    echo "🎯 Taux de cache: ${CACHE_PERCENTAGE}%"
fi

# 8. Arrêter l'ancien conteneur
echo "🔄 Arrêt de l'ancien conteneur..."
docker stop $CONTAINER_NAME --time=30 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 9. Démarrer le nouveau conteneur
echo "🚀 Démarrage du nouveau conteneur..."
docker run -d \
    --name $CONTAINER_NAME \
    --network host \
    --restart unless-stopped \
    --health-cmd="curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1" \
    --health-interval=60s \
    --health-timeout=30s \
    --health-retries=5 \
    --health-start-period=120s \
    $REGISTRY/$IMAGE_NAME:latest

# 10. Attendre que l'application démarre
echo "⏳ Attente du démarrage de l'application..."
for i in {1..60}; do
    if docker ps | grep -q $CONTAINER_NAME; then
        if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health > /dev/null 2>&1; then
            echo "✅ Application en ligne après $i secondes"
            break
        fi
    fi
    sleep 3
    echo -n "."
done

# 11. Test de santé final
echo "🏥 Test de santé final..."
if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Application en ligne et fonctionnelle"
else
    echo "❌ L'application ne répond pas"
    docker logs $CONTAINER_NAME --tail=20
    exit 1
fi

# 12. Nettoyage
echo "🧹 Nettoyage..."
docker images $REGISTRY/$IMAGE_NAME --format "table {{.Tag}}\t{{.CreatedAt}}" | \
    grep -v "latest" | grep -v "buildcache" | tail -n +6 | \
    awk '{print $1}' | xargs -r docker rmi || true

echo "🎉 Déploiement avec cache terminé !"
echo "📊 Résumé:"
echo "   - Couches en cache: $CACHE_HITS"
echo "   - Couches reconstruites: $CACHE_MISSES"
echo "   - Taux de cache: ${CACHE_PERCENTAGE}%"
echo "⏰ $(date)" 