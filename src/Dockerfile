# Version ultra-optimisée pour build rapide
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer uniquement les dépendances essentielles
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Créer l'utilisateur non-root
RUN groupadd -r app && useradd -r -g app -m -d /app -s /bin/bash app

# Créer les répertoires nécessaires
WORKDIR /app
RUN mkdir -p /app/src/logs /app/src/static/files && \
    chown -R app:app /app

# Copier les dépendances Python
COPY --chown=app:app src/requirements.txt .

# Installer les dépendances Python (sans compilation)
USER app
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt

# Copier le code de l'application
COPY --chown=app:app src/ /app/src/

# S'assurer que les permissions sont correctes
RUN chmod -R 755 /app/src/logs /app/src/static

# Créer le script de démarrage
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "🚀 Démarrage de l application Datalys Consulting..."' >> /app/start.sh && \
    echo 'cd /app/src' >> /app/start.sh && \
    echo 'export PYTHONPATH=/app/src:$PYTHONPATH' >> /app/start.sh && \
    echo 'export PORT=8082' >> /app/start.sh && \
    echo 'export ENV=production' >> /app/start.sh && \
    echo 'echo "✅ Environnement configuré"' >> /app/start.sh && \
    echo "🌐 Démarrage sur le port $PORT" >> /app/start.sh && \
    echo 'exec python run.py' >> /app/start.sh && \
    chmod +x /app/start.sh

# Exposer le port
EXPOSE 8082

# Health check optimisé
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1

# Commande par défaut
CMD ["/app/start.sh"] 