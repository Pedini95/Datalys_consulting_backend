#!/bin/bash

# Script de démarrage pour l'application Datalys Consulting
set -e

echo "🚀 Démarrage de l'application Datalys Consulting..."

# Vérifier que l'environnement virtuel existe
if [ ! -f "/app/venv/bin/python" ]; then
    echo "❌ Environnement virtuel non trouvé. Création..."
    python3 -m venv /app/venv
    /app/venv/bin/pip install --upgrade pip
    /app/venv/bin/pip install -r /app/requirements.txt
fi

# Vérifier les variables d'environnement critiques
if [ -z "$DB_HOST" ]; then
    echo "❌ Variable DB_HOST manquante"
    exit 1
fi

if [ -z "$REDIS_HOST" ]; then
    echo "❌ Variable REDIS_HOST manquante"
    exit 1
fi

# Créer les répertoires nécessaires
mkdir -p /app/src/logs
mkdir -p /app/src/static/files

# Définir les permissions
chown -R 1000:1000 /app/src/logs /app/src/static/files

echo "✅ Configuration terminée"
echo "🌍 Démarrage de l'application sur le port ${PORT:-8081}"

# Démarrer l'application
cd /app
export PYTHONPATH=/app/src:/app:$PYTHONPATH
exec /app/venv/bin/python src/run.py 