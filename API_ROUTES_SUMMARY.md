# 📋 Résumé des Routes API - Datalys Consulting

**Date** : 9 Octobre 2025  
**Base URL** : `http://82.112.253.137:8082`

---

## ✅ Routes Testées et Fonctionnelles

### 🔐 Authentication (Pas d'auth requise)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| POST | `/auth/login` | Login avec email ou code client | `{"identifier": "email ou code", "password": "..."}` |
| POST | `/auth/verify-mfa` | Vérifier code MFA | `{"user_id": 1, "mfa_code": "123456"}` |
| POST | `/auth/change-temp-password` | Changer mot de passe temporaire | `{"email": "...", "old_password": "...", "new_password": "..."}` |
| POST | `/auth/logout` | Déconnexion | - |

### 🏥 Health Check (Pas d'auth requise)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/health` | État de santé de l'API |

### 🚨 Incidents (Auth requise)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| GET | `/incidents/metadata` | Métadonnées P0-P4, statuts, impacts | - |
| POST | `/incidents/getByCriteria` | Liste des incidents | `{"criteria": {}, "index": 0, "size": 10}` |
| POST | `/incidents/create` | Créer un incident | `{"title": "...", "priority": "P0", ...}` |
| POST | `/incidents/update` | Modifier un incident | `{"id": 1, "status": "en_cours", ...}` |
| POST | `/incidents/delete` | Supprimer un incident | `{"id": 1}` |

### 👤 Users (Auth requise)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| POST | `/users/getByCriteria` | Liste des utilisateurs | `{"criteria": {}, "index": 0, "size": 10}` |
| POST | `/users/create` | Créer un utilisateur | `{"name": "...", "email": "...", "password": "...", "role_name": "User"}` |
| POST | `/users/update` | Modifier un utilisateur | `{"id": 1, "name": "...", ...}` |
| POST | `/users/delete` | Supprimer un utilisateur | `{"id": 1}` |

### 👑 Roles (Auth requise)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| POST | `/roles/getByCriteria` | Liste des rôles | `{"criteria": {}, "index": 0, "size": 10}` |
| POST | `/roles/create` | Créer un rôle | `{"name": "...", "permissions": [...]}` |

### 🏢 Partners (Auth requise)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| POST | `/partners/getByCriteria` | Liste des partenaires | `{"criteria": {}, "index": 0, "size": 10}` |
| POST | `/partners/create` | Créer un partenaire | `{"name": "...", "email": "...", ...}` |
| POST | `/partners/update` | Modifier un partenaire | `{"id": 1, "name": "...", ...}` |
| POST | `/partners/delete` | Supprimer un partenaire | `{"id": 1}` |

### 📁 Projects (Auth requise)

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| POST | `/projects/getByCriteria` | Liste des projets | `{"criteria": {}, "index": 0, "size": 10}` |
| POST | `/projects/create` | Créer un projet | `{"title": "...", "partner_id": 1, ...}` |
| POST | `/projects/update` | Modifier un projet | `{"id": 1, "title": "...", ...}` |
| POST | `/projects/delete` | Supprimer un projet | `{"id": 1}` |

### 📊 Dashboard (Auth requise)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/dashboard` | Statistiques du dashboard |

---

## 🔑 Format d'Authentification

**Header** :
```
Authorization: Bearer <token>
```

**Obtenir un token** :
```bash
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}'
```

---

## 📝 Exemples cURL

### 1. Login
```bash
curl -X POST http://82.112.253.137:8082/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "nonssekone@gmail.com", "password": "Password123"}'
```

### 2. Métadonnées Incidents (P0-P4)
```bash
TOKEN="votre_token_ici"
curl -X GET http://82.112.253.137:8082/incidents/metadata \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Créer un Incident P0
```bash
TOKEN="votre_token_ici"
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
```

### 4. Liste des Utilisateurs
```bash
TOKEN="votre_token_ici"
curl -X POST http://82.112.253.137:8082/users/getByCriteria \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"criteria": {}, "index": 0, "size": 10}'
```

### 5. Créer un Partenaire (avec code client auto)
```bash
TOKEN="votre_token_ici"
curl -X POST http://82.112.253.137:8082/users/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouveau Partenaire",
    "email": "nouveau.partenaire@example.com",
    "password": "Test@123",
    "role_name": "User",
    "is_active": true,
    "is_temp_password": false
  }'
```

---

## 🆕 Nouvelles Fonctionnalités Implémentées

### 1. Code Client Unique ✅
- **Format** : `DATALYS-YYYY-NNN` (ex: `DATALYS-2025-003`)
- **Pour qui** : Uniquement les partenaires (rôle "User")
- **Avantage** : Login possible avec email OU code client

### 2. Système P0-P4 ✅
- **P0** : Arrêt de service (immédiat) 🔴
- **P1** : Forte dégradation de service 🟠
- **P2** : Dégradation de service 🟡
- **P3** : Incident ordinaire 🔵
- **P4** : Incident mineur 🟢

### 3. Numéro d'Incident Auto-généré ✅
- **Format** : `INC-YYYY-NNNNN` (ex: `INC-2025-00001`)
- **Automatique** : Généré à la création

### 4. MFA par Email ✅
- **Code à 6 chiffres** envoyé par email
- **Valide 5 minutes**
- **3 tentatives maximum**
- **Envoi asynchrone** (~1.7s en arrière-plan)

### 5. Notifications Automatiques ✅
- Email aux **Admin/Manager** lors de création d'incident
- Email au **partenaire** du projet
- Notification **push** (si FCM configuré)

---

## 📁 Fichiers Disponibles

1. **Collection Postman** : `Datalys_Consulting_API_Collection_Complete.json`
2. **Environnement** : `Datalys_Environment_Production.json`
3. **Guide complet** : `docs/GUIDE_TEST_API.md`
4. **Ce résumé** : `API_ROUTES_SUMMARY.md`

---

## 🎯 Utilisateurs de Test

| Nom | Email | Code Client | Mot de Passe | Rôle | MFA |
|-----|-------|-------------|--------------|------|-----|
| Pedini Nonsse | nonssekone@gmail.com | null | Password123 | Admin | ❌ Désactivé |
| Administrateur | admin@datalys.com | null | Admin@123 | Admin | ✅ Activé |
| Marie Martin | marie.martin@datalys.com | DATALYS-2025-003 | Test@123 | User | ✅ Activé |

---

## 🔧 Notes Importantes

1. **Format des routes** : La plupart des routes utilisent `/resource/action` (ex: `/users/getByCriteria`)
2. **Authentification** : Toutes les routes sauf `/auth/*` et `/health` nécessitent un token JWT
3. **CORS** : Configuré pour `https://applicationweb.datalysconsulting.com`
4. **Rate Limiting** : 5 tentatives de login par 15 minutes
5. **Upload** : Limite de 50MB par fichier

---

**Dernière mise à jour** : 9 Octobre 2025  
**Version API** : 2.0.0

