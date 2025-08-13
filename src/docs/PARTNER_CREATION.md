# 🏢 API de Création de Partenaires avec Logo Intégré

## 📋 Vue d'ensemble

L'API `POST /partners/create` supporte maintenant **deux modes de fonctionnement** :

1. **Mode JSON** : Création classique avec données JSON
2. **Mode Multipart** : Création avec upload de logo intégré

## 🔧 Fonctionnalités

### ✅ **Fonctionnalités Implémentées**

- ✅ **Détection automatique** du type de requête
- ✅ **Upload de logo intégré** dans la création
- ✅ **Validation des images** (PNG, JPG, JPEG, GIF)
- ✅ **Gestion d'erreurs** avec rollback automatique
- ✅ **Rétrocompatibilité** avec l'API existante
- ✅ **Logs détaillés** pour le debugging
- ✅ **Authentification requise** (`@require_auth`)

### 🎯 **Avantages**

- **Workflow simplifié** : Une seule requête au lieu de deux
- **Expérience utilisateur améliorée** : Moins de complexité côté frontend
- **Atomicité** : Soit tout réussit, soit tout échoue
- **Moins de gestion d'état** côté client

## 📡 Endpoints

### **POST /partners/create**

**URL :** `http://localhost:5000/partners/create`

**Headers requis :**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## 🔄 Modes de Fonctionnement

### **Mode 1 : JSON Classique**

**Content-Type :** `application/json`

**Payload :**
```json
{
  "user": {"id": 1},
  "datas": [{
    "name": "TechCorp",
    "email": "contact@techcorp.com",
    "phone": "+1234567890",
    "address": "123 Tech Street, City",
    "logo_url": "https://example.com/logo.png",
    "is_active": true
  }]
}
```

**Exemple avec cURL :**
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
      "address": "123 Tech Street, City",
      "logo_url": "https://example.com/logo.png",
      "is_active": true
    }]
  }'
```

### **Mode 2 : Multipart avec Logo Intégré**

**Content-Type :** `multipart/form-data`

**Payload :**
```
data: {"name": "TechCorp", "email": "contact@techcorp.com", "phone": "+1234567890", "address": "123 Tech Street, City", "is_active": true}
user: {"id": 1}
logo: [fichier image]
```

**Exemple avec cURL :**
```bash
curl -X POST http://localhost:5000/partners/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "data={\"name\":\"TechCorp\",\"email\":\"contact@techcorp.com\",\"phone\":\"+1234567890\",\"address\":\"123 Tech Street, City\",\"is_active\":true}" \
  -F "user={\"id\":1}" \
  -F "logo=@/path/to/logo.png"
```

## 🎨 Exemples Frontend

### **JavaScript avec Fetch**

```javascript
// Mode JSON
async function createPartnerJSON(partnerData, token) {
  const response = await fetch('/partners/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user: { id: 1 },
      datas: [partnerData]
    })
  });
  
  return response.json();
}

// Mode Multipart avec Logo
async function createPartnerWithLogo(partnerData, logoFile, token) {
  const formData = new FormData();
  formData.append('data', JSON.stringify(partnerData));
  formData.append('user', JSON.stringify({ id: 1 }));
  
  if (logoFile) {
    formData.append('logo', logoFile);
  }
  
  const response = await fetch('/partners/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return response.json();
}

// Utilisation
const partnerData = {
  name: 'TechCorp',
  email: 'contact@techcorp.com',
  phone: '+1234567890',
  address: '123 Tech Street, City',
  is_active: true
};

// Sans logo
createPartnerJSON(partnerData, token);

// Avec logo
const logoFile = document.getElementById('logoInput').files[0];
createPartnerWithLogo(partnerData, logoFile, token);
```

### **React avec Axios**

```javascript
import axios from 'axios';

// Mode JSON
const createPartnerJSON = async (partnerData, token) => {
  const response = await axios.post('/partners/create', {
    user: { id: 1 },
    datas: [partnerData]
  }, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  return response.data;
};

// Mode Multipart avec Logo
const createPartnerWithLogo = async (partnerData, logoFile, token) => {
  const formData = new FormData();
  formData.append('data', JSON.stringify(partnerData));
  formData.append('user', JSON.stringify({ id: 1 }));
  
  if (logoFile) {
    formData.append('logo', logoFile);
  }
  
  const response = await axios.post('/partners/create', formData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'multipart/form-data'
    }
  });
  
  return response.data;
};
```

## 📊 Réponses

### **Succès (200)**

```json
{
  "items": [
    {
      "id": 1,
      "name": "TechCorp",
      "email": "contact@techcorp.com",
      "phone": "+1234567890",
      "address": "123 Tech Street, City",
      "logo_url": "https://votredomaine.com/uploads/logos/logo_techcorp.png",
      "is_active": true,
      "is_deleted": false,
      "created_at": "2025-08-13T02:30:00",
      "created_by": 1,
      "updated_at": "2025-08-13T02:30:00",
      "updated_by": 1
    }
  ],
  "message": "Opération réussie",
  "code": 200
}
```

### **Erreurs (400/500)**

```json
{
  "status": "error",
  "message": "Description de l'erreur"
}
```

## 🔍 Validation

### **Champs Obligatoires**
- `name` : Nom du partenaire (string)

### **Champs Optionnels**
- `email` : Email du partenaire (string)
- `phone` : Téléphone du partenaire (string)
- `address` : Adresse du partenaire (string)
- `logo_url` : URL du logo (string)
- `is_active` : Statut actif (boolean, défaut: true)

### **Validation des Images**
- **Types acceptés** : PNG, JPG, JPEG, GIF
- **Taille maximale** : 16 MB
- **Validation automatique** du type MIME

## 🛡️ Sécurité

### **Authentification**
- ✅ **Token JWT requis** pour toutes les requêtes
- ✅ **Validation du token** avant traitement
- ✅ **Gestion des sessions** Redis

### **Validation des Fichiers**
- ✅ **Vérification du type MIME**
- ✅ **Validation des extensions**
- ✅ **Protection contre les uploads malveillants**

### **Gestion d'Erreurs**
- ✅ **Rollback automatique** en cas d'échec
- ✅ **Suppression des fichiers** uploadés en cas d'erreur
- ✅ **Logs détaillés** pour le debugging

## 🧪 Tests

### **Script de Test Automatique**

```bash
cd src
python test_partner_creation.py
```

### **Tests Manuels**

```bash
# Test mode JSON
curl -X POST http://localhost:5000/partners/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user":{"id":1},"datas":[{"name":"Test JSON","email":"test@json.com"}]}'

# Test mode multipart
curl -X POST http://localhost:5000/partners/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "data={\"name\":\"Test Logo\",\"email\":\"test@logo.com\"}" \
  -F "user={\"id\":1}" \
  -F "logo=@test_logo.png"
```

## 📝 Logs

### **Logs de Debug**

```
2025-08-13 02:30:00 - INFO - **** Begin create_partners ****
2025-08-13 02:30:00 - INFO - Mode multipart/form-data détecté
2025-08-13 02:30:00 - INFO - Logo file détecté: logo.png
2025-08-13 02:30:01 - INFO - Logo uploadé avec succès: https://votredomaine.com/uploads/logos/logo_techcorp.png
2025-08-13 02:30:01 - INFO - **** response output ****
2025-08-13 02:30:01 - INFO - **** End create_partners_with_logo ****
```

## 🔄 Migration

### **Compatibilité Ascendante**
- ✅ **API existante** continue de fonctionner
- ✅ **Aucune modification** requise côté client
- ✅ **Nouvelles fonctionnalités** optionnelles

### **Recommandations**
1. **Testez** les deux modes avant déploiement
2. **Migrez progressivement** vers le nouveau mode
3. **Gardez** la compatibilité JSON pour les clients existants

---

**Note :** Cette implémentation offre le meilleur des deux mondes : simplicité d'utilisation et rétrocompatibilité. 