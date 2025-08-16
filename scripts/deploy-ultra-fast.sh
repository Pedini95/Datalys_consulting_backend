#!/bin/bash
set -e

echo "🚀 DÉPLOIEMENT ULTRA-RAPIDE - Redémarrage seulement"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 2. Redémarrage sans rebuild (plus rapide)
echo "🔄 Redémarrage rapide..."
docker-compose restart datalys-api

# 3. Vérification immédiate
echo "🔍 Vérification..."
sleep 10

if curl -f --connect-timeout 5 --max-time 10 http://localhost:8082/health > /dev/null 2>&1; then
    echo "✅ Application redémarrée avec succès"
else
    echo "⚠️ Application en cours de démarrage, vérification des logs..."
    docker-compose logs --tail=5 datalys-api
fi

echo "🚀 Déploiement ultra-rapide terminé en ~30 secondes !" 