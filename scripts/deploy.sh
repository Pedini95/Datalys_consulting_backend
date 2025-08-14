#!/bin/bash

# Script de déploiement automatique pour Datalys Consulting API
set -e

echo "🚀 Début du déploiement automatique..."

# Variables
REGISTRY="localhost:8081"
IMAGE_NAME="datalys/api"
PROJECT_DIR="/opt/Datalys_consulting_backend"

# 1. Vérifier et redémarrer les services Docker
echo "🔧 Vérification des services Docker..."
docker start redis-db mysql-db registry || true

# 2. Aller dans le répertoire du projet
cd $PROJECT_DIR

# 3. Mettre à jour le code depuis Git
echo "📦 Mise à jour du code..."
git fetch origin
git reset --hard origin/main

# 4. Reconstruire l'image Docker
echo "🐳 Construction de l'image Docker..."
docker build -t $REGISTRY/$IMAGE_NAME:latest -f src/Dockerfile .

# 5. Redémarrer le deployment Kubernetes
echo "☸️  Redémarrage du deployment Kubernetes..."
kubectl rollout restart deployment/datalys-api

# 6. Surveiller le déploiement
echo "👀 Surveillance du déploiement..."
kubectl rollout status deployment/datalys-api --timeout=300s

# 7. Vérifier les pods
echo "🔍 Vérification des pods..."
kubectl get pods -l app=datalys-api

# 8. Test de santé
echo "🏥 Test de santé de l'application..."
sleep 30
if curl -f http://localhost:32015/health > /dev/null 2>&1; then
    echo "✅ Application en ligne et fonctionnelle"
else
    echo "❌ L'application ne répond pas"
    kubectl logs -l app=datalys-api --tail=20
    exit 1
fi

echo "🎉 Déploiement terminé avec succès !" 