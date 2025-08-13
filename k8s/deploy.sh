#!/bin/bash

# Script de déploiement Kubernetes pour Datalys Consulting Backend
# Usage: ./deploy.sh [environment]

set -e

##Configuration
NAMESPACE="datalys"
APP_NAME="datalys-api"
IMAGE_NAME="datalys/api"
IMAGE_TAG="latest"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    if ! command -v kubectl &> /dev/null; then
        error "kubectl n'est pas installé"
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé"
    fi
    
    # Vérifier la connexion au cluster
    if ! kubectl cluster-info &> /dev/null; then
        error "Impossible de se connecter au cluster Kubernetes"
    fi
    
    success "Prérequis vérifiés"
}

# Créer le namespace
create_namespace() {
    log "Création du namespace $NAMESPACE..."
    
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        kubectl create namespace $NAMESPACE
        success "Namespace $NAMESPACE créé"
    else
        warning "Namespace $NAMESPACE existe déjà"
    fi
}

# Construire et pousser l'image Docker
build_and_push_image() {
    log "Construction de l'image Docker..."
    
    # Construire l'image
    docker build -t $IMAGE_NAME:$IMAGE_TAG -f src/Dockerfile .
    
    # Tag pour le registry (si nécessaire)
    # docker tag $IMAGE_NAME:$IMAGE_TAG your-registry.com/$IMAGE_NAME:$IMAGE_TAG
    
    # Pousser l'image (décommentez si vous avez un registry)
    # docker push your-registry.com/$IMAGE_NAME:$IMAGE_TAG
    
    success "Image Docker construite: $IMAGE_NAME:$IMAGE_TAG"
}

# Appliquer les secrets
apply_secrets() {
    log "Application des secrets..."
    
    if [ -f "k8s/secrets.yaml" ]; then
        kubectl apply -f k8s/secrets.yaml -n $NAMESPACE
        success "Secrets appliqués"
    else
        warning "Fichier secrets.yaml non trouvé. Exécutez d'abord ./generate-secrets.sh"
    fi
}

# Déployer l'application
deploy_application() {
    log "Déploiement de l'application..."
    
    # Appliquer le déploiement
    kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
    
    # Attendre que les pods soient prêts
    log "Attente que les pods soient prêts..."
    kubectl wait --for=condition=ready pod -l app=$APP_NAME -n $NAMESPACE --timeout=300s
    
    success "Application déployée"
}

# Vérifier le déploiement
check_deployment() {
    log "Vérification du déploiement..."
    
    # Vérifier les pods
    echo ""
    echo "📋 Statut des pods :"
    kubectl get pods -l app=$APP_NAME -n $NAMESPACE
    
    # Vérifier les services
    echo ""
    echo "🌐 Services :"
    kubectl get services -l app=$APP_NAME -n $NAMESPACE
    
    # Vérifier les ingress
    echo ""
    echo "🚪 Ingress :"
    kubectl get ingress -l app=$APP_NAME -n $NAMESPACE
    
    # Vérifier les secrets
    echo ""
    echo "🔐 Secrets :"
    kubectl get secrets -l app=$APP_NAME -n $NAMESPACE
    
    # Vérifier les PVC
    echo ""
    echo "💾 Persistent Volume Claims :"
    kubectl get pvc -l app=$APP_NAME -n $NAMESPACE
}

# Test de santé
health_check() {
    log "Test de santé de l'application..."
    
    # Attendre que le service soit prêt
    sleep 10
    
    # Obtenir l'IP du service
    SERVICE_IP=$(kubectl get service $APP_NAME-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -n "$SERVICE_IP" ]; then
        # Test de l'endpoint de santé
        if curl -f http://$SERVICE_IP/health &> /dev/null; then
            success "Application en bonne santé"
            echo "🌐 URL de l'application: http://$SERVICE_IP"
        else
            error "L'application ne répond pas correctement"
        fi
    else
        warning "Impossible de récupérer l'IP du service LoadBalancer"
        echo "ℹ️  Vérifiez le statut du service avec : kubectl get service $APP_NAME-service -n $NAMESPACE"
    fi
}

# Afficher les logs
show_logs() {
    log "Affichage des logs de l'application..."
    
    echo ""
    echo "📋 Logs des pods :"
    kubectl logs -l app=$APP_NAME -n $NAMESPACE --tail=20
}

# Fonction de rollback
rollback() {
    log "Rollback vers la version précédente..."
    
    # Rollback du déploiement
    kubectl rollout undo deployment/$APP_NAME -n $NAMESPACE
    
    # Attendre que le rollback soit terminé
    kubectl rollout status deployment/$APP_NAME -n $NAMESPACE
    
    success "Rollback terminé"
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commandes disponibles :"
    echo "  deploy     - Déployer l'application complète"
    echo "  secrets    - Appliquer seulement les secrets"
    echo "  build      - Construire l'image Docker"
    echo "  status     - Vérifier le statut du déploiement"
    echo "  logs       - Afficher les logs"
    echo "  rollback   - Rollback vers la version précédente"
    echo "  help       - Afficher cette aide"
    echo ""
    echo "Exemples :"
    echo "  $0 deploy"
    echo "  $0 status"
    echo "  $0 logs"
}

# Fonction principale
main() {
    case "${1:-deploy}" in
        "deploy")
            log "=== Déploiement complet de Datalys Consulting Backend ==="
            check_prerequisites
            create_namespace
            build_and_push_image
            apply_secrets
            deploy_application
            check_deployment
            health_check
            success "Déploiement terminé avec succès !"
            ;;
        "secrets")
            log "=== Application des secrets ==="
            check_prerequisites
            create_namespace
            apply_secrets
            success "Secrets appliqués !"
            ;;
        "build")
            log "=== Construction de l'image Docker ==="
            build_and_push_image
            ;;
        "status")
            log "=== Statut du déploiement ==="
            check_deployment
            ;;
        "logs")
            log "=== Logs de l'application ==="
            show_logs
            ;;
        "rollback")
            log "=== Rollback de l'application ==="
            rollback
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "Commande inconnue: $1"
            show_help
            ;;
    esac
}

# Gestion des erreurs
trap 'error "Déploiement interrompu par une erreur"' ERR

# Exécution
main "$@" 