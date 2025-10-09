# 🔐 Guide de Connexion pour les Partenaires

**Version** : 2.0.0  
**Date** : 9 Octobre 2025

---

## 👥 Qu'est-ce qu'un Partenaire ?

Un **partenaire** est un utilisateur client de Datalys Consulting qui a :
- ✅ Un **rôle "User"** (client)
- ✅ Un **code client unique** (ex: `DATALYS-2025-003`)
- ✅ Un **email professionnel**
- ✅ Un **mot de passe**
- 🔐 Le **MFA activé** (obligatoire)

---

## 🔑 Deux Méthodes de Connexion

### Méthode 1 : Login avec Email (Classique)

**Avantages** :
- Familier pour l'utilisateur
- Simple à retenir

**Inconvénients** :
- ❌ Si l'email change (changement d'entreprise), l'accès est perdu

**Exemple** :
```json
{
  "identifier": "marie.martin@datalys.com",
  "password": "Test@123"
}
```

---

### Méthode 2 : Login avec Code Client (RECOMMANDÉ) ⭐

**Avantages** :
- ✅ **Permanent** : Ne change jamais
- ✅ **Indépendant de l'email** : Fonctionne même si l'email change
- ✅ **Mobilité professionnelle** : Le partenaire garde son accès

**Inconvénients** :
- Nécessite de communiquer le code client au partenaire

**Exemple** :
```json
{
  "identifier": "DATALYS-2025-003",
  "password": "Test@123"
}
```

---

## 🚀 Processus de Connexion Complet (avec MFA)

### Étape 1 : Première Requête (Login)

**Endpoint** : `POST /auth/login`

**Body** :
```json
{
  "identifier": "DATALYS-2025-003",
  "password": "Test@123"
}
```

**Réponse** :
```json
{
  "status": "success",
  "message": "MFA requis",
  "data": {
    "requires_mfa": true,
    "user_id": 3,
    "email": "marie.martin@datalys.com",
    "message": "Code de vérification envoyé par email"
  }
}
```

**Ce qui se passe** :
1. ✅ Le système vérifie l'identifiant (email ou code client)
2. ✅ Le système vérifie le mot de passe
3. 🔐 Le système génère un code MFA à 6 chiffres
4. 📧 Le code est envoyé par email à `marie.martin@datalys.com`
5. 📱 La réponse contient le `user_id` pour l'étape suivante

---

### Étape 2 : Vérifier l'Email

**Action** : Le partenaire ouvre sa boîte mail et récupère le code à 6 chiffres.

**Email reçu** :
```
Objet : Code de vérification Datalys Consulting

Bonjour Marie Martin,

Votre code de vérification est :

    123456

Ce code est valide pendant 5 minutes.

Si vous n'avez pas demandé ce code, ignorez cet email.
```

**⚠️ Important** :
- Le code est valide pendant **5 minutes**
- Vous avez **3 tentatives** maximum
- Vérifiez aussi les **SPAMS** si vous ne recevez pas l'email

---

### Étape 3 : Vérifier le Code MFA

**Endpoint** : `POST /auth/verify-mfa`

**Body (Format recommandé)** :
```json
{
  "identifier": "marie.martin@datalys.com",
  "mfa_code": "123456"
}
```

**OU avec code client** :
```json
{
  "identifier": "DATALYS-2025-003",
  "mfa_code": "123456"
}
```

**Réponse (Succès)** :
```json
{
  "status": "success",
  "message": "Connexion réussie",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "id": 3,
    "name": "Marie Martin",
    "email": "marie.martin@datalys.com",
    "client_code": "DATALYS-2025-003",
    "role_id": 3
  }
}
```

**Ce qui se passe** :
1. ✅ Le système vérifie le code MFA
2. ✅ Le système génère un **token JWT** (valide 2 heures)
3. ✅ Le partenaire est connecté

---

### Étape 4 : Utiliser le Token

**Pour toutes les requêtes suivantes**, ajouter le token dans le header :

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Exemple** :
```bash
curl -X POST http://82.112.253.137:8082/incidents/getByCriteria \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"criteria": {}, "index": 0, "size": 10}'
```

---

## 📝 Exemples Complets

### Exemple 1 : Login avec Email + MFA

```bash
# Étape 1 : Login
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "marie.martin@datalys.com",
    "password": "Test@123"
  }'

# Réponse :
# {
#   "status": "success",
#   "message": "MFA requis",
#   "data": {
#     "requires_mfa": true,
#     "user_id": 3,
#     "email": "marie.martin@datalys.com"
#   }
# }

# Étape 2 : Vérifier l'email et copier le code (ex: 123456)

# Étape 3 : Vérifier le code MFA
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "mfa_code": "123456"
  }'

# Réponse :
# {
#   "status": "success",
#   "message": "Connexion réussie",
#   "data": {
#     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#     "id": 3,
#     "name": "Marie Martin",
#     "client_code": "DATALYS-2025-003"
#   }
# }
```

---

### Exemple 2 : Login avec Code Client + MFA (RECOMMANDÉ)

```bash
# Étape 1 : Login avec code client
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "DATALYS-2025-003",
    "password": "Test@123"
  }'

# Réponse : Identique à l'exemple 1
# Le code MFA est envoyé à l'email associé au code client

# Étape 2 : Vérifier l'email (marie.martin@datalys.com)

# Étape 3 : Vérifier le code MFA avec identifier (email ou code client)
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "marie.martin@datalys.com",
    "mfa_code": "123456"
  }'
```

---

## 🎯 Scénario : Changement d'Email

### Problème
Marie Martin change d'entreprise et son email devient `marie.martin@nouvelle-entreprise.com`.

### Solution avec Code Client

**Avant** :
- Email : `marie.martin@datalys.com`
- Code Client : `DATALYS-2025-003`
- Login : ✅ Fonctionne avec les deux

**Après changement d'email** :
- Email : `marie.martin@nouvelle-entreprise.com` (mis à jour par l'admin)
- Code Client : `DATALYS-2025-003` (inchangé)
- Login avec ancien email : ❌ Ne fonctionne plus
- Login avec code client : ✅ **Fonctionne toujours !**

**Avantage** : Le partenaire garde son accès sans interruption.

---

## ⚠️ Gestion des Erreurs

### Erreur 1 : Code MFA Invalide

**Requête** :
```json
{
  "user_id": 3,
  "mfa_code": "999999"
}
```

**Réponse** :
```json
{
  "status": "error",
  "message": "Code MFA invalide",
  "remaining_attempts": 2
}
```

**Solution** : Vérifier le code et réessayer (2 tentatives restantes).

---

### Erreur 2 : Code MFA Expiré

**Réponse** :
```json
{
  "status": "error",
  "message": "Code MFA expiré. Veuillez vous reconnecter."
}
```

**Solution** : Recommencer le processus de connexion (Étape 1).

---

### Erreur 3 : Trop de Tentatives

**Réponse** :
```json
{
  "status": "error",
  "message": "Trop de tentatives. Veuillez vous reconnecter."
}
```

**Solution** : Recommencer le processus de connexion (Étape 1).

---

### Erreur 4 : Email Non Reçu

**Causes possibles** :
1. L'email est dans les **SPAMS**
2. L'adresse email est incorrecte
3. Problème de serveur SMTP

**Solutions** :
1. Vérifier les **SPAMS / Courrier indésirable**
2. Attendre 1-2 minutes (délai de livraison)
3. Réessayer le login (Étape 1)
4. Contacter l'administrateur Datalys

---

## 🔒 Sécurité

### Pourquoi le MFA est Obligatoire ?

**Protection contre** :
- 🛡️ Vol de mot de passe
- 🛡️ Attaques par force brute
- 🛡️ Accès non autorisé

**Même si quelqu'un vole votre mot de passe**, il ne peut pas se connecter sans accès à votre email.

---

### Bonnes Pratiques

1. ✅ **Utilisez le code client** pour vous connecter (plus sûr)
2. ✅ **Ne partagez jamais** votre code MFA
3. ✅ **Changez votre mot de passe** régulièrement
4. ✅ **Vérifiez l'expéditeur** de l'email MFA
5. ✅ **Ne cliquez pas** sur des liens suspects

---

## 📱 Intégration Frontend

### Exemple React/JavaScript

```javascript
// Étape 1 : Login
async function login(identifier, password) {
  const response = await fetch('http://82.112.253.137:8082/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier, password })
  });
  
  const data = await response.json();
  
  if (data.data.requires_mfa) {
    // Afficher le formulaire MFA
    return {
      requiresMFA: true,
      userId: data.data.user_id,
      email: data.data.email
    };
  }
  
  return { requiresMFA: false };
}

// Étape 2 : Vérifier MFA
async function verifyMFA(identifier, mfaCode) {
  const response = await fetch('http://82.112.253.137:8082/auth/verify-mfa', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier: identifier, mfa_code: mfaCode })
  });
  
  const data = await response.json();
  
  if (data.status === 'success') {
    // Sauvegarder le token
    localStorage.setItem('token', data.data.token);
    localStorage.setItem('user', JSON.stringify(data.data));
    return { success: true, token: data.data.token };
  }
  
  return { success: false, message: data.message };
}

// Utilisation
const loginResult = await login('DATALYS-2025-003', 'Test@123');

if (loginResult.requiresMFA) {
  // Afficher le formulaire de saisie du code MFA
  const mfaCode = prompt('Entrez le code reçu par email:');
  const verifyResult = await verifyMFA(loginResult.email, mfaCode);
  
  if (verifyResult.success) {
    console.log('Connexion réussie !');
    // Rediriger vers le dashboard
  }
}
```

---

## 📞 Support

### Contact
- **Email** : support@datalysconsulting.com
- **Téléphone** : +33 X XX XX XX XX

### FAQ

**Q : Mon code client ne fonctionne pas**  
R : Vérifiez que vous utilisez le bon format (ex: `DATALYS-2025-003`). Contactez l'administrateur si le problème persiste.

**Q : Je n'ai pas reçu le code MFA**  
R : Vérifiez vos SPAMS. Si le problème persiste, réessayez le login ou contactez le support.

**Q : Mon token a expiré**  
R : Les tokens JWT sont valides 2 heures. Reconnectez-vous pour obtenir un nouveau token.

**Q : Puis-je désactiver le MFA ?**  
R : Non, le MFA est obligatoire pour tous les utilisateurs pour des raisons de sécurité.

---

## 🎉 Résumé

### Pour se Connecter (Partenaire)

1. **Login** avec email OU code client → Reçoit `user_id`
2. **Vérifier email** → Copier le code à 6 chiffres
3. **Vérifier MFA** avec `user_id` + code → Reçoit le token JWT
4. **Utiliser le token** pour toutes les requêtes suivantes

### Recommandations

- ✅ **Privilégier le code client** pour la connexion
- 🔐 **MFA obligatoire** pour tous
- 📧 Le code MFA est toujours envoyé à l'**email**
- ⏱️ Le token JWT est valide **2 heures**

---

**Bon développement ! 🚀**

---

**Dernière mise à jour** : 9 Octobre 2025  
**Version** : 2.0.0  
**Auteur** : Équipe Datalys Consulting

