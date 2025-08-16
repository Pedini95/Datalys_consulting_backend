#!/bin/bash
set -e

echo "🧠 DÉPLOIEMENT INTELLIGENT - Gestion automatique"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 2. Vérifier l'état du conteneur et agir en conséquence
echo "🔍 Vérification de l'état du conteneur..."

if docker ps | grep -q "datalys-api"; then
    echo "📦 Conteneur en cours d'exécution - Redémarrage..."
    docker-compose restart datalys-api
elif docker ps -a | grep -q "datalys-api"; then
    echo "🔄 Conteneur arrêté - Redémarrage..."
    docker-compose start datalys-api
else
    echo "🚀 Aucun conteneur - Build et démarrage..."
    docker-compose build datalys-api
    docker-compose up -d datalys-api
fi

# 3. Attendre le démarrage
echo "⏳ Attente du démarrage complet..."
sleep 45

# 4. Vérifications multiples
echo "🔍 Vérifications de santé..."

# Vérifier que le conteneur tourne
if docker ps | grep -q "datalys-api.*Up"; then
    echo "✅ Conteneur en cours d'exécution"
else
    echo "❌ Problème avec le conteneur"
    docker-compose logs --tail=10 datalys-api
    exit 1
fi

# Vérifier l'application
for i in {1..6}; do
    if curl -f --connect-timeout 10 --max-time 20 http://localhost:8082/health > /dev/null 2>&1; then
        echo "✅ Application opérationnelle après ${i}0 secondes"
        exit 0
    fi
    echo "⏳ Tentative $i/6 - Attente supplémentaire..."
    sleep 10
done

echo "⚠️ L'application met du temps à démarrer, vérification des logs..."
docker-compose logs --tail=15 datalys-api

echo "🧠 Déploiement intelligent terminé !" 