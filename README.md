# Datalys Consulting Backend

Backend API Flask pour la gestion des projets, partenaires, incidents et fichiers de Datalys Consulting.

## 🚀 Fonctionnalités

### 🔐 Authentification
- **Login/Logout** avec JWT
- **Reset Password** par email
- **Session Management** avec Redis

### 👥 Gestion des Utilisateurs
- CRUD complet des utilisateurs
- Gestion des rôles et permissions
- Authentification sécurisée

### 🤝 Gestion des Partenaires
- Création et mise à jour des partenaires
- Upload de logos intégré
- Gestion des informations de contact (email, téléphone, adresse)

### 📁 Gestion des Projets
- Création et gestion des projets
- Association automatique aux partenaires par nom
- Statut et budget des projets

### 📂 Gestion des Dossiers
- Création de dossiers avec structure physique
- Upload de dossiers complets (ZIP, multiple fichiers)
- Hiérarchie des dossiers (parent/enfant)
- Convention de nommage hybride (ID_Nom)

### 📄 Gestion des Fichiers
- Upload de tous types de fichiers
- Téléchargement sécurisé
- Métadonnées automatiques
- Association aux dossiers

### 🚨 Gestion des Incidents
- Création et suivi des incidents
- **Alertes automatiques par email** aux partenaires
- Association aux projets et utilisateurs
- Notifications en temps réel

## 🛠️ Technologies

- **Backend**: Flask (Python)
- **Base de données**: MySQL avec SQLAlchemy ORM
- **Cache/Sessions**: Redis
- **Authentification**: JWT
- **Email**: SMTP (Hostinger)
- **Upload**: Gestion de fichiers multipart
- **API**: RESTful avec documentation Swagger

## 📋 Prérequis

- Python 3.8+
- MySQL
- Redis
- Compte SMTP (Hostinger)

## 🔧 Installation

1. **Cloner le repository**
```bash
git clone https://github.com/Pedini95/Datalys_consulting_backend.git
cd Datalys_consulting_backend
```

2. **Installer les dépendances**
```bash
pip install -r src/requirements.txt
```

3. **Configuration de l'environnement**
```bash
cp src/env.template src/.env.local
# Éditer src/.env.local avec vos paramètres
```

4. **Configuration de la base de données**
```bash
# Créer la base de données MySQL
mysql -u root -p
CREATE DATABASE datalys_consulting;
```

5. **Initialiser la base de données**
```bash
cd src
python init_db.py
```

## ⚙️ Configuration

### Variables d'environnement (.env.local)

```env
# Base de données
DB_USER=datalys
DB_PASSWORD=datalysconsulting
DB_HOST=82.112.253.137
DB_NAME=datalys_consulting

# Redis
REDIS_HOST=192.168.2.40
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=QoYJqOwtmOspiooEGpZc

# SMTP Hostinger
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=datalysconsultingapp@datalysconsulting.com
MAIL_PASSWORD=Datalysconsulting@2025
MAIL_DEFAULT_SENDER=datalysconsultingapp@datalysconsulting.com

# Application
SENDER_NAME=Datalys Consulting
APP_URL=https://datalysconsulting.com
SECRET_KEY=o9uGf31F7XJJc49uh7g57DjjN2sQyHyg

# Uploads
UPLOAD_FOLDER=./static/files
```

## 🚀 Démarrage

```bash
cd src
python run.py
```

L'API sera disponible sur `http://localhost:5000`

## 📚 API Endpoints

### 🔐 Authentification
- `POST /auth/login` - Connexion
- `POST /auth/logout` - Déconnexion
- `POST /auth/reset-password-request` - Demande de reset password

### 👥 Utilisateurs
- `GET /users` - Liste des utilisateurs
- `POST /users/create` - Créer un utilisateur
- `POST /users/update` - Mettre à jour un utilisateur
- `POST /users/delete` - Supprimer un utilisateur

### 🤝 Partenaires
- `GET /partners` - Liste des partenaires
- `POST /partners/create` - Créer un partenaire (avec logo)
- `POST /partners/update` - Mettre à jour un partenaire
- `POST /partners/delete` - Supprimer un partenaire

### 📁 Projets
- `GET /projects` - Liste des projets
- `POST /projects/create` - Créer un projet
- `POST /projects/update` - Mettre à jour un projet
- `POST /projects/delete` - Supprimer un projet

### 📂 Dossiers
- `GET /folders` - Liste des dossiers
- `POST /folders/create` - Créer un dossier
- `POST /folders/update` - Mettre à jour un dossier
- `POST /folders/delete` - Supprimer un dossier
- `POST /folders/upload` - Upload de dossier (ZIP/multiple)

### 📄 Fichiers
- `GET /files` - Liste des fichiers
- `POST /files/upload` - Upload de fichier
- `GET /files/download/<id>` - Télécharger un fichier
- `POST /files/update` - Mettre à jour un fichier
- `POST /files/delete` - Supprimer un fichier

### 🚨 Incidents
- `GET /incidents` - Liste des incidents
- `POST /incidents/create` - Créer un incident
- `POST /incidents/update` - Mettre à jour un incident
- `POST /incidents/delete` - Supprimer un incident

## 📧 Système d'Emails

### Types d'emails supportés :
- **Welcome Email** - Email de bienvenue
- **Password Reset** - Reset de mot de passe
- **Incident Alerts** - Alertes d'incidents automatiques

### Template d'alerte d'incident :
- 🚨 **Alerte visuelle professionnelle**
- 📊 **Toutes les informations de l'incident**
- 👤 **Nom de l'utilisateur qui a signalé**
-‍💼 **Nom de l'utilisateur assigné**
- 📅 **Date et heure de création**

## 🔒 Sécurité

- **JWT Authentication** sur toutes les routes protégées
- **Rate Limiting** sur les endpoints d'authentification
- **Validation des fichiers** uploadés
- **Gestion sécurisée des sessions** avec Redis
- **CORS** configuré pour les requêtes cross-origin

## 📁 Structure du Projet

```
src/
├── app.py                 # Configuration Flask
├── config.py             # Configuration de l'application
├── run.py                # Point d'entrée
├── models/               # Modèles SQLAlchemy
├── routes/               # Routes API
├── services/             # Logique métier
├── utils/                # Utilitaires
├── templates/            # Templates d'emails
├── middleware/           # Middleware (auth, rate limiting)
└── docs/                 # Documentation
```

## 🧪 Tests

```bash
# Test d'upload de validation
python test_upload_validation.py

# Test de création de partenaire
python test_partner_creation.py

# Test de création de projet
python test_project_creation.py
```

## 📝 Exemples d'Utilisation

### Créer un incident avec alerte email
```bash
curl -X POST http://localhost:5000/incidents/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user": {"id": 1},
    "datas": [{
      "title": "Problème serveur",
      "description": "Le serveur ne répond plus",
      "user_name": "John Doe",
      "project_name": "E-commerce Platform"
    }]
  }'
```

### Upload de fichier
```bash
curl -X POST http://localhost:5000/files/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.pdf" \
  -F "folder_name=Documents"
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou support, contactez l'équipe Datalys Consulting.

---

**Développé avec ❤️ par l'équipe Datalys Consulting**
# Test deployment - Fri Aug 15 13:22:30 GMT 2025
