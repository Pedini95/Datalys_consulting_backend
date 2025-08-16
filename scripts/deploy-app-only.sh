#!/bin/bash
set -e

echo "🎯 DÉPLOIEMENT APPLICATION SEULEMENT - MySQL/Redis préservés"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 2. Vérifier l'état actuel du conteneur d'application
echo "🔍 Vérification de l'état du conteneur datalys-api..."

if docker ps | grep -q "datalys-api.*Up"; then
    echo "📦 Conteneur en cours d'exécution - Rebuild et redémarrage..."
    
    # Rebuild avec le nouveau code
    echo "🔨 Rebuild de l'image application..."
    docker-compose -f docker-compose.deploy.yml build --no-cache datalys-api
    
    # Redémarrage seulement de l'application
    echo "🔄 Redémarrage de l'application..."
    docker-compose -f docker-compose.deploy.yml restart datalys-api
    
elif docker ps -a | grep -q "datalys-api"; then
    echo "⏸️ Conteneur arrêté - Rebuild et démarrage..."
    
    # Rebuild avec le nouveau code
    echo "🔨 Rebuild de l'image application..."
    docker-compose -f docker-compose.deploy.yml build --no-cache datalys-api
    
    # Démarrage seulement de l'application
    echo "🚀 Démarrage de l'application..."
    docker-compose -f docker-compose.deploy.yml up -d datalys-api
    
else
    echo "🆕 Aucun conteneur existant - Création et démarrage..."
    
    # Build et démarrage seulement de l'application
    echo "🔨 Build de l'image application..."
    docker-compose -f docker-compose.deploy.yml build datalys-api
    
    echo "🚀 Démarrage de l'application..."
    docker-compose -f docker-compose.deploy.yml up -d datalys-api
fi

# 3. Attendre le démarrage complet
echo "⏳ Attente du démarrage complet..."
sleep 45

# 4. Vérifications de santé
echo "🔍 Vérifications de santé..."

# Vérifier que le conteneur de l'application tourne
if docker ps | grep -q "datalys-api.*Up"; then
    echo "✅ Conteneur d'application opérationnel"
else
    echo "❌ Problème avec le conteneur d'application"
    docker-compose -f docker-compose.deploy.yml logs --tail=15 datalys-api
    exit 1
fi

# Vérifier que l'application répond
for i in {1..12}; do
    if curl -f --connect-timeout 10 --max-time 20 http://localhost:8082/health > /dev/null 2>&1; then
        echo "✅ Application accessible et fonctionnelle après ${i}0 secondes"
        echo ""
        echo "🎉 DÉPLOIEMENT RÉUSSI !"
        echo "🌐 Application accessible sur le port 8082"
        echo "💾 MySQL et Redis préservés et inchangés"
        exit 0
    fi
    echo "⏳ Tentative $i/12 - L'application démarre..."
    sleep 10
done

# Si on arrive ici, il y a un problème
echo "⚠️ L'application met du temps à démarrer ou ne répond pas"
echo "📋 Logs pour diagnostic :"
docker-compose -f docker-compose.deploy.yml logs --tail=20 datalys-api

echo "🎯 Déploiement application terminé (vérifiez les logs ci-dessus)" 