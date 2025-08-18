#!/bin/bash

# Script de correction des permissions pour les uploads de fichiers
# Datalys Consulting Backend

echo "🔧 Correction des permissions pour les uploads de fichiers..."

# Arrêter les containers existants
echo "📦 Arrêt des containers existants..."
docker-compose --profile production down

# Créer les dossiers nécessaires sur l'hôte
echo "📁 Création des dossiers d'upload..."
mkdir -p ./src/static/files/logos
mkdir -p ./src/static/files/files
mkdir -p ./src/static/files/projects

# Définir les permissions correctes
echo "🔐 Configuration des permissions..."
sudo chown -R 1000:1000 ./src/static/files/
sudo chmod -R 775 ./src/static/files/

# Rebuilder l'image avec les corrections
echo "🏗️ Reconstruction de l'image avec les permissions corrigées..."
docker-compose --profile production build --no-cache

# Redémarrer les services
echo "🚀 Redémarrage des services..."
docker-compose --profile production up -d

# Vérifier que les containers sont en marche
echo "✅ Vérification du statut des services..."
docker-compose ps

echo "🎉 Correction des permissions terminée !"
echo "📝 Les uploads de fichiers devraient maintenant fonctionner correctement." 