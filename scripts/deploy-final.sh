#!/bin/bash
set -e

echo "🚀 DÉPLOIEMENT DÉFINITIF - FORCE UPDATE COMPLET"
echo "==============================================="
echo "⏰ $(date)"

# Aller dans le bon répertoire
cd /opt/Datalys_consulting_backend

echo "🛑 1. Arrêt et nettoyage COMPLET..."
# Arrêter tous les conteneurs
docker-compose -f docker-compose.deploy.yml down --volumes --remove-orphans 2>/dev/null || true

# Supprimer toutes les images liées au projet
docker images | grep -E "(datalys|consulting)" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

# Nettoyer le cache Docker
docker system prune -af --volumes 2>/dev/null || true

echo "📥 2. Récupération FORCÉE du code..."
# Sauvegarder les modifications locales
git stash 2>/dev/null || true

# Nettoyer complètement le répertoire Git
git clean -fd
git reset --hard HEAD

# Forcer la mise à jour depuis le serveur
git fetch origin develop --force
git reset --hard origin/develop

# Vérifier que le pull a fonctionné
LATEST_COMMIT=$(git rev-parse HEAD)
echo "✅ Code à jour - Commit: $LATEST_COMMIT"

echo "🔧 3. Correction des permissions..."
mkdir -p ./logs ./uploads ./src/logs ./src/static/files
chmod -R 755 ./logs ./uploads ./src/logs ./src/static 2>/dev/null || true

echo "🔨 4. Reconstruction COMPLÈTE (sans cache)..."
# Forcer la reconstruction sans cache
DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose -f docker-compose.deploy.yml build --no-cache --force-rm

echo "🚀 5. Démarrage des services..."
docker-compose -f docker-compose.deploy.yml up -d

echo "⏳ 6. Vérification complète..."
sleep 20

# Vérifier que les conteneurs sont en marche
echo "📊 État des conteneurs:"
docker-compose -f docker-compose.deploy.yml ps

# Test de santé avec plusieurs tentatives
for i in {1..10}; do
    if curl -f --connect-timeout 5 --max-time 10 http://localhost:8082/health >/dev/null 2>&1; then
        echo "✅ SUCCESS: Application opérationnelle !"
        echo "🔗 API disponible sur: http://82.112.253.137:8082"
        echo "🔗 Health check: http://82.112.253.137:8082/health"
        exit 0
    fi
    echo "⏳ Tentative $i/10 - En attente..."
    sleep 10
done

echo "⚠️ WARNING: Application pas encore complètement opérationnelle"
echo "📋 Logs récents:"
docker-compose -f docker-compose.deploy.yml logs --tail=20 datalys-api

echo "🎉 Déploiement terminé - Vérifiez les logs si nécessaire" 