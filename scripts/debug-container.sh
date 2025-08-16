#!/bin/bash

echo "🔍 Debug du conteneur actuel..."
echo "=================================="

# Vérifier les conteneurs en cours
echo "📋 Conteneurs en cours :"
docker-compose ps

echo ""
echo "📁 Contenu du répertoire models :"
docker exec datalys-api ls -la /app/src/models/ || echo "❌ Impossible d'accéder au conteneur"

echo ""
echo "📄 Contenu de __init__.py :"
docker exec datalys-api cat /app/src/models/__init__.py || echo "❌ Impossible de lire __init__.py"

echo ""
echo "🔍 Test d'import direct :"
docker exec datalys-api bash -c "cd /app/src && python -c 'from models import Role; print(\"✅ Import réussi\")'" || echo "❌ Import échoué"

echo ""
echo "📋 Logs du conteneur :"
docker-compose logs --tail=20 datalys-api 