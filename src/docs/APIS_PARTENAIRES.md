# 📡 APIs Partenaires - Documentation Complète

## 🎯 Vue d'ensemble

Ce document décrit toutes les APIs liées à la gestion des partenaires, incluant la création automatique de comptes utilisateurs et l'envoi d'emails avec credentials.

## 🔐 Authentification

Toutes les APIs nécessitent un token JWT valide dans le header :
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 1. 📝 Création de Partenaires

### **POST /partners/create**

**Description :** Crée un ou plusieurs partenaires avec comptes utilisateurs automatiques et envoi d'email avec credentials.

**URL :** `http://localhost:5000/partners/create`

**Headers :**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Payload :**
```json
{
  "user": {"id": 1},
  "datas": [{
    "name": "TechCorp",
    "email": "contact@techcorp.com",
    "phone": "+1234567890",
    "address": "123 Tech Street, City"
  }]
}
```

**Champs :**
- **user.id** (obligatoire) : ID de l'utilisateur qui crée
- **datas** (obligatoire) : Liste des partenaires à créer
  - **name** (obligatoire) : Nom du partenaire (2-255 caractères)
  - **email** (optionnel) : Email du partenaire (format valide, max 255 caractères)
  - **phone** (optionnel) : Téléphone (min 10 chiffres, max 50 caractères)
  - **address** (optionnel) : Adresse (5-1000 caractères)

**Validations :**
- ✅ Nom obligatoire et valide
- ✅ Email format valide si fourni
- ✅ Téléphone avec au moins 10 chiffres si fourni
- ✅ Adresse avec au moins 5 caractères si fournie
- ✅ `is_active` automatiquement initialisé à `true`

**Résultat automatique :**
- ✅ Partenaire créé dans table `partners`
- ✅ Utilisateur créé dans table `users` avec rôle 'partner'
- ✅ Email envoyé avec credentials de connexion
- ✅ Mot de passe temporaire généré automatiquement

**Réponse succès (200) :**
```json
{
  "items": [
    {
      "id": 1,
      "name": "TechCorp",
      "email": "contact@techcorp.com",
      "phone": "+1234567890",
      "address": "123 Tech Street, City",
      "is_active": true,
      "created_at": "2025-01-17T10:30:00"
    }
  ],
  "message": "Opération réussie",
  "code": 200
}
```

**Erreurs possibles :**
- `400` : Validation des champs échouée
- `401` : Token d'authentification invalide
- `500` : Erreur interne du serveur

---

## 2. 🖼️ Upload de Logo Partenaire

### **POST /partners/upload-logo/{partner_id}**

**Description :** Upload ou remplace le logo d'un partenaire existant.

**URL :** `http://localhost:5000/partners/upload-logo/{partner_id}`

**Headers :**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data
```

**Payload :**
```
logo: [fichier image]
```

**Permissions :**
- ✅ **Admin** : Peut uploader le logo de n'importe quel partenaire
- ✅ **Partenaire** : Peut uploader son propre logo

**Réponse succès (200) :**
```json
{
  "partner": {
    "id": 1,
    "name": "TechCorp",
    "logo_url": "/static/files/logos/logo_techcorp.png",
    "is_active": true
  },
  "message": "Logo mis à jour avec succès",
  "code": 200
}
```

**Erreurs possibles :**
- `400` : Aucun fichier logo fourni
- `403` : Accès non autorisé
- `404` : Partenaire non trouvé
- `500` : Erreur interne du serveur

---

## 3. 📊 Dashboard Partenaire

### **GET /dashboard/partner/{partner_id}**

**Description :** Récupère le dashboard complet d'un partenaire avec statistiques et données récentes.

**URL :** `http://localhost:5000/dashboard/partner/{partner_id}`

**Headers :**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Permissions :**
- ✅ **Admin** : Accès à tous les dashboards partenaires
- ✅ **Partenaire** : Accès seulement à son propre dashboard

**Réponse succès (200) :**
```json
{
  "code": 200,
  "data": {
    "partner_id": 1,
    "summary": {
      "total_projects": 5,
      "total_incidents": 12,
      "total_files": 25,
      "active_projects": 3,
      "open_incidents": 4
    },
    "projects": [...],
    "recent_incidents": [...],
    "incident_stats": {
      "total": 12,
      "by_status": {"ouvert": 4, "en_cours": 3, "resolu": 5},
      "by_priority": {"haute": 2, "moyenne": 8, "basse": 2}
    },
    "recent_files": [...],
    "activity_summary": {...}
  },
  "message": "Opération réussie"
}
```

---

## 4. 📋 Projets d'un Partenaire

### **POST /dashboard/partner/{partner_id}/projects**

**Description :** Récupère tous les projets d'un partenaire avec pagination et filtres.

**URL :** `http://localhost:5000/dashboard/partner/{partner_id}/projects`

**Headers :**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Payload :**
```json
{
  "index": 0,
  "size": 20,
  "data": {
    "is_active": true,
    "name": "nom_projet"
  }
}
```

**Champs :**
- **index** (optionnel) : Position de départ (défaut: 0)
- **size** (optionnel) : Nombre d'éléments par page (défaut: 20)
- **data** (optionnel) : Filtres
  - **is_active** : Filtrer par statut actif
  - **name** : Recherche par nom de projet

**Réponse succès (200) :**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Projet E-commerce",
      "is_active": true,
      "created_at": "2025-01-15T09:00:00"
    }
  ],
  "count": 5,
  "message": "Opération réussie",
  "code": 200
}
```

---

## 5. 🚨 Incidents d'un Partenaire

### **POST /dashboard/partner/{partner_id}/incidents**

**Description :** Récupère tous les incidents d'un partenaire avec pagination et filtres.

**URL :** `http://localhost:5000/dashboard/partner/{partner_id}/incidents`

**Headers :**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Payload :**
```json
{
  "index": 0,
  "size": 20,
  "data": {
    "status": "ouvert",
    "priority": "haute",
    "type": "bug"
  }
}
```

**Champs :**
- **index** (optionnel) : Position de départ (défaut: 0)
- **size** (optionnel) : Nombre d'éléments par page (défaut: 20)
- **data** (optionnel) : Filtres
  - **status** : Filtrer par statut (ouvert, en_cours, resolu, ferme)
  - **priority** : Filtrer par priorité (basse, moyenne, haute, critique)
  - **type** : Filtrer par type (incident, message, support, notification)

**Réponse succès (200) :**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Bug critique détecté",
      "status": "ouvert",
      "priority": "haute",
      "type": "incident",
      "created_at": "2025-01-17T10:30:00"
    }
  ],
  "count": 12,
  "message": "Opération réussie",
  "code": 200
}
```

---

## 6. 👨‍💼 Dashboard Admin

### **GET /dashboard/admin/overview**

**Description :** Dashboard global pour administrateurs avec vue d'ensemble de toute la plateforme.

**URL :** `http://localhost:5000/dashboard/admin/overview`

**Headers :**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Permissions :**
- ✅ **Admin uniquement** : Accès restreint aux administrateurs

**Réponse succès (200) :**
```json
{
  "code": 200,
  "data": {
    "global_summary": {
      "total_projects": 25,
      "total_incidents": 150,
      "total_files": 300,
      "active_projects": 18,
      "open_incidents": 45,
      "critical_incidents": 8
    },
    "partner_stats": [
      {
        "partner_id": 1,
        "partner_name": "TechCorp",
        "total_projects": 5,
        "active_projects": 3
      }
    ],
    "incident_priority_stats": {
      "critique": 8,
      "haute": 25,
      "moyenne": 85,
      "basse": 32
    },
    "recent_projects": [...],
    "recent_incidents": [...],
    "recent_activity": [...]
  },
  "message": "Opération réussie"
}
```

---

## 📧 Email Automatique

### **Contenu de l'email envoyé automatiquement :**

**Sujet :** `🎉 Bienvenue chez Datalys Consulting - Vos identifiants de connexion`

**Contenu :**
- **En-tête** : Logo et message de bienvenue
- **Identifiants** : Email, nom d'utilisateur, mot de passe temporaire
- **Bouton de connexion** : Lien direct vers la page de connexion
- **Instructions de sécurité** : Recommandations importantes
- **Fonctionnalités** : Liste des possibilités une fois connecté

**Sécurité :**
- Mot de passe temporaire généré automatiquement
- Recommandation de changement lors de la première connexion
- Avertissements de sécurité inclus

---

## 🔐 Sécurité et Permissions

### **Rôles et Accès :**

| API | Admin | Partner | User |
|-----|-------|---------|------|
| `/partners/create` | ✅ | ❌ | ❌ |
| `/partners/upload-logo/{id}` | ✅ | ✅ (son propre) | ❌ |
| `/dashboard/partner/{id}` | ✅ | ✅ (son propre) | ❌ |
| `/dashboard/partner/{id}/projects` | ✅ | ✅ (son propre) | ❌ |
| `/dashboard/partner/{id}/incidents` | ✅ | ✅ (son propre) | ❌ |
| `/dashboard/admin/overview` | ✅ | ❌ | ❌ |

### **Validation des données :**
- ✅ **Côté serveur** : Validation complète de tous les champs
- ✅ **Nettoyage automatique** : Suppression des espaces inutiles
- ✅ **Messages d'erreur clairs** : Indication précise des problèmes
- ✅ **Protection contre les injections** : Validation des types et formats

---

## 🚀 Exemples d'utilisation

### **1. Créer un partenaire :**
```bash
curl -X POST http://localhost:5000/partners/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"id": 1},
    "datas": [{
      "name": "TechCorp",
      "email": "contact@techcorp.com",
      "phone": "+1234567890",
      "address": "123 Tech Street, City"
    }]
  }'
```

### **2. Uploader un logo :**
```bash
curl -X POST http://localhost:5000/partners/upload-logo/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "logo=@/path/to/logo.png"
```

### **3. Consulter le dashboard partenaire :**
```bash
curl -X GET http://localhost:5000/dashboard/partner/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Notes Techniques

### **Base de données :**
- **Table `partners`** : Informations du partenaire
- **Table `users`** : Compte utilisateur avec rôle 'partner'
- **Liaison** : Via email commun entre partenaire et utilisateur

### **Workflow automatique :**
1. **Création partenaire** → Validation des données
2. **Génération mot de passe** → Cryptographiquement sécurisé
3. **Création utilisateur** → Avec rôle 'partner'
4. **Envoi email** → Avec credentials de connexion
5. **Accès dashboard** → Interface partenaire personnalisée

### **Gestion des erreurs :**
- **Rollback automatique** : En cas d'échec, suppression des données créées
- **Logs détaillés** : Traçabilité complète des opérations
- **Messages d'erreur** : Clairs et informatifs pour le débogage

---

## ✅ Statut des APIs

| API | Statut | Description |
|-----|--------|-------------|
| `/partners/create` | ✅ **Implémentée** | Création avec validation complète |
| `/partners/upload-logo/{id}` | ✅ **Implémentée** | Upload de logo avec permissions |
| `/dashboard/partner/{id}` | ✅ **Implémentée** | Dashboard partenaire complet |
| `/dashboard/partner/{id}/projects` | ✅ **Implémentée** | Projets avec pagination |
| `/dashboard/partner/{id}/incidents` | ✅ **Implémentée** | Incidents avec pagination |
| `/dashboard/admin/overview` | ✅ **Implémentée** | Dashboard admin global |

**Toutes les APIs sont opérationnelles et prêtes à l'utilisation !** 🎉 