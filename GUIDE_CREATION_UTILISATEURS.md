# 📚 Guide complet - Création d'utilisateurs et gestion des mots de passe

## 🎯 Vue d'ensemble

Ce guide explique comment créer des utilisateurs (admins, managers, partners) et gérer les mots de passe temporaires dans l'application.

---

## 📋 Table des matières

1. [Endpoints disponibles](#endpoints-disponibles)
2. [Création de partenaires](#création-de-partenaires)
3. [Création d'utilisateurs admin/manager](#création-dutilisateurs-adminmanager)
4. [Gestion des mots de passe temporaires](#gestion-des-mots-de-passe-temporaires)
5. [Flux complet](#flux-complet)
6. [Dépannage](#dépannage)

---

## 🔌 Endpoints disponibles

### Pour les partenaires

| Endpoint | Méthode | Description | Authentification |
|----------|---------|-------------|------------------|
| `/partners/create` | POST | Créer un partenaire avec compte utilisateur | Admin requis |

### Pour les utilisateurs (admin/manager/user)

| Endpoint | Méthode | Description | Authentification |
|----------|---------|-------------|------------------|
| `/users/create` | POST | Créer des utilisateurs avec mot de passe fourni | Admin requis |
| `/users/create-with-temp-password` | POST | Créer des utilisateurs avec mot de passe auto-généré | Admin requis |

### Pour l'authentification

| Endpoint | Méthode | Description | Authentification |
|----------|---------|-------------|------------------|
| `/auth/change-temp-password` | POST | Changer un mot de passe temporaire | Non |
| `/auth/check-user-status` | POST | Vérifier le statut d'un utilisateur | Non |
| `/auth/admin/reset-temp-password` | POST | Réinitialiser le mot de passe temporaire | Admin requis |

---

## 🤝 Création de partenaires

### Endpoint: `POST /partners/create`

**Prérequis:** Token JWT d'un administrateur

**Requête:**
```json
{
  "name": "Nom du partenaire",
  "email": "partner@example.com",
  "phone": "+237123456789",
  "address": "Adresse du partenaire",
  "country_code": "+237"
}
```

**Réponse:**
```json
{
  "data": {
    "id": 123,
    "name": "Nom du partenaire",
    "email": "partner@example.com",
    ...
  },
  "credentials": {
    "client_code": "DTLSA3K9M2",
    "email": "partner@example.com",
    "temp_password": "aB3$xY9!mN2p",
    "email_sent": true
  },
  "message": {
    "message": "Partenaire et compte utilisateur créés avec succès",
    "code": 201
  },
  "code": 201
}
```

**Ce qui se passe:**
1. ✅ Un compte partenaire est créé
2. ✅ Un compte utilisateur avec rôle "partner" est créé
3. ✅ Un **code client unique** est généré automatiquement (format: DTLSXXXXXX)
4. ✅ Un mot de passe temporaire est généré automatiquement (12 caractères)
5. ✅ Un email est envoyé au partenaire avec ses credentials
6. ✅ Le code client et le mot de passe temporaire sont retournés dans la réponse

**Email envoyé:**
- Sujet: "Vos identifiants de connexion - Datalys Consulting"
- Contenu: Nom, **code client** (identifiant de connexion), mot de passe temporaire, lien vers l'application

**⚠️ Important:** Les partenaires se connectent avec leur **code client** (ex: DTLSA3K9M2), PAS avec leur email!

---

## 👥 Création d'utilisateurs admin/manager

### Option 1: Avec mot de passe fourni

**Endpoint:** `POST /users/create`

**Prérequis:** Token JWT d'un administrateur

**Requête:**
```json
{
  "user": {
    "id": 1
  },
  "datas": [
    {
      "name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "password": "MonMotDePasse123!",
      "role_name": "admin"
    }
  ]
}
```

**Réponse:**
```json
{
  "items": [
    {
      "id": 456,
      "name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "role": {
        "name": "admin"
      },
      ...
    }
  ],
  "message": {
    "message": "OPERATION SUCCESSFULLY",
    "code": 200
  },
  "code": 200
}
```

**Ce qui se passe:**
1. ✅ Un compte utilisateur est créé avec le mot de passe fourni
2. ✅ Un email est envoyé avec les credentials (email + mot de passe)
3. ⚠️ Le mot de passe n'est PAS marqué comme temporaire

**Rôles autorisés:** `admin`, `manager`, `user`

---

### Option 2: Avec mot de passe temporaire auto-généré (RECOMMANDÉ)

**Endpoint:** `POST /users/create-with-temp-password`

**Prérequis:** Token JWT d'un administrateur

**Requête:**
```json
{
  "user": {
    "id": 1
  },
  "datas": [
    {
      "name": "Marie Martin",
      "email": "marie.martin@example.com",
      "role_name": "manager"
    }
  ]
}
```

**Réponse:**
```json
{
  "items": [
    {
      "id": 789,
      "name": "Marie Martin",
      "email": "marie.martin@example.com",
      "is_temp_password": true,
      "role": {
        "name": "manager"
      },
      ...
    }
  ],
  "credentials": [
    {
      "email": "marie.martin@example.com",
      "temp_password": "xK8#pL2@qW9m",
      "email_sent": true
    }
  ],
  "message": {
    "message": "OPERATION SUCCESSFULLY",
    "code": 200
  },
  "code": 200
}
```

**Ce qui se passe:**
1. ✅ Un mot de passe temporaire est généré automatiquement (12 caractères)
2. ✅ Un compte utilisateur est créé avec `is_temp_password = true`
3. ✅ Un email est envoyé avec les credentials
4. ✅ Le mot de passe temporaire est retourné dans la réponse
5. ✅ L'utilisateur devra changer son mot de passe à la première connexion

**Rôles autorisés:** `admin`, `manager`, `user`, `partner`

**Avantages:**
- 🔒 Plus sécurisé (mot de passe fort généré automatiquement)
- 📧 L'utilisateur reçoit son mot de passe par email
- 🔄 Force le changement de mot de passe à la première connexion
- 📝 Pas besoin de créer/mémoriser un mot de passe

---

## 🔐 Gestion des mots de passe temporaires

### Changer un mot de passe temporaire

**Endpoint:** `POST /auth/change-temp-password`

**Requête:**
```json
{
  "email": "user@example.com",
  "current_password": "xK8#pL2@qW9m",
  "new_password": "MonNouveauMotDePasse123!"
}
```

**Réponse:**
```json
{
  "status": "success",
  "message": "Mot de passe changé avec succès",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 789,
      "email": "user@example.com",
      ...
    }
  }
}
```

**Conditions:**
- ✅ L'utilisateur doit avoir `is_temp_password = true`
- ✅ Le mot de passe actuel doit être correct
- ✅ Le nouveau mot de passe doit avoir au moins 8 caractères

---

### Vérifier le statut d'un utilisateur (Débogage)

**Endpoint:** `POST /auth/check-user-status`

**Requête:**
```json
{
  "email": "user@example.com",
  "test_password": "xK8#pL2@qW9m"
}
```

**Réponse:**
```json
{
  "status": "success",
  "user_info": {
    "id": 789,
    "name": "Marie Martin",
    "email": "marie.martin@example.com",
    "is_active": true,
    "is_temp_password": true,
    "role": "manager",
    "password_hash": "a1b2c3d4e5f6..."
  },
  "password_test": {
    "provided_password": "xK8#pL2@qW9m",
    "calculated_hash": "a1b2c3d4e5f6...",
    "matches": true
  }
}
```

**Utilité:** Vérifier si un mot de passe correspond au hash stocké

---

### Réinitialiser un mot de passe temporaire (Admin)

**Endpoint:** `POST /auth/admin/reset-temp-password`

**Prérequis:** Token JWT d'un administrateur

**Requête:**
```json
{
  "email": "user@example.com",
  "new_temp_password": "Temp@2025"
}
```

**Réponse:**
```json
{
  "status": "success",
  "message": "Mot de passe temporaire réinitialisé avec succès pour user@example.com",
  "temp_password": "Temp@2025"
}
```

**Ce qui se passe:**
1. ✅ Le mot de passe est réinitialisé
2. ✅ `is_temp_password` est mis à `true`
3. ⚠️ Aucun email n'est envoyé (l'admin doit communiquer le mot de passe)

---

## 🔄 Flux complet

### Pour un partenaire

```
1. Admin crée le partenaire
   POST /partners/create
   {
     "name": "Partenaire XYZ",
     "email": "xyz@example.com",
     "phone": "+237123456789"
   }
   
2. Système génère automatiquement
   ✅ Code client: "DTLSA3K9M2"
   ✅ Mot de passe temporaire: "aB3$xY9!mN2p"
   
3. Email envoyé au partenaire
   ✉️ Contient: code client + mot de passe temporaire
   
4. Partenaire se connecte avec son CODE CLIENT
   POST /auth/login
   {
     "identifier": "DTLSA3K9M2",  ← CODE CLIENT, pas l'email!
     "password": "aB3$xY9!mN2p"
   }
   
5. Partenaire change son mot de passe
   POST /auth/change-temp-password
   {
     "email": "xyz@example.com",
     "current_password": "aB3$xY9!mN2p",
     "new_password": "MonNouveauMotDePasse123!"
   }
   
6. Partenaire peut maintenant utiliser l'application
   Il se connecte toujours avec son CODE CLIENT
```

### Pour un admin/manager

```
1. Admin crée l'utilisateur
   POST /users/create-with-temp-password
   
2. Système génère mot de passe temporaire
   Ex: "xK8#pL2@qW9m"
   
3. Email envoyé à l'utilisateur
   ✉️ Contient: email + mot de passe temporaire
   
4. Utilisateur se connecte
   POST /auth/login
   
5. Utilisateur change son mot de passe
   POST /auth/change-temp-password
   
6. Utilisateur peut maintenant utiliser l'application
```

---

## 🔧 Dépannage

### Erreur: "Mot de passe actuel incorrect"

**Causes possibles:**
1. Le mot de passe fourni ne correspond pas au hash en base de données
2. Le compte n'a pas été créé avec la bonne méthode
3. Le mot de passe a déjà été changé

**Solutions:**
1. Utiliser `/auth/check-user-status` pour vérifier le statut
2. Utiliser `/auth/admin/reset-temp-password` pour réinitialiser
3. Vérifier les logs du serveur pour le mot de passe généré
4. Vérifier l'email reçu par l'utilisateur

---

### Erreur: "Ce compte n'a pas de mot de passe temporaire"

**Cause:** `is_temp_password = false` ou non défini

**Solutions:**
1. Utiliser `/auth/admin/reset-temp-password` pour marquer le mot de passe comme temporaire
2. Recréer le compte avec `/users/create-with-temp-password`

---

### Email non reçu

**Vérifications:**
1. Vérifier la configuration SMTP dans `.env`
2. Vérifier les logs du serveur pour les erreurs d'envoi
3. Vérifier le dossier spam
4. Vérifier que `email_sent = true` dans la réponse API

**Configuration requise dans `.env`:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@datalysconsulting.com
APP_URL=https://applicationweb.datalysconsulting.com
```

---

## 📊 Comparaison des méthodes

| Critère | /users/create | /users/create-with-temp-password | /partners/create |
|---------|---------------|----------------------------------|------------------|
| Mot de passe fourni | ✅ Oui | ❌ Non (auto-généré) | ❌ Non (auto-généré) |
| Code client généré | ❌ Non | ❌ Non* | ✅ Oui (DTLSXXXXXX) |
| Email envoyé | ✅ Oui | ✅ Oui | ✅ Oui |
| is_temp_password | ❌ Non | ✅ Oui | ✅ Oui |
| Force changement | ❌ Non | ✅ Oui | ✅ Oui |
| Identifiant connexion | Email | Email | **Code client** |
| Rôles | admin, manager, user | admin, manager, user, partner | partner uniquement |
| Recommandé pour | Comptes permanents | Nouveaux utilisateurs | Partenaires |

*Le code client est généré uniquement si le rôle est "partner" ou "user"

---

## 🔒 Sécurité

### Génération de mot de passe temporaire

- **Longueur:** 12 caractères
- **Composition:** Majuscules, minuscules, chiffres, caractères spéciaux
- **Méthode:** `secrets.choice()` (cryptographiquement sécurisé)
- **Exemple:** `aB3$xY9!mN2p`

### Génération de code client (partenaires)

- **Format:** DTLSXXXXXX (10 caractères)
- **Préfixe:** DTLS (Datalys)
- **Partie aléatoire:** 6 caractères alphanumériques
- **Caractères:** Majuscules et chiffres (sans 0, O, I, 1 pour éviter confusion)
- **Unicité:** Vérifiée en base de données
- **Exemples:** DTLSA3K9M2, DTLS7BX4P1, DTLSQ8N5R6

### Hashage

- **Algorithme:** SHA1
- **Fonction:** `encrypt()` dans `utils/utilities.py`
- **Irréversible:** Les mots de passe ne peuvent pas être récupérés

### Bonnes pratiques

1. ✅ Toujours utiliser `/users/create-with-temp-password` pour les nouveaux utilisateurs
2. ✅ Forcer le changement de mot de passe à la première connexion
3. ✅ Ne jamais enregistrer les mots de passe en clair
4. ✅ Communiquer les mots de passe uniquement par email sécurisé
5. ✅ Utiliser des mots de passe forts (minimum 8 caractères)

---

## 📞 Support

Pour toute question ou problème, consultez:
- `SOLUTION_MOT_DE_PASSE.md` - Guide de dépannage détaillé
- Logs du serveur dans `/var/log/` ou console
- Documentation API complète

---

**Dernière mise à jour:** 2025-10-15
