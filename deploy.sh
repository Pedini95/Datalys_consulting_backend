#!/bin/bash

# Script de déploiement automatique pour Datalys Consulting Backend
# Usage: ./deploy.sh [environment]

set -e  # Arrêter en cas d'erreur

# Configuration
PROJECT_DIR="/home/datalys/Datalys_consulting_backend"
APP_DIR="$PROJECT_DIR/src"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/deploy.log"
BACKUP_DIR="$PROJECT_DIR/backups"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Le répertoire du projet n'existe pas: $PROJECT_DIR"
    fi
    
    if [ ! -d "$VENV_DIR" ]; then
        error "L'environnement virtuel n'existe pas: $VENV_DIR"
    fi
    
    if ! command -v pm2 &> /dev/null; then
        error "PM2 n'est pas installé"
    fi
    
    if ! command -v nginx &> /dev/null; then
        error "Nginx n'est pas installé"
    fi
    
    success "Prérequis vérifiés"
}

# Sauvegarde de la version actuelle
backup_current_version() {
    log "Sauvegarde de la version actuelle..."
    
    mkdir -p "$BACKUP_DIR"
    BACKUP_NAME="backup_$(date +'%Y%m%d_%H%M%S')"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    if [ -d "$APP_DIR" ]; then
        cp -r "$APP_DIR" "$BACKUP_PATH"
        log "Sauvegarde créée: $BACKUP_PATH"
    fi
}

# Mise à jour du code
update_code() {
    log "Mise à jour du code depuis Git..."
    
    cd "$PROJECT_DIR"
    
    # Sauvegarde des modifications locales
    if ! git stash push -m "Auto-stash before deployment $(date)" &> /dev/null; then
        warning "Aucune modification locale à sauvegarder"
    fi
    
    # Pull des dernières modifications
    if git pull origin main; then
        success "Code mis à jour avec succès"
    else
        error "Échec de la mise à jour du code"
    fi
}

# Installation des dépendances
install_dependencies() {
    log "Installation des dépendances..."
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    if pip install -r requirements.txt; then
        success "Dépendances installées avec succès"
    else
        error "Échec de l'installation des dépendances"
    fi
}

# Vérification de la configuration
check_configuration() {
    log "Vérification de la configuration..."
    
    cd "$APP_DIR"
    
    # Vérifier que les fichiers de config existent
    if [ ! -f ".env.local" ] && [ ! -f ".env.production" ]; then
        error "Aucun fichier de configuration trouvé (.env.local ou .env.production)"
    fi
    
    # Test de connexion à la base de données
    if python -c "from config import db; db.engine.execute('SELECT 1')" &> /dev/null; then
        success "Connexion à la base de données OK"
    else
        error "Impossible de se connecter à la base de données"
    fi
}

# Redémarrage de l'application
restart_application() {
    log "Redémarrage de l'application..."
    
    # Redémarrage PM2
    if pm2 restart datalys-app; then
        success "Application redémarrée avec PM2"
    else
        error "Échec du redémarrage de l'application"
    fi
    
    # Rechargement Nginx
    if sudo systemctl reload nginx; then
        success "Nginx rechargé"
    else
        error "Échec du rechargement de Nginx"
    fi
}

# Test de santé
health_check() {
    log "Test de santé de l'application..."
    
    # Attendre que l'application démarre
    sleep 5
    
    # Test de l'endpoint de santé
    if curl -f http://localhost/health &> /dev/null; then
        success "Application en bonne santé"
    else
        error "L'application ne répond pas correctement"
    fi
}

# Nettoyage des anciennes sauvegardes
cleanup_old_backups() {
    log "Nettoyage des anciennes sauvegardes..."
    
    # Garder seulement les 5 dernières sauvegardes
    cd "$BACKUP_DIR"
    ls -t | tail -n +6 | xargs -r rm -rf
    success "Anciennes sauvegardes nettoyées"
}

# Fonction principale
main() {
    log "=== Début du déploiement ==="
    
    check_prerequisites
    backup_current_version
    update_code
    install_dependencies
    check_configuration
    restart_application
    health_check
    cleanup_old_backups
    
    log "=== Déploiement terminé avec succès ==="
    success "L'application est maintenant en ligne!"
}

# Gestion des erreurs
trap 'error "Déploiement interrompu par une erreur"' ERR

# Exécution
main "$@" 