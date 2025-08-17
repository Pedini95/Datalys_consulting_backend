#!/bin/bash

echo "🚀 DÉPLOIEMENT SIMPLIFIÉ - Force Update"
echo "========================================"

# 1. Arrêter et supprimer TOUT
echo "📦 Nettoyage complet..."
docker-compose -f docker-compose.deploy.yml down --rmi all --volumes --remove-orphans
docker system prune -af --volumes

# 2. Pull du code le plus récent
echo "📥 Récupération du code..."
git fetch origin
git reset --hard origin/develop
git clean -fd

# 3. Rebuild complet sans cache
echo "🔨 Reconstruction complète..."
docker-compose -f docker-compose.deploy.yml build --no-cache

# 4. Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose -f docker-compose.deploy.yml up -d

# 5. Vérification
echo "✅ Vérification..."
sleep 10
curl -f http://localhost:8082/health || echo "⚠️ Application pas encore prête"

echo "🎉 Déploiement terminé !" 