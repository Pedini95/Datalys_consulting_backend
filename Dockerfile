FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY src/requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/

# Créer les répertoires nécessaires
RUN mkdir -p /app/src/static/files/logos \
    && mkdir -p /app/src/static/files/files \
    && mkdir -p /app/src/static/files/projects \
    && mkdir -p /app/logs

# Définir les permissions
RUN chmod -R 755 /app/src/static

# Exposer le port
EXPOSE 5000

# Variables d'environnement par défaut
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/src

# Commande de démarrage
CMD ["python", "src/run.py"] 