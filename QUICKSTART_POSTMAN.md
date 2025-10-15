# 🚀 Quick Start - Collection Postman

## En 3 étapes simples

### 1️⃣ Importer la collection
```
Postman → Import → Sélectionner "Datalys_Consulting_API.postman_collection.json"
```

### 2️⃣ Tester l'authentification
```
1. Exécuter: "1. Authentication > Login"
   → Code MFA envoyé par email

2. Vérifier votre email et copier le code (6 chiffres)

3. Exécuter: "1. Authentication > Verify MFA"
   → Token JWT stocké automatiquement ✅
```

### 3️⃣ Tester n'importe quelle route
```
Toutes les routes utilisent automatiquement le token.
Exemple:
- "3. Incidents > Get Incidents By Criteria"
- "4. Dashboard > Dashboard Client"
- "3. Incidents > Export Incidents - PDF"
```

---

## 📋 Structure de la collection

```
├── 1. Authentication (Login, MFA, Logout)
├── 2. Users (CRUD utilisateurs)
├── 3. Incidents (CRUD + Export + Refus solution)
│   ├── Get Metadata
│   ├── Get/Create/Update/Delete
│   ├── Upload File / Get Files
│   ├── Refuse Solution
│   └── Export CSV/Excel/PDF ⭐ NOUVEAU
├── 4. Dashboard (Client, Partner, Admin)
├── 5. Partners (CRUD)
├── 6. Projects (CRUD)
├── 7. Files (Upload, Liste)
└── 8. Health Check
```

---

## 🎯 Exemples rapides

### Créer un incident
```json
POST /incidents/create
{
  "user": {"id": 1},
  "datas": [{
    "title": "Problème urgent",
    "priority": "P1",
    "domain": "reseau"
  }]
}
```

### Exporter en PDF (Admin/Manager)
```json
POST /incidents/export
{
  "format": "pdf",
  "include_stats": true
}
```

### Dashboard client
```json
POST /dashboard/client
{
  "user": {"id": 1}
}
```

---

## ⚡ Variables auto-configurées

- ✅ `{{base_url}}` = http://82.112.253.137:8082
- ✅ `{{token}}` = Rempli après MFA
- ✅ `{{user_id}}` = Rempli après login
- ✅ `{{incident_id}}` = Rempli après création

**Aucune configuration manuelle nécessaire !**

---

## 🔐 Contrôles d'accès

| Route | Qui peut accéder ? |
|-------|--------------------|
| Export rapports | Admin + Manager |
| Delete incident | Admin + Manager |
| Create/Delete user | Admin uniquement |
| Refuse solution | Client créateur uniquement |
| Dashboard client | Tous |

---

## 📞 Aide

Voir le guide complet : `GUIDE_POSTMAN_COLLECTION.md`

**Base URL :** http://82.112.253.137:8082
