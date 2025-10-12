# 🔒 Audit de Sécurité - Datalys Consulting Backend

**Date:** 12 octobre 2025  
**Contexte:** Suite à l'attaque ransomware du 12/10/2025  
**Status:** ⚠️ CRITIQUE - Actions immédiates requises

---

## 📊 Résumé Exécutif

### ✅ Points Positifs (Déjà Corrigés)
- Port MySQL 3306 bloqué de l'extérieur
- Mot de passe root MySQL changé (`Datalys@2025`)
- Utilisateur MySQL dédié créé (`datalys_app`)
- MFA activé pour tous les utilisateurs
- Hash scrypt (Werkzeug) pour les mots de passe
- Ransomware supprimé

### ❌ Vulnérabilités CRITIQUES Restantes

| Priorité | Vulnérabilité | Impact | Status |
|----------|---------------|---------|--------|
| 🔴 P0 | Mots de passe en clair dans docker-compose.yml | Exposition complète | **À CORRIGER** |
| 🔴 P0 | SECRET_KEY faible en production | Compromission JWT/sessions | **À CORRIGER** |
| 🔴 P0 | Pas de sauvegarde automatique | Perte de données | **À CORRIGER** |
| 🟠 P1 | Firebase credentials en clair | Accès Firebase non autorisé | **À CORRIGER** |
| 🟠 P1 | Logs non sécurisés | Exposition d'informations sensibles | **À CORRIGER** |
| 🟠 P1 | Rate limiting insuffisant | DDoS/Brute force | **À AMÉLIORER** |
| 🟡 P2 | Pas de monitoring de sécurité | Détection tardive d'intrusion | **À IMPLÉMENTER** |
| 🟡 P2 | Pas de fail2ban | Attaques brute force SSH | **À IMPLÉMENTER** |

---

## 🔴 VULNÉRABILITÉS CRITIQUES (P0)

### 1. Mots de passe en clair dans docker-compose.yml

**Fichier:** `docker-compose.deploy.yml` ligne 45, 59

```yaml
# ❌ PROBLÈME
- DB_PASSWORD=${DB_PASSWORD:-datalysconsulting}
- MAIL_PASSWORD=${MAIL_PASSWORD:-Datalysconsulting@2025}
```

**Impact:**
- Accès complet à la base de données si le fichier est compromis
- Accès au compte email (envoi de spam, phishing)
- Fichier souvent committé par erreur sur Git

**Solution:**
```bash
# 1. Créer un fichier .env HORS DU REPO
cat > /root/datalys-backend/.env << EOF
DB_PASSWORD=DatalysApp2025
MAIL_PASSWORD=VotreMotDePasseEmailSecurise
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF

# 2. Protéger le fichier
chmod 600 /root/datalys-backend/.env

# 3. Modifier docker-compose.yml
env_file:
  - .env
```

**Action immédiate:** ✅ FAIT (utilisateur dédié créé, mais fichier docker-compose à nettoyer)

---

### 2. SECRET_KEY faible en production

**Fichier:** `docker-compose.deploy.yml` ligne 63

```yaml
# ❌ PROBLÈME
- SECRET_KEY=${SECRET_KEY:-development-secret-change-in-production}
```

**Impact:**
- Tokens JWT facilement forgeables
- Sessions utilisateurs déchiffrables
- Attaques CSRF possibles

**Solution:**
```bash
# Générer une vraie clé secrète
openssl rand -hex 32
# Exemple: 3a7f5d9c2b8e6f1a4d7c9b2e5f8a1d4c7b9e2f5a8d1c4b7e0f3a6d9c2e5f8b1a

# Mettre dans .env (JAMAIS en clair dans docker-compose)
SECRET_KEY=3a7f5d9c2b8e6f1a4d7c9b2e5f8a1d4c7b9e2f5a8d1c4b7e0f3a6d9c2e5f8b1a
JWT_SECRET_KEY=9f2e5c8b1d4a7e0c3f6b9d2e5a8c1f4b7e0d3a6c9f2e5b8d1a4c7f0e3b6a9d2
```

**Action requise:** 🔴 À FAIRE MAINTENANT

---

### 3. Pas de sauvegarde automatique

**Impact:**
- En cas de ransomware, perte totale des données
- Pas de point de restauration
- Risque financier et légal (RGPD)

**Solution:**
```bash
# 1. Script de backup automatique
cat > /usr/local/bin/backup-mysql.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup avec compression
mysqldump -u root -pDatalys@2025 datalys_consulting \
  | gzip > $BACKUP_DIR/datalys_$DATE.sql.gz

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "datalys_*.sql.gz" -mtime +7 -delete

# Copier vers un stockage externe (S3, FTP, etc.)
# aws s3 cp $BACKUP_DIR/datalys_$DATE.sql.gz s3://backups/
EOF

chmod +x /usr/local/bin/backup-mysql.sh

# 2. Cron quotidien à 3h du matin
crontab -e
# Ajouter: 0 3 * * * /usr/local/bin/backup-mysql.sh
```

**Action requise:** 🔴 À FAIRE AUJOURD'HUI

---

## 🟠 VULNÉRABILITÉS IMPORTANTES (P1)

### 4. Firebase credentials en clair

**Fichier:** `src/config/firebase-service-account.json`

**Impact:**
- Accès complet à Firebase
- Envoi de notifications push non autorisées
- Manipulation des données Firebase

**Solution:**
```bash
# 1. Chiffrer le fichier
openssl enc -aes-256-cbc -salt \
  -in firebase-service-account.json \
  -out firebase-service-account.json.enc \
  -k "VotreCléDeChiffrement"

# 2. Déchiffrer au runtime
openssl enc -aes-256-cbc -d \
  -in firebase-service-account.json.enc \
  -out /tmp/firebase-service-account.json \
  -k "$FIREBASE_DECRYPT_KEY"

# 3. OU utiliser des secrets Kubernetes/Docker
docker secret create firebase_creds firebase-service-account.json
```

**Action requise:** 🟠 À FAIRE CETTE SEMAINE

---

### 5. Rate limiting insuffisant

**Fichier:** `src/middleware/rate_limiter.py`

**Impact:**
- Attaques brute force sur login
- DDoS applicatif
- Abus d'API

**Solution actuelle:** Rate limiter en mémoire (perdu au redémarrage)

**Amélioration:**
```python
# Utiliser Redis pour le rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    strategy="fixed-window"
)

# Par route
@app.route("/auth/login", methods=["POST"])
@limiter.limit("5 per minute")  # Max 5 tentatives/minute
def login():
    pass
```

**Action requise:** 🟠 À IMPLÉMENTER

---

## 🟡 VULNÉRABILITÉS MOYENNES (P2)

### 6. Pas de monitoring de sécurité

**Impact:**
- Détection tardive des intrusions
- Pas d'alertes en cas d'anomalie
- Pas de logs centralisés

**Solution:**
```bash
# 1. Installer fail2ban
apt-get install fail2ban

# 2. Configurer pour SSH et MySQL
cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
maxretry = 3
bantime = 3600

[mysql-auth]
enabled = true
filter = mysql-auth
logpath = /var/log/mysql/error.log
maxretry = 5
bantime = 3600
EOF

systemctl restart fail2ban

# 3. Monitoring avec Prometheus/Grafana (optionnel)
```

**Action requise:** 🟡 À PLANIFIER

---

### 7. Logs non sécurisés

**Problème:**
- Logs peuvent contenir des données sensibles
- Pas de rotation automatique
- Accessibles sans authentification

**Solution:**
```python
# Ne JAMAIS logger de mots de passe
# ❌ BAD
logger.info(f"Login attempt: {email} / {password}")

# ✅ GOOD
logger.info(f"Login attempt: {email}")

# Rotation des logs
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
```

**Action requise:** 🟡 À RÉVISER

---

## 📋 CHECKLIST DE SÉCURITÉ

### Immédiat (Aujourd'hui)
- [ ] Déplacer tous les secrets vers un fichier `.env` protégé
- [ ] Générer une vraie `SECRET_KEY` forte
- [ ] Configurer les backups MySQL automatiques
- [ ] Vérifier que `.env` est dans `.gitignore`
- [ ] Auditer les logs pour supprimer les données sensibles

### Cette semaine
- [ ] Chiffrer le fichier Firebase credentials
- [ ] Implémenter rate limiting avec Redis
- [ ] Configurer fail2ban pour SSH
- [ ] Mettre en place une rotation des logs
- [ ] Tester la restauration des backups

### Ce mois
- [ ] Implémenter un système de monitoring (Prometheus/Grafana)
- [ ] Mettre en place des alertes de sécurité
- [ ] Audit complet du code pour les vulnérabilités OWASP Top 10
- [ ] Documenter les procédures de sécurité

---

## 🛡️ BONNES PRATIQUES À SUIVRE

### 1. Gestion des Secrets
```bash
# ✅ GOOD: Utiliser des gestionnaires de secrets
# - Docker Secrets
# - Kubernetes Secrets
# - HashiCorp Vault
# - AWS Secrets Manager

# ❌ BAD: Secrets en clair dans le code/config
```

### 2. Principe du Moindre Privilège
```sql
-- ✅ GOOD: Utilisateur dédié avec privilèges limités
GRANT SELECT, INSERT, UPDATE, DELETE ON datalys_consulting.* 
TO 'datalys_app'@'localhost';

-- ❌ BAD: Utiliser root pour l'application
```

### 3. Defense in Depth (Défense en Profondeur)
- Firewall (UFW) ✅
- Authentification forte (MFA) ✅
- Chiffrement des données sensibles ⚠️
- Monitoring et alertes ❌
- Backups réguliers ❌

### 4. Mises à Jour Régulières
```bash
# Automatiser les mises à jour de sécurité
apt-get install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 🚨 PROCÉDURE EN CAS D'INCIDENT

1. **Détection**
   - Alertes automatiques
   - Monitoring des logs
   - Rapports utilisateurs

2. **Isolation**
   ```bash
   # Bloquer immédiatement l'accès
   ufw deny from <IP_SUSPECTE>
   docker stop datalys-api
   ```

3. **Investigation**
   - Analyser les logs
   - Identifier le vecteur d'attaque
   - Évaluer l'impact

4. **Récupération**
   - Restaurer depuis backup
   - Patcher la vulnérabilité
   - Changer tous les mots de passe

5. **Post-Mortem**
   - Documenter l'incident
   - Améliorer les défenses
   - Communiquer aux parties prenantes

---

## 📞 CONTACTS URGENCE SÉCURITÉ

- **Admin Système:** pedini kone
- **Email:** nonssekone@outlook.com
- **Backup Admin:** admin@datalysconsulting.com

---

## 📚 RESSOURCES

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS MySQL Benchmark](https://www.cisecurity.org/benchmark/mysql)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [ANSSI - Bonnes pratiques](https://www.ssi.gouv.fr/)

---

**Document créé le:** 12 octobre 2025  
**Dernière révision:** 12 octobre 2025  
**Statut:** 🔴 Actions urgentes requises

