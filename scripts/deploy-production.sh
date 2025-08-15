#!/bin/bash

echo "🚀 Déploiement automatique Docker optimisé sur le serveur de production..."
echo "⏰ $(date)"

# Variables pour la production
REGISTRY="localhost:8081"
IMAGE_NAME="datalys/api"
PROJECT_DIR="/opt/Datalys_consulting_backend"
CONTAINER_NAME="datalys-api"

# Vérifier si BuildKit est disponible
if docker buildx version &> /dev/null; then
    echo "✅ BuildKit disponible, activation..."
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    BUILDKIT_AVAILABLE=true
else
    echo "⚠️  BuildKit non disponible, utilisation du build Docker classique"
    BUILDKIT_AVAILABLE=false
fi

# 1. Vérifier et redémarrer les services Docker essentiels
echo "🔧 Vérification des services Docker..."
docker start redis-db mysql-db registry || true

# 2. Aller dans le répertoire du projet
cd $PROJECT_DIR
echo "📁 Répertoire de travail: $(pwd)"

# 3. Mettre à jour le code depuis Git
echo "📦 Mise à jour du code..."
git fetch origin
git reset --hard origin/develop

# 4. Vérifier si l'image existe déjà avec le même hash
echo "🔍 Vérification du cache Docker..."
CURRENT_HASH=$(git rev-parse HEAD)
CACHED_IMAGE="$REGISTRY/$IMAGE_NAME:$CURRENT_HASH"

if docker images | grep -q "$CURRENT_HASH"; then
    echo "✅ Image en cache trouvée, utilisation de la version existante"
    docker tag $CACHED_IMAGE $REGISTRY/$IMAGE_NAME:latest
else
    echo "🔄 Construction de l'image Docker optimisée..."
    
    if [ "$BUILDKIT_AVAILABLE" = true ]; then
        # Construction avec BuildKit et cache optimisé
        docker build \
          --build-arg BUILDKIT_INLINE_CACHE=1 \
          --cache-from $REGISTRY/$IMAGE_NAME:latest \
          --cache-from $REGISTRY/$IMAGE_NAME:buildcache \
          --tag $REGISTRY/$IMAGE_NAME:latest \
          --tag $CACHED_IMAGE \
          --tag $REGISTRY/$IMAGE_NAME:buildcache \
          --progress=plain \
          -f src/Dockerfile .
    else
        # Construction avec Docker classique
        docker build \
          --cache-from $REGISTRY/$IMAGE_NAME:latest \
          --tag $REGISTRY/$IMAGE_NAME:latest \
          --tag $CACHED_IMAGE \
          -f src/Dockerfile .
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Construction réussie"
        echo "💾 Sauvegarde de l'image dans le cache..."
    else
        echo "❌ Échec de la construction"
        exit 1
    fi
fi

# 5. Arrêter et supprimer l'ancien conteneur
echo "🔄 Arrêt de l'ancien conteneur..."
docker rm -f $CONTAINER_NAME || true

# 6. Démarrer le nouveau conteneur avec health check
echo "🚀 Démarrage du nouveau conteneur..."
docker run -d \
  --name $CONTAINER_NAME \
  --network host \
  --restart unless-stopped \
  --health-cmd="curl -f http://localhost:8082/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  $REGISTRY/$IMAGE_NAME:latest

# 7. Attendre que l'application démarre avec health check
echo "⏳ Attente du démarrage de l'application..."
for i in {1..30}; do
    if docker ps | grep -q $CONTAINER_NAME; then
        if curl -f http://localhost:8082/health > /dev/null 2>&1; then
            echo "✅ Application en ligne après $i secondes"
            break
        fi
    fi
    sleep 2
    echo -n "."
done

# 8. Vérifier que le conteneur fonctionne
echo "🔍 Vérification du conteneur..."
if docker ps | grep -q $CONTAINER_NAME; then
    echo "✅ Conteneur en cours d'exécution"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep $CONTAINER_NAME
else
    echo "❌ Le conteneur ne fonctionne pas"
    docker logs $CONTAINER_NAME --tail=20
    exit 1
fi

# 9. Test de santé final
echo "🏥 Test de santé de l'application..."
if curl -f http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Application en ligne et fonctionnelle sur le port 8082"
else
    echo "❌ L'application ne répond pas"
    docker logs $CONTAINER_NAME --tail=20
    exit 1
fi

# 10. Vérifier l'ouverture du port dans le firewall
echo "🔥 Vérification du firewall..."
if ufw status | grep -q "8082"; then
    echo "✅ Port 8082 ouvert dans le firewall"
else
    echo "⚠️  Ouverture du port 8082 dans le firewall..."
    ufw allow 8082
fi

# 11. Nettoyage des anciennes images (garder les 5 dernières)
echo "🧹 Nettoyage des anciennes images..."
docker images $REGISTRY/$IMAGE_NAME --format "table {{.Tag}}\t{{.CreatedAt}}" | grep -v "latest" | grep -v "buildcache" | tail -n +6 | awk '{print $1}' | xargs -r docker rmi || true

# 12. Nettoyage des conteneurs arrêtés et images non utilisées
echo "🧹 Nettoyage général Docker..."
docker container prune -f
docker image prune -f

echo "🎉 Déploiement terminé avec succès !"
echo "🌐 URL de l'API: http://***:8082"
echo "⚡ Build optimisé avec cache Docker"
echo "⏰ $(date)" 