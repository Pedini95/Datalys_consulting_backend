# Fonctionnalités Administrateur - État d'implémentation

## Vue d'ensemble

Ce document récapitule toutes les fonctionnalités disponibles pour les administrateurs dans l'application Datalys Consulting.

---

## ✅ 1. Liste de tous les incidents avec leurs statuts

### Implémentation : **OUI - COMPLET**

**Route :** `POST /incidents/getByCriteria`

**Fonctionnalités :**
- ✅ Liste paginée de tous les incidents
- ✅ Filtrage par multiples critères :
  - `id`, `title`, `description`
  - `status` : nouveau, en_cours, en_attente, en_arbitrage, resolu, ferme
  - `priority` : P0, P1, P2, P3, P4
  - `impact` : arret_service, service_degrade, majeur, mineur
  - `domain` : reseau, infrastructure, cloud, energie
  - `user_id` : Créateur de l'incident
  - `project_id` : Projet lié
  - `assigned_to` : Expert assigné
  - `parent_id` : Incident parent
  - `is_read` : Lu/non lu
- ✅ Tri par ID décroissant (plus récents en premier)
- ✅ Pagination avec `index` et `size`

**Exemple de requête :**
```json
POST /incidents/getByCriteria
{
  "index": 0,
  "size": 20,
  "data": {
    "status": "en_cours",
    "priority": "P1",
    "domain": "reseau"
  }
}
```

**Réponse :**
```json
{
  "code": 200,
  "message": "Succès",
  "items": [...],
  "count": 45
}
```

**Fichier :** `src/routes/incidents.py:18-41`

---

## ⚠️ 2. Génération de rapports

### Implémentation : **NON - À DÉVELOPPER**

**État actuel :**
- ❌ Pas de route pour exporter en PDF
- ❌ Pas de route pour exporter en Excel/CSV
- ❌ Pas de génération de rapports automatiques

**Ce qui devrait être implémenté :**
- Route `/incidents/export` avec formats : PDF, Excel, CSV
- Rapports périodiques (hebdomadaire, mensuel)
- Statistiques avancées (temps moyen de résolution, SLA, etc.)
- Graphiques et tableaux de bord

**Recommandation :** À implémenter en priorité

---

## ✅ 3. Ajouter des notes sur les incidents

### Implémentation : **OUI - COMPLET**

**Champ disponible :** `resolution_notes` (Text)

**Route de mise à jour :** `POST /incidents/update`

**Fonctionnalités :**
- ✅ Champ `resolution_notes` dans le modèle Incident
- ✅ Possibilité d'ajouter/modifier les notes via update
- ✅ Notes visibles dans `as_dict()` de l'incident
- ✅ Notes stockées dans la base de données

**Exemple de requête :**
```json
POST /incidents/update
{
  "user": {"id": 1, "email": "admin@datalys.com"},
  "datas": [
    {
      "id": 123,
      "resolution_notes": "Problème résolu en redémarrant le serveur. Surveillance pendant 24h recommandée."
    }
  ]
}
```

**Fichier :**
- Model: `src/models/incident.py:51`
- Route: `src/routes/incidents.py:132-224`

---

## ✅ 4. Ajouter des fichiers sur les incidents

### Implémentation : **OUI - COMPLET**

**Routes disponibles :**

### 4.1 Upload de fichier sur un incident
`POST /incidents/<incident_id>/upload-file`

**Fonctionnalités :**
- ✅ Upload de fichiers vers un incident spécifique
- ✅ Tous types de fichiers acceptés (PDF, Word, Excel, images, etc.)
- ✅ Stockage dans `static/files/incidents/incident_{id}/`
- ✅ Lien incident_id dans la table files
- ✅ Vérification que l'incident existe
- ✅ URL complète retournée avec APP_URL

**Exemple de requête :**
```bash
POST /incidents/123/upload-file
Content-Type: multipart/form-data

file: [fichier]
user: {"id": 1, "email": "admin@datalys.com"}
```

**Réponse :**
```json
{
  "code": 200,
  "message": "Fichier uploadé avec succès",
  "data": {
    "file": {
      "id": 456,
      "name": "rapport_incident.pdf",
      "incident_id": 123,
      "file_url": "https://datalysconsulting.com/static/files/incidents/incident_123/rapport_incident.pdf",
      "created_at": "2025-10-14T10:30:00"
    },
    "incident_number": "INC-2025-00123"
  }
}
```

### 4.2 Récupérer les fichiers d'un incident
`GET /incidents/<incident_id>/files`

**Fonctionnalités :**
- ✅ Liste tous les fichiers liés à un incident
- ✅ Pagination avec query params `index` et `size`
- ✅ Retourne le nombre total de fichiers

**Exemple de requête :**
```bash
GET /incidents/123/files?index=0&size=10
Authorization: Bearer <token>
```

**Fichiers :**
- Model: `src/models/file.py:12` (champ incident_id)
- Routes: `src/routes/files.py:410-538`
- Migration: `src/migrations/add_incident_id_to_files.sql` (✅ appliquée)

---

## ✅ 5. Contrôle d'accès par niveau de sécurité (rôle)

### Implémentation : **OUI - COMPLET**

**Middleware disponible :** `src/middleware/role_security.py`

### 5.1 Décorateur `@require_role`

**Usage :**
```python
from middleware.role_security import require_role

@bp.route('/admin/settings', methods=['POST'])
@require_auth  # Vérifier l'authentification d'abord
@require_role('admin')  # Puis vérifier le rôle
def admin_settings():
    # Réservé aux admins
    pass

@bp.route('/partners/data', methods=['POST'])
@require_auth
@require_role(['admin', 'manager'])  # Admins OU managers
def partner_data():
    # Réservé aux admins et managers
    pass
```

### 5.2 Fonctions de filtrage des données

**`filter_data_by_role(data_list, user_role, user_id)`**
- Filtre automatiquement les données selon le rôle
- Admin : voit tout
- Manager : voit les données de son périmètre
- User : voit uniquement ses propres données

**`get_role_based_criteria(base_criteria, user_role, user_id)`**
- Ajoute automatiquement des critères de filtrage basés sur le rôle
- Utilisé dans les requêtes getByCriteria

### 5.3 Rôles disponibles

| Rôle | ID | Accès |
|------|-----|-------|
| `admin` | 1 | Accès complet à toutes les fonctionnalités |
| `manager` | 2 | Accès aux données de gestion (à définir) |
| `user` | 3 | Accès limité à ses propres données |

### 5.4 Architecture de sécurité

```
Requête HTTP
    ↓
@require_auth → Vérifie le JWT token
    ↓
@require_role(['admin']) → Vérifie le rôle
    ↓
filter_data_by_role() → Filtre les données retournées
    ↓
Réponse HTTP
```

**Fichier :** `src/middleware/role_security.py`

---

## 📊 Dashboard Admin

### Implémentation : **OUI - COMPLET**

**Route :** `POST /dashboard/admin`

**Fonctionnalités :**
- ✅ Statistiques globales de tous les partenaires
- ✅ Activité récente de tous les utilisateurs
- ✅ Statistiques des incidents par priorité
- ✅ Actions par jour (7 derniers jours)
- ✅ Actions par type
- ✅ Top 10 utilisateurs les plus actifs
- ✅ Liste des 10 derniers incidents

**Exemple de réponse :**
```json
{
  "code": 200,
  "message": "Succès",
  "data": {
    "partner_stats": [
      {"partner_id": 1, "partner_name": "Société ABC", "total_projects": 5, "active_projects": 3}
    ],
    "recent_activity": [...],
    "incident_priority_stats": {
      "P0": 2,
      "P1": 10,
      "P2": 25,
      "P3": 40,
      "P4": 15
    },
    "global_activity_stats": {
      "daily_actions": [...],
      "actions_by_type": [...],
      "top_users": [...]
    },
    "recent_incidents": [...]
  }
}
```

**Fichier :** `src/routes/dashboard.py:290-334`

---

## Autres routes utiles pour admin

### Métadonnées des incidents
`GET /incidents/metadata`

Retourne toutes les valeurs valides pour :
- Priorités (P0-P4)
- Statuts
- Impacts
- Domaines
- Mapping impact → priorité recommandée

**Fichier :** `src/routes/incidents.py:258-314`

### CRUD complet sur incidents
- ✅ `POST /incidents/create` - Créer
- ✅ `POST /incidents/update` - Mettre à jour
- ✅ `POST /incidents/delete` - Supprimer (soft delete)
- ✅ `POST /incidents/getByCriteria` - Lister/filtrer

---

## Résumé par fonctionnalité

| Fonctionnalité | État | Fichier | Commentaire |
|---------------|------|---------|-------------|
| Liste incidents avec filtres | ✅ COMPLET | routes/incidents.py:18-41 | Tous les filtres disponibles |
| Génération rapports | ❌ À FAIRE | - | PDF/Excel/CSV à implémenter |
| Ajout notes | ✅ COMPLET | models/incident.py:51 | Champ resolution_notes |
| Ajout fichiers | ✅ COMPLET | routes/files.py:410-538 | Upload + liste |
| Contrôle accès rôle | ✅ COMPLET | middleware/role_security.py | @require_role disponible |
| Dashboard admin | ✅ COMPLET | routes/dashboard.py:290-334 | Stats globales |
| Métadonnées | ✅ COMPLET | routes/incidents.py:258-314 | P0-P4, statuts, etc. |

---

## Recommandations

### Priorité haute : Génération de rapports

Il manque la fonctionnalité de génération de rapports. Voici ce qui devrait être implémenté :

#### Route proposée : `/incidents/export`

```python
@bp.route('/incidents/export', methods=['POST'])
@cross_origin()
@require_auth
@require_role('admin')  # Réservé aux admins
def export_incidents():
    """
    Exporter les incidents dans différents formats

    Body:
    {
      "format": "pdf|excel|csv",
      "criteria": {...},  # Mêmes critères que getByCriteria
      "date_from": "2025-01-01",
      "date_to": "2025-12-31",
      "include_stats": true
    }
    """
    pass
```

**Bibliothèques recommandées :**
- PDF : `reportlab` ou `weasyprint`
- Excel : `openpyxl` ou `xlsxwriter`
- CSV : module `csv` natif Python

### Priorité moyenne : Amélioration du contrôle d'accès

**Actuellement :**
- Le décorateur `@require_role` existe mais n'est pas utilisé sur toutes les routes
- Certaines routes sont uniquement protégées par `@require_auth`

**À faire :**
1. Ajouter `@require_role('admin')` sur les routes sensibles
2. Implémenter le filtrage automatique par rôle dans `getByCriteria`
3. Documenter les permissions de chaque route

### Exemple d'implémentation sécurisée :

```python
@bp.route('/incidents/delete', methods=['POST'])
@cross_origin()
@require_auth
@require_role(['admin', 'manager'])  # ← Ajouter cette ligne
def delete_incidents():
    # Seuls admin et manager peuvent supprimer
    pass
```

---

## Conclusion

### État global : 80% implémenté ✅

**Ce qui fonctionne :**
- ✅ Liste complète des incidents avec filtres avancés
- ✅ Ajout de notes (resolution_notes)
- ✅ Upload et récupération de fichiers sur incidents
- ✅ Middleware de sécurité par rôle disponible
- ✅ Dashboard admin avec statistiques globales

**Ce qui manque :**
- ❌ Génération de rapports (PDF, Excel, CSV)
- ⚠️ Application systématique du contrôle d'accès par rôle sur toutes les routes

L'administrateur peut déjà effectuer la majorité des opérations demandées. La génération de rapports est la seule fonctionnalité majeure manquante.
