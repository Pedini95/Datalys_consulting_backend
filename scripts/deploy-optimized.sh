#!/bin/bash

echo "🚀 Déploiement optimisé avec gestion des timeouts - Datalys Consulting Backend"
echo "⏰ $(date)"
echo "=================================================="

# Variables
REGISTRY="localhost:8081"
IMAGE_NAME="datalys/api"
PROJECT_DIR="/opt/Datalys_consulting_backend"
CONTAINER_NAME="datalys-api"
MAX_RETRIES=3
RETRY_DELAY=30

# Fonction pour attendre avec timeout
wait_for_service() {
    local service_name=$1
    local service_url=$2
    local max_attempts=$3
    local timeout=$4
    
    echo "⏳ Attente du service $service_name..."
    for i in $(seq 1 $max_attempts); do
        if curl -f --connect-timeout 10 --max-time $timeout "$service_url" > /dev/null 2>&1; then
            echo "✅ $service_name accessible après $i tentatives"
            return 0
        fi
        echo -n "."
        sleep 5
    done
    echo "❌ $service_name inaccessible après $max_attempts tentatives"
    return 1
}

# Fonction pour redémarrer un service avec retry
restart_service_with_retry() {
    local service_name=$1
    local max_retries=$2
    
    for attempt in $(seq 1 $max_retries); do
        echo "🔄 Tentative $attempt/$max_retries pour redémarrer $service_name..."
        docker restart $service_name 2>/dev/null && return 0
        sleep $RETRY_DELAY
    done
    echo "❌ Échec du redémarrage de $service_name après $max_retries tentatives"
    return 1
}

# 1. Vérifier et redémarrer les services essentiels avec retry
echo "🔧 Vérification des services Docker essentiels..."
for service in redis-db mysql-db registry; do
    if ! docker ps | grep -q $service; then
        echo "⚠️ Service $service non démarré, tentative de redémarrage..."
        restart_service_with_retry $service $MAX_RETRIES
    else
        echo "✅ Service $service déjà en cours d'exécution"
    fi
done

# 2. Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
wait_for_service "MySQL" "http://localhost:3306" 10 30 || {
    echo "❌ MySQL non accessible, arrêt du déploiement"
    exit 1
}

wait_for_service "Redis" "http://localhost:6379" 10 30 || {
    echo "❌ Redis non accessible, arrêt du déploiement"
    exit 1
}

# 3. Aller dans le répertoire du projet
cd $PROJECT_DIR
echo "📁 Répertoire de travail: $(pwd)"

# 4. Mettre à jour le code depuis Git
echo "📦 Mise à jour du code..."
git fetch origin
git reset --hard origin/develop

# 5. Vérifier l'espace disque
echo "💾 Vérification de l'espace disque..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️ Espace disque faible ($DISK_USAGE%), nettoyage..."
    docker system prune -f
    docker image prune -f
fi

# 6. Construction de l'image avec BuildKit et cache optimisé
echo "🐳 Construction de l'image Docker optimisée..."
CURRENT_HASH=$(git rev-parse HEAD)
CACHED_IMAGE="$REGISTRY/$IMAGE_NAME:$CURRENT_HASH"

# Utiliser BuildKit si disponible
if docker buildx version &> /dev/null; then
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    
    docker build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from $REGISTRY/$IMAGE_NAME:latest \
        --cache-from $REGISTRY/$IMAGE_NAME:buildcache \
        --tag $REGISTRY/$IMAGE_NAME:latest \
        --tag $CACHED_IMAGE \
        --tag $REGISTRY/$IMAGE_NAME:buildcache \
        --progress=plain \
        -f src/Dockerfile.optimized . || {
        echo "❌ Échec de la construction avec BuildKit, tentative avec Docker classique..."
        docker build \
            --cache-from $REGISTRY/$IMAGE_NAME:latest \
            --tag $REGISTRY/$IMAGE_NAME:latest \
            --tag $CACHED_IMAGE \
            -f src/Dockerfile .
    }
else
    docker build \
        --cache-from $REGISTRY/$IMAGE_NAME:latest \
        --tag $REGISTRY/$IMAGE_NAME:latest \
        --tag $CACHED_IMAGE \
        -f src/Dockerfile .
fi

if [ $? -ne 0 ]; then
    echo "❌ Échec de la construction de l'image"
    exit 1
fi

echo "✅ Construction réussie"

# 7. Arrêter l'ancien conteneur avec timeout
echo "🔄 Arrêt de l'ancien conteneur..."
docker stop $CONTAINER_NAME --time=30 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 8. Démarrer le nouveau conteneur avec health check optimisé
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
    --memory=512m \
    --cpus=0.5 \
    $REGISTRY/$IMAGE_NAME:latest

if [ $? -ne 0 ]; then
    echo "❌ Échec du démarrage du conteneur"
    docker logs $CONTAINER_NAME --tail=20
    exit 1
fi

# 9. Attendre que l'application démarre avec health check optimisé
echo "⏳ Attente du démarrage de l'application..."
wait_for_service "API" "http://localhost:8082/health" 60 30 || {
    echo "❌ L'application ne répond pas après 60 tentatives"
    echo "📋 Logs du conteneur:"
    docker logs $CONTAINER_NAME --tail=50
    echo "🔍 Statut du conteneur:"
    docker ps -a | grep $CONTAINER_NAME
    exit 1
}

# 10. Test de santé final avec retry
echo "🏥 Test de santé final..."
for attempt in $(seq 1 3); do
    if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health > /dev/null 2>&1; then
        echo "✅ Application en ligne et fonctionnelle sur le port 8082"
        break
    else
        echo "⚠️ Tentative $attempt/3 échouée, nouvelle tentative dans 10s..."
        sleep 10
    fi
done

if [ $? -ne 0 ]; then
    echo "❌ L'application ne répond pas après 3 tentatives"
    docker logs $CONTAINER_NAME --tail=50
    exit 1
fi

# 11. Vérifier l'ouverture du port dans le firewall
echo "🔥 Vérification du firewall..."
if ufw status | grep -q "8082"; then
    echo "✅ Port 8082 ouvert dans le firewall"
else
    echo "⚠️ Ouverture du port 8082 dans le firewall..."
    ufw allow 8082
fi

# 12. Nettoyage optimisé
echo "🧹 Nettoyage des anciennes images..."
docker images $REGISTRY/$IMAGE_NAME --format "table {{.Tag}}\t{{.CreatedAt}}" | \
    grep -v "latest" | grep -v "buildcache" | tail -n +6 | \
    awk '{print $1}' | xargs -r docker rmi || true

docker container prune -f
docker image prune -f

echo "🎉 Déploiement optimisé terminé avec succès !"
echo "🌐 URL de l'API: http://***:8082"
echo "⚡ Build optimisé avec gestion des timeouts"
echo "⏰ $(date)" 