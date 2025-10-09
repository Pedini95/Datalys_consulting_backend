# 📘 Documentation Complète des APIs - Datalys Consulting

**Version** : 2.0.0  
**Date** : 9 Octobre 2025  
**Base URL** : `http://82.112.253.137:8082`

---

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Authentification](#authentification)
3. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
4. [Gestion des Incidents](#gestion-des-incidents)
5. [Gestion des Projets](#gestion-des-projets)
6. [Gestion des Partenaires](#gestion-des-partenaires)
7. [Gestion des Rôles](#gestion-des-rôles)
8. [Dashboard](#dashboard)
9. [Health Check](#health-check)
10. [Codes d'Erreur](#codes-derreur)
11. [Exemples Complets](#exemples-complets)

---

## 🚀 Introduction

### Base URL
```
http://82.112.253.137:8082
```

### Format des Réponses

**Succès** :
```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": { ... }
}
```

**Erreur** :
```json
{
  "code": 400,
  "message": "Description de l'erreur",
  "data": null
}
```

### Authentification

Toutes les routes (sauf `/auth/*` et `/health`) nécessitent un token JWT dans le header :

```
Authorization: Bearer <votre_token_jwt>
```

---

## 🔐 Authentification

### 1. Login (Email ou Code Client)

**Endpoint** : `POST /auth/login`

**Description** : Connexion avec email ou code client. Si MFA activé, retourne un `user_id` pour la vérification.

**Body** :
```json
{
  "identifier": "email@example.com ou DATALYS-2025-XXX",
  "password": "votre_mot_de_passe"
}
```

**Réponse (MFA Activé - Par défaut pour tous)** :
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

**Exemple cURL** :
```bash
# Login Admin/Manager avec email
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "nonssekone@gmail.com",
    "password": "Password123"
  }'

# Login Partenaire avec email
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "marie.martin@datalys.com",
    "password": "Test@123"
  }'

# Login Partenaire avec code client (RECOMMANDÉ)
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "DATALYS-2025-003",
    "password": "Test@123"
  }'
```

**💡 Pour les Partenaires** :
- ✅ **Option 1** : Login avec **email** (ex: `marie.martin@datalys.com`)
- ✅ **Option 2** : Login avec **code client** (ex: `DATALYS-2025-003`) - **RECOMMANDÉ**
- 🔐 **MFA obligatoire** dans les deux cas
- 📧 Le code MFA est toujours envoyé à l'**email** du partenaire

---

### 2. Vérifier Code MFA

**Endpoint** : `POST /auth/verify-mfa`

**Description** : Vérifier le code MFA à 6 chiffres reçu par email.

**Body (Format recommandé avec identifier)** :
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

**OU ancien format (rétrocompatible)** :
```json
{
  "user_id": 3,
  "mfa_code": "123456"
}
```

**Réponse** :
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

**Erreurs possibles** :
- `400` : Code invalide
- `400` : Code expiré (5 minutes)
- `429` : Trop de tentatives (3 max)

**Exemple cURL** :
```bash
# Format recommandé avec email
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "marie.martin@datalys.com",
    "mfa_code": "123456"
  }'

# Avec code client
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "DATALYS-2025-003",
    "mfa_code": "123456"
  }'

# Ancien format (toujours supporté)
curl -X POST http://82.112.253.137:8082/auth/verify-mfa \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "mfa_code": "123456"
  }'
```

---

### 3. Changer Mot de Passe Temporaire

**Endpoint** : `POST /auth/change-temp-password`

**Description** : Changer un mot de passe temporaire.

**Body** :
```json
{
  "email": "marie.martin@datalys.com",
  "old_password": "Test@123",
  "new_password": "NewPassword@123"
}
```

**Réponse** :
```json
{
  "status": "success",
  "message": "Mot de passe changé avec succès",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": { ... }
  }
}
```

**Exemple cURL** :
```bash
curl -X POST http://82.112.253.137:8082/auth/change-temp-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "marie.martin@datalys.com",
    "old_password": "Test@123",
    "new_password": "NewPassword@123"
  }'
```

---

### 4. Logout

**Endpoint** : `POST /auth/logout`

**Description** : Déconnexion de l'utilisateur.

**Headers** :
```
Authorization: Bearer <token>
```

**Réponse** :
```json
{
  "status": "success",
  "message": "Déconnexion réussie"
}
```

**Exemple cURL** :
```bash
curl -X POST http://82.112.253.137:8082/auth/logout \
  -H "Authorization: Bearer <votre_token>"
```

---

## 👤 Gestion des Utilisateurs

### 1. Liste des Utilisateurs

**Endpoint** : `POST /users/getByCriteria`

**Description** : Récupérer la liste des utilisateurs avec pagination et filtres.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "criteria": {
    "is_active": true,
    "role_id": 3
  },
  "index": 0,
  "size": 10
}
```

**Paramètres** :
- `criteria` (object, optionnel) : Filtres de recherche
  - `is_active` (boolean) : Utilisateurs actifs
  - `role_id` (integer) : Filtrer par rôle
  - `email` (string) : Filtrer par email
  - `name` (string) : Filtrer par nom
  - `client_code` (string) : Filtrer par code client
- `index` (integer) : Page (commence à 0)
- `size` (integer) : Nombre d'éléments par page

**Réponse** :
```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": [
    {
      "id": 3,
      "name": "Marie Martin",
      "email": "marie.martin@datalys.com",
      "client_code": "DATALYS-2025-003",
      "role_id": 3,
      "is_active": true,
      "is_temp_password": false,
      "created_at": "2025-10-09T10:00:00Z"
    },
    {
      "id": 5,
      "name": "Pedini Nonsse",
      "email": "nonssekone@gmail.com",
      "client_code": null,
      "role_id": 1,
      "is_active": true,
      "is_temp_password": false,
      "created_at": "2025-10-09T12:00:00Z"
    }
  ]
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/users/getByCriteria \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {"is_active": true},
    "index": 0,
    "size": 10
  }'
```

---

### 2. Créer un Utilisateur

**Endpoint** : `POST /users/create`

**Description** : Créer un nouvel utilisateur. Si `role_name = "User"`, un code client est généré automatiquement.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "name": "Nouveau Partenaire",
  "email": "nouveau.partenaire@example.com",
  "password": "Test@123",
  "role_name": "User",
  "is_active": true,
  "is_temp_password": false
}
```

**Paramètres** :
- `name` (string, requis) : Nom complet
- `email` (string, requis) : Email unique
- `password` (string, requis) : Mot de passe
- `role_name` (string, requis) : "Admin", "Manager", ou "User"
- `is_active` (boolean, optionnel) : Actif par défaut
- `is_temp_password` (boolean, optionnel) : Mot de passe temporaire

**Réponse** :
```json
{
  "code": 200,
  "message": "User créé avec succès",
  "data": {
    "id": 6,
    "name": "Nouveau Partenaire",
    "email": "nouveau.partenaire@example.com",
    "client_code": "DATALYS-2025-006",
    "role_id": 3,
    "is_active": true,
    "is_temp_password": false,
    "created_at": "2025-10-09T15:30:00Z"
  }
}
```

**Notes importantes** :
- ✅ **Partenaires (User)** : Code client généré automatiquement
- ❌ **Admin/Manager** : PAS de code client (null)

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

# Créer un partenaire (avec code client)
curl -X POST http://82.112.253.137:8082/users/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Partenaire",
    "email": "test.partenaire@example.com",
    "password": "Test@123",
    "role_name": "User",
    "is_active": true,
    "is_temp_password": false
  }'

# Créer un admin (sans code client)
curl -X POST http://82.112.253.137:8082/users/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouvel Admin",
    "email": "nouvel.admin@datalys.com",
    "password": "Admin@123",
    "role_name": "Admin",
    "is_active": true,
    "is_temp_password": false
  }'
```

---

### 3. Modifier un Utilisateur

**Endpoint** : `POST /users/update`

**Description** : Modifier les informations d'un utilisateur existant.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "id": 6,
  "name": "Nom Modifié",
  "is_active": false
}
```

**Paramètres** :
- `id` (integer, requis) : ID de l'utilisateur
- Tous les autres champs sont optionnels

**Réponse** :
```json
{
  "code": 200,
  "message": "User modifié avec succès",
  "data": {
    "id": 6,
    "name": "Nom Modifié",
    "email": "nouveau.partenaire@example.com",
    "client_code": "DATALYS-2025-006",
    "is_active": false,
    "updated_at": "2025-10-09T16:00:00Z"
  }
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/users/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 6,
    "name": "Nom Modifié",
    "is_active": false
  }'
```

---

### 4. Supprimer un Utilisateur

**Endpoint** : `POST /users/delete`

**Description** : Supprimer un utilisateur (soft delete).

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "id": 6
}
```

**Réponse** :
```json
{
  "code": 200,
  "message": "User supprimé avec succès",
  "data": null
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/users/delete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": 6}'
```

---

## 🚨 Gestion des Incidents

### 1. Métadonnées des Incidents (P0-P4)

**Endpoint** : `GET /incidents/metadata`

**Description** : Récupérer les métadonnées (priorités P0-P4, statuts, impacts, domaines).

**Headers** :
```
Authorization: Bearer <token>
```

**Réponse** :
```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": {
    "priorities": [
      {
        "value": "P0",
        "label": "Arrêt de service (immédiat)",
        "color": "red"
      },
      {
        "value": "P1",
        "label": "Forte dégradation de service",
        "color": "orange"
      },
      {
        "value": "P2",
        "label": "Dégradation de service",
        "color": "yellow"
      },
      {
        "value": "P3",
        "label": "Incident ordinaire",
        "color": "blue"
      },
      {
        "value": "P4",
        "label": "Incident mineur",
        "color": "green"
      }
    ],
    "statuses": [
      {"value": "nouveau", "label": "Nouveau", "color": "blue"},
      {"value": "en_cours", "label": "En cours", "color": "orange"},
      {"value": "en_attente", "label": "En attente", "color": "gray"},
      {"value": "en_arbitrage", "label": "En arbitrage", "color": "purple"},
      {"value": "resolu", "label": "Résolu", "color": "green"},
      {"value": "ferme", "label": "Fermé", "color": "black"}
    ],
    "impacts": [
      {
        "value": "arret_service",
        "label": "Arrêt de service",
        "recommended_priority": "P0"
      },
      {
        "value": "service_degrade",
        "label": "Service dégradé",
        "recommended_priority": "P1"
      },
      {
        "value": "majeur",
        "label": "Impact majeur",
        "recommended_priority": "P2"
      },
      {
        "value": "mineur",
        "label": "Impact mineur",
        "recommended_priority": "P3"
      }
    ],
    "domains": [
      {"value": "reseau", "label": "Réseau"},
      {"value": "infrastructure", "label": "Infrastructure système"},
      {"value": "cloud", "label": "Cloud"},
      {"value": "energie", "label": "Énergie"}
    ]
  }
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X GET http://82.112.253.137:8082/incidents/metadata \
  -H "Authorization: Bearer $TOKEN"
```

---

### 2. Liste des Incidents

**Endpoint** : `POST /incidents/getByCriteria`

**Description** : Récupérer la liste des incidents avec pagination et filtres.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "criteria": {
    "priority": "P0",
    "status": "nouveau",
    "project_id": 1
  },
  "index": 0,
  "size": 10
}
```

**Paramètres** :
- `criteria` (object, optionnel) : Filtres
  - `priority` (string) : P0, P1, P2, P3, P4
  - `status` (string) : nouveau, en_cours, en_attente, resolu, ferme
  - `project_id` (integer) : Filtrer par projet
  - `assigned_to` (integer) : Filtrer par assigné
  - `impact` (string) : arret_service, service_degrade, majeur, mineur
  - `domain` (string) : reseau, infrastructure, cloud, energie
- `index` (integer) : Page
- `size` (integer) : Nombre d'éléments

**Réponse** :
```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": [
    {
      "id": 1,
      "incident_number": "INC-2025-00001",
      "title": "Arrêt complet du service",
      "description": "Le serveur ne répond plus",
      "type": "incident",
      "priority": "P0",
      "priority_label": "Arrêt de service (immédiat)",
      "status": "nouveau",
      "status_color": "blue",
      "impact": "arret_service",
      "impact_label": "Arrêt de service",
      "domain": "infrastructure",
      "declarant_name": "Marie Martin",
      "category": "Technique",
      "project_id": 1,
      "assigned_to": null,
      "created_at": "2025-10-09T15:00:00Z"
    }
  ]
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/incidents/getByCriteria \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {"priority": "P0"},
    "index": 0,
    "size": 10
  }'
```

---

### 3. Créer un Incident

**Endpoint** : `POST /incidents/create`

**Description** : Créer un nouvel incident. Le numéro d'incident est généré automatiquement. Des emails sont envoyés aux experts (Admin/Manager) et au partenaire.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
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

**Paramètres** :
- `title` (string, requis) : Titre de l'incident
- `description` (string, requis) : Description détaillée
- `type` (string, requis) : "incident" ou "support"
- `priority` (string, requis) : P0, P1, P2, P3, P4
- `impact` (string, optionnel) : arret_service, service_degrade, majeur, mineur
- `domain` (string, optionnel) : reseau, infrastructure, cloud, energie
- `declarant_name` (string, optionnel) : Nom du déclarant
- `category` (string, optionnel) : Catégorie
- `project_id` (integer, requis) : ID du projet

**Réponse** :
```json
{
  "code": 200,
  "message": "Incident créé avec succès",
  "data": {
    "id": 1,
    "incident_number": "INC-2025-00001",
    "title": "Arrêt complet du service",
    "description": "Le serveur principal ne répond plus depuis 10 minutes",
    "type": "incident",
    "priority": "P0",
    "priority_label": "Arrêt de service (immédiat)",
    "status": "nouveau",
    "status_color": "blue",
    "impact": "arret_service",
    "impact_label": "Arrêt de service",
    "domain": "infrastructure",
    "declarant_name": "Marie Martin",
    "category": "Technique",
    "project_id": 1,
    "created_at": "2025-10-09T15:30:00Z"
  }
}
```

**Automatisations** :
- ✅ Numéro d'incident généré : `INC-2025-00001`
- ✅ Email envoyé aux Admin/Manager
- ✅ Email envoyé au partenaire du projet
- ✅ Notification push (si FCM configuré)

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

# Incident P0 (Critique)
curl -X POST http://82.112.253.137:8082/incidents/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Arrêt complet du service",
    "description": "Le serveur ne répond plus",
    "type": "incident",
    "priority": "P0",
    "impact": "arret_service",
    "domain": "infrastructure",
    "declarant_name": "Marie Martin",
    "category": "Technique",
    "project_id": 1
  }'

# Incident P3 (Normal)
curl -X POST http://82.112.253.137:8082/incidents/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Problème d'\''affichage mineur",
    "description": "Un bouton ne s'\''affiche pas correctement",
    "type": "incident",
    "priority": "P3",
    "impact": "mineur",
    "domain": "reseau",
    "declarant_name": "Jean Dupont",
    "category": "Interface",
    "project_id": 1
  }'
```

---

### 4. Modifier un Incident

**Endpoint** : `POST /incidents/update`

**Description** : Modifier un incident existant.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "id": 1,
  "status": "en_cours",
  "assigned_to": 2,
  "priority": "P1"
}
```

**Paramètres** :
- `id` (integer, requis) : ID de l'incident
- Tous les autres champs sont optionnels

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

# Assigner et passer en cours
curl -X POST http://82.112.253.137:8082/incidents/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "status": "en_cours",
    "assigned_to": 2
  }'

# Mettre en attente avec motif
curl -X POST http://82.112.253.137:8082/incidents/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "status": "en_attente",
    "motif_attente": "En attente de réponse du client"
  }'

# Résoudre l'incident
curl -X POST http://82.112.253.137:8082/incidents/update \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "status": "resolu",
    "resolution_notes": "Problème résolu en redémarrant le serveur"
  }'
```

---

### 5. Supprimer un Incident

**Endpoint** : `POST /incidents/delete`

**Description** : Supprimer un incident (soft delete).

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "id": 1
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/incidents/delete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

---

## 📁 Gestion des Projets

### 1. Liste des Projets

**Endpoint** : `POST /projects/getByCriteria`

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "criteria": {
    "status": "en_cours",
    "partner_id": 1
  },
  "index": 0,
  "size": 10
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/projects/getByCriteria \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {},
    "index": 0,
    "size": 10
  }'
```

---

### 2. Créer un Projet

**Endpoint** : `POST /projects/create`

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "title": "Projet Test API",
  "description": "Description du projet",
  "partner_id": 1,
  "status": "en_cours",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/projects/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nouveau Projet",
    "description": "Description du projet",
    "partner_id": 1,
    "status": "en_cours",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'
```

---

### 3. Modifier un Projet

**Endpoint** : `POST /projects/update`

**Body** :
```json
{
  "id": 1,
  "title": "Titre Modifié",
  "status": "termine"
}
```

---

### 4. Supprimer un Projet

**Endpoint** : `POST /projects/delete`

**Body** :
```json
{
  "id": 1
}
```

---

## 🏢 Gestion des Partenaires

### 1. Liste des Partenaires

**Endpoint** : `POST /partners/getByCriteria`

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "criteria": {},
  "index": 0,
  "size": 10
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/partners/getByCriteria \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {},
    "index": 0,
    "size": 10
  }'
```

---

### 2. Créer un Partenaire

**Endpoint** : `POST /partners/create`

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "name": "Entreprise Test",
  "email": "contact@entreprise-test.com",
  "phone": "+33612345678",
  "address": "123 Rue de Test, 75001 Paris",
  "country_code": "FR"
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/partners/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouvelle Entreprise",
    "email": "contact@nouvelle-entreprise.com",
    "phone": "+33612345678",
    "address": "123 Rue de Test, 75001 Paris",
    "country_code": "FR"
  }'
```

---

### 3. Modifier un Partenaire

**Endpoint** : `POST /partners/update`

**Body** :
```json
{
  "id": 1,
  "name": "Nom Modifié",
  "phone": "+33698765432"
}
```

---

### 4. Supprimer un Partenaire

**Endpoint** : `POST /partners/delete`

**Body** :
```json
{
  "id": 1
}
```

---

## 👑 Gestion des Rôles

### 1. Liste des Rôles

**Endpoint** : `POST /roles/getByCriteria`

**Headers** :
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body** :
```json
{
  "criteria": {},
  "index": 0,
  "size": 10
}
```

**Réponse** :
```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": [
    {
      "id": 1,
      "name": "Admin",
      "permissions": ["all"]
    },
    {
      "id": 2,
      "name": "Manager",
      "permissions": ["read", "write", "update"]
    },
    {
      "id": 3,
      "name": "User",
      "permissions": ["read"]
    }
  ]
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X POST http://82.112.253.137:8082/roles/getByCriteria \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {},
    "index": 0,
    "size": 10
  }'
```

---

## 📊 Dashboard

### Statistiques Dashboard

**Endpoint** : `GET /dashboard`

**Description** : Récupérer les statistiques du dashboard (incidents, projets, utilisateurs).

**Headers** :
```
Authorization: Bearer <token>
```

**Réponse** :
```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": {
    "total_incidents": 15,
    "incidents_ouverts": 8,
    "incidents_resolus": 7,
    "total_projets": 5,
    "projets_actifs": 3,
    "total_utilisateurs": 12,
    "utilisateurs_actifs": 10
  }
}
```

**Exemple cURL** :
```bash
TOKEN="votre_token_ici"

curl -X GET http://82.112.253.137:8082/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🏥 Health Check

### Vérifier l'État de l'API

**Endpoint** : `GET /health`

**Description** : Vérifier l'état de santé de l'API et de la base de données. **Pas d'authentification requise**.

**Réponse** :
```json
{
  "status": "healthy",
  "application": {
    "status": "running",
    "version": "1.0.0"
  },
  "database": {
    "status": "connected",
    "version": "8.0.43",
    "tables_count": 9,
    "error": null
  },
  "timestamp": null
}
```

**Exemple cURL** :
```bash
curl -X GET http://82.112.253.137:8082/health
```

---

## ⚠️ Codes d'Erreur

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Requête réussie |
| 400 | Bad Request | Paramètres invalides ou manquants |
| 401 | Unauthorized | Token manquant ou invalide |
| 403 | Forbidden | Accès refusé (permissions insuffisantes) |
| 404 | Not Found | Ressource non trouvée |
| 409 | Conflict | Conflit (ex: email déjà existant) |
| 429 | Too Many Requests | Trop de tentatives (rate limiting) |
| 500 | Internal Server Error | Erreur serveur |

---

## 🎯 Exemples Complets

### Scénario 1 : Créer un Partenaire et un Incident

```bash
# 1. Login Admin
TOKEN=$(curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}' \
  | jq -r '.data.token')

echo "Token: $TOKEN"

# 2. Créer un partenaire
PARTNER_RESPONSE=$(curl -s -X POST http://82.112.253.137:8082/partners/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Entreprise ABC",
    "email": "contact@abc.com",
    "phone": "+33612345678",
    "address": "123 Rue de Paris, 75001 Paris",
    "country_code": "FR"
  }')

PARTNER_ID=$(echo $PARTNER_RESPONSE | jq -r '.data.id')
echo "Partenaire créé - ID: $PARTNER_ID"

# 3. Créer un projet pour ce partenaire
PROJECT_RESPONSE=$(curl -s -X POST http://82.112.253.137:8082/projects/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Projet ABC\",
    \"description\": \"Description du projet\",
    \"partner_id\": $PARTNER_ID,
    \"status\": \"en_cours\",
    \"start_date\": \"2025-01-01\",
    \"end_date\": \"2025-12-31\"
  }")

PROJECT_ID=$(echo $PROJECT_RESPONSE | jq -r '.data.id')
echo "Projet créé - ID: $PROJECT_ID"

# 4. Créer un incident P0 pour ce projet
INCIDENT_RESPONSE=$(curl -s -X POST http://82.112.253.137:8082/incidents/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Arrêt complet du service\",
    \"description\": \"Le serveur ne répond plus\",
    \"type\": \"incident\",
    \"priority\": \"P0\",
    \"impact\": \"arret_service\",
    \"domain\": \"infrastructure\",
    \"declarant_name\": \"Contact ABC\",
    \"category\": \"Technique\",
    \"project_id\": $PROJECT_ID
  }")

INCIDENT_NUMBER=$(echo $INCIDENT_RESPONSE | jq -r '.data.incident_number')
echo "Incident créé - Numéro: $INCIDENT_NUMBER"
echo "✅ Email envoyé aux experts et au partenaire"
```

---

### Scénario 2 : Créer un Utilisateur Partenaire et Tester le Login

```bash
# 1. Login Admin
TOKEN=$(curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}' \
  | jq -r '.data.token')

# 2. Créer un utilisateur partenaire
USER_RESPONSE=$(curl -s -X POST http://82.112.253.137:8082/users/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Partenaire",
    "email": "test.partenaire@example.com",
    "password": "Test@123",
    "role_name": "User",
    "is_active": true,
    "is_temp_password": false
  }')

CLIENT_CODE=$(echo $USER_RESPONSE | jq -r '.data.client_code')
echo "Utilisateur créé - Code client: $CLIENT_CODE"

# 3. Désactiver le MFA pour faciliter le test
ssh root@82.112.253.137 "docker exec -i mysql-db mysql -uroot -proot datalys_consulting -e \"UPDATE users SET mfa_enabled = 0 WHERE email = 'test.partenaire@example.com';\""

# 4. Tester le login avec email
echo "Test login avec email..."
curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "test.partenaire@example.com", "password": "Test@123"}' \
  | jq '.data | {token: .token[:50], client_code}'

# 5. Tester le login avec code client
echo "Test login avec code client..."
curl -s -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"identifier\": \"$CLIENT_CODE\", \"password\": \"Test@123\"}" \
  | jq '.data | {token: .token[:50], email}'
```

---

## 🆕 Nouvelles Fonctionnalités

### 1. Code Client Unique ✅

**Description** : Chaque partenaire (rôle "User") reçoit un code client unique au format `DATALYS-YYYY-NNN`.

**Avantages** :
- Login possible avec email OU code client
- Indépendant de l'email (mobilité professionnelle)
- Permanent et unique

**Exemple** :
```json
{
  "name": "Marie Martin",
  "email": "marie.martin@datalys.com",
  "client_code": "DATALYS-2025-003",
  "role_id": 3
}
```

**Note** : Les Admin et Manager n'ont PAS de code client (null).

---

### 2. Système de Priorités P0-P4 ✅

| Priorité | Label | Couleur | Description |
|----------|-------|---------|-------------|
| P0 | Arrêt de service (immédiat) | 🔴 Rouge | Service complètement arrêté |
| P1 | Forte dégradation de service | 🟠 Orange | Service fortement dégradé |
| P2 | Dégradation de service | 🟡 Jaune | Service partiellement dégradé |
| P3 | Incident ordinaire | 🔵 Bleu | Incident normal |
| P4 | Incident mineur | 🟢 Vert | Incident sans impact majeur |

---

### 3. Numéro d'Incident Auto-généré ✅

**Format** : `INC-YYYY-NNNNN`

**Exemple** : `INC-2025-00001`

**Génération** : Automatique à la création, unique et séquentiel par année.

---

### 4. MFA par Email ✅ (OBLIGATOIRE)

**Fonctionnement** :
1. Login → Code à 6 chiffres envoyé par email
2. Email envoyé en **~1.7 secondes** (asynchrone)
3. Code valide pendant **5 minutes**
4. **3 tentatives** maximum

**⚠️ IMPORTANT** : Le MFA est **OBLIGATOIRE** pour tous les utilisateurs (Admin, Manager, User).

**Processus de connexion** :
```
1. POST /auth/login → Retourne user_id + "MFA requis"
2. Vérifier l'email → Copier le code à 6 chiffres
3. POST /auth/verify-mfa → Retourne le token JWT
```

---

### 5. Notifications Automatiques ✅

**Lors de la création d'un incident** :
- ✅ Email envoyé à tous les **Admin** et **Manager**
- ✅ Email envoyé au **partenaire** du projet
- ✅ Notification push (si FCM configuré)
- ✅ Envoi **asynchrone** (non-bloquant)

---

## 📞 Support et Ressources

### Fichiers Disponibles

1. **Collection Postman** : `Datalys_Consulting_API_Collection_Complete.json`
2. **Environnement** : `Datalys_Environment_Production.json`
3. **Guide de test** : `docs/GUIDE_TEST_API.md`
4. **Résumé des routes** : `API_ROUTES_SUMMARY.md`
5. **Cette documentation** : `DOCUMENTATION_API_COMPLETE.md`

### Utilisateurs de Test

| Nom | Email | Code Client | Mot de Passe | Rôle | MFA |
|-----|-------|-------------|--------------|------|-----|
| Pedini Nonsse | nonssekone@gmail.com | null | Password123 | Admin | ❌ |
| Administrateur | admin@datalys.com | null | Admin@123 | Admin | ✅ |
| Marie Martin | marie.martin@datalys.com | DATALYS-2025-003 | Test@123 | User | ✅ |

### Configuration

- **Base URL** : `http://82.112.253.137:8082`
- **CORS** : `https://applicationweb.datalysconsulting.com`
- **Rate Limiting** : 5 tentatives de login / 15 minutes
- **Upload** : Limite de 50MB par fichier
- **Token JWT** : Validité de 2 heures

---

## 🎉 Conclusion

Cette documentation couvre toutes les APIs disponibles dans Datalys Consulting v2.0.0.

**Prochaines étapes** :
1. Importer la collection Postman
2. Tester les endpoints avec les exemples cURL
3. Intégrer les APIs dans votre frontend

**Bon développement ! 🚀**

---

**Dernière mise à jour** : 9 Octobre 2025  
**Version** : 2.0.0  
**Auteur** : Équipe Datalys Consulting

