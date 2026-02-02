# 🚀 Datalys Consulting Backend

API backend sécurisée pour Datalys Consulting avec déploiement automatique.

## ⚡ Démarrage Rapide

### Déploiement Automatique (Recommandé)

```bash
# Configuration en 1 commande
./scripts/setup-github-deploy.sh
```

Puis suivez les instructions pour configurer GitHub Secrets. **Temps:** 5 minutes.

📖 **Guide complet:** [docs/AUTO_DEPLOY_QUICKSTART.md](docs/AUTO_DEPLOY_QUICKSTART.md)

### Développement Local

```bash
# Installation
python3 -m venv venv
source venv/bin/activate
pip install -r src/requirements.txt

# Configuration
cp src/env.template src/.env
# Éditez src/.env avec vos paramètres

# Lancement
cd src
python run.py
```

## 🔐 Sécurité

Suite à l'attaque ransomware du 12 octobre 2025, plusieurs mesures de sécurité ont été mises en place:

- ✅ **MySQL sécurisé** - Port 3306 bloqué, mot de passe fort
- ✅ **Backups automatiques** - Quotidiens à 3h00, rétention 7 jours
- ✅ **Fail2ban actif** - Protection SSH + MySQL
- ✅ **Secrets sécurisés** - .env avec permissions 600
- ✅ **MFA activé** - Authentification à deux facteurs
- ✅ **Hash scrypt** - Remplacement de SHA1

📊 **Niveau de sécurité:** 9/10 (était 3/10 avant l'audit)

📖 **Audit complet:** [docs/SECURITY_AUDIT_2025-10-12.md](docs/SECURITY_AUDIT_2025-10-12.md)

## 🌐 Accès Production

- **API:** http://152.228.130.133:8082
- **Health Check:** http://152.228.130.133:8082/health
- **Serveur:** VPS OVH (152.228.130.133) - Strasbourg, France

## 📚 Documentation

### Déploiement
- [⚡ Guide Rapide](docs/AUTO_DEPLOY_QUICKSTART.md) - Configuration en 5 minutes
- [🔧 Guide Complet](docs/GITHUB_ACTIONS_SETUP.md) - Documentation détaillée
- [📋 Guide de Déploiement](deployment-guide.md) - Procédures manuelles

### Sécurité
- [🔒 Audit de Sécurité](docs/SECURITY_AUDIT_2025-10-12.md) - Vulnérabilités et solutions
- [🗄️ Reconstruction DB](docs/DATABASE_RECONSTRUCTION_2025-10-12.md) - Post-ransomware

### Fonctionnalités
- [📧 Configuration Email](src/docs/EMAIL_SETUP.md)
- [🔐 Sécurité](src/docs/SECURITY.md)
- [👥 Gestion Partenaires](src/docs/PARTNER_CREATION.md)
- [🖼️ Gestion Logos](src/docs/LOGO_MANAGEMENT.md)
- [📝 Historique Actions](docs/ACTION_HISTORY_SYSTEM.md)
- [🔍 Audit API](docs/API_AUDIT.md)

### API
- [📖 Documentation API Complète](DOCUMENTATION_API_COMPLETE.md)
- [📦 Collection Postman](Datalys_Consulting_API_Collection.json)

## 🏗️ Architecture

```
src/
├── models/          # Modèles SQLAlchemy (9 tables)
├── routes/          # Endpoints API (13 blueprints)
├── services/        # Logique métier
├── middleware/      # Auth, rate limiting, RBAC
├── utils/           # Utilitaires (FCM, email, validation)
└── templates/       # Templates email HTML

scripts/
├── security/        # Scripts de sécurisation
└── setup-github-deploy.sh  # Configuration déploiement auto

.github/workflows/
└── deploy.yml       # Pipeline CI/CD
```

## 🔄 Workflow de Développement

```
1. Développer localement
   ↓
2. Commiter et pusher sur main
   git push origin main
   ↓
3. GitHub Actions déploie automatiquement (2-3 min)
   ↓
4. Vérifier sur http://152.228.130.133:8082
```

## 🛠️ Technologies

- **Backend:** Flask 3.1.0, Python 3.11
- **Database:** MySQL 8.0
- **Cache:** Redis
- **Auth:** JWT + MFA (TOTP)
- **Notifications:** Firebase Cloud Messaging
- **Email:** SMTP (Hostinger/OVH)
- **Deployment:** Docker, GitHub Actions
- **Security:** Fail2ban, UFW, Scrypt hashing

## 📊 Statistiques

- **9 modèles** de données
- **13 blueprints** API
- **14 foreign keys** entre tables
- **50+ endpoints** REST
- **Uptime:** 99.9% (depuis sécurisation)

## 🚨 Support

- **Admin:** Pedini Kone (nonssekone@outlook.com)
- **Logs API:** `docker logs datalys-api`
- **Logs MySQL:** `docker logs mysql-db`
- **Logs Fail2ban:** `/var/log/fail2ban.log`
- **Backups:** `/backup/mysql/`

## 📝 Changelog

### 2025-10-12 - Sécurisation Majeure
- 🔒 Réponse à attaque ransomware
- ✅ 8 mesures de sécurité déployées
- 📊 Niveau de sécurité: 3/10 → 9/10
- 🗄️ Base de données reconstruite avec toutes les relations

### 2025-10-09 - Système de Support
- ✅ Incidents bidirectionnels (partenaire ↔ experts)
- ✅ Code client unique pour login
- ✅ Système P0-P4 avec SLA

---

**Dernière mise à jour:** 12 octobre 2025  
**Version:** 2.0.0 (Post-Sécurisation)  
**Statut:** ✅ Production
