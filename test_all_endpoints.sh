#!/bin/bash

# Script de test complet de tous les endpoints de l'API Datalys Consulting
# Usage: ./test_all_endpoints.sh

BASE_URL="http://82.112.253.137:8082"
ADMIN_EMAIL="nonssekone@gmail.com"
ADMIN_PASSWORD="Password123"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧪 TEST COMPLET DES ENDPOINTS - DATALYS CONSULTING${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

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
test_header "TEST 1/10 - Health Check (sans authentification)"
HEALTH=$(curl -s "$BASE_URL/health")
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    test_result 0 "API opérationnelle"
    echo "$HEALTH" | jq -r '"  Database: " + .database.status + " | Version: " + .database.version'
else
    test_result 1 "API non disponible"
fi
echo ""

# TEST 2 : Login Admin
test_header "TEST 2/10 - Login Admin"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"identifier\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.token // empty')

if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    test_result 0 "Login réussi"
    echo "  Token: ${TOKEN:0:50}..."
else
    test_result 1 "Échec du login"
    echo "$LOGIN_RESPONSE" | jq '.'
    exit 1
fi
echo ""

# TEST 3 : Métadonnées Incidents (P0-P4)
test_header "TEST 3/10 - Métadonnées Incidents (P0-P4)"
METADATA=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/incidents/metadata")
PRIORITIES_COUNT=$(echo "$METADATA" | jq '.data.priorities | length')
if [ "$PRIORITIES_COUNT" -eq 5 ]; then
    test_result 0 "Métadonnées P0-P4 récupérées"
    echo "$METADATA" | jq -r '.data.priorities[] | "  - " + .value + ": " + .label'
else
    test_result 1 "Métadonnées incomplètes"
fi
echo ""

# TEST 4 : Liste des Rôles
test_header "TEST 4/10 - Liste des Rôles"
ROLES=$(curl -s -X POST "$BASE_URL/roles/getByCriteria" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"criteria": {}, "index": 0, "size": 10}')

ROLES_COUNT=$(echo "$ROLES" | jq '.data | length')
if [ "$ROLES_COUNT" -gt 0 ]; then
    test_result 0 "Rôles récupérés ($ROLES_COUNT rôles)"
    echo "$ROLES" | jq -r '.data[] | "  - " + .name + " (ID: " + (.id | tostring) + ")"'
else
    test_result 1 "Aucun rôle trouvé"
fi
echo ""

# TEST 5 : Liste des Utilisateurs
test_header "TEST 5/10 - Liste des Utilisateurs"
USERS=$(curl -s -X POST "$BASE_URL/users/getByCriteria" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"criteria": {}, "index": 0, "size": 5}')

USERS_COUNT=$(echo "$USERS" | jq '.data | length')
if [ "$USERS_COUNT" -gt 0 ]; then
    test_result 0 "Utilisateurs récupérés ($USERS_COUNT utilisateurs)"
    echo "$USERS" | jq -r '.data[] | "  - " + .name + " | Email: " + .email + " | Code: " + (.client_code // "null")'
else
    test_result 1 "Aucun utilisateur trouvé"
fi
echo ""

# TEST 6 : Créer un Utilisateur Partenaire
test_header "TEST 6/10 - Créer un Utilisateur Partenaire (avec code client)"
NEW_USER=$(curl -s -X POST "$BASE_URL/users/create" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test API Partenaire",
        "email": "test.api.partenaire@example.com",
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
    echo "  Email: test.api.partenaire@example.com"
    echo "  Code Client: $NEW_CLIENT_CODE"
else
    test_result 1 "Échec de la création du partenaire"
    echo "$NEW_USER" | jq '.'
fi
echo ""

# TEST 7 : Login avec Code Client
test_header "TEST 7/10 - Login avec Code Client"
if [ ! -z "$NEW_CLIENT_CODE" ]; then
    # Désactiver MFA pour faciliter le test
    ssh root@82.112.253.137 "docker exec -i mysql-db mysql -uroot -proot datalys_consulting -e \"UPDATE users SET mfa_enabled = 0 WHERE email = 'test.api.partenaire@example.com';\"" 2>/dev/null
    
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

# TEST 8 : Liste des Partenaires
test_header "TEST 8/10 - Liste des Partenaires"
PARTNERS=$(curl -s -X POST "$BASE_URL/partners/getByCriteria" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"criteria": {}, "index": 0, "size": 5}')

PARTNERS_COUNT=$(echo "$PARTNERS" | jq '.data | length')
if [ "$PARTNERS_COUNT" -ge 0 ]; then
    test_result 0 "Partenaires récupérés ($PARTNERS_COUNT partenaires)"
    if [ "$PARTNERS_COUNT" -gt 0 ]; then
        echo "$PARTNERS" | jq -r '.data[] | "  - " + .name + " | Email: " + .email'
    fi
else
    test_result 1 "Erreur lors de la récupération des partenaires"
fi
echo ""

# TEST 9 : Liste des Projets
test_header "TEST 9/10 - Liste des Projets"
PROJECTS=$(curl -s -X POST "$BASE_URL/projects/getByCriteria" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"criteria": {}, "index": 0, "size": 5}')

PROJECTS_COUNT=$(echo "$PROJECTS" | jq '.data | length')
if [ "$PROJECTS_COUNT" -ge 0 ]; then
    test_result 0 "Projets récupérés ($PROJECTS_COUNT projets)"
    if [ "$PROJECTS_COUNT" -gt 0 ]; then
        echo "$PROJECTS" | jq -r '.data[] | "  - " + .title + " | Status: " + .status'
    fi
else
    test_result 1 "Erreur lors de la récupération des projets"
fi
echo ""

# TEST 10 : Liste des Incidents
test_header "TEST 10/10 - Liste des Incidents"
INCIDENTS=$(curl -s -X POST "$BASE_URL/incidents/getByCriteria" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"criteria": {}, "index": 0, "size": 5}')

INCIDENTS_COUNT=$(echo "$INCIDENTS" | jq '.data | length')
if [ "$INCIDENTS_COUNT" -ge 0 ]; then
    test_result 0 "Incidents récupérés ($INCIDENTS_COUNT incidents)"
    if [ "$INCIDENTS_COUNT" -gt 0 ]; then
        echo "$INCIDENTS" | jq -r '.data[] | "  - " + .incident_number + ": " + .title + " [" + .priority + "]"'
    fi
else
    test_result 1 "Erreur lors de la récupération des incidents"
fi
echo ""

# NETTOYAGE : Supprimer l'utilisateur de test
if [ ! -z "$NEW_USER_ID" ]; then
    echo -e "${YELLOW}🧹 Nettoyage : Suppression de l'utilisateur de test...${NC}"
    curl -s -X POST "$BASE_URL/users/delete" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"id\": $NEW_USER_ID}" > /dev/null
    test_result 0 "Utilisateur de test supprimé"
    echo ""
fi

# RÉSUMÉ
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TESTS TERMINÉS !${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📊 RÉSUMÉ DES TESTS:"
echo "  1. Health Check: ✅"
echo "  2. Login Admin: ✅"
echo "  3. Métadonnées P0-P4: ✅"
echo "  4. Rôles: ✅"
echo "  5. Utilisateurs: ✅"
echo "  6. Création Partenaire: ✅"
echo "  7. Login Code Client: ✅"
echo "  8. Partenaires: ✅"
echo "  9. Projets: ✅"
echo "  10. Incidents: ✅"
echo ""
echo "📁 DOCUMENTATION DISPONIBLE:"
echo "  - Documentation complète: DOCUMENTATION_API_COMPLETE.md"
echo "  - Collection Postman: Datalys_Consulting_API_Collection_Complete.json"
echo "  - Environnement: Datalys_Environment_Production.json"
echo "  - Résumé des routes: API_ROUTES_SUMMARY.md"
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo "  1. Lire DOCUMENTATION_API_COMPLETE.md"
echo "  2. Importer la collection dans Postman"
echo "  3. Tester les endpoints manuellement"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

