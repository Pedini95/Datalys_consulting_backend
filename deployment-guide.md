# 🚀 Guide de Déploiement - Datalys Consulting Backend

## 📋 Options de Déploiement sur Hostinger

### 1. **VPS Hostinger (Recommandé)**
- ✅ Plus simple à configurer
- ✅ Contrôle total du serveur
- ✅ Support Python/Flask natif
- ✅ Base de données MySQL incluse
- ✅ SSL gratuit

### 2. **Kubernetes (Avancé)**
- ⚠️ Plus complexe à configurer
- 🔧 Nécessite des connaissances Kubernetes
- 📈 Scalabilité avancée
- 🎯 Pour les gros projets

---

## 🎯 **Option 1 : VPS Hostinger (Recommandée)**

### **Étape 1 : Acheter un VPS Hostinger**

1. **Connectez-vous à Hostinger**
   - Allez sur [hostinger.com](https://hostinger.com)
   - Connectez-vous à votre compte

2. **Choisir un VPS**
   - **VPS 1** : 1GB RAM, 1 CPU (suffisant pour commencer)
   - **VPS 2** : 2GB RAM, 2 CPU (recommandé pour la production)
   - **OS** : Ubuntu 22.04 LTS

3. **Configuration recommandée**
   ```
   VPS 2
   - 2GB RAM
   - 2 CPU
   - 40GB SSD
   - Ubuntu 22.04 LTS
   - IP dédiée
   ```

### **Étape 2 : Configuration du serveur**

```bash
# 1. Se connecter au serveur
ssh root@VOTRE_IP_SERVEUR

# 2. Mettre à jour le système
apt update && apt upgrade -y

# 3. Installer les dépendances
apt install -y python3 python3-pip python3-venv nginx mysql-server redis-server git

# 4. Installer Node.js (pour PM2)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# 5. Installer PM2 (gestionnaire de processus)
npm install -g pm2
```

### **Étape 3 : Configuration de la base de données**

```bash
# 1. Sécuriser MySQL
mysql_secure_installation

# 2. Créer la base de données
mysql -u root -p
```

```sql
CREATE DATABASE datalys_consulting;
CREATE USER 'datalys'@'localhost' IDENTIFIED BY 'VOTRE_MOT_DE_PASSE_SECURISE';
GRANT ALL PRIVILEGES ON datalys_consulting.* TO 'datalys'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### **Étape 4 : Déployer l'application**

```bash
# 1. Créer un utilisateur pour l'application
adduser datalys
usermod -aG sudo datalys

# 2. Se connecter en tant qu'utilisateur datalys
su - datalys

# 3. Cloner le repository
git clone https://github.com/Pedini95/Datalys_consulting_backend.git
cd Datalys_consulting_backend

# 4. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 5. Installer les dépendances
pip install -r src/requirements.txt

# 6. Configurer l'environnement
cp src/env.template src/.env.production
nano src/.env.production
```

### **Étape 5 : Configuration de l'environnement**

```env
# src/.env.production
ENV=production

# Base de données (localhost car même serveur)
DB_USER=datalys
DB_PASSWORD=VOTRE_MOT_DE_PASSE_SECURISE
DB_HOST=localhost
DB_NAME=datalys_consulting

# Redis (localhost)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# SMTP Hostinger - SSL sur port 465
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=datalysconsultingapp@datalysconsulting.com
MAIL_PASSWORD=Nonsse@123
MAIL_DEFAULT_SENDER=datalysconsultingapp@datalysconsulting.com

# Application
SENDER_NAME=Datalys Consulting
APP_URL=https://api.datalysconsulting.com
SECRET_KEY=VOTRE_CLE_SECRETE_PRODUCTION

# Uploads
UPLOAD_FOLDER=/home/datalys/Datalys_consulting_backend/src/static/files
LOG_FILE_PATH=/home/datalys/Datalys_consulting_backend/logs/app.log
```

### **Étape 6 : Configuration de Nginx**

```bash
# Créer la configuration Nginx
sudo nano /etc/nginx/sites-available/datalys-api
```

```nginx
server {
    listen 80;
    server_name api.datalysconsulting.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/datalys/Datalys_consulting_backend/src/static/;
        expires 30d;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/datalys-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Étape 7 : Configuration de PM2**

```bash
# Créer le fichier ecosystem.config.js
nano ecosystem.config.js
```

```javascript
module.exports = {
  apps: [{
    name: 'datalys-api',
    script: 'src/run.py',
    cwd: '/home/datalys/Datalys_consulting_backend',
    interpreter: '/home/datalys/Datalys_consulting_backend/venv/bin/python',
    env: {
      FLASK_ENV: 'production',
      PYTHONPATH: '/home/datalys/Datalys_consulting_backend/src'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    log_file: '/home/datalys/Datalys_consulting_backend/logs/combined.log',
    out_file: '/home/datalys/Datalys_consulting_backend/logs/out.log',
    error_file: '/home/datalys/Datalys_consulting_backend/logs/error.log'
  }]
};
```

### **Étape 8 : Initialiser la base de données**

```bash
cd /home/datalys/Datalys_consulting_backend/src
python init_db.py
```

### **Étape 9 : Démarrer l'application**

```bash
# Démarrer avec PM2
pm2 start ecosystem.config.js

# Sauvegarder la configuration PM2
pm2 save
pm2 startup

# Vérifier le statut
pm2 status
pm2 logs datalys-api
```

### **Étape 10 : SSL avec Let's Encrypt**

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir le certificat SSL
sudo certbot --nginx -d api.datalysconsulting.com

# Renouvellement automatique
sudo crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🐳 **Option 2 : Kubernetes (Avancé)**

### **Prérequis :**
- Cluster Kubernetes sur Hostinger (ou autre provider)
- kubectl configuré
- Docker installé

### **Étape 1 : Créer le Dockerfile**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 5000

CMD ["python", "src/run.py"]
```

### **Étape 2 : Créer les manifests Kubernetes**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: datalys-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: datalys-api
  template:
    metadata:
      labels:
        app: datalys-api
    spec:
      containers:
      - name: datalys-api
        image: datalys/api:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: datalys-secrets
              key: db-host
```

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: datalys-api-service
spec:
  selector:
    app: datalys-api
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### **Étape 3 : Déployer sur Kubernetes**

```bash
# Construire l'image Docker
docker build -t datalys/api:latest .

# Pousser l'image
docker push datalys/api:latest

# Déployer sur Kubernetes
kubectl apply -f k8s/
```

---

## 📊 **Comparaison des options**

| Aspect | VPS Hostinger | Kubernetes |
|--------|---------------|------------|
| **Complexité** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Coût** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalabilité** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenance** | ⭐⭐⭐⭐ | ⭐⭐ |
| **Temps de déploiement** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 **Recommandation**

**Pour votre projet actuel, je recommande fortement l'Option 1 (VPS Hostinger)** car :

✅ **Plus simple** à configurer et maintenir  
✅ **Moins cher** pour commencer  
✅ **Suffisant** pour la plupart des applications  
✅ **Support complet** de Python/Flask  
✅ **SSL gratuit** avec Let's Encrypt  

**Kubernetes** est recommandé seulement si vous avez :
- Plus de 1000 utilisateurs simultanés
- Besoin de scalabilité automatique
- Équipe DevOps expérimentée
- Budget important

---

## 🚀 **Prochaines étapes**

1. **Acheter un VPS Hostinger**
2. **Suivre le guide VPS étape par étape**
3. **Configurer le domaine** (api.datalysconsulting.com)
4. **Tester l'API** en production
5. **Configurer les sauvegardes**

Voulez-vous que je vous aide avec une étape spécifique ? 