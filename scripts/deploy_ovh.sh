#!/bin/bash
# ========================================
# DATALYS CONSULTING - SCRIPT DE DÉPLOIEMENT OVH
# ========================================
# Usage: ./deploy_ovh.sh
# ========================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "  DATALYS CONSULTING - DÉPLOIEMENT OVH"
echo "========================================"
echo -e "${NC}"

# ========================================
# VARIABLES DE CONFIGURATION
# ========================================
SERVER_IP="152.228.130.133"
APP_DIR="/home/ubuntu/Datalys_consulting_backend"
DB_PASSWORD="jn9zAiwCZo7V5rpcVeugQKJaZR5cMpl"
MYSQL_ROOT_PASSWORD="pCzRiri2qt0TiCR9p7x7QgIXs0gK5wQy"
REDIS_PASSWORD="XYF2KjC2EGufO2O9EewW4w"

# ========================================
# ÉTAPE 1: MISE À JOUR DU SYSTÈME
# ========================================
echo -e "${YELLOW}[1/7] Mise à jour du système...${NC}"
apt update && apt upgrade -y

# ========================================
# ÉTAPE 2: INSTALLATION DE DOCKER
# ========================================
echo -e "${YELLOW}[2/7] Installation de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓ Docker installé${NC}"
else
    echo -e "${GREEN}✓ Docker déjà installé${NC}"
fi

# Installation de Docker Compose
if ! docker compose version &> /dev/null; then
    apt install -y docker-compose-plugin
    echo -e "${GREEN}✓ Docker Compose installé${NC}"
else
    echo -e "${GREEN}✓ Docker Compose déjà installé${NC}"
fi

# ========================================
# ÉTAPE 3: INSTALLATION DE NGINX & CERTBOT
# ========================================
echo -e "${YELLOW}[3/7] Installation de Nginx et Certbot...${NC}"
apt install -y nginx certbot python3-certbot-nginx git
systemctl enable nginx
systemctl start nginx
echo -e "${GREEN}✓ Nginx et Certbot installés${NC}"

# ========================================
# ÉTAPE 4: CONFIGURATION DU PARE-FEU
# ========================================
echo -e "${YELLOW}[4/7] Configuration du pare-feu...${NC}"
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw allow 8082/tcp   # API (temporaire, à supprimer après config Nginx)
ufw --force enable
echo -e "${GREEN}✓ Pare-feu configuré${NC}"

# ========================================
# ÉTAPE 5: CLONAGE DU PROJET
# ========================================
echo -e "${YELLOW}[5/7] Configuration du projet...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Si le projet existe déjà, le mettre à jour
if [ -d ".git" ]; then
    git pull origin develop
    echo -e "${GREEN}✓ Projet mis à jour${NC}"
else
    echo -e "${YELLOW}Veuillez cloner votre repository Git ici:${NC}"
    echo "cd $APP_DIR && git clone <votre-repo-url> ."
fi

# ========================================
# ÉTAPE 6: CONFIGURATION ENVIRONNEMENT
# ========================================
echo -e "${YELLOW}[6/7] Configuration de l'environnement...${NC}"

# Créer le fichier .env de production
cat > $APP_DIR/.env << EOF
# ========================================
# DATALYS CONSULTING - PRODUCTION OVH
# ========================================

# Database MySQL
DB_HOST=mysql-db
DB_PORT=3306
DB_NAME=datalys_consulting
DB_USER=datalys
DB_PASSWORD=${DB_PASSWORD}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

# Email SMTP (configurez selon votre fournisseur: Hostinger ou OVH)
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=appweb@datalysconsulting.com
MAIL_PASSWORD=Datalysconsulting@2025
MAIL_DEFAULT_SENDER=appweb@datalysconsulting.com
SENDER_NAME=Datalys Consulting

# Redis Cache
REDIS_HOST=redis-db
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=${REDIS_PASSWORD}

# Flask Configuration - PRODUCTION
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
FLASK_DEBUG=False

# Application
APP_URL=https://applicationweb.datalysconsulting.com
UPLOAD_FOLDER=/app/src/static/files

# Firebase Cloud Messaging
FIREBASE_ENABLED=True
FCM_AUTO_NOTIFY_HIGH_PRIORITY=True
FCM_AUTO_NOTIFY_CRITICAL_PRIORITY=True

# Logging
LOG_LEVEL=WARNING
LOG_FILE_PATH=/app/src/logs/datalys_consulting.log
EOF

chmod 600 $APP_DIR/.env
echo -e "${GREEN}✓ Fichier .env créé${NC}"

# ========================================
# ÉTAPE 7: LANCEMENT DES SERVICES
# ========================================
echo -e "${YELLOW}[7/7] Lancement des services Docker...${NC}"

# Créer le volume MySQL s'il n'existe pas
docker volume create mysql_data 2>/dev/null || true

# Modifier docker-compose pour ne pas utiliser de volume externe
sed -i 's/external: true/external: false/g' $APP_DIR/docker-compose.yml 2>/dev/null || true

# Lancer les services
cd $APP_DIR
docker compose --profile production up -d --build

# Attendre que MySQL soit prêt
echo -e "${YELLOW}Attente du démarrage de MySQL...${NC}"
sleep 30

# Initialiser la base de données
echo -e "${YELLOW}Initialisation de la base de données...${NC}"
docker exec -i mysql-db mysql -u root -p${MYSQL_ROOT_PASSWORD} < $APP_DIR/scripts/init_database.sql 2>/dev/null || true

echo -e "${GREEN}✓ Services démarrés${NC}"

# ========================================
# RÉSUMÉ
# ========================================
echo ""
echo -e "${BLUE}========================================"
echo "  DÉPLOIEMENT TERMINÉ"
echo "========================================${NC}"
echo ""
echo -e "${GREEN}Services actifs:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo "1. Configurer le DNS pour pointer vers ${SERVER_IP}"
echo "2. Obtenir le certificat SSL:"
echo "   certbot --nginx -d applicationweb.datalysconsulting.com"
echo ""
echo -e "${GREEN}URLs de test:${NC}"
echo "  API Health: http://${SERVER_IP}:8082/health"
echo ""
echo -e "${YELLOW}Identifiants admin:${NC}"
echo "  Email: admin@datalys.com"
echo "  Password: Admin@123 (à changer)"
echo ""
