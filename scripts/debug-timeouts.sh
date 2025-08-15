#!/bin/bash

echo "🔍 Diagnostic des timeouts - Datalys Consulting Backend"
echo "⏰ $(date)"
echo "=================================================="

# Variables
CONTAINER_NAME="datalys-api"
PROJECT_DIR="/opt/Datalys_consulting_backend"

# 1. Vérifier l'état des services Docker
echo "🐳 État des services Docker:"
echo "----------------------------"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Vérifier les ressources système
echo ""
echo "💻 Ressources système:"
echo "---------------------"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Mémoire: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "Disque: $(df -h / | tail -1 | awk '{print $5}') utilisé"

# 3. Vérifier les logs du conteneur
echo ""
echo "📋 Logs du conteneur (dernières 50 lignes):"
echo "-------------------------------------------"
if docker ps | grep -q $CONTAINER_NAME; then
    docker logs $CONTAINER_NAME --tail=50
else
    echo "❌ Conteneur $CONTAINER_NAME non trouvé"
fi

# 4. Vérifier la connectivité réseau
echo ""
echo "🌐 Connectivité réseau:"
echo "----------------------"
echo "Port 8082: $(netstat -tlnp | grep 8082 || echo 'Non ouvert')"
echo "Port 3306 (MySQL): $(netstat -tlnp | grep 3306 || echo 'Non ouvert')"
echo "Port 6379 (Redis): $(netstat -tlnp | grep 6379 || echo 'Non ouvert')"

# 5. Test de connectivité des services
echo ""
echo "🔌 Test de connectivité des services:"
echo "------------------------------------"
echo "Test MySQL:"
timeout 10 mysql -h localhost -P 3306 -u root -p -e "SELECT 1;" 2>/dev/null && echo "✅ MySQL accessible" || echo "❌ MySQL inaccessible"

echo "Test Redis:"
timeout 10 redis-cli ping 2>/dev/null && echo "✅ Redis accessible" || echo "❌ Redis inaccessible"

echo "Test API Health:"
timeout 30 curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health 2>/dev/null && echo "✅ API accessible" || echo "❌ API inaccessible"

# 6. Vérifier les variables d'environnement
echo ""
echo "⚙️ Variables d'environnement critiques:"
echo "--------------------------------------"
if docker ps | grep -q $CONTAINER_NAME; then
    echo "DB_HOST: $(docker exec $CONTAINER_NAME env | grep DB_HOST || echo 'Non défini')"
    echo "DB_PORT: $(docker exec $CONTAINER_NAME env | grep DB_PORT || echo 'Non défini')"
    echo "REDIS_HOST: $(docker exec $CONTAINER_NAME env | grep REDIS_HOST || echo 'Non défini')"
    echo "REDIS_PORT: $(docker exec $CONTAINER_NAME env | grep REDIS_PORT || echo 'Non défini')"
    echo "TIME_OUT: $(docker exec $CONTAINER_NAME env | grep TIME_OUT || echo 'Non défini')"
else
    echo "❌ Impossible de vérifier les variables d'environnement (conteneur non trouvé)"
fi

# 7. Vérifier les timeouts dans la configuration
echo ""
echo "⏱️ Configuration des timeouts:"
echo "-----------------------------"
if [ -f "$PROJECT_DIR/src/config.py" ]; then
    echo "TIME_OUT: $(grep -o 'TIME_OUT.*[0-9]*' $PROJECT_DIR/src/config.py | head -1)"
    echo "DB_CONNECT_TIMEOUT: $(grep -o 'DB_CONNECT_TIMEOUT.*[0-9]*' $PROJECT_DIR/src/config.py | head -1)"
    echo "REDIS_CONNECT_TIMEOUT: $(grep -o 'REDIS_CONNECT_TIMEOUT.*[0-9]*' $PROJECT_DIR/src/config.py | head -1)"
else
    echo "❌ Fichier config.py non trouvé"
fi

# 8. Recommandations
echo ""
echo "💡 Recommandations:"
echo "------------------"
echo "1. Si MySQL est inaccessible: vérifier que le conteneur mysql-db est démarré"
echo "2. Si Redis est inaccessible: vérifier que le conteneur redis-db est démarré"
echo "3. Si l'API ne répond pas: vérifier les logs du conteneur pour les erreurs"
echo "4. Si les timeouts sont courts: augmenter les valeurs dans config.py"
echo "5. Si les ressources sont faibles: libérer de l'espace disque/mémoire"

echo ""
echo "🔍 Diagnostic terminé - $(date)" 