#!/bin/bash
set -e

echo "🚀 DÉPLOIEMENT AVEC VÉRIFICATION ET APPLICATION DES MIGRATIONS"
echo "⏰ $(date)"
echo "=========================================================="

cd /opt/Datalys_consulting_backend

# 1. Pull des dernières modifications
echo "📥 Pull des dernières modifications..."
git fetch origin develop --depth=1
git reset --hard origin/develop

# 2. Vérifier et appliquer les migrations si nécessaire
echo "🔍 Vérification du statut des migrations..."
cd src
python3 ../scripts/check-migration-status.py

if [ $? -eq 0 ]; then
    echo "✅ Migrations vérifiées/appliquées avec succès"
else
    echo "❌ Erreur lors de la vérification/application des migrations"
    echo "🛠️ Tentative de résolution automatique..."
    
    # Alternative: utiliser le script d'initialisation de la DB
    python3 init_db.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Base de données initialisée avec succès"
    else
        echo "❌ Échec de l'initialisation de la base de données"
        exit 1
    fi
fi

cd ..

# 3. Redémarrer les services
echo "🔄 Redémarrage des services..."

# Arrêter les containers actuels
docker-compose -f docker-compose.deploy.yml down

# Rebuilder et redémarrer
docker-compose -f docker-compose.deploy.yml up -d --build

# 4. Vérifier que les services sont démarrés
echo "⏳ Attente du démarrage des services..."
sleep 10

# Vérifier le statut
docker-compose -f docker-compose.deploy.yml ps

# 5. Test de santé
echo "🏥 Test de santé de l'API..."
sleep 5

# Tester l'endpoint de santé
if curl -f http://localhost:8081/health >/dev/null 2>&1; then
    echo "✅ API opérationnelle"
else
    echo "⚠️ API non accessible, vérification des logs..."
    docker-compose -f docker-compose.deploy.yml logs --tail=20 app
fi

echo "🎉 Déploiement terminé!"
echo "📋 Pour vérifier les logs: docker-compose -f docker-compose.deploy.yml logs -f app" 