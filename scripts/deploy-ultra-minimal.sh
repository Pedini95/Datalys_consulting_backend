#!/bin/bash
set -e

APP_DIR="/opt/Datalys_consulting_backend"

echo "🚀 Déploiement ultra-minimal..."

cd "$APP_DIR"

# Créer le docker-compose.yml directement sur le serveur
cat > docker-compose.yml << 'EOF'
version: "3.9"

services:
  datalys-api:
    image: datalys-consulting/api:latest
    container_name: datalys-api
    restart: unless-stopped
    ports:
      - "8082:8082"
    volumes:
      - ./uploads:/app/src/static/files
      - ./logs:/app/src/logs
    environment:
      - FLASK_ENV=production
      - PYTHONPATH=/app/src
      - PORT=8082
    healthcheck:
      test: ["CMD", "curl", "-f", "--connect-timeout", "10", "--max-time", "30", "http://localhost:8082/health"]
      interval: 60s
      timeout: 30s
      retries: 5
      start_period: 120s
    networks:
      - datalys-network

networks:
  datalys-network:
    driver: bridge
EOF

echo "⬇️ Pull de la dernière image..."
docker compose pull

echo "🔄 Redémarrage des services..."
docker compose up -d

echo "⏳ Attente du démarrage..."
sleep 30

echo "🔍 Vérification de la santé..."
if curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health; then
    echo "✅ Déploiement terminé avec succès !"
else
    echo "❌ Health check échoué"
    docker compose logs --tail=20 datalys-api
    exit 1
fi

echo "🧹 Nettoyage des anciennes images..."
docker image prune -f 