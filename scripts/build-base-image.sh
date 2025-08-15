#!/bin/bash

echo "🔨 Construction de l'image de base optimisée..."
echo "⏰ $(date)"

# Variables
REGISTRY="localhost:8081"
BASE_IMAGE_NAME="datalys/base"

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

# Vérifier si l'image de base existe déjà
if docker images | grep -q "$BASE_IMAGE_NAME"; then
    echo "⚠️  Image de base existe déjà. Voulez-vous la reconstruire ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "✅ Utilisation de l'image de base existante"
        exit 0
    fi
fi

echo "🔄 Construction de l'image de base..."

if [ "$BUILDKIT_AVAILABLE" = true ]; then
    docker build \
      --tag $REGISTRY/$BASE_IMAGE_NAME:latest \
      --progress=plain \
      -f src/Dockerfile.base .
else
    docker build \
      --tag $REGISTRY/$BASE_IMAGE_NAME:latest \
      -f src/Dockerfile.base .
fi

if [ $? -eq 0 ]; then
    echo "✅ Image de base construite avec succès"
    echo "📊 Taille de l'image:"
    docker images $REGISTRY/$BASE_IMAGE_NAME:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    echo ""
    echo "🚀 Maintenant vous pouvez utiliser Dockerfile.optimized pour des builds ultra-rapides !"
else
    echo "❌ Échec de la construction de l'image de base"
    exit 1
fi 