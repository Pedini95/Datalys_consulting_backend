# 🎯 APIs Prêtes pour l'Intégration Frontend

## 📋 Guide d'Intégration avec Payloads Complets - Datalys Consulting

---

## **🔐 1. AUTHENTIFICATION (Priorité 1)**

### **🚪 POST /auth/login**
```javascript
// Requête
POST http://82.112.253.137:8082/auth/login
Content-Type: application/json

{
    "email": "admin@datalysconsulting.com",
    "password": "password123"
}

// Réponse Succès
{
    "status": "success",
    "message": "Connexion réussie",
    "data": {
        "id": 1,
        "name": "Admin User",
        "email": "admin@datalysconsulting.com",
        "role_id": 1,
        "is_active": true,
        "created_at": "2025-08-12T20:42:22",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}

// Réponse Erreur
{
    "status": "error",
    "message": "Email ou mot de passe incorrect"
}
```

### **🚪 POST /auth/logout**
```javascript
// Requête
POST http://82.112.253.137:8082/auth/logout
Authorization: Bearer <token>

// Réponse
{
    "status": "success",
    "message": "Déconnexion réussie"
}
```

### **🔑 POST /auth/reset-password-request**
```javascript
// Requête
POST http://82.112.253.137:8082/auth/reset-password-request
Content-Type: application/json

{
    "email": "user@example.com"
}

// Réponse
{
    "status": "success",
    "message": "Email de réinitialisation envoyé"
}
```

---

## **👑 2. APIs ADMIN - Payloads Détaillés**

### **👥 GESTION UTILISATEURS**

#### **📋 POST /users/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/users/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 10,
    "data": {
        "is_active": true,
        "role_id": 1,
        "email": "admin@"  // Recherche partielle
    }
}

// Réponse
{
    "items": [
        {
            "id": 1,
            "name": "Admin User",
            "email": "admin@datalysconsulting.com",
            "role_id": 1,
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-12T20:42:22",
            "created_by": "1",
            "updated_at": "2025-08-12T20:42:22",
            "updated_by": "1",
            "username": "Admin User"
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

#### **✅ POST /users/create**
```javascript
// Requête
POST http://82.112.253.137:8082/users/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "name": "Nouvel Utilisateur",
    "email": "nouveau@datalysconsulting.com",
    "password": "password123",
    "role_id": 2,
    "is_active": true
}

// Réponse Succès
{
    "code": 200,
    "items": [
        {
            "id": 5,
            "name": "Nouvel Utilisateur",
            "email": "nouveau@datalysconsulting.com",
            "role_id": 2,
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-16T23:45:00",
            "created_by": 1,
            "updated_at": "2025-08-16T23:45:00",
            "updated_by": 1
        }
    ],
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

#### **📝 POST /users/update**
```javascript
// Requête
POST http://82.112.253.137:8082/users/update
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "id": 5,
    "name": "Utilisateur Modifié",
    "email": "modifie@datalysconsulting.com",
    "is_active": false
}

// Réponse
{
    "code": 200,
    "items": [
        {
            "id": 5,
            "name": "Utilisateur Modifié",
            "email": "modifie@datalysconsulting.com",
            "is_active": false,
            "updated_at": "2025-08-16T23:50:00",
            "updated_by": 1
        }
    ],
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

#### **🗑️ POST /users/delete**
```javascript
// Requête
POST http://82.112.253.137:8082/users/delete
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "id": 5
}

// Réponse
{
    "code": 200,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

---

### **🤝 GESTION PARTENAIRES**

#### **📋 POST /partners/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/partners/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 10,
    "data": {
        "is_active": true,
        "name": "momo"  // Recherche partielle
    }
}

// Réponse
{
    "items": [
        {
            "id": 10,
            "name": "momo",
            "email": "momo@mtn.com",
            "phone": "+2310909090",
            "address": "bypass monrovia",
            "logo_url": "http://82.112.253.137:8082/files/serve/logos/20250816_234246_9b7001f4-dc51-4317-bb0b-87ab77cd0699.png",
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-16T23:42:47",
            "created_by": 7,
            "updated_at": "2025-08-16T23:42:47",
            "updated_by": 7
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

#### **✅ POST /partners/create**
```javascript
// Requête (multipart/form-data)
POST http://82.112.253.137:8082/partners/create
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

data: {
    "name": "Nouveau Partenaire",
    "email": "partner@example.com",
    "phone": "+1234567890",
    "address": "123 Business Street",
    "is_active": true
}
user: {
    "id": 1
}
logo: <fichier_image>  // Optionnel

// Réponse
{
    "code": 200,
    "items": [
        {
            "id": 11,
            "name": "Nouveau Partenaire",
            "email": "partner@example.com",
            "phone": "+1234567890",
            "address": "123 Business Street",
            "logo_url": "http://82.112.253.137:8082/files/serve/logos/20250817_000000_uuid.png",
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-17T00:00:00",
            "created_by": 1,
            "updated_at": "2025-08-17T00:00:00",
            "updated_by": 1
        }
    ],
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

---

### **📋 GESTION PROJETS**

#### **📋 POST /projects/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/projects/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 10,
    "data": {
        "is_active": true,
        "partner_id": 10
    }
}

// Réponse
{
    "items": [
        {
            "id": 2,
            "name": "Projet Consulting",
            "description": "Projet de conseil stratégique",
            "partner_id": 10,
            "status": "en_cours",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-16T15:30:00",
            "created_by": 1,
            "updated_at": "2025-08-16T15:30:00",
            "updated_by": 1
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

#### **✅ POST /projects/create**
```javascript
// Requête
POST http://82.112.253.137:8082/projects/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "name": "Nouveau Projet",
    "description": "Description du projet",
    "partner_id": 10,
    "status": "planifie",
    "start_date": "2025-02-01",
    "end_date": "2025-11-30",
    "budget": 50000,
    "is_active": true
}

// Réponse
{
    "code": 200,
    "items": [
        {
            "id": 3,
            "name": "Nouveau Projet",
            "description": "Description du projet",
            "partner_id": 10,
            "status": "planifie",
            "start_date": "2025-02-01",
            "end_date": "2025-11-30",
            "budget": 50000,
            "is_active": true,
            "created_at": "2025-08-17T00:05:00",
            "created_by": 1
        }
    ],
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

---

### **📁 GESTION DOSSIERS**

#### **📋 POST /folders/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/folders/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 20,
    "data": {
        "project_id": 2,
        "is_active": true
    }
}

// Réponse
{
    "items": [
        {
            "id": 1,
            "name": "Documents Contrats",
            "description": "Dossier des contrats clients",
            "project_id": 2,
            "parent_folder_id": null,
            "path": "/Documents Contrats",
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-16T16:00:00",
            "created_by": 1,
            "updated_at": "2025-08-16T16:00:00",
            "updated_by": 1
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

#### **✅ POST /folders/create**
```javascript
// Requête
POST http://82.112.253.137:8082/folders/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "name": "Nouveau Dossier",
    "description": "Description du dossier",
    "project_id": 2,
    "parent_folder_id": 1,
    "is_active": true
}

// Réponse
{
    "code": 200,
    "items": [
        {
            "id": 4,
            "name": "Nouveau Dossier",
            "description": "Description du dossier",
            "project_id": 2,
            "parent_folder_id": 1,
            "path": "/Documents Contrats/Nouveau Dossier",
            "is_active": true,
            "created_at": "2025-08-17T00:10:00",
            "created_by": 1
        }
    ],
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

---

### **📄 GESTION FICHIERS**

#### **📋 POST /files/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/files/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 20,
    "data": {
        "project_id": 2,
        "folder_id": 1,
        "is_active": true
    }
}

// Réponse
{
    "items": [
        {
            "id": 1,
            "name": "contrat_client_v1.pdf",
            "original_name": "Contrat Client Final.pdf",
            "file_path": "/static/files/documents/20250816_160000_uuid.pdf",
            "file_url": "http://82.112.253.137:8082/files/serve/documents/20250816_160000_uuid.pdf",
            "file_size": 2048576,
            "mime_type": "application/pdf",
            "project_id": 2,
            "folder_id": 1,
            "description": "Contrat principal du client",
            "tags": ["contrat", "legal"],
            "is_active": true,
            "is_deleted": false,
            "created_at": "2025-08-16T16:00:00",
            "created_by": 1,
            "updated_at": "2025-08-16T16:00:00",
            "updated_by": 1
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

#### **⬆️ POST /files/upload**
```javascript
// Requête (multipart/form-data)
POST http://82.112.253.137:8082/files/upload
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

file: <fichier>
project_id: "2"
folder_id: "1"
description: "Document important"
tags: "contrat,client"

// Réponse
{
    "status": "success",
    "message": "Fichier uploadé avec succès",
    "data": {
        "file_id": 2,
        "file_path": "/static/files/documents/20250817_001500_uuid.pdf",
        "file_url": "http://82.112.253.137:8082/files/serve/documents/20250817_001500_uuid.pdf",
        "filename": "20250817_001500_uuid.pdf",
        "original_name": "document.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf"
    }
}
```

#### **⬇️ GET /files/download/{file_id}**
```javascript
// Requête
GET http://82.112.253.137:8082/files/download/1
Authorization: Bearer <admin_token>

// Réponse : Fichier binaire avec headers
Content-Type: application/pdf
Content-Disposition: attachment; filename="contrat_client_v1.pdf"
Content-Length: 2048576
```

#### **🔗 GET /files/serve/{filename}**
```javascript
// Requête
GET http://82.112.253.137:8082/files/serve/documents/20250816_160000_uuid.pdf

// Réponse : Fichier servi directement
Content-Type: application/pdf
Content-Length: 2048576
Cache-Control: no-cache
```

---

### **🚨 GESTION INCIDENTS**

#### **📋 POST /incidents/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/incidents/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 10,
    "data": {
        "status": "ouvert",
        "priority": "haute"
    }
}

// Réponse
{
    "items": [
        {
            "id": 1,
            "title": "Problème d'accès aux documents",
            "description": "Impossible d'accéder aux fichiers du projet",
            "status": "ouvert",
            "priority": "haute",
            "category": "technique",
            "project_id": 2,
            "user_id": 7,
            "assigned_to": 1,
            "resolution_notes": null,
            "is_active": true,
            "created_at": "2025-08-16T18:00:00",
            "updated_at": "2025-08-16T18:00:00"
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

#### **✅ POST /incidents/create**
```javascript
// Requête
POST http://82.112.253.137:8082/incidents/create
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "title": "Nouveau problème",
    "description": "Description détaillée du problème",
    "priority": "moyenne",
    "category": "fonctionnel",
    "project_id": 2,
    "user_id": 7
}

// Réponse
{
    "code": 200,
    "items": [
        {
            "id": 2,
            "title": "Nouveau problème",
            "description": "Description détaillée du problème",
            "status": "ouvert",
            "priority": "moyenne",
            "category": "fonctionnel",
            "project_id": 2,
            "user_id": 7,
            "created_at": "2025-08-17T00:20:00",
            "created_by": 1
        }
    ],
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    }
}
```

---

## **🤝 3. APIs PARTENAIRE - Payloads avec Filtrage**

### **📊 Consultation MES Projets (Partenaire)**
```javascript
// Requête (même API mais filtrée automatiquement)
POST http://82.112.253.137:8082/projects/getByCriteria
Authorization: Bearer <partner_token>
Content-Type: application/json

{
    "index": 0,
    "size": 10,
    "data": {
        "is_active": true
    }
}

// Réponse (SEULEMENT les projets du partenaire connecté)
{
    "items": [
        {
            "id": 2,
            "name": "MON Projet Consulting",
            "description": "Mon projet en cours",
            "partner_id": 10,  // ID du partenaire connecté
            "status": "en_cours",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "is_active": true,
            "created_at": "2025-08-16T15:30:00"
        }
    ],
    "count": 1,  // Seulement SES projets
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

### **📁 Consultation MES Dossiers (Partenaire)**
```javascript
// Requête
POST http://82.112.253.137:8082/folders/getByCriteria
Authorization: Bearer <partner_token>
Content-Type: application/json

{
    "index": 0,
    "size": 20,
    "data": {
        "is_active": true
    }
}

// Réponse (SEULEMENT les dossiers de SES projets)
{
    "items": [
        {
            "id": 1,
            "name": "MES Documents",
            "project_id": 2,  // Projet du partenaire
            "path": "/MES Documents",
            "is_active": true,
            "created_at": "2025-08-16T16:00:00"
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

---

## **📊 4. APIs MONITORING**

### **🔋 GET /health**
```javascript
// Requête
GET http://82.112.253.137:8082/health

// Réponse
{
    "status": "healthy",
    "timestamp": null,
    "database": {
        "status": "connected",
        "version": "8.0.43",
        "tables_count": 9,
        "error": null
    },
    "application": {
        "status": "running",
        "version": "1.0.0"
    }
}
```

### **🔧 GET /api/sessions/health**
```javascript
// Requête
GET http://82.112.253.137:8082/api/sessions/health

// Réponse
{
    "message": "État du système de sessions",
    "redis_status": "✅ Connecté",
    "session_manager_ready": true
}
```

---

## **📈 5. APIs HISTORIQUE**

### **📋 POST /action_history/getByCriteria**
```javascript
// Requête
POST http://82.112.253.137:8082/action_history/getByCriteria
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "index": 0,
    "size": 50,
    "data": {
        "user_id": 1,
        "action_type": "CREATE",
        "entity_type": "Partner"
    }
}

// Réponse
{
    "items": [
        {
            "id": 1,
            "user_id": 1,
            "action_type": "CREATE",
            "entity_type": "Partner",
            "entity_id": 10,
            "description": "Création du partenaire 'momo'",
            "ip_address": "102.214.136.50",
            "user_agent": "PostmanRuntime/7.45.0",
            "created_at": "2025-08-16T23:42:47"
        }
    ],
    "count": 1,
    "message": {
        "code": 200,
        "message": "OPERATION SUCCESSFULLY"
    },
    "code": 200
}
```

---

# 🔒 GESTION DES ERREURS COMMUNES

## **Erreurs d'Authentification :**
```javascript
// Token manquant
{
    "status": "error",
    "message": "Token d'authentification manquant"
}

// Token invalide
{
    "status": "error", 
    "message": "Session expirée ou invalide"
}

// Permissions insuffisantes
{
    "status": "error",
    "message": "Action non autorisée"
}
```

## **Erreurs de Validation :**
```javascript
// Données manquantes
{
    "status": "error",
    "message": "Champs requis manquants: name, email"
}

// Contraintes de validation
{
    "status": "error",
    "message": "Un partenaire avec l'email 'test@example.com' existe déjà"
}

// Fichier trop volumineux
{
    "status": "error",
    "message": "Fichier trop volumineux. Taille max: 50MB"
}
```

---

# ✅ CONCLUSION

## **🎉 APIs Prêtes avec Payloads Complets !**

Toutes les APIs sont documentées avec :
- ✅ **URLs complètes** avec serveur de production
- ✅ **Headers requis** (Authorization, Content-Type)  
- ✅ **Payloads d'exemple** pour toutes les requêtes
- ✅ **Réponses détaillées** avec structure complète
- ✅ **Gestion d'erreurs** communes
- ✅ **Filtrage automatique** pour les partenaires

## **🚀 Ready to Code !**

L'équipe frontend peut maintenant :
1. **Commencer l'intégration** immédiatement
2. **Copier/coller** les exemples de requêtes
3. **Adapter** les payloads selon les besoins
4. **Tester** avec les données réelles du serveur

---

*Document complet pour l'équipe Frontend*  
*Serveur : http://82.112.253.137:8082*  
*Version : 2.0*  
*Date : Août 2025* 