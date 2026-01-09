#!/bin/bash
# Script de monitoring et auto-restart pour l'API Datalys
# À ajouter dans cron: */5 * * * * /root/Datalys_consulting_backend/monitor-api.sh >> /var/log/datalys-monitor.log 2>&1

CONTAINER_NAME="datalys-api"
API_URL="http://localhost:8082/health"
MAX_RETRIES=3

check_api() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$API_URL" 2>/dev/null || echo "000")
    echo "$HTTP_CODE"
}

restart_container() {
    echo "[$(date)] API ne répond pas, redémarrage du conteneur..."
    docker restart "$CONTAINER_NAME"
    sleep 15
}

# Vérifier si le conteneur tourne
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "[$(date)] Le conteneur $CONTAINER_NAME n'est pas en cours d'exécution"
    docker start "$CONTAINER_NAME" 2>/dev/null || {
        echo "[$(date)] Impossible de démarrer le conteneur, lancement via docker-compose..."
        cd /root/Datalys_consulting_backend
        docker-compose up -d datalys-api
    }
    exit 0
fi

# Vérifier la santé de l'API
for i in $(seq 1 $MAX_RETRIES); do
    HTTP_CODE=$(check_api)

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
        if [ $i -gt 1 ]; then
            echo "[$(date)] API fonctionne après $i tentatives"
        fi
        exit 0
    fi

    if [ $i -lt $MAX_RETRIES ]; then
        sleep 5
    fi
done

# Si on arrive ici, l'API ne répond pas après MAX_RETRIES
restart_container

# Vérifier après le redémarrage
sleep 10
HTTP_CODE=$(check_api)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
    echo "[$(date)] API redémarrée avec succès"
else
    echo "[$(date)] ERREUR: API ne répond toujours pas après le redémarrage (HTTP $HTTP_CODE)"
    # Envoyer une notification (optionnel)
    # curl -X POST "votre-webhook-url" -d "API Datalys down"
fi
