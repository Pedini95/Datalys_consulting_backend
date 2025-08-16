#!/bin/bash
set -e

echo "⚡ DÉPLOIEMENT RAPIDE - Correction des imports"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 2. Rebuild rapide avec cache
echo "🔨 Rebuild rapide avec cache..."
docker-compose build

# 3. Redémarrage rapide
echo "🚀 Redémarrage rapide..."
docker-compose restart

# 4. Vérification rapide
echo "🔍 Vérification rapide..."
sleep 15

if curl -f --connect-timeout 5 --max-time 15 http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Application redémarrée avec succès"
else
    echo "⚠️ Application en cours de démarrage..."
    docker-compose logs --tail=10 datalys-api
fi

echo "⚡ Déploiement rapide terminé !" 