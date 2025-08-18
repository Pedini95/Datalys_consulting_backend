#!/bin/bash
set -e

# 🚀 DÉPLOIEMENT ZERO-DOWNTIME
# ============================

# Configuration
COMPOSE_FILE="docker-compose.deploy.yml"
COMPOSE_PROFILE="production"
SERVICE_NAME="datalys-api"
HEALTH_ENDPOINT="http://localhost:8082/health"
MAX_HEALTH_CHECKS=30
HEALTH_CHECK_INTERVAL=10

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Fonction de health check
check_health() {
    local attempts=0
    log "🔍 Vérification de la santé du service..."
    
    while [ $attempts -lt $MAX_HEALTH_CHECKS ]; do
        if curl -f --connect-timeout 5 --max-time 10 "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            success "Service opérationnel !"
            return 0
        fi
        
        attempts=$((attempts + 1))
        warning "Tentative $attempts/$MAX_HEALTH_CHECKS - Service non prêt"
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    error "Service n'a pas réussi le health check après $MAX_HEALTH_CHECKS tentatives"
}

# Fonction de rollback
rollback() {
    local previous_image=$1
    warning "🔄 Rollback vers l'image précédente: $previous_image"
    
    export IMAGE_TAG="$previous_image"
    docker-compose -f "$COMPOSE_FILE" --profile "$COMPOSE_PROFILE" up -d --no-deps "$SERVICE_NAME"
    
    if check_health; then
        success "Rollback réussi !"
    else
        error "Rollback échoué - intervention manuelle requise"
    fi
}

# Début du déploiement
log "🚀 DÉPLOIEMENT ZERO-DOWNTIME - $(date)"
log "📦 Image: ${IMAGE_TAG:-latest}"
log "🎯 Service: $SERVICE_NAME"
log "📄 Compose: $COMPOSE_FILE"
log "🏷️  Profile: $COMPOSE_PROFILE"

# Vérifier que IMAGE_TAG est défini
if [ -z "$IMAGE_TAG" ]; then
    warning "IMAGE_TAG non défini, utilisation de 'latest'"
    export IMAGE_TAG="latest"
fi

# Sauvegarder l'image actuelle pour rollback
CURRENT_IMAGE=$(docker inspect "$SERVICE_NAME" --format='{{.Config.Image}}' 2>/dev/null || echo "none")
log "💾 Image actuelle: $CURRENT_IMAGE"

# Étape 1: Variables d'environnement pour versioning
log "📋 1. Configuration des variables d'environnement..."
export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
export COMMIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
export ENVIRONMENT="production"

# Étape 2: Vérification que le service actuel fonctionne
log "🔍 2. Vérification du service actuel..."
if ! check_health; then
    warning "Service actuel non fonctionnel - déploiement forcé"
fi

# Étape 3: Préservation des permissions des fichiers d'upload
log "🔐 3. Configuration des permissions pour les uploads..."
mkdir -p ./src/static/files/logos ./src/static/files/files ./src/static/files/projects
chown -R 1000:1000 ./src/static/files/ 2>/dev/null || warning "Impossible de changer le propriétaire (permissions insuffisantes)"
chmod -R 775 ./src/static/files/ 2>/dev/null || warning "Impossible de changer les permissions"

# Étape 4: Reconstruction de l'image (si nécessaire)
log "🏗️  4. Reconstruction de l'image..."
if ! docker-compose -f "$COMPOSE_FILE" --profile "$COMPOSE_PROFILE" build --no-cache "$SERVICE_NAME"; then
    error "Échec de la reconstruction de l'image"
fi

# Étape 5: Démarrage du nouveau conteneur
log "🆙 5. Démarrage du nouveau service..."
if ! docker-compose -f "$COMPOSE_FILE" --profile "$COMPOSE_PROFILE" up -d --no-deps "$SERVICE_NAME"; then
    error "Échec du démarrage du nouveau service"
fi

# Étape 6: Health check du nouveau service
log "🏥 6. Vérification de la santé du nouveau service..."
if ! check_health; then
    warning "Nouveau service défaillant - tentative de rollback"
    if [ "$CURRENT_IMAGE" != "none" ]; then
        PREVIOUS_TAG=$(echo "$CURRENT_IMAGE" | cut -d':' -f2)
        rollback "$PREVIOUS_TAG"
    else
        error "Pas d'image précédente pour rollback"
    fi
fi

# Étape 7: Nettoyage des anciennes images
log "🧹 7. Nettoyage des anciennes images..."
docker image prune -f --filter "until=24h" || warning "Échec du nettoyage des images"

# Étape 8: Vérification finale
log "🔍 8. Vérification finale..."
if check_health; then
    success "Déploiement réussi !"
    log "🔗 Application: http://$(hostname -I | awk '{print $1}'):8082"
    log "📊 Health: $HEALTH_ENDPOINT"
    log "📦 Version: $IMAGE_TAG"
    log "🕐 Durée: $SECONDS secondes"
else
    error "Déploiement échoué - vérification finale non passée"
fi

# Affichage des informations de la version
log "📋 Informations de version déployée:"
docker inspect "$SERVICE_NAME" --format='Image: {{.Config.Image}}' || true
docker inspect "$SERVICE_NAME" --format='Started: {{.State.StartedAt}}' || true

success "✨ Déploiement zero-downtime terminé avec succès !" 