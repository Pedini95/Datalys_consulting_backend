#!/bin/bash

# ============================================================================
# Script de Redéploiement après Reconstruction de la Base de Données
# Date: 2025-10-12
# Usage: ./scripts/redeploy-after-ransomware.sh
# ============================================================================

set -e  # Arrêter en cas d'erreur

echo "════════════════════════════════════════════════════════════"
echo "🔄 REDÉPLOIEMENT APRÈS RECONSTRUCTION DE LA BASE DE DONNÉES"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
SERVER="82.112.253.137"
USER="root"
DOCKER_COMPOSE_FILE="docker-compose.yml"
NEW_DB_PASSWORD="Datalys@2025"
ADMIN_EMAIL="admin@datalysconsulting.com"
ADMIN_PASSWORD="Password123"

echo "📋 Configuration:"
echo "   Serveur: $SERVER"
echo "   Nouveau mot de passe DB: $NEW_DB_PASSWORD"
echo ""

# Étape 1: Vérifier la connexion SSH
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Vérification de la connexion SSH..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ssh $USER@$SERVER "echo 'Connexion OK'" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connexion SSH établie${NC}"
else
    echo -e "${RED}❌ Impossible de se connecter au serveur${NC}"
    exit 1
fi
echo ""

# Étape 2: Vérifier que la base de données est OK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Vérification de la base de données..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
DB_CHECK=$(ssh $USER@$SERVER "docker exec mysql-db mysql -u root -p$NEW_DB_PASSWORD -e 'SHOW DATABASES LIKE \"datalys_consulting\";' 2>/dev/null | grep datalys_consulting || echo 'NOT_FOUND'")
if [[ "$DB_CHECK" == *"datalys_consulting"* ]]; then
    echo -e "${GREEN}✅ Base de données datalys_consulting trouvée${NC}"
else
    echo -e "${RED}❌ Base de données datalys_consulting introuvable${NC}"
    exit 1
fi

# Vérifier le nombre de tables
TABLE_COUNT=$(ssh $USER@$SERVER "docker exec mysql-db mysql -u root -p$NEW_DB_PASSWORD datalys_consulting -e 'SHOW TABLES;' 2>/dev/null | wc -l")
TABLE_COUNT=$((TABLE_COUNT - 1))  # Enlever la ligne d'en-tête
echo "   Tables trouvées: $TABLE_COUNT/9"
if [ "$TABLE_COUNT" -eq 9 ]; then
    echo -e "${GREEN}✅ Toutes les tables sont présentes${NC}"
else
    echo -e "${YELLOW}⚠️  Nombre de tables incorrect (attendu: 9, trouvé: $TABLE_COUNT)${NC}"
fi
echo ""

# Étape 3: Mettre à jour docker-compose.yml
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Mise à jour de docker-compose.yml..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Backup du fichier actuel
ssh $USER@$SERVER "cd /root/datalys-backend && cp docker-compose.yml docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)"
echo "   Backup créé: docker-compose.yml.backup-$(date +%Y%m%d-%H%M%S)"

# Mettre à jour le mot de passe
ssh $USER@$SERVER "cd /root/datalys-backend && sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=\"$NEW_DB_PASSWORD\"/' docker-compose.yml"
echo -e "${GREEN}✅ Mot de passe DB mis à jour dans docker-compose.yml${NC}"
echo ""

# Étape 4: Arrêter les conteneurs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Arrêt des conteneurs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh $USER@$SERVER "cd /root/datalys-backend && docker-compose down"
echo -e "${GREEN}✅ Conteneurs arrêtés${NC}"
echo ""

# Étape 5: Redémarrer les conteneurs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Redémarrage des conteneurs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh $USER@$SERVER "cd /root/datalys-backend && docker-compose up -d"
echo -e "${GREEN}✅ Conteneurs redémarrés${NC}"
echo ""

# Attendre que les conteneurs soient prêts
echo "⏳ Attente du démarrage des conteneurs (30s)..."
sleep 30

# Étape 6: Vérifier l'état des conteneurs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Vérification de l'état des conteneurs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ssh $USER@$SERVER "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
echo ""

# Vérifier le health check de l'API
echo "🔍 Vérification du health check de l'API..."
HEALTH_CHECK=$(ssh $USER@$SERVER "curl -s http://localhost:8082/health || echo 'FAILED'")
if [[ "$HEALTH_CHECK" == *"healthy"* ]] || [[ "$HEALTH_CHECK" == *"ok"* ]]; then
    echo -e "${GREEN}✅ API opérationnelle${NC}"
else
    echo -e "${RED}❌ API non opérationnelle${NC}"
    echo "Logs de l'API:"
    ssh $USER@$SERVER "docker logs datalys-api --tail 20"
    exit 1
fi
echo ""

# Étape 7: Tester le login
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Test de connexion avec le compte admin..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LOGIN_RESPONSE=$(ssh $USER@$SERVER "curl -s -X POST http://localhost:8082/auth/login \
  -H 'Content-Type: application/json' \
  -d '{\"identifier\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}'" 2>/dev/null)

if [[ "$LOGIN_RESPONSE" == *"token"* ]] || [[ "$LOGIN_RESPONSE" == *"access_token"* ]]; then
    echo -e "${GREEN}✅ Login réussi !${NC}"
    echo "   Email: $ADMIN_EMAIL"
    echo "   Token reçu"
else
    echo -e "${RED}❌ Échec du login${NC}"
    echo "Réponse: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Résumé final
echo "════════════════════════════════════════════════════════════"
echo "🎉 REDÉPLOIEMENT TERMINÉ AVEC SUCCÈS !"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 Résumé:"
echo "   ✅ Base de données: OK ($TABLE_COUNT tables)"
echo "   ✅ Docker: OK (conteneurs redémarrés)"
echo "   ✅ API: OK (health check passed)"
echo "   ✅ Auth: OK (login successful)"
echo ""
echo "🔐 Identifiants Admin:"
echo "   Email: $ADMIN_EMAIL"
echo "   Password: $ADMIN_PASSWORD"
echo ""
echo "🌐 URL de l'API:"
echo "   http://$SERVER:8082"
echo ""
echo "📋 Prochaines étapes recommandées:"
echo "   1. Mettre en place des backups automatiques"
echo "   2. Configurer fail2ban pour MySQL"
echo "   3. Auditer les logs de sécurité"
echo "   4. Changer le mot de passe admin par défaut"
echo ""

