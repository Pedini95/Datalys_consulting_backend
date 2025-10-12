#!/bin/bash

# ============================================================================
# Script de Configuration du Déploiement Automatique GitHub Actions
# Date: 2025-10-12
# Usage: ./scripts/setup-github-deploy.sh
# ============================================================================

set -e

echo "════════════════════════════════════════════════════════════"
echo "🚀 CONFIGURATION DÉPLOIEMENT AUTOMATIQUE GITHUB ACTIONS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
SSH_KEY_PATH="$HOME/.ssh/github_actions_deploy"
SERVER_HOST="82.112.253.137"
SERVER_USER="root"

echo "📋 Ce script va:"
echo "   1. Générer une paire de clés SSH pour GitHub Actions"
echo "   2. Ajouter la clé publique au serveur"
echo "   3. Vous donner les instructions pour configurer GitHub"
echo ""
read -p "Continuer? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Opération annulée"
    exit 0
fi
echo ""

# Étape 1: Générer la clé SSH
echo "🔐 Étape 1/3: Génération de la clé SSH..."
if [ -f "$SSH_KEY_PATH" ]; then
    echo -e "${YELLOW}⚠️  La clé existe déjà: $SSH_KEY_PATH${NC}"
    read -p "Voulez-vous la régénérer? (y/N): " REGENERATE
    if [ "$REGENERATE" = "y" ] || [ "$REGENERATE" = "Y" ]; then
        rm -f "$SSH_KEY_PATH" "$SSH_KEY_PATH.pub"
        echo "Ancienne clé supprimée"
    else
        echo "Utilisation de la clé existante"
    fi
fi

if [ ! -f "$SSH_KEY_PATH" ]; then
    ssh-keygen -t ed25519 -C "github-actions@datalysconsulting.com" -f "$SSH_KEY_PATH" -N ""
    echo -e "${GREEN}✅ Clé SSH générée${NC}"
else
    echo -e "${GREEN}✅ Clé SSH existante${NC}"
fi
echo ""

# Étape 2: Ajouter la clé au serveur
echo "📤 Étape 2/3: Ajout de la clé publique au serveur..."
echo "Connexion à $SERVER_USER@$SERVER_HOST..."

# Copier la clé publique
if ssh-copy-id -i "$SSH_KEY_PATH.pub" "$SERVER_USER@$SERVER_HOST" 2>/dev/null; then
    echo -e "${GREEN}✅ Clé publique ajoutée au serveur${NC}"
else
    echo -e "${YELLOW}⚠️  ssh-copy-id a échoué, ajout manuel...${NC}"
    
    # Méthode alternative
    PUB_KEY=$(cat "$SSH_KEY_PATH.pub")
    ssh "$SERVER_USER@$SERVER_HOST" "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PUB_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Clé publique ajoutée manuellement${NC}"
    else
        echo -e "${RED}❌ Échec de l'ajout de la clé${NC}"
        exit 1
    fi
fi

# Tester la connexion
echo ""
echo "🧪 Test de connexion avec la nouvelle clé..."
if ssh -i "$SSH_KEY_PATH" -o BatchMode=yes "$SERVER_USER@$SERVER_HOST" "echo 'Connexion réussie'" 2>/dev/null; then
    echo -e "${GREEN}✅ Connexion SSH fonctionnelle${NC}"
else
    echo -e "${RED}❌ La connexion SSH a échoué${NC}"
    exit 1
fi
echo ""

# Étape 3: Instructions pour GitHub
echo "════════════════════════════════════════════════════════════"
echo "📝 Étape 3/3: Configuration des Secrets GitHub"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}Allez sur GitHub:${NC}"
echo "   1. Ouvrez votre repository sur GitHub"
echo "   2. Allez dans Settings → Secrets and variables → Actions"
echo "   3. Cliquez sur 'New repository secret'"
echo ""
echo "Créez ces 3 secrets:"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Secret 1: SSH_HOST${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Nom: SSH_HOST"
echo "Valeur:"
echo "$SERVER_HOST"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Secret 2: SSH_USER${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Nom: SSH_USER"
echo "Valeur:"
echo "$SERVER_USER"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Secret 3: SSH_PRIVATE_KEY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Nom: SSH_PRIVATE_KEY"
echo "Valeur: (Copiez TOUT le contenu ci-dessous, y compris BEGIN et END)"
echo ""
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"
cat "$SSH_KEY_PATH"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"
echo ""

# Sauvegarder dans un fichier pour faciliter la copie
SECRETS_FILE="/tmp/github_secrets_$(date +%Y%m%d_%H%M%S).txt"
cat > "$SECRETS_FILE" << EOF
════════════════════════════════════════════════════════════
SECRETS GITHUB ACTIONS - Datalys Consulting
════════════════════════════════════════════════════════════

Secret 1: SSH_HOST
──────────────────
$SERVER_HOST

Secret 2: SSH_USER
──────────────────
$SERVER_USER

Secret 3: SSH_PRIVATE_KEY
──────────────────────────
$(cat "$SSH_KEY_PATH")

════════════════════════════════════════════════════════════
IMPORTANT: Supprimez ce fichier après utilisation !
rm $SECRETS_FILE
════════════════════════════════════════════════════════════
EOF

echo -e "${GREEN}✅ Les secrets ont été sauvegardés dans: $SECRETS_FILE${NC}"
echo ""
echo "📋 Vous pouvez copier les valeurs depuis ce fichier:"
echo "   cat $SECRETS_FILE"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Supprimez ce fichier après avoir configuré GitHub:${NC}"
echo "   rm $SECRETS_FILE"
echo ""

# Résumé
echo "════════════════════════════════════════════════════════════"
echo "✅ CONFIGURATION TERMINÉE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Configurez les 3 secrets sur GitHub"
echo "   2. Commitez et pushez sur la branche main"
echo "   3. Le déploiement se fera automatiquement"
echo ""
echo "📚 Documentation complète:"
echo "   docs/GITHUB_ACTIONS_SETUP.md"
echo ""
echo "🧪 Pour tester manuellement:"
echo "   GitHub → Actions → 🚀 Deploy to Production → Run workflow"
echo ""

