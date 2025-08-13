#!/bin/bash

# Script de déploiement pour Datalys Consulting Backend
# Usage: ./deploy.sh

set -e

echo "🚀 Déploiement de Datalys Consulting Backend..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
APP_NAME="datalys-api"
APP_DIR="/home/datalys/Datalys_consulting_backend"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si on est sur le serveur de production
if [ ! -d "$APP_DIR" ]; then
    log_error "Répertoire de l'application non trouvé: $APP_DIR"
    log_info "Ce script doit être exécuté sur le serveur de production"
    exit 1
fi

# Aller dans le répertoire de l'application
cd "$APP_DIR"

log_info "📁 Répertoire de travail: $(pwd)"

# Sauvegarder les logs actuels
if [ -d "$LOG_DIR" ]; then
    log_info "📋 Sauvegarde des logs actuels..."
    tar -czf "logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$LOG_DIR" .
fi

# Mettre à jour le code depuis Git
log_info "🔄 Mise à jour du code depuis Git..."
git fetch origin
git reset --hard origin/develop

# Activer l'environnement virtuel
log_info "🐍 Activation de l'environnement virtuel..."
source "$VENV_DIR/bin/activate"

# Mettre à jour les dépendances
log_info "📦 Mise à jour des dépendances..."
pip install --upgrade pip
pip install -r src/requirements.txt

# Créer les répertoires nécessaires
log_info "📁 Création des répertoires..."
mkdir -p "$LOG_DIR"
mkdir -p src/static/files/logos
mkdir -p src/static/files/files
mkdir -p src/static/files/projects

# Vérifier la configuration
if [ ! -f "src/.env.production" ]; then
    log_warn "⚠️  Fichier .env.production non trouvé"
    log_info "Création du fichier .env.production..."
    cp src/env.template src/.env.production
    log_warn "⚠️  Veuillez configurer src/.env.production avant de continuer"
    exit 1
fi

# Redémarrer l'application avec PM2
log_info "🔄 Redémarrage de l'application..."
pm2 restart "$APP_NAME" || pm2 start ecosystem.config.js

# Vérifier le statut
log_info "📊 Vérification du statut..."
pm2 status "$APP_NAME"

# Vérifier les logs
log_info "📋 Derniers logs de l'application:"
pm2 logs "$APP_NAME" --lines 10

# Test de santé
log_info "🏥 Test de santé de l'application..."
sleep 5
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    log_info "✅ Application en ligne et fonctionnelle"
else
    log_error "❌ L'application ne répond pas"
    log_info "Vérifiez les logs avec: pm2 logs $APP_NAME"
    exit 1
fi

# Redémarrer Nginx si nécessaire
log_info "🌐 Redémarrage de Nginx..."
sudo systemctl reload nginx

log_info "🎉 Déploiement terminé avec succès!"
log_info "📊 Statut: pm2 status"
log_info "📋 Logs: pm2 logs $APP_NAME"
log_info "🌐 URL: https://api.datalysconsulting.com" 