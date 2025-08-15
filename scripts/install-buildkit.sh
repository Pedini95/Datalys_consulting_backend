#!/bin/bash

echo "🔧 Installation de BuildKit pour Docker"
echo "========================================"

# Vérifier si on est root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root"
    exit 1
fi

# 1. Mettre à jour les packages
echo "📦 Mise à jour des packages..."
apt-get update

# 2. Installer BuildKit
echo "🔨 Installation de docker-buildx-plugin..."
apt-get install -y docker-buildx-plugin

# 3. Vérifier l'installation
echo "✅ Vérification de l'installation..."
if docker buildx version &> /dev/null; then
    echo "✅ BuildKit installé avec succès"
    docker buildx version
else
    echo "❌ Échec de l'installation de BuildKit"
    exit 1
fi

# 4. Configurer BuildKit par défaut
echo "⚙️ Configuration de BuildKit..."
docker buildx create --use --name datalys-builder || true

# 5. Ajouter les variables d'environnement
echo "🔧 Configuration des variables d'environnement..."
if ! grep -q "DOCKER_BUILDKIT=1" /etc/environment; then
    echo "export DOCKER_BUILDKIT=1" >> /etc/environment
fi

if ! grep -q "COMPOSE_DOCKER_CLI_BUILD=1" /etc/environment; then
    echo "export COMPOSE_DOCKER_CLI_BUILD=1" >> /etc/environment
fi

# 6. Redémarrer Docker pour appliquer les changements
echo "🔄 Redémarrage de Docker..."
systemctl restart docker

# 7. Vérifier la configuration
echo "✅ Vérification finale..."
source /etc/environment
docker buildx ls

echo "🎉 BuildKit installé et configuré avec succès !"
echo "🚀 Vous pouvez maintenant utiliser les scripts de déploiement optimisés" 