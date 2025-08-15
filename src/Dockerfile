# Étape 1 : Builder des dépendances Python
FROM python:3.11-slim AS builder

# Activer BuildKit pour de meilleures performances
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer dépendances système minimales pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Créer l'environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances Python
WORKDIR /app
COPY requirements.txt .

# Installer les dépendances Python avec cache optimisé
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt

# Étape 2 : Image finale légère
FROM python:3.11-slim AS production

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Installer uniquement les dépendances runtime (sans outils de build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libfreetype6 \
    liblcms2-2 \
    libopenjp2-7 \
    libtiff5 \
    libwebp6 \
    libharfbuzz0b \
    libfribidi0 \
    libxcb1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Créer l'utilisateur non-root
RUN groupadd -r app && useradd -r -g app -m -d /app -s /bin/bash app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Créer les répertoires nécessaires
WORKDIR /app
RUN mkdir -p /app/src/logs /app/src/static/files && \
    chown -R app:app /app

# Copier le code de l'application
COPY --chown=app:app src/ /app/src/

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
    echo 'exec /opt/venv/bin/python run.py' >> /app/start.sh && \
    chmod +x /app/start.sh

# Changer vers l'utilisateur non-root
USER app

# Exposer le port
EXPOSE 8082

# Health check optimisé
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1

# Commande par défaut
CMD ["/app/start.sh"] 