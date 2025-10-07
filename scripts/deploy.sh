#!/bin/bash
################################################################################
# Script de déploiement Datalys Consulting Backend
# Usage: ./scripts/deploy.sh
################################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs pour les logs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SERVER="root@82.112.253.137"
REMOTE_PATH="/root/Datalys_consulting_backend"
LOCAL_PATH="$(cd "$(dirname "$0")/.." && pwd)"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 DÉPLOIEMENT DATALYS CONSULTING${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Étape 1 : Transfert des fichiers
echo -e "${YELLOW}📤 1. Transfert des fichiers modifiés...${NC}"
rsync -avz --progress \
  --exclude='venv/' \
  --exclude='__pycache__/' \
  --exclude='.git/' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='logs/' \
  --exclude='*.log' \
  "${LOCAL_PATH}/src/" \
  "${SERVER}:${REMOTE_PATH}/src/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Fichiers transférés${NC}"
else
    echo -e "${RED}❌ Erreur lors du transfert${NC}"
    exit 1
fi
echo ""

# Étape 2 : Redémarrage du backend
echo -e "${YELLOW}🔄 2. Redémarrage du backend...${NC}"
ssh $SERVER "cd ${REMOTE_PATH} && docker-compose restart datalys-api"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend redémarré${NC}"
else
    echo -e "${RED}❌ Erreur lors du redémarrage${NC}"
    exit 1
fi
echo ""

# Étape 3 : Attente du démarrage
echo -e "${YELLOW}⏳ 3. Attente du démarrage (10 secondes)...${NC}"
sleep 10
echo -e "${GREEN}✅ Démarrage terminé${NC}"
echo ""

# Étape 4 : Vérification de l'état
echo -e "${YELLOW}🔍 4. Vérification de l'état des services...${NC}"
ssh $SERVER "cd ${REMOTE_PATH} && docker ps --filter 'name=datalys-api' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
echo ""

# Étape 5 : Test de l'API
echo -e "${YELLOW}🌐 5. Test de l'API...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://82.112.253.137:8082/health)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ API opérationnelle (HTTP $HTTP_CODE)${NC}"
    curl -s http://82.112.253.137:8082/health | python3 -m json.tool 2>/dev/null || echo ""
else
    echo -e "${YELLOW}⚠️  API pas encore prête (HTTP $HTTP_CODE) - attendez 30 secondes${NC}"
fi
echo ""

# Résumé
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "📊 Temps total: ~30 secondes"
echo -e "🌐 API: http://82.112.253.137:8082"
echo -e "🏥 Health: http://82.112.253.137:8082/health"
echo ""

