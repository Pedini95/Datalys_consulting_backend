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

# Dossiers nécessaires - structure complète avec tous les sous-dossiers
RUN mkdir -p /app/src/logs \
    /app/src/static/files \
    /app/src/static/files/files \
    /app/src/static/files/logos \
    /app/src/static/files/projects \
    /app/src/static/files/incidents \
    /app/src/static/logos \
    /app/src/static/projects \
    /app/src/static/incidents

# Installer les deps Python en root (dans /usr/local)
COPY src/requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# Installer toutes les dépendances depuis requirements.txt
# On installe en une seule passe pour éviter les corruptions
RUN python -m pip install --no-cache-dir --timeout 600 --upgrade -r requirements.txt && \
    python -c "import click; print('✅ click version:', click.__version__)" && \
    python -c "import flask; print('✅ Flask version:', flask.__version__)"

# Copier le code et donner les droits au user
COPY --chown=app:app src/ /app/src
COPY --chown=app:app scripts/ /app/scripts

# ##Créer le script de démarrage avec Gunicorn
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo " Démarrage de l application Datalys Consulting avec Gunicorn..."' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Corriger les permissions des volumes bind-montés (nécessaire à chaque démarrage)' >> /app/start.sh && \
    echo 'chmod -R 777 /app/src/static /app/src/logs 2>/dev/null || true' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Migration automatique de la structure des fichiers' >> /app/start.sh && \
    echo 'echo " Vérification de la structure des fichiers..."' >> /app/start.sh && \
    echo 'STATIC_DIR="/app/src/static"' >> /app/start.sh && \
    echo 'mkdir -p "$STATIC_DIR/logos" "$STATIC_DIR/files" "$STATIC_DIR/projects" "$STATIC_DIR/incidents"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Migrer les logos si nécessaire' >> /app/start.sh && \
    echo 'if [ -d "$STATIC_DIR/files/logos" ] && [ "$(ls -A $STATIC_DIR/files/logos 2>/dev/null)" ]; then' >> /app/start.sh && \
    echo '  echo "   Migration des logos..."' >> /app/start.sh && \
    echo '  cp -rn "$STATIC_DIR/files/logos/"* "$STATIC_DIR/logos/" 2>/dev/null || true' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Migrer les projects si nécessaire' >> /app/start.sh && \
    echo 'if [ -d "$STATIC_DIR/files/projects" ] && [ "$(ls -A $STATIC_DIR/files/projects 2>/dev/null)" ]; then' >> /app/start.sh && \
    echo '  echo "   Migration des projects..."' >> /app/start.sh && \
    echo '  cp -rn "$STATIC_DIR/files/projects/"* "$STATIC_DIR/projects/" 2>/dev/null || true' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Migrer les fichiers génériques si nécessaire' >> /app/start.sh && \
    echo 'if [ -d "$STATIC_DIR/files/files" ] && [ "$(ls -A $STATIC_DIR/files/files 2>/dev/null)" ]; then' >> /app/start.sh && \
    echo '  echo "   Migration des fichiers génériques..."' >> /app/start.sh && \
    echo '  cp -rn "$STATIC_DIR/files/files/"* "$STATIC_DIR/files/" 2>/dev/null || true' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo " Structure des fichiers vérifiée"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'export PORT=${PORT:-8082}' >> /app/start.sh && \
    echo 'export ENV=production' >> /app/start.sh && \
    echo 'export PYTHONPATH=/app/src' >> /app/start.sh && \
    echo 'echo " Environnement configuré"' >> /app/start.sh && \
    echo 'echo " Debug: Current working directory: $(pwd)"' >> /app/start.sh && \
    echo 'echo " Debug: Python path: $PYTHONPATH"' >> /app/start.sh && \
    echo 'echo " Debug: Testing import:"' >> /app/start.sh && \
    echo 'cd /app/src && python -c "from models import Role; print(\" Role imported successfully\")" || echo " Import failed"' >> /app/start.sh && \
    echo "echo \" Démarrage Gunicorn sur le port \$PORT\"" >> /app/start.sh && \
    echo 'cd /app/src' >> /app/start.sh && \
    echo 'exec gunicorn --config gunicorn_config.py app:app' >> /app/start.sh && \
    chmod +x /app/start.sh

# Le conteneur tourne en root pour pouvoir corriger les permissions des volumes montés
# La sécurité périmétrique est assurée par nginx en frontal

# Exposer le port
EXPOSE 8082

# Health check optimisé
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f --connect-timeout 10 --max-time 30 http://localhost:8082/health || exit 1

# Commande par défaut
CMD ["/app/start.sh"] 