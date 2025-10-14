#!/bin/bash

# Script d'installation des dépendances pour la génération de rapports
# Date : 2025-10-14

echo "========================================="
echo "Installation des dépendances de rapports"
echo "========================================="
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✓ Python 3 détecté : $(python3 --version)"
echo ""

# Vérifier que pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✓ pip3 détecté : $(pip3 --version)"
echo ""

# Installer les dépendances
echo "📦 Installation des dépendances..."
echo ""

pip3 install openpyxl==3.1.2
if [ $? -eq 0 ]; then
    echo "✓ openpyxl installé avec succès"
else
    echo "❌ Erreur lors de l'installation de openpyxl"
    exit 1
fi

pip3 install reportlab==4.0.7
if [ $? -eq 0 ]; then
    echo "✓ reportlab installé avec succès"
else
    echo "❌ Erreur lors de l'installation de reportlab"
    exit 1
fi

pip3 install Pillow==10.1.0
if [ $? -eq 0 ]; then
    echo "✓ Pillow installé avec succès"
else
    echo "❌ Erreur lors de l'installation de Pillow"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ Installation terminée avec succès !"
echo "========================================="
echo ""
echo "Vous pouvez maintenant générer des rapports en utilisant:"
echo "  POST /incidents/export"
echo ""
echo "Formats supportés : PDF, Excel, CSV"
echo ""
