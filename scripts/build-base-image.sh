#!/bin/bash

echo "🔨 Construction de l'image de base optimisée..."
echo "⏰ $(date)"

# Variables
REGISTRY="localhost:8081"
BASE_IMAGE_NAME="datalys/base"

# Enable Docker BuildKit for better performance
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

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
docker build \
  --tag $REGISTRY/$BASE_IMAGE_NAME:latest \
  --progress=plain \
  -f src/Dockerfile.base .

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