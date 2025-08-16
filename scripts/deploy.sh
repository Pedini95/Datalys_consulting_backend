#!/bin/bash
set -e

echo "🚀 DÉPLOIEMENT AUTOMATIQUE - Ultra-rapide et sécurisé"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull ultra-rapide
echo "📥 Pull ultra-rapide..."
git fetch origin develop --depth=1
git reset --hard origin/develop

# 2. Fixer les permissions logs et uploads (correction automatique)
echo "🔧 Correction automatique des permissions..."
mkdir -p ./logs ./uploads
chown -R 999:999 ./logs ./uploads 2>/dev/null || true
chmod -R 755 ./logs ./uploads 2>/dev/null || true

# 3. Check si rebuild nécessaire (optimisation intelligente)
CURRENT_HASH=$(git rev-parse HEAD)
LAST_BUILD_HASH_FILE="/tmp/datalys_last_build_hash"

if [ -f "$LAST_BUILD_HASH_FILE" ] && [ "$(cat $LAST_BUILD_HASH_FILE)" = "$CURRENT_HASH" ]; then
    echo "🚀 Code inchangé - Redémarrage simple..."
    
    # Redémarrage rapide sans rebuild
    if docker ps | grep -q "datalys-api.*Up"; then
        echo "🔄 Redémarrage express..."
        docker-compose -f docker-compose.deploy.yml restart datalys-api
    else
        echo "🚀 Démarrage express..."
        docker-compose -f docker-compose.deploy.yml up -d datalys-api
    fi
    
    # Health check rapide
    echo "🔍 Vérification express..."
    sleep 10
    for i in {1..3}; do
        if curl -f --connect-timeout 5 --max-time 10 http://localhost:8082/health > /dev/null 2>&1; then
            echo "✅ Application opérationnelle en ~15 secondes !"
            exit 0
        fi
        sleep 5
    done
    
else
    echo "🔨 Nouveau code détecté - Build optimisé avec cache..."
    
    # Build avec cache intelligent (SANS --no-cache)
    if docker ps | grep -q "datalys-api.*Up"; then
        echo "📦 Rebuild avec cache..."
        docker-compose -f docker-compose.deploy.yml build datalys-api
        docker-compose -f docker-compose.deploy.yml restart datalys-api
    else
        echo "🚀 Build et démarrage..."
        docker-compose -f docker-compose.deploy.yml build datalys-api
        docker-compose -f docker-compose.deploy.yml up -d datalys-api
    fi
    
    # Enregistrer le hash pour les prochains déploiements
    echo "$CURRENT_HASH" > "$LAST_BUILD_HASH_FILE"
    
    # Health check optimisé
    echo "🔍 Vérification optimisée..."
    sleep 15
    for i in {1..6}; do
        if curl -f --connect-timeout 5 --max-time 10 http://localhost:8082/health > /dev/null 2>&1; then
            echo "✅ Application opérationnelle après ${i}5 secondes !"
            echo "🎉 DÉPLOIEMENT ULTRA-RAPIDE TERMINÉ !"
            exit 0
        fi
        echo "⏳ Tentative $i/6..."
        sleep 5
    done
fi

# Si on arrive ici, il y a un problème
echo "⚠️ Problème détecté, logs de diagnostic :"
docker-compose -f docker-compose.deploy.yml logs --tail=10 datalys-api

echo "⚡ Déploiement ultra-rapide terminé avec diagnostic" 