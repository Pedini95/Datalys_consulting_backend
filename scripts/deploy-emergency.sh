#!/bin/bash
set -e

echo "🚨 DÉPLOIEMENT D'URGENCE - Correction des imports"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Arrêter tous les conteneurs
echo "🛑 Arrêt des conteneurs..."
docker-compose down

# 2. Nettoyer les images
echo "🧹 Nettoyage des images..."
docker image prune -f
docker system prune -f

# 3. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 4. Rebuild avec cache intelligent
echo "🔨 Rebuild avec cache intelligent..."
docker-compose build --pull

# 5. Redémarrage
echo "🚀 Redémarrage..."
docker-compose up -d

# 6. Attendre le démarrage
echo "⏳ Attente du démarrage..."
sleep 30

# 7. Vérification
echo "🔍 Vérification..."
if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Application en ligne et fonctionnelle"
else
    echo "❌ L'application ne répond pas"
    docker-compose logs --tail=20 datalys-api
    exit 1
fi

echo "🎉 Déploiement d'urgence terminé !" 