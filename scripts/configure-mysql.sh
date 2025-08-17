#!/bin/bash

# ========================================
# SCRIPT DE CONFIGURATION MYSQL
# ========================================
# 
# Ce script configure MySQL pour écouter sur l'IP publique
# À exécuter si MySQL redémarre en mode localhost uniquement
#

set -e

echo "🔧 Configuration MySQL pour Datalys Consulting..."

# Variables
MYSQL_CONTAINER="mysql-db"
PUBLIC_IP="82.112.253.137"
MYSQL_PORT="3306"

echo "📋 Vérification de l'état actuel..."
CURRENT_BINDING=$(netstat -tlnp | grep :$MYSQL_PORT | head -1)
echo "État actuel: $CURRENT_BINDING"

if [[ $CURRENT_BINDING == *"127.0.0.1:$MYSQL_PORT"* ]]; then
    echo "⚠️  MySQL écoute sur localhost uniquement - Reconfiguration nécessaire"
    
    echo "🛑 Arrêt du conteneur MySQL..."
    docker stop $MYSQL_CONTAINER || true
    
    echo "🔄 Récupération des informations du conteneur..."
    MYSQL_IMAGE=$(docker inspect $MYSQL_CONTAINER --format='{{.Config.Image}}' 2>/dev/null || echo "mysql:8.0")
    
    echo "🗑️  Suppression de l'ancien conteneur..."
    docker rm $MYSQL_CONTAINER || true
    
    echo "🚀 Recréation avec le bon port mapping..."
    docker run -d \
        --name $MYSQL_CONTAINER \
        -p $PUBLIC_IP:$MYSQL_PORT:$MYSQL_PORT \
        --restart unless-stopped \
        --env MYSQL_ROOT_PASSWORD=root \
        --env MYSQL_DATABASE=datalys_consulting \
        --env MYSQL_USER=datalys \
        --env MYSQL_PASSWORD=datalysconsulting \
        $MYSQL_IMAGE
    
    echo "⏳ Attente du démarrage MySQL..."
    sleep 15
    
    echo "✅ MySQL reconfiguré avec succès !"
    
elif [[ $CURRENT_BINDING == *"$PUBLIC_IP:$MYSQL_PORT"* ]]; then
    echo "✅ MySQL écoute déjà sur l'IP publique - Aucune action nécessaire"
else
    echo "❌ Aucun MySQL détecté sur le port $MYSQL_PORT"
    exit 1
fi

echo "📊 État final:"
netstat -tlnp | grep :$MYSQL_PORT

echo ""
echo "🎉 Configuration MySQL terminée !"
echo "💡 MySQL écoute maintenant sur: $PUBLIC_IP:$MYSQL_PORT" 