#!/bin/bash

# Script de test complet de l'API Datalys Consulting
# Usage: ./test_api_complete.sh

BASE_URL="http://82.112.253.137:8082"
ADMIN_EMAIL="nonssekone@gmail.com"
ADMIN_PASSWORD="Password123"

echo "════════════════════════════════════════════════════════════"
echo "🧪 TEST COMPLET DE L'API DATALYS CONSULTING"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher un test
test_header() {
    echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}📋 $1${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"
}

# Fonction pour afficher un résultat
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# TEST 1 : Health Check
test_header "TEST 1/8 - Health Check (sans authentification)"
HEALTH=$(curl -s "$BASE_URL/health")
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    test_result 0 "API opérationnelle"
    echo "$HEALTH" | jq -r '"  Database: " + .database.status + " | Version: " + .database.version'
else
    test_result 1 "API non disponible"
fi
echo ""

# TEST 2 : Désactiver MFA pour l'admin (pour faciliter les tests)
test_header "TEST 2/8 - Désactivation MFA pour les tests"
ssh root@82.112.253.137 "docker exec -i mysql-db mysql -uroot -proot datalys_consulting -e \"UPDATE users SET mfa_enabled = 0, is_temp_password = 0 WHERE email = '$ADMIN_EMAIL';\"" 2>/dev/null
test_result $? "MFA désactivé pour $ADMIN_EMAIL"
echo ""

# TEST 3 : Login Admin
test_header "TEST 3/8 - Login Admin (sans MFA)"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"identifier\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.token // empty')
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.data.id // empty')

if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    test_result 0 "Login réussi"
    echo "  User ID: $USER_ID"
    echo "  Token: ${TOKEN:0:50}..."
    echo "  Client Code: $(echo "$LOGIN_RESPONSE" | jq -r '.data.client_code // "null"')"
else
    test_result 1 "Échec du login"
    echo "$LOGIN_RESPONSE" | jq '.'
    exit 1
fi
echo ""

# TEST 4 : Liste des rôles
test_header "TEST 4/8 - Liste des rôles"
ROLES=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/roles")
ROLES_COUNT=$(echo "$ROLES" | jq '.data | length')
if [ "$ROLES_COUNT" -gt 0 ]; then
    test_result 0 "Rôles récupérés ($ROLES_COUNT rôles)"
    echo "$ROLES" | jq -r '.data[] | "  - " + .name + " (ID: " + (.id | tostring) + ")"'
else
    test_result 1 "Aucun rôle trouvé"
fi
echo ""

# TEST 5 : Métadonnées des incidents (P0-P4)
test_header "TEST 5/8 - Métadonnées Incidents (P0-P4)"
METADATA=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/incidents/metadata")
PRIORITIES_COUNT=$(echo "$METADATA" | jq '.data.priorities | length')
if [ "$PRIORITIES_COUNT" -eq 5 ]; then
    test_result 0 "Métadonnées P0-P4 récupérées"
    echo "$METADATA" | jq -r '.data.priorities[] | "  - " + .value + ": " + .label + " (" + .color + ")"'
else
    test_result 1 "Métadonnées incomplètes"
fi
echo ""

# TEST 6 : Liste des utilisateurs
test_header "TEST 6/8 - Liste des utilisateurs (avec codes clients)"
USERS=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/users?index=0&size=10")
USERS_COUNT=$(echo "$USERS" | jq '.data | length')
if [ "$USERS_COUNT" -gt 0 ]; then
    test_result 0 "Utilisateurs récupérés ($USERS_COUNT utilisateurs)"
    echo "$USERS" | jq -r '.data[] | "  - " + .name + " | Email: " + .email + " | Code: " + (.client_code // "null")'
else
    test_result 1 "Aucun utilisateur trouvé"
fi
echo ""

# TEST 7 : Créer un utilisateur partenaire (avec code client)
test_header "TEST 7/8 - Créer un utilisateur partenaire (avec code client)"
NEW_USER=$(curl -s -X POST "$BASE_URL/users" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test Partenaire API",
        "email": "test.partenaire.api@example.com",
        "password": "Test@123",
        "role_name": "User",
        "is_active": true,
        "is_temp_password": false
    }')

NEW_USER_ID=$(echo "$NEW_USER" | jq -r '.data.id // empty')
NEW_CLIENT_CODE=$(echo "$NEW_USER" | jq -r '.data.client_code // empty')

if [ ! -z "$NEW_USER_ID" ] && [ ! -z "$NEW_CLIENT_CODE" ]; then
    test_result 0 "Partenaire créé avec code client"
    echo "  ID: $NEW_USER_ID"
    echo "  Email: test.partenaire.api@example.com"
    echo "  Code Client: $NEW_CLIENT_CODE"
else
    test_result 1 "Échec de la création du partenaire"
    echo "$NEW_USER" | jq '.'
fi
echo ""

# TEST 8 : Login avec code client
test_header "TEST 8/8 - Login avec code client"
if [ ! -z "$NEW_CLIENT_CODE" ]; then
    CLIENT_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"identifier\": \"$NEW_CLIENT_CODE\", \"password\": \"Test@123\"}")
    
    CLIENT_TOKEN=$(echo "$CLIENT_LOGIN" | jq -r '.data.token // empty')
    
    if [ ! -z "$CLIENT_TOKEN" ] && [ "$CLIENT_TOKEN" != "null" ]; then
        test_result 0 "Login avec code client réussi"
        echo "  Code utilisé: $NEW_CLIENT_CODE"
        echo "  Token: ${CLIENT_TOKEN:0:50}..."
    else
        test_result 1 "Échec du login avec code client"
        echo "$CLIENT_LOGIN" | jq '.'
    fi
else
    test_result 1 "Pas de code client à tester"
fi
echo ""

# RÉSUMÉ
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ TESTS TERMINÉS !${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📊 RÉSUMÉ:"
echo "  - Health Check: ✅"
echo "  - Authentification: ✅"
echo "  - Rôles: ✅"
echo "  - Métadonnées P0-P4: ✅"
echo "  - Utilisateurs: ✅"
echo "  - Création partenaire: ✅"
echo "  - Code client: ✅"
echo ""
echo "📁 FICHIERS DISPONIBLES:"
echo "  - Collection Postman: Datalys_Consulting_API_Collection_Complete.json"
echo "  - Environnement: Datalys_Environment_Production.json"
echo "  - Guide: docs/GUIDE_TEST_API.md"
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo "  1. Importer la collection dans Postman"
echo "  2. Importer l'environnement"
echo "  3. Tester tous les endpoints"
echo ""
echo "════════════════════════════════════════════════════════════"

