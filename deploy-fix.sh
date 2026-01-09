#!/bin/bash
set -e

echo "=== Script de déploiement Datalys Backend ==="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_info() { echo -e "${YELLOW}➜${NC} $1"; }

# 1. Arrêter tous les conteneurs et nettoyer
log_info "Arrêt des conteneurs existants..."
docker-compose down || true
docker stop datalys-api 2>/dev/null || true
docker rm datalys-api 2>/dev/null || true
log_success "Conteneurs arrêtés"

# 2. Nettoyer les images corrompues
log_info "Nettoyage des images Docker..."
docker rmi $(docker images 'datalys_consulting_backend-datalys-api' -q) 2>/dev/null || true
docker builder prune -f
log_success "Images nettoyées"

# 3. Rebuild complet sans cache
log_info "Reconstruction de l'image (cela peut prendre 3-5 minutes)..."
cd /root/Datalys_consulting_backend
docker-compose build --no-cache --pull datalys-api
log_success "Image reconstruite"

# 4. Démarrer les services
log_info "Démarrage des services..."
docker-compose up -d mysql-db redis-db
sleep 5
docker-compose up -d datalys-api
log_success "Services démarrés"

# 5. Attendre que l'API démarre
log_info "Attente du démarrage de l'API (30 secondes)..."
sleep 30

# 6. Vérifier les logs
log_info "Vérification des logs..."
docker logs datalys-api --tail 20

# 7. Tester l'API
log_info "Test de l'API..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/health || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
    log_success "API fonctionne! (HTTP $HTTP_CODE)"
    echo ""
    echo "=== Déploiement terminé avec succès ==="
    docker ps | grep datalys
else
    log_error "API ne répond pas correctement (HTTP $HTTP_CODE)"
    echo ""
    echo "Logs d'erreur:"
    docker logs datalys-api --tail 50
    exit 1
fi
