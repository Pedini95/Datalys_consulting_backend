FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Dépendances système minimales (curl pour healthchecks/diagnostic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Créer l'utilisateur applicatif
RUN groupadd -r app && useradd -r -g app -m -d /app -s /bin/bash app
WORKDIR /app/src

# Dossiers nécessaires
RUN mkdir -p /app/src/logs /app/src/static/files

# Installer les deps Python en root (dans /usr/local)
COPY src/requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt

# Copier le code et donner les droits au user
COPY --chown=app:app src/ /app/src

# S'assurer que l'utilisateur app a les permissions d'écriture
RUN chown -R app:app /app/src/logs /app/src/static && \
    chmod -R 755 /app/src/logs /app/src/static

USER app

# Créer le script de démarrage
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "🚀 Démarrage de l application Datalys Consulting..."' >> /app/start.sh && \
    echo 'export PYTHONPATH=/app/src:$PYTHONPATH' >> /app/start.sh && \
    echo 'export PORT=8082' >> /app/start.sh && \
    echo 'export ENV=production' >> /app/start.sh && \
    echo 'echo "✅ Environnement configuré"' >> /app/start.sh && \
    echo "echo \"🌐 Démarrage sur le port \$PORT\"" >> /app/start.sh && \
    echo 'exec python run.py' >> /app/start.sh && \
    chmod +x /app/start.sh

# Exposer le port
EXPOSE 8082

# Health check optimisé
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1

# Commande par défaut
CMD ["/app/start.sh"] 