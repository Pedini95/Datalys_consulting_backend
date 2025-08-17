#!/bin/bash
set -e

echo "🚀 DÉPLOIEMENT DEPUIS LOCAL VERS SERVEUR"
echo "========================================="
echo "⏰ $(date)"

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "docker-compose.deploy.yml" ]; then
    echo "❌ Erreur: Exécutez ce script depuis la racine du projet"
    exit 1
fi

# Variables
SERVER_HOST="root@82.112.253.137"
SERVER_PATH="/opt/Datalys_consulting_backend"

echo "📝 1. Vérification et commit des modifications locales..."

# Vérifier s'il y a des modifications non commitées
if ! git diff-index --quiet HEAD --; then
    echo "⚠️ Modifications non commitées détectées"
    read -p "Voulez-vous les commiter automatiquement ? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        echo "💬 Entrez un message de commit (ou appuyez sur Entrée pour un message par défaut):"
        read COMMIT_MSG
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="🔧 Mise à jour automatique - $(date '+%Y-%m-%d %H:%M')"
        fi
        git commit -m "$COMMIT_MSG"
        echo "✅ Modifications commitées"
    else
        echo "❌ Veuillez commiter vos modifications avant le déploiement"
        exit 1
    fi
fi

echo "📤 2. Push vers le serveur Git..."
git push origin develop

# Attendre un peu pour s'assurer que le push est terminé
sleep 2

echo "🚀 3. Déploiement sur le serveur..."

# Copier le script de déploiement définitif sur le serveur
scp scripts/deploy-final.sh $SERVER_HOST:$SERVER_PATH/

# Exécuter le déploiement sur le serveur
ssh $SERVER_HOST "cd $SERVER_PATH && chmod +x deploy-final.sh && ./deploy-final.sh"

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "🔗 Votre application est disponible sur: http://82.112.253.137:8082"
echo "🔗 Health check: http://82.112.253.137:8082/health"
echo ""

# Test rapide depuis local
echo "🔍 Test rapide de l'API..."
if curl -f --connect-timeout 10 --max-time 15 http://82.112.253.137:8082/health >/dev/null 2>&1; then
    echo "✅ SUCCESS: API accessible depuis votre machine locale !"
else
    echo "⚠️ API pas encore accessible - Attendez quelques minutes et réessayez"
fi 