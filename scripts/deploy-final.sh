#!/bin/bash
set -e

echo "🏁 DÉPLOIEMENT FINAL - Application complète avec base de données"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull du code le plus récent
echo "📥 Pull du code le plus récent..."
git fetch origin
git reset --hard origin/develop

# 2. Arrêter tous les services
echo "🛑 Arrêt de tous les services..."
docker-compose down

# 3. Démarrer les services avec la base de données
echo "🚀 Démarrage de tous les services..."
docker-compose up -d

# 4. Attendre que MySQL soit prêt
echo "⏳ Attente du démarrage de MySQL..."
sleep 30

# Vérifier que MySQL est prêt
for i in {1..10}; do
    if docker exec mysql-db mysqladmin ping -h localhost -u root -ppassword > /dev/null 2>&1; then
        echo "✅ MySQL est prêt après ${i}0 secondes"
        break
    fi
    echo "⏳ MySQL en cours de démarrage... ($i/10)"
    sleep 10
done

# 5. Attendre le démarrage de l'application
echo "⏳ Attente du démarrage de l'application..."
sleep 30

# 6. Vérifications finales
echo "🔍 Vérifications finales..."

# Vérifier que tous les conteneurs tournent
if docker ps | grep -q "datalys-api.*Up" && docker ps | grep -q "mysql-db.*Up"; then
    echo "✅ Tous les conteneurs sont opérationnels"
else
    echo "❌ Problème avec les conteneurs"
    docker-compose ps
    exit 1
fi

# Vérifier l'application
for i in {1..15}; do
    if curl -f --connect-timeout 10 --max-time 20 http://localhost:8082/health > /dev/null 2>&1; then
        echo "✅ Application opérationnelle après ${i}0 secondes"
        echo "🎉 DÉPLOIEMENT FINAL RÉUSSI !"
        echo "🌐 Application accessible sur le port 8082"
        exit 0
    fi
    echo "⏳ Tentative $i/15 - L'application démarre..."
    sleep 10
done

echo "📋 Logs pour diagnostic :"
echo "--- Logs de l'application ---"
docker-compose logs --tail=15 datalys-api
echo "--- Logs de MySQL ---"
docker-compose logs --tail=10 mysql-db

echo "🏁 Déploiement final terminé !" 