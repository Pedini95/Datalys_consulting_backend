#!/bin/bash

# Script pour vérifier si le VPS actuel peut supporter Kubernetes
# Usage: ./check-vps.sh

echo "🔍 Vérification de votre VPS Hostinger pour Kubernetes"
echo "======================================================"

# Vérifier le système d'exploitation
echo ""
echo "📋 Système d'exploitation :"
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    echo "   • Distribution: $NAME"
    echo "   • Version: $VERSION"
    echo "   • Architecture: $(uname -m)"
else
    echo "   ❌ Impossible de détecter le système d'exploitation"
fi

# Vérifier la mémoire
echo ""
echo "💾 Mémoire RAM :"
MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEMORY_GB=$((MEMORY_KB / 1024 / 1024))
echo "   • Total: ${MEMORY_GB} GB"

if [[ $MEMORY_GB -ge 4 ]]; then
    echo "   ✅ Suffisant pour Kubernetes (minimum 4GB)"
else
    echo "   ❌ Insuffisant pour Kubernetes (minimum 4GB requis)"
fi

# Vérifier l'espace disque
echo ""
echo "💿 Espace disque :"
DISK_GB=$(df / | tail -1 | awk '{print $4}')
DISK_GB=$((DISK_GB / 1024 / 1024))
echo "   • Disponible: ${DISK_GB} GB"

if [[ $DISK_GB -ge 20 ]]; then
    echo "   ✅ Suffisant pour Kubernetes (minimum 20GB)"
else
    echo "   ❌ Insuffisant pour Kubernetes (minimum 20GB requis)"
fi

# Vérifier les privilèges
echo ""
echo "🔐 Privilèges :"
if [[ $EUID -eq 0 ]]; then
    echo "   ✅ Exécution en tant que root"
else
    echo "   ❌ Nécessite les privilèges root"
fi

# Vérifier les packages installés
echo ""
echo "📦 Packages installés :"
if command -v docker &> /dev/null; then
    echo "   ✅ Docker installé"
else
    echo "   ❌ Docker non installé"
fi

if command -v kubectl &> /dev/null; then
    echo "   ✅ kubectl installé"
else
    echo "   ❌ kubectl non installé"
fi

if command -v helm &> /dev/null; then
    echo "   ✅ Helm installé"
else
    echo "   ❌ Helm non installé"
fi

# Vérifier les ports utilisés
echo ""
echo "🌐 Ports utilisés :"
if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo "   ⚠️  Port 80 utilisé"
else
    echo "   ✅ Port 80 disponible"
fi

if netstat -tlnp 2>/dev/null | grep -q ":443 "; then
    echo "   ⚠️  Port 443 utilisé"
else
    echo "   ✅ Port 443 disponible"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8081 "; then
    echo "   ⚠️  Port 8081 utilisé (votre app Flask)"
else
    echo "   ✅ Port 8081 disponible"
fi

# Recommandations
echo ""
echo "🎯 Recommandations :"

if [[ $MEMORY_GB -ge 4 && $DISK_GB -ge 20 ]]; then
    echo "   ✅ Votre VPS peut supporter Kubernetes"
    echo ""
    echo "📝 Prochaines étapes :"
    echo "   1. Sauvegarder votre application actuelle"
    echo "   2. Installer Kubernetes (k3s)"
    echo "   3. Migrer progressivement"
    echo ""
    echo "⚠️  Attention :"
    echo "   • L'installation va redémarrer certains services"
    echo "   • Prévoir un temps d'arrêt de 10-15 minutes"
    echo "   • Sauvegarder vos données importantes"
else
    echo "   ❌ Votre VPS ne peut pas supporter Kubernetes"
    echo ""
    echo "💡 Solutions :"
    echo "   1. Upgrader votre VPS Hostinger"
    echo "   2. Utiliser un VPS séparé pour Kubernetes"
    echo "   3. Garder votre VPS actuel + VPS Kubernetes"
fi

echo ""
echo "🔧 Commandes utiles :"
echo "   • Voir les processus: ps aux | grep python"
echo "   • Voir les services: systemctl list-units --type=service"
echo "   • Voir l'utilisation disque: df -h"
echo "   • Voir l'utilisation mémoire: free -h" 