#!/bin/bash

# Script pour générer les secrets Kubernetes pour Datalys Consulting Backend
# Usage: ./generate-secrets.sh

set -e

echo "🔐 Génération des secrets Kubernetes pour Datalys Consulting Backend"
echo "=================================================================="

# Vérifier si kubectl est installé
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Demander les valeurs des secrets
echo ""
echo "📝 Veuillez entrer les informations de configuration :"
echo ""

# Base de données
read -p "🏠 Host de la base de données (ex: 82.112.253.137): " DB_HOST
read -p "👤 Utilisateur de la base de données (ex: datalys): " DB_USER
read -s -p "🔑 Mot de passe de la base de données: " DB_PASSWORD
echo ""
read -p "📊 Nom de la base de données (ex: datalys_consulting): " DB_NAME

# Redis
read -p "🔴 Host Redis (ex: 192.168.2.40): " REDIS_HOST
read -s -p "🔑 Mot de passe Redis (laissez vide si aucun): " REDIS_PASSWORD
echo ""

# Application
read -s -p "🔐 Clé secrète de l'application: " SECRET_KEY
echo ""

# Email SMTP
read -p "📧 Username SMTP (ex: datalysconsultingapp@datalysconsulting.com): " MAIL_USERNAME
read -s -p "🔑 Mot de passe SMTP: " MAIL_PASSWORD
echo ""
read -p "📤 Email expéditeur par défaut: " MAIL_DEFAULT_SENDER

# Webhook (optionnel)
read -s -p "🔗 Secret webhook (optionnel, laissez vide si pas utilisé): " WEBHOOK_SECRET
echo ""

echo ""
echo "🔄 Génération des secrets encodés en base64..."
echo ""

# Encoder les valeurs en base64
DB_HOST_B64=$(echo -n "$DB_HOST" | base64)
DB_USER_B64=$(echo -n "$DB_USER" | base64)
DB_PASSWORD_B64=$(echo -n "$DB_PASSWORD" | base64)
DB_NAME_B64=$(echo -n "$DB_NAME" | base64)
REDIS_HOST_B64=$(echo -n "$REDIS_HOST" | base64)
REDIS_PASSWORD_B64=$(echo -n "$REDIS_PASSWORD" | base64)
SECRET_KEY_B64=$(echo -n "$SECRET_KEY" | base64)
MAIL_USERNAME_B64=$(echo -n "$MAIL_USERNAME" | base64)
MAIL_PASSWORD_B64=$(echo -n "$MAIL_PASSWORD" | base64)
MAIL_DEFAULT_SENDER_B64=$(echo -n "$MAIL_DEFAULT_SENDER" | base64)
WEBHOOK_SECRET_B64=$(echo -n "$WEBHOOK_SECRET" | base64)

# Créer le fichier de secrets temporaire
cat > k8s/secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: datalys-secrets
  labels:
    app: datalys-api
type: Opaque
data:
  # Base de données
  db-host: $DB_HOST_B64
  db-user: $DB_USER_B64
  db-password: $DB_PASSWORD_B64
  db-name: $DB_NAME_B64
  
  # Redis
  redis-host: $REDIS_HOST_B64
  redis-password: $REDIS_PASSWORD_B64
  
  # Application
  secret-key: $SECRET_KEY_B64
  
  # Email SMTP
  mail-username: $MAIL_USERNAME_B64
  mail-password: $MAIL_PASSWORD_B64
  mail-default-sender: $MAIL_DEFAULT_SENDER_B64
  
  # Webhook (optionnel)
  webhook-secret: $WEBHOOK_SECRET_B64
EOF

echo "✅ Fichier de secrets généré: k8s/secrets.yaml"
echo ""

# Demander si on veut appliquer les secrets
read -p "🚀 Voulez-vous appliquer les secrets au cluster Kubernetes ? (y/N): " APPLY_SECRETS

if [[ $APPLY_SECRETS =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔄 Application des secrets au cluster..."
    
    # Vérifier la connexion au cluster
    if kubectl cluster-info &> /dev/null; then
        kubectl apply -f k8s/secrets.yaml
        echo "✅ Secrets appliqués avec succès !"
        
        # Vérifier que les secrets sont créés
        echo ""
        echo "📋 Vérification des secrets créés :"
        kubectl get secret datalys-secrets
    else
        echo "❌ Impossible de se connecter au cluster Kubernetes"
        echo "   Vérifiez que kubectl est configuré correctement"
    fi
else
    echo ""
    echo "ℹ️  Les secrets sont prêts dans k8s/secrets.yaml"
    echo "   Vous pouvez les appliquer manuellement avec :"
    echo "   kubectl apply -f k8s/secrets.yaml"
fi

echo ""
echo "🔒 Nettoyage des variables sensibles..."
unset DB_HOST DB_USER DB_PASSWORD DB_NAME
unset REDIS_HOST REDIS_PASSWORD SECRET_KEY
unset MAIL_USERNAME MAIL_PASSWORD MAIL_DEFAULT_SENDER WEBHOOK_SECRET

echo "✅ Génération terminée !"
echo ""
echo "📝 Prochaines étapes :"
echo "   1. Appliquer les secrets : kubectl apply -f k8s/secrets.yaml"
echo "   2. Déployer l'application : kubectl apply -f k8s/deployment.yaml"
echo "   3. Vérifier le déploiement : kubectl get pods -l app=datalys-api" 