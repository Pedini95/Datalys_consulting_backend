# 🧪 Guide de Test des APIs - Datalys Consulting

**Date** : 9 Octobre 2025  
**Version** : 2.0.0

---

## 📋 Table des Matières

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Scénarios de Test](#scénarios-de-test)
4. [Nouvelles Fonctionnalités](#nouvelles-fonctionnalités)
5. [Troubleshooting](#troubleshooting)

---

## 📦 Installation

### Option 1 : Postman (Recommandé)

1. **Télécharger Postman** : https://www.postman.com/downloads/
2. **Importer la collection** :
   - Ouvrir Postman
   - Cliquer sur "Import"
   - Sélectionner `Datalys_Consulting_API_Collection_Complete.json`
3. **Importer l'environnement** :
   - Cliquer sur "Import"
   - Sélectionner `Datalys_Environment_Production.json`
4. **Sélectionner l'environnement** :
   - En haut à droite, sélectionner "Datalys Consulting - Production"

### Option 2 : Insomnia

1. **Télécharger Insomnia** : https://insomnia.rest/download
2. **Importer la collection** :
   - Application → Import/Export → Import Data
   - Sélectionner `Datalys_Consulting_API_Collection_Complete.json`

### Option 3 : cURL (Ligne de commande)

Les exemples cURL sont fournis dans ce guide.

---

## ⚙️ Configuration

### Variables d'environnement

| Variable | Valeur | Description |
|----------|--------|-------------|
| `base_url` | `http://82.112.253.137:8082` | URL de l'API |
| `token` | Auto-rempli | Token JWT après login |
| `user_id` | Auto-rempli | ID utilisateur |
| `mfa_code` | À remplir | Code MFA reçu par email |
| `admin_email` | `nonssekone@gmail.com` | Email admin |
| `admin_password` | `Password123` | Mot de passe admin |
| `partner_email` | `marie.martin@datalys.com` | Email partenaire |
| `partner_password` | `Test@123` | Mot de passe partenaire |
| `partner_code_client` | `DATALYS-2025-003` | Code client partenaire |

---

## 🧪 Scénarios de Test

### Scénario 1 : Connexion Admin (sans MFA)

**Étape 1 : Désactiver le MFA**
```sql
-- Exécuter sur le VPS
UPDATE users SET mfa_enabled = 0 WHERE email = 'nonssekone@gmail.com';
```

**Étape 2 : Login**
```bash
POST {{base_url}}/auth/login
{
  "identifier": "nonssekone@gmail.com",
  "password": "Password123"
}
```

**Réponse attendue** :
```json
{
  "status": "success",
  "message": "Connexion réussie",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "id": 5,
    "name": "Pedini Nonsse",
    "email": "nonssekone@gmail.com",
    "client_code": null,
    "role_id": 1
  }
}
```

✅ **Note** : Les Admin n'ont PAS de `client_code` (null)

---

### Scénario 2 : Connexion Partenaire avec MFA

**Étape 1 : Login avec Email**
```bash
POST {{base_url}}/auth/login
{
  "identifier": "marie.martin@datalys.com",
  "password": "Test@123"
}
```

**Réponse attendue** :
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

**Étape 2 : Vérifier l'email**
- Ouvrir la boîte mail de `marie.martin@datalys.com`
- Copier le code à 6 chiffres (ex: `123456`)
- **Vérifier aussi les SPAMS !**

**Étape 3 : Vérifier le code MFA**
```bash
POST {{base_url}}/auth/verify-mfa
{
  "user_id": 3,
  "mfa_code": "123456"
}
```

**Réponse attendue** :
```json
{
  "status": "success",
  "message": "Connexion réussie",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "id": 3,
    "name": "Marie Martin",
    "email": "marie.martin@datalys.com",
    "client_code": "DATALYS-2025-003",
    "role_id": 3
  }
}
```

✅ **Note** : Les partenaires ont un `client_code`

---

### Scénario 3 : Connexion avec Code Client

**Étape 1 : Login avec Code Client**
```bash
POST {{base_url}}/auth/login
{
  "identifier": "DATALYS-2025-003",
  "password": "Test@123"
}
```

**Réponse** : Identique au Scénario 2 (MFA requis)

✅ **Avantage** : Le partenaire peut se connecter même si son email change !

---

### Scénario 4 : Créer un Incident P0 (Critique)

**Prérequis** : Être connecté (avoir un token)

**Requête** :
```bash
POST {{base_url}}/incidents
Authorization: Bearer {{token}}
{
  "title": "Arrêt complet du service",
  "description": "Le serveur principal ne répond plus depuis 10 minutes",
  "type": "incident",
  "priority": "P0",
  "impact": "arret_service",
  "domain": "infrastructure",
  "declarant_name": "Marie Martin",
  "category": "Technique",
  "project_id": 1
}
```

**Réponse attendue** :
```json
{
  "status": "success",
  "message": "Incident créé avec succès",
  "data": {
    "id": 1,
    "incident_number": "INC-2025-00001",
    "title": "Arrêt complet du service",
    "priority": "P0",
    "priority_label": "Arrêt de service (immédiat)",
    "status": "nouveau",
    "status_color": "blue",
    "impact": "arret_service",
    "impact_label": "Arrêt de service",
    "domain": "infrastructure",
    "declarant_name": "Marie Martin",
    "created_at": "2025-10-09T15:30:00Z"
  }
}
```

✅ **Automatique** :
- Numéro d'incident généré : `INC-2025-00001`
- Email envoyé aux experts (Admin/Manager)
- Notification push (si FCM configuré)

---

### Scénario 5 : Récupérer les Métadonnées des Incidents

**Requête** :
```bash
GET {{base_url}}/incidents/metadata
Authorization: Bearer {{token}}
```

**Réponse attendue** :
```json
{
  "status": "success",
  "data": {
    "priorities": [
      {"value": "P0", "label": "Arrêt de service (immédiat)", "color": "red"},
      {"value": "P1", "label": "Forte dégradation de service", "color": "orange"},
      {"value": "P2", "label": "Dégradation de service", "color": "yellow"},
      {"value": "P3", "label": "Incident ordinaire", "color": "blue"},
      {"value": "P4", "label": "Incident mineur", "color": "green"}
    ],
    "statuses": [
      {"value": "nouveau", "label": "Nouveau", "color": "blue"},
      {"value": "en_cours", "label": "En cours", "color": "orange"},
      {"value": "en_attente", "label": "En attente", "color": "gray"},
      {"value": "en_arbitrage", "label": "En arbitrage", "color": "purple"},
      {"value": "resolu", "label": "Résolu", "color": "green"},
      {"value": "ferme", "label": "Fermé", "color": "black"}
    ],
    "impacts": [...],
    "domains": [...]
  }
}
```

---

### Scénario 6 : Créer un Utilisateur Partenaire

**Requête** :
```bash
POST {{base_url}}/users
Authorization: Bearer {{token}}
{
  "name": "Nouveau Partenaire",
  "email": "nouveau.partenaire@example.com",
  "password": "Test@123",
  "role_name": "User",
  "is_active": true,
  "is_temp_password": true
}
```

**Réponse attendue** :
```json
{
  "status": "success",
  "message": "User créé avec succès",
  "data": {
    "id": 6,
    "name": "Nouveau Partenaire",
    "email": "nouveau.partenaire@example.com",
    "client_code": "DATALYS-2025-006",
    "role_id": 3,
    "is_active": true,
    "is_temp_password": true
  }
}
```

✅ **Automatique** : Code client généré (`DATALYS-2025-006`)

---

### Scénario 7 : Créer un Utilisateur Admin

**Requête** :
```bash
POST {{base_url}}/users
Authorization: Bearer {{token}}
{
  "name": "Nouvel Admin",
  "email": "nouvel.admin@datalys.com",
  "password": "Admin@123",
  "role_name": "Admin",
  "is_active": true,
  "is_temp_password": false
}
```

**Réponse attendue** :
```json
{
  "status": "success",
  "message": "User créé avec succès",
  "data": {
    "id": 7,
    "name": "Nouvel Admin",
    "email": "nouvel.admin@datalys.com",
    "client_code": null,
    "role_id": 1,
    "is_active": true,
    "is_temp_password": false
  }
}
```

✅ **Automatique** : PAS de code client pour les Admin (`null`)

---

## 🆕 Nouvelles Fonctionnalités

### 1. Code Client Unique ✅

**Pour qui ?** Uniquement les partenaires (rôle "User")

**Format** : `DATALYS-YYYY-NNN` (ex: `DATALYS-2025-003`)

**Avantages** :
- Login possible avec email OU code client
- Indépendant de l'email (mobilité professionnelle)
- Permanent et unique

**Test** :
```bash
# Login avec email
POST /auth/login {"identifier": "marie.martin@datalys.com", ...}

# Login avec code client
POST /auth/login {"identifier": "DATALYS-2025-003", ...}
```

---

### 2. Système P0-P4 ✅

**Priorités** :
- **P0** : Arrêt de service (immédiat) 🔴
- **P1** : Forte dégradation de service 🟠
- **P2** : Dégradation de service 🟡
- **P3** : Incident ordinaire 🔵
- **P4** : Incident mineur 🟢

**Nouveaux champs** :
- `incident_number` : Auto-généré (INC-2025-00001)
- `priority` : P0, P1, P2, P3, P4
- `impact` : arret_service, service_degrade, majeur, mineur
- `domain` : reseau, infrastructure, cloud, energie
- `declarant_name` : Nom du déclarant
- `motif_attente` : Si statut = "en_attente"

---

### 3. MFA par Email ✅

**Fonctionnement** :
1. Login → Code à 6 chiffres envoyé par email
2. Email envoyé en **1.7 secondes** (asynchrone)
3. Code valide pendant **5 minutes**
4. **3 tentatives** maximum

**Désactiver le MFA** (pour tests) :
```sql
UPDATE users SET mfa_enabled = 0 WHERE email = 'votre.email@example.com';
```

---

### 4. Notifications Automatiques ✅

**Lors de la création d'un incident** :
- ✅ Email envoyé à tous les **Admin** et **Manager**
- ✅ Email envoyé au **partenaire** du projet
- ✅ Notification push (si FCM configuré)
- ✅ Envoi **asynchrone** (non-bloquant)

---

## 🔧 Troubleshooting

### Problème : "Token invalide" ou "401 Unauthorized"

**Solution** :
1. Vérifier que le token est bien dans le header : `Authorization: Bearer <token>`
2. Re-login pour obtenir un nouveau token
3. Vérifier que le token n'a pas expiré (2h de validité)

---

### Problème : "Email manquant" lors du login

**Cause** : Utilisation de l'ancien format

**Solution** : Utiliser `identifier` au lieu de `email`
```json
// ❌ Ancien format
{"email": "...", "password": "..."}

// ✅ Nouveau format
{"identifier": "...", "password": "..."}
```

---

### Problème : MFA trop lent (10-30 secondes)

**Cause** : Envoi synchrone d'email

**Solution** : ✅ Déjà corrigé ! L'envoi est maintenant asynchrone (~100ms de réponse)

---

### Problème : Email MFA non reçu

**Solutions** :
1. ✅ Vérifier les **SPAMS / Courrier indésirable**
2. Vérifier les logs : `docker logs datalys-api | grep Email`
3. Vérifier la configuration SMTP
4. Désactiver temporairement le MFA pour tester

---

### Problème : Admin a un code client

**Cause** : Ancienne version du code

**Solution** : ✅ Déjà corrigé ! Les Admin n'ont plus de code client

Pour nettoyer :
```sql
UPDATE users u 
JOIN roles r ON u.role_id = r.id 
SET u.client_code = NULL 
WHERE r.name IN ('Admin', 'Manager');
```

---

## 📊 Codes de Réponse HTTP

| Code | Signification | Action |
|------|---------------|--------|
| 200 | Succès | ✅ OK |
| 400 | Requête invalide | Vérifier les paramètres |
| 401 | Non authentifié | Re-login |
| 403 | Accès refusé | Vérifier les permissions |
| 404 | Ressource non trouvée | Vérifier l'ID |
| 429 | Trop de requêtes | Attendre (rate limiting) |
| 500 | Erreur serveur | Vérifier les logs |

---

## 🎯 Checklist de Test Complet

### Authentification
- [ ] Login avec email (Admin)
- [ ] Login avec email (Partenaire)
- [ ] Login avec code client (Partenaire)
- [ ] MFA : Réception email
- [ ] MFA : Vérification code
- [ ] MFA : Code invalide (erreur attendue)
- [ ] MFA : Code expiré (erreur attendue)
- [ ] Changement mot de passe temporaire
- [ ] Logout

### Utilisateurs
- [ ] Liste des utilisateurs
- [ ] Créer Admin (sans code client)
- [ ] Créer Manager (sans code client)
- [ ] Créer Partenaire (avec code client)
- [ ] Détails utilisateur
- [ ] Modifier utilisateur
- [ ] Supprimer utilisateur

### Incidents
- [ ] Métadonnées (P0-P4, statuts, impacts, domaines)
- [ ] Liste des incidents
- [ ] Créer incident P0
- [ ] Créer incident P3
- [ ] Vérifier numéro auto-généré (INC-2025-XXXXX)
- [ ] Vérifier email aux experts
- [ ] Modifier incident
- [ ] Mettre en attente (avec motif)
- [ ] Résoudre incident
- [ ] Fermer incident

### Projets
- [ ] Liste des projets
- [ ] Créer projet
- [ ] Détails projet
- [ ] Modifier projet

### Partenaires
- [ ] Liste des partenaires
- [ ] Créer partenaire
- [ ] Détails partenaire

### Dashboard
- [ ] Statistiques dashboard

### Health Check
- [ ] Health check (sans auth)

---

## 📞 Support

Pour toute question :
- **Documentation** : `/docs/`
- **Collection Postman** : `Datalys_Consulting_API_Collection_Complete.json`
- **Environnement** : `Datalys_Environment_Production.json`

---

**Dernière mise à jour** : 9 Octobre 2025  
**Version** : 2.0.0  
**Auteur** : Équipe Datalys Consulting

