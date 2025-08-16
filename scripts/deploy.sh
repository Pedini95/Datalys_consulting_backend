#!/bin/bash
set -e

echo "🚀 DÉPLOIEMENT AUTOMATIQUE - Ultra-rapide et sécurisé"
echo "⏰ $(date)"
echo "=================================================="

cd /opt/Datalys_consulting_backend

# 1. Sauvegarder le hash actuel AVANT le pull
OLD_HASH=$(git rev-parse HEAD 2>/dev/null || echo "none")

# 2. Pull ultra-rapide
echo "📥 Pull ultra-rapide..."
git fetch origin develop --depth=1
git reset --hard origin/develop

# 3. Obtenir le nouveau hash APRÈS le pull
CURRENT_HASH=$(git rev-parse HEAD)

# 4. Fixer les permissions logs et uploads (correction automatique)
echo "🔧 Correction automatique des permissions..."
mkdir -p ./logs ./uploads
chown -R 999:999 ./logs ./uploads 2>/dev/null || true
chmod -R 755 ./logs ./uploads 2>/dev/null || true

# 5. Configurer les réseaux Docker (correction automatique)
echo "🌐 Configuration automatique des réseaux Docker..."
# Connecter MySQL et Redis au réseau de l'application si pas déjà connectés
docker network connect datalys_consulting_backend_default mysql-db 2>/dev/null || true
docker network connect datalys_consulting_backend_default redis-db 2>/dev/null || true

# 6. Vérifier si rebuild nécessaire (logique corrigée)
LAST_BUILD_HASH_FILE="/tmp/datalys_last_build_hash"
FORCE_REBUILD=false

# Vérifier s'il y a des changements dans les fichiers source Python
if [ "$OLD_HASH" != "$CURRENT_HASH" ]; then
    echo "📝 Changements détectés entre $OLD_HASH et $CURRENT_HASH"
    
    # Vérifier s'il y a des changements dans les fichiers source critiques
    if git diff --name-only "$OLD_HASH" "$CURRENT_HASH" 2>/dev/null | grep -E '\.(py|txt|yml|yaml|json|env)$' > /dev/null; then
        echo "🔨 Changements dans les fichiers source détectés - Rebuild nécessaire"
        FORCE_REBUILD=true
    fi
fi

# Toujours forcer rebuild si le fichier hash n'existe pas ou si forced
if [ ! -f "$LAST_BUILD_HASH_FILE" ]; then
    echo "🔨 Première installation ou fichier hash manquant - Rebuild nécessaire"
    FORCE_REBUILD=true
fi

if [ "$FORCE_REBUILD" = "false" ] && [ -f "$LAST_BUILD_HASH_FILE" ] && [ "$(cat $LAST_BUILD_HASH_FILE)" = "$CURRENT_HASH" ]; then
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
            # Mettre à jour le hash seulement si le redémarrage réussit
            echo "$CURRENT_HASH" > "$LAST_BUILD_HASH_FILE"
            exit 0
        fi
        sleep 5
    done
    
    # Si le redémarrage simple échoue, forcer un rebuild
    echo "⚠️ Redémarrage simple échoué - Basculement vers rebuild complet"
    FORCE_REBUILD=true
fi

if [ "$FORCE_REBUILD" = "true" ]; then
    echo "🔨 Rebuild complet en cours..."
    
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
    
    # Health check optimisé
    echo "🔍 Vérification optimisée..."
    sleep 15
    for i in {1..6}; do
        if curl -f --connect-timeout 5 --max-time 10 http://localhost:8082/health > /dev/null 2>&1; then
            echo "✅ Application opérationnelle après rebuild complet !"
            # Enregistrer le hash pour les prochains déploiements SEULEMENT si succès
            echo "$CURRENT_HASH" > "$LAST_BUILD_HASH_FILE"
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

echo "⚡ Déploiement terminé avec diagnostic" 