# 🔐 Solution au problème de mot de passe temporaire

## 📋 Résumé du problème

Vous avez reçu l'erreur suivante lors de l'appel à `/auth/change-temp-password`:

```json
{
  "message": "Mot de passe actuel incorrect",
  "status": "error"
}
```

## 🔍 Cause racine identifiée

**Le mot de passe temporaire n'était PAS envoyé par email lors de la création du partenaire!**

### Problèmes découverts:

1. ❌ La route `/partners/create` utilisait `partner_service.create()` au lieu de `partner_service.create_with_user()`
2. ❌ Aucun email n'était envoyé avec les credentials (username et mot de passe temporaire)
3. ❌ Le partenaire ne recevait jamais son mot de passe temporaire généré automatiquement

### Pourquoi "Temp@2025" ne fonctionnait pas:

- Quand un partenaire est créé, la fonction `generate_temp_password()` génère un mot de passe **aléatoire** de 12 caractères
- Ce mot de passe contient des lettres majuscules, minuscules, chiffres et caractères spéciaux
- Exemple: `aB3$xY9!mN2p`
- Le mot de passe "Temp@2025" que vous testiez n'était donc pas le bon

## ✅ Solutions implémentées

### 1. Modification de la route `/partners/create`

**Fichier modifié:** `src/routes/partners.py`

La route a été mise à jour pour:
- ✅ Utiliser `partner_service.create_with_user()` quand un email est fourni
- ✅ Envoyer automatiquement un email avec les credentials
- ✅ Retourner le mot de passe temporaire dans la réponse API (pour le débogage)

**Exemple de réponse après création:**

```json
{
  "data": {
    "id": 123,
    "name": "Nom du partenaire",
    "email": "yablaiyablairubenvirgil19@gmail.com",
    ...
  },
  "credentials": {
    "username": "yablaiyablairubenvirgil19@gmail.com",
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

### 2. Nouveaux endpoints ajoutés

**Fichier modifié:** `src/routes/auth.py`

#### A. `/auth/check-user-status` - Vérifier le statut d'un utilisateur

Permet de vérifier les informations d'un utilisateur et tester un mot de passe:

```bash
POST http://82.112.253.137:8082/auth/check-user-status
Content-Type: application/json

{
  "email": "yablaiyablairubenvirgil19@gmail.com",
  "test_password": "aB3$xY9!mN2p"
}
```

**Réponse:**
```json
{
  "status": "success",
  "user_info": {
    "id": 123,
    "name": "Nom de l'utilisateur",
    "email": "yablaiyablairubenvirgil19@gmail.com",
    "is_active": true,
    "is_temp_password": true,
    "role": "partner",
    "password_hash": "..."
  },
  "password_test": {
    "provided_password": "aB3$xY9!mN2p",
    "calculated_hash": "...",
    "matches": true
  }
}
```

#### B. `/auth/admin/reset-temp-password` - Réinitialiser le mot de passe (Admin)

Permet à un administrateur de réinitialiser le mot de passe temporaire d'un utilisateur:

```bash
POST http://82.112.253.137:8082/auth/admin/reset-temp-password
Content-Type: application/json
Authorization: Bearer <ADMIN_TOKEN>

{
  "email": "yablaiyablairubenvirgil19@gmail.com",
  "new_temp_password": "Temp@2025"
}
```

**Réponse:**
```json
{
  "status": "success",
  "message": "Mot de passe temporaire réinitialisé avec succès pour yablaiyablairubenvirgil19@gmail.com",
  "temp_password": "Temp@2025"
}
```

⚠️ **Prérequis:** Token JWT d'un administrateur (rôle `admin` ou `super_admin`)

## 🎯 Comment résoudre votre problème actuel

### Option 1: Utiliser l'endpoint admin (Recommandé)

Si vous avez un compte administrateur:

1. Connectez-vous en tant qu'admin pour obtenir un token JWT
2. Utilisez `/auth/admin/reset-temp-password` pour définir "Temp@2025" comme mot de passe temporaire
3. Utilisez `/auth/change-temp-password` avec "Temp@2025"

### Option 2: Retrouver le mot de passe temporaire original

1. Vérifiez les logs du serveur lors de la création du partenaire
2. Vérifiez l'email envoyé au partenaire
3. Vérifiez la réponse API de création du partenaire (si elle a été sauvegardée)

### Option 3: Recréer le compte

Si le compte n'a pas encore de données importantes:

1. Supprimez le compte existant
2. Recréez-le avec la nouvelle route `/partners/create` (qui envoie maintenant l'email)
3. Le partenaire recevra son mot de passe temporaire par email

## 📧 Template d'email

Le partenaire reçoit maintenant un email avec le template `email_partner_credentials.html` contenant:

- Son nom
- Son email de connexion
- Son mot de passe temporaire
- Un lien vers l'application
- Des instructions pour se connecter

## 🔄 Flux complet de création de partenaire

```
1. Admin crée un partenaire avec email
   POST /partners/create
   
2. Système génère un mot de passe temporaire aléatoire
   Ex: "aB3$xY9!mN2p"
   
3. Système crée le compte utilisateur avec rôle "partner"
   - password_hash = encrypt("aB3$xY9!mN2p")
   - is_temp_password = true
   
4. Système envoie un email au partenaire
   - Email contient le mot de passe temporaire
   
5. Partenaire reçoit l'email et se connecte
   POST /auth/login
   {
     "identifier": "email@example.com",
     "password": "aB3$xY9!mN2p"
   }
   
6. Partenaire change son mot de passe temporaire
   POST /auth/change-temp-password
   {
     "email": "email@example.com",
     "current_password": "aB3$xY9!mN2p",
     "new_password": "MonNouveauMotDePasse123!"
   }
```

## 🧪 Scripts de débogage créés

Trois scripts Python ont été créés pour vous aider:

1. **`debug_password.py`** - Calcule les hash SHA1 des mots de passe
2. **`check_db_password.py`** - Vérifie directement dans la base de données
3. **`verify_password.py`** - Version améliorée avec variables d'environnement

## 📝 Notes importantes

- ⚠️ Le mot de passe temporaire est **sensible à la casse**
- ⚠️ Le mot de passe est hashé avec **SHA1** (fonction `encrypt()` dans `utils/utilities.py`)
- ⚠️ L'email doit être configuré correctement dans `.env` pour que l'envoi fonctionne
- ✅ Le mot de passe temporaire est maintenant retourné dans la réponse API pour faciliter le débogage
- ✅ Un log est créé quand l'email est envoyé avec succès

## 🚀 Prochaines étapes recommandées

1. **Tester la création d'un nouveau partenaire** pour vérifier que l'email est bien envoyé
2. **Vérifier la configuration email** dans `.env` (SMTP_HOST, SMTP_PORT, MAIL_USERNAME, etc.)
3. **Utiliser l'endpoint admin** pour réinitialiser le mot de passe du compte existant
4. **Documenter le mot de passe temporaire** lors de la création pour référence future

## ❓ Questions fréquentes

**Q: Pourquoi le mot de passe n'était pas envoyé avant?**
R: La route utilisait `partner_service.create()` au lieu de `create_with_user()`, et aucun code n'envoyait l'email.

**Q: Le mot de passe temporaire est-il sécurisé?**
R: Oui, il est généré avec `secrets.choice()` (cryptographiquement sécurisé) et contient 12 caractères avec majuscules, minuscules, chiffres et caractères spéciaux.

**Q: Que se passe-t-il si l'email échoue?**
R: Le partenaire est quand même créé, mais le mot de passe temporaire est retourné dans la réponse API. Un log d'erreur est créé.

**Q: Comment un admin peut-il voir le mot de passe d'un utilisateur?**
R: Les mots de passe sont hashés et ne peuvent pas être récupérés. Un admin peut seulement les réinitialiser avec `/auth/admin/reset-temp-password`.
