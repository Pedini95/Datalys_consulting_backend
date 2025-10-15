# Guide d'utilisation - Collection Postman Datalys Consulting API

## 📦 Collection complète pour tester toutes les APIs

**Base URL :** `http://82.112.253.137:8082`

---

## 🚀 Installation

### 1. Importer la collection dans Postman

1. Ouvrir Postman
2. Cliquer sur **Import** (en haut à gauche)
3. Sélectionner le fichier `Datalys_Consulting_API.postman_collection.json`
4. La collection apparaît dans la sidebar

### 2. Variables d'environnement

La collection contient 4 variables automatiques :

| Variable | Description | Rempli automatiquement |
|----------|-------------|------------------------|
| `{{base_url}}` | URL de base de l'API | ✅ Oui (http://82.112.253.137:8082) |
| `{{token}}` | Token JWT après login | ✅ Oui (après MFA) |
| `{{user_id}}` | ID utilisateur connecté | ✅ Oui (après login) |
| `{{incident_id}}` | ID incident créé | ✅ Oui (après création) |

**Note :** Aucune configuration manuelle nécessaire ! Les scripts de test automatisent tout.

---

## 📋 Ordre de test recommandé

### **Étape 1 : Authentication** 🔐

#### 1.1 Login
```
POST /auth/login
Body: {
  "identifier": "admin@datalysconsulting.com",
  "password": "Admin@2025"
}
```

**Résultat :**
- ✅ MFA activé → Code envoyé par email
- ✅ `user_id` stocké automatiquement
- ⚠️ Vérifier votre email pour obtenir le code MFA (6 chiffres)

#### 1.2 Verify MFA
```
POST /auth/verify-mfa
Body: {
  "identifier": "admin@datalysconsulting.com",
  "mfa_code": "123456"  ← Code reçu par email
}
```

**Résultat :**
- ✅ Token JWT stocké automatiquement dans `{{token}}`
- ✅ Toutes les autres requêtes utiliseront ce token automatiquement

---

### **Étape 2 : Tester les fonctionnalités** 🧪

Une fois authentifié, vous pouvez tester dans n'importe quel ordre :

#### A. Incidents (Fonctionnalité principale)

1. **Get Metadata** - Obtenir les valeurs valides (priorités, statuts, etc.)
2. **Get Incidents** - Liste avec filtres
3. **Create Incident** - Créer un incident (stocke `incident_id` automatiquement)
4. **Update Incident** - Modifier (ajouter notes, changer statut)
5. **Upload File** - Joindre un fichier à l'incident
6. **Get Files** - Liste des fichiers de l'incident
7. **Refuse Solution** - Refuser et réouvrir (client uniquement)
8. **Export CSV/Excel/PDF** - Générer rapports (admin/manager uniquement)
9. **Delete** - Supprimer (admin/manager uniquement)

#### B. Dashboard

1. **Dashboard Client** - Vue personnelle de ses incidents
2. **Dashboard Partner** - Vue des incidents d'un partenaire
3. **Dashboard Admin** - Vue globale (admin uniquement)

#### C. Users (Admin/Manager)

1. **Get Users** - Liste des utilisateurs
2. **Create User** - Créer (admin uniquement)
3. **Update User** - Modifier
4. **Delete User** - Supprimer (admin uniquement)

#### D. Partners & Projects

1. **Get Partners** - Liste des partenaires
2. **Create Partner** - Créer un partenaire
3. **Get Projects** - Liste des projets
4. **Create Project** - Créer un projet

#### E. Files

1. **Get Files** - Liste des fichiers
2. **Upload File** - Uploader un fichier

---

## 🔍 Détails par dossier

### 1️⃣ Authentication

| Requête | Méthode | Description | Résultat |
|---------|---------|-------------|----------|
| Login | POST | Connexion avec email/code client | Code MFA envoyé + user_id stocké |
| Verify MFA | POST | Validation du code MFA | Token JWT stocké automatiquement |
| Logout | POST | Déconnexion | Session fermée |

**Scripts automatiques :**
- ✅ Login → Stocke `user_id`
- ✅ Verify MFA → Stocke `token` dans les variables

---

### 2️⃣ Users (Admin/Manager)

| Requête | Méthode | Accès | Description |
|---------|---------|-------|-------------|
| Get Users | POST | Admin + Manager | Liste paginée |
| Create User | POST | **Admin uniquement** | Création utilisateur |
| Update User | POST | Tous | Modification |
| Delete User | POST | **Admin uniquement** | Suppression soft |

**Rôles disponibles :**
- `admin` - Accès complet
- `manager` - Gestion
- `user` - Client/Partenaire

---

### 3️⃣ Incidents (Fonctionnalité principale)

#### Routes principales

| Requête | Méthode | Accès | Description |
|---------|---------|-------|-------------|
| Get Metadata | GET | Tous | Priorités, statuts, impacts, domaines |
| Get Incidents | POST | Tous | Liste avec filtres avancés |
| Create Incident | POST | Tous | Création avec numéro auto (INC-2025-XXXXX) |
| Update Incident | POST | Tous | Modification (notes, statut, etc.) |
| Delete Incident | POST | **Admin + Manager** | Suppression |

#### Routes avancées

| Requête | Méthode | Accès | Description |
|---------|---------|-------|-------------|
| Refuse Solution | POST | Client créateur | Refuser et réouvrir |
| Upload File | POST | Tous | Joindre fichier |
| Get Files | GET | Tous | Liste fichiers |
| **Export CSV** | POST | **Admin + Manager** | Rapport CSV |
| **Export Excel** | POST | **Admin + Manager** | Rapport Excel (.xlsx) |
| **Export PDF** | POST | **Admin + Manager** | Rapport PDF |

**Filtres disponibles (Get Incidents) :**
```json
{
  "status": "nouveau|en_cours|en_attente|en_arbitrage|resolu|ferme",
  "priority": "P0|P1|P2|P3|P4",
  "impact": "arret_service|service_degrade|majeur|mineur",
  "domain": "reseau|infrastructure|cloud|energie",
  "user_id": 123,
  "project_id": 456,
  "assigned_to": 789
}
```

**Exemple d'export Excel avec statistiques :**
```json
{
  "format": "excel",
  "criteria": {
    "priority": "P1",
    "status": "resolu"
  },
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "include_stats": true
}
```

---

### 4️⃣ Dashboard

| Requête | Accès | Données affichées |
|---------|-------|-------------------|
| Dashboard Client | User | Ses propres incidents + stats |
| Dashboard Partner | Tous | Incidents des projets du partenaire |
| Dashboard Admin | Admin | Vue globale + stats toutes activités |

**Statistiques fournies :**
- Total incidents, par statut, par priorité
- Incidents urgents (P0/P1)
- Incidents en attente client
- SLA dépassés
- Refus de solutions
- Activité récente

---

### 5️⃣ Partners & Projects

| Entité | Routes disponibles |
|--------|-------------------|
| Partners | Get, Create, Update, Delete |
| Projects | Get, Create, Update, Delete |

**Relation :** 1 Partner → N Projects → N Incidents

---

### 6️⃣ Files

| Requête | Type | Description |
|---------|------|-------------|
| Get Files | POST | Liste avec filtres (folder_id, incident_id) |
| Upload File | POST | Upload multipart/form-data |

**Formats acceptés :** PDF, Word, Excel, Images, CSV, Texte, etc.

---

### 7️⃣ Health Check

| Requête | Méthode | Description |
|---------|---------|-------------|
| Health Check | GET | Vérifier que l'API fonctionne |

**Réponse :**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T10:30:00"
}
```

---

## 🎯 Scénarios de test complets

### Scénario 1 : Cycle de vie d'un incident

1. **Login** → Obtenir token
2. **Verify MFA** → Activer session
3. **Create Incident** → Créer incident P1 réseau
4. **Upload File** → Joindre capture d'écran
5. **Update Incident** → Passer en "en_cours" + ajouter notes
6. **Update Incident** → Passer en "resolu" avec solution
7. **Refuse Solution** → Client refuse (incident réouvert)
8. **Update Incident** → Nouvelle solution + passer en "resolu"
9. **Export PDF** → Générer rapport final

### Scénario 2 : Gestion admin

1. **Login Admin** → Authentification
2. **Dashboard Admin** → Vue d'ensemble
3. **Get Incidents** → Filtrer P0/P1 en cours
4. **Export Excel** → Rapport mensuel avec stats
5. **Create User** → Ajouter nouveau client
6. **Get Users** → Vérifier création

### Scénario 3 : Vue client

1. **Login Client** → Code client DTLSXXXXXX
2. **Dashboard Client** → Voir ses incidents
3. **Create Incident** → Créer nouvelle demande
4. **Get Incidents** → Voir statut de ses demandes
5. **Refuse Solution** → Refuser si non satisfait

---

## 🔒 Contrôles d'accès

### Routes publiques (pas de token)
- `POST /auth/login`
- `POST /auth/verify-mfa`
- `GET /health`

### Routes authentifiées (token requis)
- Toutes les autres routes

### Routes Admin uniquement
- `POST /users/create`
- `POST /users/delete`

### Routes Admin + Manager
- `POST /users/getByCriteria`
- `POST /incidents/delete`
- `POST /incidents/export` (tous formats)

### Routes Client
- `POST /incidents/<id>/refuse-solution` (uniquement si créateur)

---

## ⚠️ Codes d'erreur courants

| Code | Signification | Action |
|------|---------------|--------|
| 200 | ✅ Succès | Tout va bien |
| 401 | ❌ Non authentifié | Refaire login + MFA |
| 403 | ❌ Accès refusé | Rôle insuffisant (ex: user essaie route admin) |
| 404 | ❌ Non trouvé | Ressource inexistante |
| 500 | ❌ Erreur serveur | Contacter support |

**Exemple 403 :**
```json
{
  "status": "error",
  "message": "Accès réservé aux rôles: admin, manager"
}
```

---

## 💡 Astuces Postman

### 1. Exécuter toute la collection
1. Cliquer sur les 3 points `...` de la collection
2. Sélectionner **Run collection**
3. Choisir l'ordre et lancer les tests

### 2. Variables automatiques
Les scripts de test stockent automatiquement :
- `{{token}}` après Verify MFA
- `{{user_id}}` après Login
- `{{incident_id}}` après Create Incident

### 3. Télécharger les exports
Pour les routes `/incidents/export` :
1. Cliquer sur **Send and Download**
2. Le fichier sera téléchargé automatiquement

### 4. Upload de fichiers
Pour uploader un fichier :
1. Body → form-data
2. Sélectionner `file` (type File)
3. Choisir le fichier local

---

## 📊 Exemple de réponse complète

### Create Incident
**Request :**
```json
{
  "user": {"id": 1},
  "datas": [{
    "title": "Problème réseau",
    "priority": "P1",
    "impact": "service_degrade",
    "domain": "reseau"
  }]
}
```

**Response :**
```json
{
  "code": 200,
  "message": "Succès",
  "items": [{
    "id": 123,
    "incident_number": "INC-2025-00123",
    "title": "Problème réseau",
    "status": "nouveau",
    "priority": "P1",
    "impact": "service_degrade",
    "domain": "reseau",
    "sla_prise_en_charge_deadline": "2025-10-14T11:00:00",
    "sla_resolution_deadline": "2025-10-14T14:00:00",
    "created_at": "2025-10-14T10:30:00",
    "priority_label": "Forte dégradation de service",
    "status_color": "blue"
  }]
}
```

---

## 🎓 Formation rapide

### Pour un développeur frontend :
1. Importer la collection
2. Tester **Login** + **Verify MFA**
3. Observer les réponses
4. Copier les structures pour votre code

### Pour un testeur QA :
1. Exécuter le **Scénario 1** complet
2. Vérifier chaque réponse
3. Tester les cas d'erreur (mauvais token, rôle insuffisant)
4. Valider les exports (CSV, Excel, PDF)

### Pour un admin :
1. Tester **Dashboard Admin**
2. Tester **Export Excel** avec statistiques
3. Tester **Create/Delete User**
4. Vérifier les contrôles d'accès

---

## 📞 Support

**Documentation complète :**
- `src/docs/ADMIN_FEATURES.md`
- `src/docs/DASHBOARD_CLIENT.md`
- `src/docs/IMPLEMENTATION_RAPPORTS_ET_SECURITE.md`

**En cas de problème :**
1. Vérifier que l'API est accessible : `GET /health`
2. Vérifier le token JWT (expire après 2h)
3. Refaire Login + MFA si nécessaire

---

**Version :** 1.0
**Dernière mise à jour :** 2025-10-14
**Base URL :** http://82.112.253.137:8082
