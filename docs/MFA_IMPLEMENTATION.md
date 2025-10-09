# 🔐 MFA (Multi-Factor Authentication) - Documentation

## 📋 Vue d'ensemble

Le système MFA (Authentification Multi-Facteurs) a été implémenté pour renforcer la sécurité de l'application. Lors de chaque connexion, un code à 6 chiffres est envoyé par email à l'utilisateur.

---

## 🎯 Workflow MFA

```
┌──────────────┐
│  UTILISATEUR │
└──────────────┘
       │
       │ 1. POST /auth/login
       │    { email, password }
       ▼
┌──────────────┐
│   BACKEND    │
│              │
│ ✅ Vérifie   │
│ mot de passe │
│              │
│ 📧 Génère    │
│ code: 123456 │
│              │
│ 📧 Envoie    │
│ par email    │
└──────────────┘
       │
       │ 2. Retourne { requires_mfa: true, user_id: X }
       ▼
┌──────────────┐
│ BOÎTE EMAIL  │
│              │
│ 📧 Code: 123456 │
└──────────────┘
       │
       │ 3. Utilisateur reçoit code
       ▼
┌──────────────┐
│  UTILISATEUR │
│              │
│ Entre code   │
│ 123456       │
└──────────────┘
       │
       │ 4. POST /auth/verify-mfa
       │    { user_id, mfa_code }
       ▼
┌──────────────┐
│   BACKEND    │
│              │
│ ✅ Vérifie   │
│ code correct │
│              │
│ ✅ Génère    │
│ token JWT    │
└──────────────┘
       │
       │ 5. Retourne { token, user_data }
       ▼
┌──────────────┐
│ UTILISATEUR  │
│ CONNECTÉ ✅  │
└──────────────┘
```

---

## 🔧 Modifications apportées

### 1. **Modèle User** (`src/models/user.py`)

Ajout de 4 nouveaux champs :

```python
# Champs MFA
mfa_enabled = db.Column(db.Boolean, default=True)  # MFA activé par défaut
mfa_code = db.Column(db.String(10), nullable=True)  # Code temporaire (6 chiffres)
mfa_code_expiry = db.Column(db.DateTime, nullable=True)  # Expiration (5 minutes)
mfa_code_attempts = db.Column(db.Integer, default=0)  # Tentatives échouées
```

### 2. **Service d'authentification** (`src/services/auth_service.py`)

Modification de la méthode `login()` :

- Après vérification du mot de passe, génère un code MFA à 6 chiffres
- Sauvegarde le code avec une expiration de 5 minutes
- Envoie le code par email
- Retourne `{ requires_mfa: true, user_id: X }`

```python
# Générer un code MFA à 6 chiffres
mfa_code = utilities.generate_numeric_code(6)

# Sauvegarder le code et sa date d'expiration (5 minutes)
user.mfa_code = mfa_code
user.mfa_code_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
user.mfa_code_attempts = 0
db.session.commit()

# Envoyer le code par email
email_service.send_mfa_code_email(user.email, user.name, mfa_code)
```

### 3. **Nouvelle route** (`src/routes/auth.py`)

Ajout de la route `/auth/verify-mfa` :

```python
@bp.route('/auth/verify-mfa', methods=['POST'])
@cross_origin()
@login_rate_limit()
def verify_mfa():
    """
    Vérifier le code MFA et générer le token JWT
    
    Body:
        - user_id: ID de l'utilisateur
        - mfa_code: Code à 6 chiffres reçu par email
    """
```

**Vérifications effectuées :**
- ✅ Utilisateur existe et est actif
- ✅ Code MFA existe
- ✅ Code n'est pas expiré (< 5 minutes)
- ✅ Nombre de tentatives < 3
- ✅ Code correspond

### 4. **Template email** (`src/templates/email_mfa_code.html`)

Nouveau template HTML pour l'email contenant :
- 🔐 Icône de sécurité
- Code à 6 chiffres en gros et en couleur
- ⏱️ Avertissement d'expiration (5 minutes)
- 📊 Informations de connexion (date, heure, email)
- 🛡️ Avertissement de sécurité

### 5. **Service email** (`src/utils/notification.py`)

Nouvelle méthode `send_mfa_code_email()` :

```python
def send_mfa_code_email(self, user_email: str, user_name: str, mfa_code: str) -> bool:
    """
    Envoyer un email avec le code MFA
    """
```

### 6. **Migration SQL** (`src/migrations/add_mfa_to_users.sql`)

```sql
ALTER TABLE users 
ADD COLUMN mfa_enabled TINYINT(1) DEFAULT 1,
ADD COLUMN mfa_code VARCHAR(10) DEFAULT NULL,
ADD COLUMN mfa_code_expiry DATETIME DEFAULT NULL,
ADD COLUMN mfa_code_attempts INT DEFAULT 0;

CREATE INDEX idx_users_mfa_code ON users(mfa_code);
CREATE INDEX idx_users_mfa_expiry ON users(mfa_code_expiry);
```

---

## 📡 API Endpoints

### 1. **Login (Étape 1)**

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "admin@datalys.com",
  "password": "Admin@123"
}
```

**Response (MFA requis):**
```json
{
  "status": "success",
  "data": {
    "requires_mfa": true,
    "user_id": 1,
    "email": "admin@datalys.com",
    "message": "Code de vérification envoyé par email"
  },
  "message": "MFA requis"
}
```

**Email envoyé:**
```
De: noreply@datalysconsulting.com
À: admin@datalys.com
Objet: 🔐 Code de vérification - Datalys Consulting

Votre code de vérification est :

    123456

Ce code expire dans 5 minutes.
```

---

### 2. **Vérification MFA (Étape 2)**

**Endpoint:** `POST /auth/verify-mfa`

**Request:**
```json
{
  "user_id": 1,
  "mfa_code": "123456"
}
```

**Response (Succès):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Administrateur",
    "email": "admin@datalys.com",
    "role_id": 1,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    ...
  },
  "message": "Connexion réussie"
}
```

**Response (Code incorrect):**
```json
{
  "status": "error",
  "message": "Code incorrect. 2 tentative(s) restante(s)"
}
```

**Response (Code expiré):**
```json
{
  "status": "error",
  "message": "Code expiré. Veuillez vous reconnecter."
}
```

**Response (Trop de tentatives):**
```json
{
  "status": "error",
  "message": "Trop de tentatives échouées. Veuillez vous reconnecter."
}
```

---

## 🔒 Sécurité

### Protections implémentées

| Protection | Description | Valeur |
|------------|-------------|--------|
| **Expiration** | Le code expire automatiquement | 5 minutes |
| **Usage unique** | Le code est supprimé après utilisation | ✅ |
| **Limite tentatives** | Maximum de tentatives incorrectes | 3 tentatives |
| **Code aléatoire** | Nouveau code à chaque connexion | 6 chiffres |
| **Pas de réutilisation** | Impossible de réutiliser un ancien code | ✅ |
| **Index DB** | Optimisation des recherches | ✅ |

### Workflow de nettoyage

Après une vérification réussie :
```python
user.mfa_code = None
user.mfa_code_expiry = None
user.mfa_code_attempts = 0
db.session.commit()
```

---

## 🎨 Interface Frontend (Recommandations)

### Écran 1 : Login

```
┌─────────────────────────────────┐
│  CONNEXION                      │
├─────────────────────────────────┤
│                                 │
│  Email:                         │
│  [admin@datalys.com        ]    │
│                                 │
│  Mot de passe:                  │
│  [**********               ]    │
│                                 │
│        [SE CONNECTER]           │
│                                 │
└─────────────────────────────────┘
```

### Écran 2 : Vérification MFA

```
┌─────────────────────────────────┐
│  VÉRIFICATION                   │
├─────────────────────────────────┤
│                                 │
│  📧 Un code a été envoyé à :    │
│     admin@datalys.com           │
│                                 │
│  Entrez le code :               │
│  [  1  ][  2  ][  3  ]          │
│  [  4  ][  5  ][  6  ]          │
│                                 │
│  ⏱️ Expire dans 4:32            │
│                                 │
│        [VÉRIFIER]               │
│                                 │
│  Pas reçu ? [Renvoyer code]     │
│                                 │
└─────────────────────────────────┘
```

---

## 🧪 Tests

### Test 1 : Login avec MFA activé

```bash
# Étape 1 : Login
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@datalys.com",
    "password": "Admin@123"
  }'

# Réponse attendue :
# {
#   "status": "success",
#   "data": {
#     "requires_mfa": true,
#     "user_id": 1,
#     "message": "Code de vérification envoyé par email"
#   }
# }

# Étape 2 : Vérifier le code (récupéré dans l'email)
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "mfa_code": "123456"
  }'

# Réponse attendue :
# {
#   "status": "success",
#   "data": {
#     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#     ...
#   }
# }
```

### Test 2 : Code incorrect

```bash
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "mfa_code": "999999"
  }'

# Réponse attendue :
# {
#   "status": "error",
#   "message": "Code incorrect. 2 tentative(s) restante(s)"
# }
```

### Test 3 : Code expiré

Attendre 5 minutes après le login, puis :

```bash
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "mfa_code": "123456"
  }'

# Réponse attendue :
# {
#   "status": "error",
#   "message": "Code expiré. Veuillez vous reconnecter."
# }
```

---

## ⚙️ Configuration

### Variables d'environnement

```env
# Email SMTP (déjà configuré)
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USERNAME=noreply@datalysconsulting.com
MAIL_PASSWORD=your_password

# MFA Settings (dans le code)
MFA_CODE_LENGTH=6
MFA_CODE_EXPIRY_MINUTES=5
MFA_MAX_ATTEMPTS=3
```

### Désactiver MFA pour un utilisateur

```sql
UPDATE users 
SET mfa_enabled = 0 
WHERE email = 'admin@datalys.com';
```

---

## 📊 Base de données

### Structure de la table `users`

```sql
mysql> DESCRIBE users;
+-------------------+--------------+------+-----+---------+----------------+
| Field             | Type         | Null | Key | Default | Extra          |
+-------------------+--------------+------+-----+---------+----------------+
| id                | int          | NO   | PRI | NULL    | auto_increment |
| name              | varchar(255) | NO   |     | NULL    |                |
| email             | varchar(120) | NO   | UNI | NULL    |                |
| password_hash     | varchar(255) | NO   |     | NULL    |                |
| is_temp_password  | tinyint(1)   | YES  |     | NULL    |                |
| fcm_token         | varchar(255) | YES  |     | NULL    |                |
| role_id           | int          | YES  | MUL | NULL    |                |
| is_active         | tinyint(1)   | YES  |     | NULL    |                |
| is_deleted        | tinyint(1)   | YES  |     | NULL    |                |
| created_at        | datetime     | YES  |     | NULL    |                |
| created_by        | varchar(255) | YES  |     | NULL    |                |
| updated_at        | datetime     | YES  |     | NULL    |                |
| updated_by        | varchar(255) | YES  |     | NULL    |                |
| mfa_enabled       | tinyint(1)   | YES  |     | 1       |                |
| mfa_code          | varchar(10)  | YES  | MUL | NULL    |                |
| mfa_code_expiry   | datetime     | YES  | MUL | NULL    |                |
| mfa_code_attempts | int          | YES  |     | 0       |                |
+-------------------+--------------+------+-----+---------+----------------+
```

### Index créés

```sql
-- Index sur le code MFA
CREATE INDEX idx_users_mfa_code ON users(mfa_code);

-- Index sur l'expiration du code
CREATE INDEX idx_users_mfa_expiry ON users(mfa_code_expiry);
```

---

## 🚀 Déploiement

### Étapes de déploiement

1. **Transférer les fichiers :**
   ```bash
   ./scripts/deploy.sh
   ```

2. **Exécuter la migration SQL :**
   ```bash
   ssh root@82.112.253.137 "docker exec mysql-db mysql -u root -p'root' datalys_consulting < /root/Datalys_consulting_backend/src/migrations/add_mfa_to_users.sql"
   ```

3. **Redémarrer le backend :**
   ```bash
   ssh root@82.112.253.137 "cd /root/Datalys_consulting_backend && docker-compose restart datalys-api"
   ```

4. **Vérifier :**
   ```bash
   curl http://82.112.253.137:8082/health
   ```

---

## 📝 Notes importantes

1. **MFA activé par défaut** : Tous les utilisateurs ont `mfa_enabled = 1` par défaut
2. **Code à 6 chiffres** : Généré aléatoirement à chaque login
3. **Expiration 5 minutes** : Le code expire automatiquement
4. **3 tentatives max** : Après 3 échecs, l'utilisateur doit se reconnecter
5. **Email requis** : L'utilisateur doit avoir accès à sa boîte email
6. **Session Redis** : Créée uniquement après validation du code MFA

---

## 🔄 Prochaines améliorations possibles

1. **MFA optionnel** : Permettre aux utilisateurs de désactiver le MFA
2. **Code par SMS** : Alternative à l'email
3. **Remember device** : "Se souvenir de cet appareil pendant 30 jours"
4. **Backup codes** : Codes de secours en cas de perte d'accès à l'email
5. **Authenticator app** : Support de Google Authenticator / Authy
6. **Historique de connexion** : Logs des tentatives de connexion

---

## ✅ Checklist de vérification

- [x] Champs MFA ajoutés au modèle User
- [x] Template email créé
- [x] Méthode send_mfa_code_email() implémentée
- [x] Route /auth/login modifiée
- [x] Route /auth/verify-mfa créée
- [x] Migration SQL exécutée
- [x] Déploiement sur VPS
- [x] Backend redémarré
- [ ] Tests effectués
- [ ] Documentation mise à jour

---

## 📞 Support

Pour toute question ou problème :
- **Email** : support@datalysconsulting.com
- **Documentation** : `/docs/MFA_IMPLEMENTATION.md`

---

**Date de mise en œuvre** : 9 octobre 2025  
**Version** : 1.0.0  
**Statut** : ✅ Déployé en production

