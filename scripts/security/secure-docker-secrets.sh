#!/bin/bash

# ============================================================================
# Script de Sécurisation des Secrets Docker
# Date: 2025-10-12
# Usage: ./scripts/security/secure-docker-secrets.sh
# ============================================================================

set -e

echo "════════════════════════════════════════════════════════════"
echo "🔐 SÉCURISATION DES SECRETS DOCKER"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Répertoire de travail
WORK_DIR="/root/datalys-backend"

echo "📍 Répertoire de travail: $WORK_DIR"
cd $WORK_DIR
echo ""

# Vérifier si .env existe déjà
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Le fichier .env existe déjà${NC}"
    read -p "Voulez-vous le recréer? (y/N): " RECREATE
    if [ "$RECREATE" != "y" ] && [ "$RECREATE" != "Y" ]; then
        echo "Opération annulée"
        exit 0
    fi
    mv .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Backup créé${NC}"
fi

# Générer des secrets forts
echo "🔑 Génération de secrets forts..."
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
echo -e "${GREEN}✅ Secrets générés${NC}"
echo ""

# Demander les informations
echo "📝 Veuillez fournir les informations suivantes:"
echo ""

read -p "Mot de passe MySQL (actuel: DatalysApp2025): " DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-DatalysApp2025}

read -p "Mot de passe Email: " MAIL_PASSWORD

echo ""
echo "🔄 Création du fichier .env..."

# Créer le fichier .env
cat > .env << EOF
# ============================================================================
# SECRETS DE PRODUCTION - NE JAMAIS COMMITTER CE FICHIER
# Date de création: $(date '+%Y-%m-%d %H:%M:%S')
# ============================================================================

# Database
DB_HOST=172.17.0.2
DB_PORT=3306
DB_NAME=datalys_consulting
DB_USER=datalys_app
DB_PASSWORD=$DB_PASSWORD

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY

# Email (SMTP Hostinger)
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=appweb@datalysconsulting.com
MAIL_PASSWORD=$MAIL_PASSWORD
MAIL_DEFAULT_SENDER=appweb@datalysconsulting.com
SENDER_NAME=Datalys Consulting

# App Config
FLASK_ENV=production
FLASK_DEBUG=False
ENV=production
UPLOAD_FOLDER=/app/src/static/files
LOG_FILE_PATH=/app/src/logs/datalys_consulting.log

# Firebase
FIREBASE_ENABLED=True
FCM_AUTO_NOTIFY_HIGH_PRIORITY=True
FCM_AUTO_NOTIFY_CRITICAL_PRIORITY=True

# App Info
APP_VERSION=latest
APP_URL=http://82.112.253.137:8082

# Timeouts
TIME_OUT=60
DB_CONNECT_TIMEOUT=30
DB_READ_TIMEOUT=60
REDIS_CONNECT_TIMEOUT=30
REDIS_READ_TIMEOUT=60
HTTP_TIMEOUT=30
HTTP_CONNECT_TIMEOUT=10

# Session
SESSION_EXPIRE_MINUTES=30
EOF

echo -e "${GREEN}✅ Fichier .env créé${NC}"
echo ""

# Sécuriser le fichier
echo "🔒 Sécurisation du fichier .env..."
chmod 600 .env
chown root:root .env
echo -e "${GREEN}✅ Permissions configurées (600, root:root)${NC}"
echo ""

# Vérifier que .env est dans .gitignore
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo -e "${GREEN}✅ .env ajouté à .gitignore${NC}"
else
    echo -e "${GREEN}✅ .env déjà dans .gitignore${NC}"
fi
echo ""

# Nettoyer docker-compose.yml des secrets en clair
echo "🧹 Nettoyage de docker-compose.yml..."
if [ -f "docker-compose.deploy.yml" ]; then
    # Backup
    cp docker-compose.deploy.yml docker-compose.deploy.yml.backup
    
    # Remplacer les valeurs par défaut par des variables
    sed -i 's/DB_PASSWORD:-datalysconsulting/DB_PASSWORD/g' docker-compose.deploy.yml
    sed -i 's/MAIL_PASSWORD:-Datalysconsulting@2025/MAIL_PASSWORD/g' docker-compose.deploy.yml
    sed -i 's/SECRET_KEY:-development-secret-change-in-production/SECRET_KEY/g' docker-compose.deploy.yml
    
    echo -e "${GREEN}✅ docker-compose.yml nettoyé${NC}"
else
    echo -e "${YELLOW}⚠️  docker-compose.deploy.yml non trouvé${NC}"
fi
echo ""

# Afficher les secrets générés
echo "════════════════════════════════════════════════════════════"
echo "✅ SECRETS CONFIGURÉS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🔑 SECRET_KEY: ${SECRET_KEY:0:20}..."
echo "🔑 JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:20}..."
echo ""
echo -e "${RED}⚠️  IMPORTANT:${NC}"
echo "  • NE PARTAGEZ JAMAIS ces secrets"
echo "  • Le fichier .env ne doit JAMAIS être commité"
echo "  • Sauvegardez ces secrets dans un gestionnaire de mots de passe"
echo ""
echo "📋 Prochaines étapes:"
echo "  1. Redémarrer les conteneurs Docker"
echo "  2. Vérifier que l'application fonctionne"
echo "  3. Supprimer les anciens fichiers de backup"
echo ""
echo "Commandes:"
echo "  docker-compose --env-file .env up -d"
echo ""

