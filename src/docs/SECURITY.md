# 🔐 Sécurité & Authentification

Ce document décrit toutes les fonctionnalités de sécurité implémentées dans l'application.

## 📋 Table des Matières

1. [JWT Authentication](#jwt-authentication)
2. [Gestion des Rôles & Permissions](#gestion-des-rôles--permissions)
3. [Rate Limiting](#rate-limiting)
4. [Protection contre les Attaques](#protection-contre-les-attaques)
5. [Utilisation des Middlewares](#utilisation-des-middlewares)
6. [Exemples d'Utilisation](#exemples-dutilisation)

## 🔑 JWT Authentication

### Fonctionnalités Implémentées

- ✅ **Login sécurisé** avec génération de token JWT
- ✅ **Logout** avec invalidation du statut de connexion
- ✅ **Refresh token** pour prolonger les sessions
- ✅ **Vérification automatique** des tokens sur les routes protégées
- ✅ **Gestion des sessions** avec statut de connexion

### Endpoints Disponibles

```bash
# Connexion
POST /auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Déconnexion
POST /auth/logout
Authorization: Bearer <token>

# Récupérer l'utilisateur connecté
GET /auth/me
Authorization: Bearer <token>

# Rafraîchir le token
POST /auth/refresh-token
Authorization: Bearer <token>

# Changer le mot de passe
POST /auth/change-password
Authorization: Bearer <token>
{
  "current_password": "oldpass",
  "new_password": "newpass"
}

# Demander un reset de mot de passe
POST /auth/reset-password-request
{
  "email": "user@example.com"
}

# Confirmer le reset de mot de passe
POST /auth/reset-password-confirm
{
  "reset_token": "token",
  "new_password": "newpass"
}
```

## 🔐 Gestion des Rôles & Permissions

### Système de Rôles

Dans cette application, **un utilisateur ne peut avoir qu'un seul rôle** à la fois. Le rôle détermine les permissions de l'utilisateur.

### Middlewares Disponibles

#### 1. `@require_role(role_name)`
Vérifie que l'utilisateur a un rôle spécifique.

```python
@app.route('/admin/users')
@require_role("Admin")
def admin_users():
    return {"message": "Accès admin autorisé"}
```

#### 2. `@require_permission(permission)`
Vérifie que l'utilisateur a une permission spécifique.

```python
@app.route('/users/delete/<id>')
@require_permission("delete")
def delete_user(id):
    return {"message": "Utilisateur supprimé"}
```

#### 3. `@require_any_role(roles_list)`
Vérifie que l'utilisateur a au moins un des rôles spécifiés.

```python
@app.route('/manager/dashboard')
@require_any_role(["Manager", "Admin"])
def manager_dashboard():
    return {"message": "Dashboard manager"}
```

#### 4. `@admin_only`
Décorateur prédéfini pour les routes admin uniquement.

```python
@app.route('/admin/settings')
@admin_only
def admin_settings():
    return {"message": "Paramètres admin"}
```

#### 5. `@user_or_admin`
Décorateur prédéfini pour les utilisateurs et admins.

```python
@app.route('/profile')
@user_or_admin
def user_profile():
    return {"message": "Profil utilisateur"}
```

### Système de Permissions

Les permissions sont définies par rôle :

```python
role_permissions = {
    'Admin': ['read', 'write', 'delete', 'admin'],
    'Manager': ['read', 'write'],
    'User': ['read'],
    'Guest': ['read']
}
```

### Gestion des Rôles par Projet

Bien qu'un utilisateur n'ait qu'un seul rôle global, il peut avoir des **permissions spécifiques par projet** via la table `user_project_permissions` :

```python
# Exemple : Un utilisateur avec le rôle "User" peut avoir des permissions admin sur un projet spécifique
user_project_permissions = {
    'user_id': 1,
    'project_id': 5,
    'can_read': True,
    'can_write': True,
    'can_delete': True,
    'can_admin': True
}
```

## 🛡 Rate Limiting

### Configuration

```python
# Tentatives de connexion
max_login_attempts = 5
block_duration = 300  # 5 minutes

# Requêtes générales
max_requests_per_minute = 60
```

### Décorateurs Disponibles

#### 1. `@login_rate_limit()`
Protège contre les attaques brute force sur la connexion.

```python
@app.route('/auth/login', methods=['POST'])
@login_rate_limit()
def login():
    # Logique de connexion
```

#### 2. `@rate_limit(max_requests, window)`
Limite le nombre de requêtes par IP.

```python
@app.route('/api/data')
@rate_limit(max_requests=100, window=60)
def get_data():
    # Logique de récupération de données
```

### Comportement

- **Tentatives de connexion** : Blocage après 5 échecs pendant 5 minutes
- **Requêtes générales** : Limitation à 60 requêtes par minute par IP
- **Messages d'erreur** : Informations sur le nombre de tentatives restantes
- **Nettoyage automatique** : Suppression des anciennes tentatives

## 🚫 Protection contre les Attaques

### Attaques Brute Force

- ✅ **Détection automatique** des tentatives répétées
- ✅ **Blocage temporaire** des comptes/IP
- ✅ **Messages informatifs** sur le nombre de tentatives restantes
- ✅ **Nettoyage automatique** des tentatives expirées

### Sécurité des Tokens

- ✅ **Expiration automatique** des tokens JWT (24h)
- ✅ **Refresh automatique** des tokens
- ✅ **Validation stricte** des signatures
- ✅ **Gestion des tokens expirés**

### Validation des Données

- ✅ **Validation des emails** avant traitement
- ✅ **Hashage sécurisé** des mots de passe (SHA1)
- ✅ **Protection contre l'injection SQL** (SQLAlchemy ORM)
- ✅ **Validation des types** de données

## 🛠 Utilisation des Middlewares

### Protection d'une Route

```python
from middleware.auth_middleware import require_role, admin_only
from middleware.rate_limiter import rate_limit

@app.route('/admin/users')
@admin_only
@rate_limit(max_requests=30, window=60)
def admin_users():
    # Seuls les admins peuvent accéder
    # Maximum 30 requêtes par minute
    return {"users": get_all_users()}
```

### Protection avec Permissions

```python
from middleware.auth_middleware import require_permission

@app.route('/users/<id>', methods=['DELETE'])
@require_permission("delete")
def delete_user(id):
    # Seuls les utilisateurs avec la permission "delete" peuvent accéder
    return {"message": f"Utilisateur {id} supprimé"}
```

### Combinaison de Middlewares

```python
@app.route('/sensitive-data')
@require_role("Manager")
@rate_limit(max_requests=10, window=300)
def sensitive_data():
    # Accès restreint aux managers
    # Maximum 10 requêtes par 5 minutes
    return {"data": "Données sensibles"}
```

## 📝 Exemples d'Utilisation

### Test de Connexion avec Rate Limiting

```bash
# Tentative de connexion réussie
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Tentatives échouées (seront bloquées après 5 échecs)
for i in {1..10}; do
  curl -X POST http://localhost:5000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@example.com", "password": "wrongpass"}'
done
```

### Test d'Accès Basé sur les Rôles

```bash
# Connexion admin
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}' | \
  jq -r '.data.token')

# Accès à une route admin
curl -X GET http://localhost:5000/admin/users \
  -H "Authorization: Bearer $TOKEN"
```

### Test de Rate Limiting

```bash
# Test de rate limiting sur les requêtes
for i in {1..70}; do
  curl -X GET http://localhost:5000/api/data
  echo "Requête $i"
done
```

## 🔧 Configuration

### Variables d'Environnement

```bash
# Clé secrète pour les tokens JWT
SECRET_KEY=your-secret-key-here

# Durée d'expiration des tokens (en heures)
JWT_EXPIRATION_HOURS=24

# Configuration du rate limiting
MAX_LOGIN_ATTEMPTS=5
BLOCK_DURATION=300
MAX_REQUESTS_PER_MINUTE=60
```

### Personnalisation

Vous pouvez modifier les paramètres de sécurité dans :

- `src/middleware/rate_limiter.py` : Configuration du rate limiting
- `src/services/auth_service.py` : Configuration de l'authentification
- `src/middleware/auth_middleware.py` : Configuration des permissions

## 🚨 Bonnes Pratiques

1. **Toujours utiliser HTTPS** en production
2. **Changer régulièrement** la clé secrète JWT
3. **Monitorer** les tentatives de connexion échouées
4. **Implémenter** une rotation des logs
5. **Utiliser** des mots de passe forts
6. **Tester régulièrement** les fonctionnalités de sécurité

## 📊 Monitoring

### Logs de Sécurité

L'application enregistre automatiquement :

- Tentatives de connexion (réussies/échouées)
- Tentatives d'accès non autorisées
- Activations du rate limiting
- Erreurs de validation des tokens

### Métriques Disponibles

- Nombre de tentatives de connexion par IP
- Nombre de requêtes par minute par IP
- Durée des sessions utilisateur
- Fréquence des refresh de tokens

---

**Note** : Cette documentation couvre toutes les fonctionnalités de sécurité implémentées. Pour des besoins spécifiques, consultez les fichiers source correspondants. 