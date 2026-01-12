#!/bin/bash
# Script pour générer un fichier requirements-lock.txt avec toutes les versions figées

echo "🔍 Génération du fichier requirements-lock.txt avec versions figées..."

# Se connecter au conteneur Docker et générer le fichier
ssh root@82.112.253.137 "docker exec datalys-api pip freeze > /tmp/requirements-lock.txt && cat /tmp/requirements-lock.txt"

echo ""
echo "✅ Fichier généré. Copiez le contenu ci-dessus dans src/requirements-lock.txt"
echo ""
echo "Pour utiliser ce fichier, modifiez le Dockerfile:"
echo "  RUN python -m pip install --no-cache-dir -r requirements-lock.txt"
