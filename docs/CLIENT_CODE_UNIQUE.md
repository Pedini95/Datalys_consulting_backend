# 🆔 Code Client Unique - Documentation

**Date de mise en œuvre** : 9 Octobre 2025  
**Version** : 1.0

---

## 📋 Vue d'ensemble

Le **Code Client Unique** est un identifiant permanent attribué à chaque utilisateur lors de sa création. Il permet de se connecter à l'application **sans dépendre de l'adresse email**, résolvant ainsi les problèmes de mobilité professionnelle.

### 🎯 Problème résolu

**Scénario** : Un client change d'entreprise et perd l'accès à son ancien email professionnel.

**Avant** :
- ❌ Impossible de se connecter avec l'ancien email
- ❌ Perte d'accès à tous les projets et incidents
- ❌ Nécessite la création d'un nouveau compte

**Après** :
- ✅ Connexion possible avec le code client unique
- ✅ Accès conservé à tous les projets et incidents
- ✅ Mise à jour simple de l'email sans perte de données

---

## 🔑 Format du Code Client

```
DATALYS-YYYY-NNN
```

**Exemples** :
- `DATALYS-2025-001` (Premier utilisateur de 2025)
- `DATALYS-2025-002` (Deuxième utilisateur de 2025)
- `DATALYS-2025-123` (123ème utilisateur de 2025)

**Caractéristiques** :
- ✅ **Unique** : Chaque utilisateur a un code différent
- ✅ **Permanent** : Ne change jamais, même si l'email change
- ✅ **Séquentiel** : Numérotation automatique par année
- ✅ **Mémorisable** : Format court et structuré

---

## 🚀 Utilisation

### 1. Création d'un utilisateur

Lors de la création d'un utilisateur, le code client est **généré automatiquement** :

```bash
POST /users
{
  "name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "password": "MotDePasse123",
  "role_name": "User"
}
```

**Réponse** :
```json
{
  "status": "success",
  "message": "User créé avec succès",
  "data": {
    "id": 1,
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "client_code": "DATALYS-2025-001",  ← Code généré automatiquement
    "role_id": 3,
    "is_active": true,
    "created_at": "2025-10-09T12:00:00Z"
  }
}
```

---

### 2. Connexion avec le code client

Les utilisateurs peuvent maintenant se connecter de **deux façons** :

#### Option A : Connexion avec email (méthode classique)

```bash
POST /auth/login
{
  "identifier": "jean.dupont@example.com",
  "password": "MotDePasse123"
}
```

#### Option B : Connexion avec code client (nouvelle méthode)

```bash
POST /auth/login
{
  "identifier": "DATALYS-2025-001",
  "password": "MotDePasse123"
}
```

**Réponse** (identique dans les deux cas) :
```json
{
  "status": "success",
  "message": "Connexion réussie",
  "data": {
    "id": 1,
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "client_code": "DATALYS-2025-001",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "role_id": 3
  }
}
```

---

### 3. Rétrocompatibilité

Pour maintenir la compatibilité avec les anciennes versions de l'application mobile/web, le champ `email` est toujours accepté :

```bash
POST /auth/login
{
  "email": "jean.dupont@example.com",  ← Ancien format toujours supporté
  "password": "MotDePasse123"
}
```

---

## 🔧 Implémentation technique

### Base de données

**Nouvelle colonne dans la table `users`** :

```sql
ALTER TABLE users
ADD COLUMN client_code VARCHAR(50) UNIQUE DEFAULT NULL;

CREATE UNIQUE INDEX idx_users_client_code ON users(client_code);
```

### Modèle User (Python)

```python
class User(db.Model):
    # ... autres champs ...
    client_code = db.Column(db.String(50), unique=True, nullable=True, index=True)
    
    @classmethod
    def generate_client_code(cls):
        """Génère un code client unique au format DATALYS-YYYY-NNN"""
        year = datetime.now().year
        last_user = cls.query.filter(
            cls.client_code.like(f'DATALYS-{year}-%')
        ).order_by(cls.id.desc()).with_for_update().first()
        
        if last_user and last_user.client_code:
            last_num = int(last_user.client_code.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'DATALYS-{year}-{new_num:03d}'
```

### Service d'authentification

```python
def login(self, identifier: str, password: str):
    """Authentifier avec email OU code client"""
    from sqlalchemy import or_
    
    user = User.query.filter(
        or_(
            User.email == identifier,
            User.client_code == identifier
        ),
        User.is_deleted == False
    ).first()
    
    if not user:
        return None, False, "Identifiant ou mot de passe incorrect"
    
    # ... vérification du mot de passe ...
```

---

## 📊 Migration des utilisateurs existants

Pour les utilisateurs créés **avant** cette fonctionnalité, un code client est généré automatiquement lors de l'exécution de la migration SQL :

```sql
SET @counter = 0;
SET @current_year = YEAR(NOW());

UPDATE users
SET client_code = CONCAT('DATALYS-', @current_year, '-', LPAD((@counter := @counter + 1), 3, '0'))
WHERE client_code IS NULL AND is_deleted = FALSE
ORDER BY id ASC;
```

**Résultat** :
- Utilisateur ID 1 → `DATALYS-2025-001`
- Utilisateur ID 2 → `DATALYS-2025-002`
- Utilisateur ID 3 → `DATALYS-2025-003`
- etc.

---

## 🎨 Interface utilisateur

### Affichage du code client

Le code client doit être affiché dans :

1. **Page de profil utilisateur**
   ```
   ┌─────────────────────────────────┐
   │ Profil Utilisateur              │
   ├─────────────────────────────────┤
   │ Nom : Jean Dupont               │
   │ Email : jean.dupont@example.com │
   │ Code Client : DATALYS-2025-001  │ ← Affiché ici
   │ Rôle : Utilisateur              │
   └─────────────────────────────────┘
   ```

2. **Écran de connexion** (optionnel)
   ```
   ┌─────────────────────────────────┐
   │ Connexion                       │
   ├─────────────────────────────────┤
   │ Email ou Code Client :          │
   │ [___________________________]   │
   │                                 │
   │ Mot de passe :                  │
   │ [___________________________]   │
   │                                 │
   │ [Se connecter]                  │
   └─────────────────────────────────┘
   ```

3. **Email de bienvenue**
   ```
   Bonjour Jean Dupont,
   
   Votre compte a été créé avec succès !
   
   Vos identifiants de connexion :
   - Email : jean.dupont@example.com
   - Code Client : DATALYS-2025-001
   
   Vous pouvez vous connecter avec votre email OU votre code client.
   ```

---

## ✅ Avantages

### Pour les clients
- ✅ **Mobilité professionnelle** : Changement d'entreprise sans perte d'accès
- ✅ **Identifiant permanent** : Ne dépend pas de l'email
- ✅ **Simplicité** : Code court et facile à mémoriser
- ✅ **Flexibilité** : Choix entre email et code client

### Pour Datalys Consulting
- ✅ **Réduction des tickets support** : Moins de demandes de récupération de compte
- ✅ **Fidélisation client** : Les clients conservent leur historique
- ✅ **Professionnalisme** : Solution moderne et robuste
- ✅ **Conformité RGPD** : Permet la mise à jour de l'email sans perte de données

---

## 🔒 Sécurité

### Unicité garantie
- ✅ Contrainte `UNIQUE` en base de données
- ✅ Verrouillage de ligne (`with_for_update()`) lors de la génération
- ✅ Gestion des erreurs de collision

### Protection des données
- ✅ Le code client ne contient aucune information personnelle
- ✅ Pas de lien direct avec l'email ou le nom
- ✅ Format standardisé et prévisible

### Authentification
- ✅ MFA (Multi-Factor Authentication) toujours actif
- ✅ Rate limiting sur les tentatives de connexion
- ✅ Même niveau de sécurité qu'avec l'email

---

## 📝 Notes importantes

1. **Le code client ne peut pas être modifié** une fois généré
2. **Le code client est visible par l'utilisateur** (pas un secret)
3. **Le code client ne remplace pas l'email** (les deux coexistent)
4. **Le code client est optionnel** lors de la création manuelle d'un utilisateur

---

## 🧪 Tests

### Test 1 : Création d'utilisateur
```bash
curl -X POST http://localhost:8082/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "Test@123",
    "role_name": "User"
  }'
```

**Vérifier** : Le champ `client_code` est présent dans la réponse.

### Test 2 : Connexion avec email
```bash
curl -X POST http://localhost:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "test@example.com",
    "password": "Test@123"
  }'
```

**Vérifier** : Connexion réussie.

### Test 3 : Connexion avec code client
```bash
curl -X POST http://localhost:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "DATALYS-2025-001",
    "password": "Test@123"
  }'
```

**Vérifier** : Connexion réussie avec le même résultat.

---

## 🚀 Déploiement

### Étapes de déploiement

1. **Appliquer la migration SQL**
   ```bash
   mysql -u root -p datalys_db < src/migrations/add_client_code_to_users.sql
   ```

2. **Redémarrer le backend**
   ```bash
   docker-compose restart datalys-api
   ```

3. **Vérifier les codes générés**
   ```sql
   SELECT id, name, email, client_code FROM users WHERE is_deleted = FALSE;
   ```

4. **Informer les utilisateurs**
   - Envoyer un email avec leur code client
   - Mettre à jour la documentation utilisateur
   - Former l'équipe support

---

## 📞 Support

Pour toute question ou problème :
- **Documentation technique** : `/docs/CLIENT_CODE_UNIQUE.md`
- **Migration SQL** : `/src/migrations/add_client_code_to_users.sql`
- **Modèle User** : `/src/models/user.py`
- **Service Auth** : `/src/services/auth_service.py`

---

**Dernière mise à jour** : 9 Octobre 2025  
**Auteur** : Équipe Datalys Consulting

