#!/bin/bash

echo "🚀 Déploiement avec gestion des timeouts étendus - Datalys Consulting Backend"
echo "⏰ $(date)"
echo "=================================================="

# Variables
REGISTRY="localhost:8081"
IMAGE_NAME="datalys/api"
PROJECT_DIR="/opt/Datalys_consulting_backend"
CONTAINER_NAME="datalys-api"
BUILD_TIMEOUT=1800  # 30 minutes pour la construction
DEPLOY_TIMEOUT=900  # 15 minutes pour le déploiement

# Fonction pour exécuter avec timeout
run_with_timeout() {
    local timeout=$1
    local command="$2"
    local description="$3"
    
    echo "⏳ $description (timeout: ${timeout}s)..."
    timeout $timeout bash -c "$command"
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        echo "❌ Timeout après ${timeout}s pour: $description"
        return 1
    elif [ $exit_code -ne 0 ]; then
        echo "❌ Échec pour: $description (code: $exit_code)"
        return 1
    else
        echo "✅ Succès: $description"
        return 0
    fi
}

# 1. Vérifier et redémarrer les services Docker
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

# 5. Construction de l'image avec timeout étendu
echo "🐳 Construction de l'image Docker avec timeout étendu..."
CURRENT_HASH=$(git rev-parse HEAD)
CACHED_IMAGE="$REGISTRY/$IMAGE_NAME:$CURRENT_HASH"

# Utiliser BuildKit si disponible avec timeout
if docker buildx version &> /dev/null; then
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    
    build_command="docker build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from $REGISTRY/$IMAGE_NAME:latest \
        --cache-from $REGISTRY/$IMAGE_NAME:buildcache \
        --tag $REGISTRY/$IMAGE_NAME:latest \
        --tag $CACHED_IMAGE \
        --tag $REGISTRY/$IMAGE_NAME:buildcache \
        --progress=plain \
        -f src/Dockerfile.optimized ."
else
    build_command="docker build \
        --cache-from $REGISTRY/$IMAGE_NAME:latest \
        --tag $REGISTRY/$IMAGE_NAME:latest \
        --tag $CACHED_IMAGE \
        -f src/Dockerfile.optimized ."
fi

if ! run_with_timeout $BUILD_TIMEOUT "$build_command" "Construction de l'image Docker"; then
    echo "❌ Échec de la construction, tentative avec Dockerfile standard..."
    fallback_command="docker build \
        --cache-from $REGISTRY/$IMAGE_NAME:latest \
        --tag $REGISTRY/$IMAGE_NAME:latest \
        --tag $CACHED_IMAGE \
        -f src/Dockerfile ."
    
    if ! run_with_timeout $BUILD_TIMEOUT "$fallback_command" "Construction avec Dockerfile standard"; then
        echo "❌ Échec de la construction avec les deux méthodes"
        exit 1
    fi
fi

# 6. Arrêter l'ancien conteneur
echo "🔄 Arrêt de l'ancien conteneur..."
docker stop $CONTAINER_NAME --time=60 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 7. Démarrer le nouveau conteneur avec health check optimisé
echo "🚀 Démarrage du nouveau conteneur..."
docker run -d \
    --name $CONTAINER_NAME \
    --network host \
    --restart unless-stopped \
    --health-cmd="curl -f --connect-timeout 15 --max-time 45 http://localhost:8082/health || exit 1" \
    --health-interval=90s \
    --health-timeout=45s \
    --health-retries=5 \
    --health-start-period=180s \
    --memory=1g \
    --cpus=1.0 \
    $REGISTRY/$IMAGE_NAME:latest

if [ $? -ne 0 ]; then
    echo "❌ Échec du démarrage du conteneur"
    docker logs $CONTAINER_NAME --tail=20
    exit 1
fi

# 8. Attendre que l'application démarre avec timeout étendu
echo "⏳ Attente du démarrage de l'application..."
startup_command="
for i in {1..120}; do
    if docker ps | grep -q $CONTAINER_NAME; then
        if curl -f --connect-timeout 15 --max-time 45 http://localhost:8082/health > /dev/null 2>&1; then
            echo '✅ Application en ligne après \$i secondes'
            exit 0
        fi
    fi
    sleep 5
    echo -n '.'
done
echo '❌ Application ne répond pas après 120 tentatives'
exit 1
"

if ! run_with_timeout $DEPLOY_TIMEOUT "$startup_command" "Attente du démarrage de l'application"; then
    echo "❌ L'application ne démarre pas"
    echo "📋 Logs du conteneur:"
    docker logs $CONTAINER_NAME --tail=100
    echo "🔍 Statut du conteneur:"
    docker ps -a | grep $CONTAINER_NAME
    exit 1
fi

# 9. Test de santé final avec retry
echo "🏥 Test de santé final..."
health_command="
for attempt in {1..5}; do
    if curl -f --connect-timeout 15 --max-time 45 http://localhost:8082/health > /dev/null 2>&1; then
        echo '✅ Application en ligne et fonctionnelle sur le port 8082'
        exit 0
    else
        echo \"⚠️ Tentative \$attempt/5 échouée, nouvelle tentative dans 15s...\"
        sleep 15
    fi
done
echo '❌ L application ne répond pas après 5 tentatives'
exit 1
"

if ! run_with_timeout 300 "$health_command" "Test de santé final"; then
    echo "❌ L'application ne répond pas"
    docker logs $CONTAINER_NAME --tail=50
    exit 1
fi

# 10. Vérifier l'ouverture du port dans le firewall
echo "🔥 Vérification du firewall..."
if ufw status | grep -q "8082"; then
    echo "✅ Port 8082 ouvert dans le firewall"
else
    echo "⚠️ Ouverture du port 8082 dans le firewall..."
    ufw allow 8082
fi

# 11. Nettoyage optimisé
echo "🧹 Nettoyage des anciennes images..."
docker images $REGISTRY/$IMAGE_NAME --format "table {{.Tag}}\t{{.CreatedAt}}" | \
    grep -v "latest" | grep -v "buildcache" | tail -n +6 | \
    awk '{print $1}' | xargs -r docker rmi || true

docker container prune -f
docker image prune -f

echo "🎉 Déploiement avec timeouts étendus terminé avec succès !"
echo "🌐 URL de l'API: http://***:8082"
echo "⚡ Build optimisé avec gestion des timeouts étendus"
echo "⏰ $(date)" 