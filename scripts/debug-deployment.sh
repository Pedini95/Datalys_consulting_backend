#!/bin/bash

echo "🔍 DIAGNOSTIC DES PROBLÈMES DE DÉPLOIEMENT"
echo "==========================================="
echo "⏰ $(date)"

# Variables
SERVER_HOST="root@82.112.253.137"
SERVER_PATH="/opt/Datalys_consulting_backend"

echo ""
echo "📊 1. État Git local vs distant..."
echo "Local branch: $(git branch --show-current)"
echo "Local commit: $(git rev-parse HEAD)"
echo "Local changes: $(git status --porcelain | wc -l) fichiers modifiés"

echo ""
echo "📊 2. État Git sur le serveur..."
ssh $SERVER_HOST "cd $SERVER_PATH && echo 'Server branch: \$(git branch --show-current)' && echo 'Server commit: \$(git rev-parse HEAD)' && echo 'Server changes: \$(git status --porcelain | wc -l) fichiers modifiés'"

echo ""
echo "📊 3. État des conteneurs Docker..."
ssh $SERVER_HOST "cd $SERVER_PATH && docker-compose -f docker-compose.deploy.yml ps"

echo ""
echo "📊 4. Images Docker..."
ssh $SERVER_HOST "docker images | grep -E '(datalys|consulting)' || echo 'Aucune image trouvée'"

echo ""
echo "📊 5. Logs récents de l'application..."
ssh $SERVER_HOST "cd $SERVER_PATH && docker-compose -f docker-compose.deploy.yml logs --tail=10 datalys-api 2>/dev/null || echo 'Conteneur pas en marche'"

echo ""
echo "📊 6. Test de connectivité..."
if curl -f --connect-timeout 5 --max-time 10 http://82.112.253.137:8082/health >/dev/null 2>&1; then
    echo "✅ API accessible"
else
    echo "❌ API non accessible"
fi

echo ""
echo "📊 7. Espace disque sur le serveur..."
ssh $SERVER_HOST "df -h /"

echo ""
echo "📊 8. Processus Docker sur le serveur..."
ssh $SERVER_HOST "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "🔧 RECOMMANDATIONS:"
echo "- Si les commits sont différents → Exécutez: ./scripts/deploy-from-local.sh"
echo "- Si les conteneurs sont arrêtés → Problème de configuration"
echo "- Si l'API n'est pas accessible → Problème réseau ou application"
echo "- Si manque d'espace disque → Nettoyez avec: docker system prune -af" 