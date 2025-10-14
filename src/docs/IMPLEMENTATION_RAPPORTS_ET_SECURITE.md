# Implémentation : Génération de Rapports et Contrôle d'Accès

## Date : 2025-10-14

Ce document décrit l'implémentation complète de la génération de rapports et du contrôle d'accès par rôle dans l'application.

---

## ✅ 1. Génération de Rapports (PDF, Excel, CSV)

### 1.1 Fichiers créés

#### `utils/report_generator.py` ✨ NOUVEAU
Classe `ReportGenerator` avec 3 méthodes principales :

- **`generate_csv(incidents, include_stats)`**
  - Format CSV simple
  - En-têtes : Numéro, Titre, Description, Statut, Priorité, Impact, Domaine, etc.
  - Statistiques optionnelles (comptage par statut, priorité, domaine)

- **`generate_excel(incidents, include_stats)`**
  - Format Excel avec mise en forme (couleurs, bordures)
  - Coloration automatique par statut :
    - Résolu = Vert
    - En cours = Jaune
    - Nouveau = Rouge
  - Feuille "Statistiques" séparée si `include_stats=True`

- **`generate_pdf(incidents, include_stats)`**
  - Format PDF paysage (A4)
  - Tableau formaté avec en-têtes stylés
  - Statistiques en haut du document
  - Logo et date de génération

### 1.2 Route d'export

#### `POST /incidents/export` ✨ NOUVEAU

**Accès :** Admin et Manager uniquement (`@require_role(['admin', 'manager'])`)

**Body :**
```json
{
  "user": {"id": 1, "email": "admin@datalys.com"},
  "format": "pdf",           // ou "excel" ou "csv"
  "criteria": {              // Critères de filtrage (optionnel)
    "status": "en_cours",
    "priority": "P1",
    "domain": "reseau"
  },
  "date_from": "2025-01-01", // Filtrer par date de création (optionnel)
  "date_to": "2025-12-31",
  "include_stats": true      // Inclure les statistiques (défaut: false)
}
```

**Réponse :**
- Fichier téléchargeable directement
- Nom du fichier : `incidents_YYYYMMDD_HHMMSS.{format}`
- MIME types corrects :
  - CSV : `text/csv`
  - Excel : `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - PDF : `application/pdf`

**Exemples d'utilisation :**

```bash
# Export CSV simple
curl -X POST https://api.datalysconsulting.com/incidents/export \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}' \
  --output incidents.csv

# Export Excel avec statistiques et filtres
curl -X POST https://api.datalysconsulting.com/incidents/export \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "excel",
    "criteria": {"status": "resolu", "priority": "P1"},
    "include_stats": true
  }' \
  --output incidents_p1_resolus.xlsx

# Export PDF pour une période donnée
curl -X POST https://api.datalysconsulting.com/incidents/export \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "date_from": "2025-01-01",
    "date_to": "2025-03-31",
    "include_stats": true
  }' \
  --output rapport_Q1_2025.pdf
```

**Limite :** Maximum 10 000 incidents par export (pour éviter les surcharges)

### 1.3 Dépendances requises

Fichier créé : `requirements_reports.txt`

```
openpyxl==3.1.2         # Génération Excel
reportlab==4.0.7        # Génération PDF
Pillow==10.1.0          # Support images (requis par reportlab)
```

**Installation :**
```bash
cd /Users/pkone/Documents/workspace_flask_python/Datalys_consulting_backend
pip install -r requirements_reports.txt
```

---

## ✅ 2. Contrôle d'Accès par Rôle

### 2.1 Middleware existant

**Fichier :** `middleware/role_security.py` (déjà existant)

**Décorateur principal :** `@require_role(roles)`

**Usage :**
```python
from middleware.role_security import require_role

# Réservé aux admins uniquement
@require_role('admin')
def admin_only_route():
    pass

# Admins OU managers
@require_role(['admin', 'manager'])
def admin_or_manager_route():
    pass
```

### 2.2 Routes protégées (NOUVELLES)

#### `routes/incidents.py`

| Route | Décorateur | Accès |
|-------|------------|-------|
| `POST /incidents/export` | `@require_role(['admin', 'manager'])` | ✨ NOUVEAU |
| `POST /incidents/delete` | `@require_role(['admin', 'manager'])` | ✨ NOUVEAU |

#### `routes/users.py`

| Route | Décorateur | Accès |
|-------|------------|-------|
| `POST /users/getByCriteria` | `@require_role(['admin', 'manager'])` | ✨ NOUVEAU |
| `POST /users/create` | `@require_role('admin')` | ✨ NOUVEAU (remplace vérif manuelle) |
| `POST /users/delete` | `@require_role('admin')` | ✨ NOUVEAU |

**Note :** Les vérifications manuelles ont été remplacées par le décorateur `@require_role` pour plus de cohérence et de sécurité.

### 2.3 Architecture de sécurité

```
┌────────────────────────────────────────────────┐
│          Requête HTTP                          │
└────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│   @require_auth                                │
│   ✓ Vérifier JWT token valide                 │
│   ✓ Récupérer l'utilisateur (g.current_user)  │
└────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│   @require_role(['admin', 'manager'])          │
│   ✓ Vérifier le rôle de l'utilisateur         │
│   ✗ Bloquer si rôle non autorisé (403)        │
└────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│   Logique métier de la route                  │
│   → Traitement de la requête                  │
└────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│   Réponse HTTP                                 │
└────────────────────────────────────────────────┘
```

### 2.4 Codes d'erreur

| Code | Statut | Signification |
|------|--------|---------------|
| 200 | Success | Opération réussie |
| 401 | Unauthorized | Token JWT manquant ou invalide |
| 403 | Forbidden | Rôle insuffisant pour accéder à cette ressource |
| 404 | Not Found | Ressource non trouvée |
| 500 | Internal Server Error | Erreur serveur |

**Exemple de réponse 403 :**
```json
{
  "status": "error",
  "message": "Accès réservé aux rôles: admin, manager"
}
```

---

## 📊 Résumé des changements

### Fichiers créés

1. ✅ `utils/report_generator.py` - Générateur de rapports (CSV, Excel, PDF)
2. ✅ `requirements_reports.txt` - Dépendances pour les rapports
3. ✅ `docs/IMPLEMENTATION_RAPPORTS_ET_SECURITE.md` - Cette documentation

### Fichiers modifiés

1. ✅ `routes/incidents.py`
   - Ajout de la route `/incidents/export`
   - Ajout de `@require_role` sur `/incidents/delete`
   - Import de `send_file`, `require_role`, `io`, `datetime`

2. ✅ `routes/users.py`
   - Ajout de `@require_role` sur toutes les routes sensibles
   - Remplacement des vérifications manuelles par le décorateur
   - Import de `require_role`

### Statistiques

| Fonctionnalité | Avant | Après | Statut |
|----------------|-------|-------|--------|
| Génération de rapports | ❌ | ✅ | Implémenté |
| Export PDF | ❌ | ✅ | Implémenté |
| Export Excel | ❌ | ✅ | Implémenté |
| Export CSV | ❌ | ✅ | Implémenté |
| Contrôle accès incidents | Partiel | ✅ | Renforcé |
| Contrôle accès users | Manuel | ✅ | Standardisé |
| Middleware sécurité | Existant | ✅ | Appliqué |

---

## 🚀 Instructions de déploiement

### 1. Installer les dépendances

```bash
cd /Users/pkone/Documents/workspace_flask_python/Datalys_consulting_backend
pip install -r requirements_reports.txt
```

### 2. Redémarrer l'application

```bash
# Si utilisation de Docker
docker-compose restart

# Si utilisation directe de Python
pkill -f "python run.py"
python run.py
```

### 3. Tester la génération de rapports

```bash
# Tester l'export CSV
curl -X POST http://localhost:5000/incidents/export \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}' \
  --output test.csv

# Vérifier le fichier
cat test.csv
```

### 4. Vérifier le contrôle d'accès

```bash
# Essayer d'exporter avec un token user (non admin)
# → Devrait retourner 403 Forbidden
curl -X POST http://localhost:5000/incidents/export \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}'

# Essayer avec un token admin
# → Devrait retourner le fichier CSV
curl -X POST http://localhost:5000/incidents/export \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"format": "csv"}' \
  --output success.csv
```

---

## 📝 Notes importantes

### Performances

- **Limite d'export :** 10 000 incidents maximum par rapport
- **Génération asynchrone :** Pour de très gros volumes, envisager de passer à une génération asynchrone avec Celery

### Sécurité

- ✅ Tous les exports nécessitent une authentification (`@require_auth`)
- ✅ Seuls les admins et managers peuvent exporter
- ✅ Les fichiers ne sont pas stockés sur le serveur (envoi direct)
- ✅ Les tokens JWT sont vérifiés à chaque requête

### Personnalisation

Pour personnaliser les rapports, modifier `utils/report_generator.py` :

```python
# Exemple : Ajouter une colonne dans le CSV
headers = [
    'Numéro',
    'Titre',
    # ... colonnes existantes ...
    'Votre nouvelle colonne'  # ← Ajouter ici
]
```

### Frontend (Exemple React)

```javascript
// Télécharger un rapport Excel avec statistiques
async function downloadExcelReport() {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch('/incidents/export', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      format: 'excel',
      include_stats: true,
      criteria: {
        priority: 'P1',
        status: 'resolu'
      }
    })
  });

  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'incidents_rapport.xlsx';
    a.click();
  } else if (response.status === 403) {
    alert('Accès réservé aux administrateurs');
  }
}
```

---

## ✅ Checklist de validation

- [x] Générateur de rapports créé
- [x] Route d'export implémentée
- [x] Contrôle d'accès appliqué sur routes sensibles
- [x] Dépendances documentées
- [x] Documentation complète rédigée
- [ ] Tests unitaires créés (recommandé)
- [ ] Tests d'intégration effectués (recommandé)
- [ ] Installation des dépendances en production
- [ ] Validation avec un admin réel
- [ ] Validation avec un user non-admin (devrait être bloqué)

---

## 🎯 Prochaines étapes recommandées

1. **Tests automatisés**
   - Créer des tests unitaires pour `report_generator.py`
   - Tester les 3 formats (PDF, Excel, CSV)
   - Tester le contrôle d'accès par rôle

2. **Optimisations**
   - Implémenter la génération asynchrone pour gros volumes
   - Ajouter un cache pour les rapports fréquents
   - Compression des fichiers générés

3. **Fonctionnalités supplémentaires**
   - Rapports programmés (quotidiens, hebdomadaires)
   - Envoi automatique par email
   - Graphiques dans les PDF
   - Personnalisation des colonnes par l'utilisateur

4. **Monitoring**
   - Logger les exports (qui, quand, quel format)
   - Alertes si tentative d'export non autorisée
   - Statistiques d'utilisation des rapports

---

**Implémentation complétée le :** 2025-10-14
**Développeur :** Claude Code
**Statut :** ✅ PRÊT POUR PRODUCTION (après installation des dépendances)
