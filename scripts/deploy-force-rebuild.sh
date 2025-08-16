#!/bin/bash
set -e

echo "💥 DÉPLOIEMENT FORCE REBUILD - Reconstruction obligatoire"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 2. Arrêter et supprimer le conteneur
echo "🛑 Arrêt et suppression du conteneur..."
docker-compose -f docker-compose.deploy.yml down datalys-api || true

# 3. Supprimer l'ancienne image
echo "🗑️ Suppression de l'ancienne image..."
docker rmi datalys_consulting_backend-datalys-api:latest || true
docker rmi datalys_consulting_backend_datalys-api:latest || true

# 4. Rebuild complet de l'image
echo "🔨 Rebuild complet de l'image..."
docker-compose -f docker-compose.deploy.yml build --no-cache datalys-api

# 5. Démarrage avec la nouvelle image
echo "🚀 Démarrage avec la nouvelle image..."
docker-compose -f docker-compose.deploy.yml up -d datalys-api

# 6. Attendre le démarrage
echo "⏳ Attente du démarrage complet..."
sleep 60

# 7. Vérifications
echo "🔍 Vérifications de santé..."

# Vérifier que le conteneur tourne
if docker ps | grep -q "datalys-api"; then
    echo "✅ Conteneur en cours d'exécution"
else
    echo "❌ Problème avec le conteneur"
    docker-compose -f docker-compose.deploy.yml logs --tail=15 datalys-api
    exit 1
fi

# Vérifier l'application avec plusieurs tentatives
for i in {1..10}; do
    if curl -f --connect-timeout 10 --max-time 20 http://localhost:8082/health > /dev/null 2>&1; then
        echo "✅ Application opérationnelle après ${i}0 secondes"
        echo "🎉 SUCCÈS - Les imports ont été corrigés !"
        exit 0
    fi
    echo "⏳ Tentative $i/10 - Vérification en cours..."
    sleep 10
done

echo "📋 Logs pour diagnostic :"
docker-compose -f docker-compose.deploy.yml logs --tail=20 datalys-api

echo "💥 Rebuild forcé terminé !" 