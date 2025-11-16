FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH="/app/src"

# Dépendances système minimales (curl pour healthchecks/diagnostic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates wget \
 && rm -rf /var/lib/apt/lists/*

# Réinstaller pip proprement pour éviter les corruptions
RUN wget -q https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py && \
    pip --version

# Créer l'utilisateur applicatif
RUN groupadd -r app && useradd -r -g app -m -d /app -s /bin/bash app
WORKDIR /app

# Dossiers nécessaires
RUN mkdir -p /app/src/logs /app/src/static/files /app/src/static/files/logos /app/src/static/files/files /app/src/static/files/projects

# Installer les deps Python en root (dans /usr/local)
COPY src/requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# Installer toutes les dépendances depuis requirements.txt
RUN python -m pip install --no-cache-dir --timeout 600 -r requirements.txt

# Copier le code et donner les droits au user
COPY --chown=app:app src/ /app/src
COPY --chown=app:app scripts/ /app/scripts

# S'assurer que l'utilisateur app a les permissions d'écriture
RUN chown -R app:app /app/src/logs /app/src/static && \
    chmod -R 775 /app/src/logs /app/src/static && \
    chmod -R 775 /app/src/static/files

USER app

# Créer le script de démarrage avec Gunicorn
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "🚀 Démarrage de l application Datalys Consulting avec Gunicorn..."' >> /app/start.sh && \
    echo 'export PORT=${PORT:-8082}' >> /app/start.sh && \
    echo 'export ENV=production' >> /app/start.sh && \
    echo 'export PYTHONPATH=/app/src' >> /app/start.sh && \
    echo 'echo "✅ Environnement configuré"' >> /app/start.sh && \
    echo 'echo "🔍 Debug: Current working directory: $(pwd)"' >> /app/start.sh && \
    echo 'echo "🔍 Debug: Python path: $PYTHONPATH"' >> /app/start.sh && \
    echo 'echo "🔍 Debug: Testing import:"' >> /app/start.sh && \
    echo 'cd /app/src && python -c "from models import Role; print(\"✅ Role imported successfully\")" || echo "❌ Import failed"' >> /app/start.sh && \
    echo "echo \"🌐 Démarrage Gunicorn sur le port \$PORT\"" >> /app/start.sh && \
    echo 'cd /app/src' >> /app/start.sh && \
    echo 'exec gunicorn --config gunicorn_config.py app:app' >> /app/start.sh && \
    chmod +x /app/start.sh

# Exposer le port
EXPOSE 8082

# Health check optimisé
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1

# Commande par défaut
CMD ["/app/start.sh"] 