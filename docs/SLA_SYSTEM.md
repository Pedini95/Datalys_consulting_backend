# 📊 Système SLA (Service Level Agreement)

**Date de création:** 12 octobre 2025  
**Version:** 1.0

---

## 🎯 Vue d'ensemble

Le système SLA gère automatiquement les délais de prise en charge et de résolution des incidents en fonction de leur priorité.

---

## ⏱️ Configuration des Délais SLA

| Priorité | Prise en charge | Résolution estimée |
|----------|----------------|-------------------|
| **P1** | 30 minutes (24/7) | 4 heures ouvrées |
| **P2** | 1 heure ouvrée | 1 jour ouvré (8h) |
| **P3** | 4 heures ouvrées | 3 jours ouvrés (24h) |
| **P4** | 1 jour ouvré (8h) | 5 jours ouvrés (40h) |

> **Note:** P0 (Arrêt de service) nécessite une prise en charge immédiate et n'a pas de SLA défini.

---

## 📋 Champs de la Base de Données

### Nouveaux champs dans la table `incidents`

| Champ | Type | Description |
|-------|------|-------------|
| `taken_at` | DateTime | Date/heure de prise en charge par un expert |
| `sla_prise_en_charge_deadline` | DateTime | Deadline calculée pour la prise en charge |
| `sla_resolution_deadline` | DateTime | Deadline calculée pour la résolution |
| `sla_prise_en_charge_status` | String(20) | Statut: `'respecte'` ou `'depasse'` |
| `sla_resolution_status` | String(20) | Statut: `'respecte'` ou `'depasse'` |

---

## 🔄 Fonctionnement Automatique

### 1. À la création d'un incident

```python
# Lors de POST /incidents
{
  "title": "Problème réseau",
  "priority": "P2",
  "description": "..."
}

# Le système calcule automatiquement:
# - sla_prise_en_charge_deadline = created_at + 1 heure
# - sla_resolution_deadline = created_at + 8 heures
# - sla_prise_en_charge_status = 'respecte'
# - sla_resolution_status = 'respecte'
```

### 2. Lors de la récupération (GET /incidents)

```python
# Le système met à jour automatiquement les statuts
if now > sla_prise_en_charge_deadline and not taken_at:
    sla_prise_en_charge_status = 'depasse'

if now > sla_resolution_deadline and not resolved_at:
    sla_resolution_status = 'depasse'
```

### 3. Calcul du temps restant

```json
{
  "temps_restant_prise_en_charge": {
    "status": "respecte",
    "depassement": false,
    "jours": 0,
    "heures": 0,
    "minutes": 45,
    "total_minutes": 45
  },
  "temps_restant_resolution": {
    "status": "respecte",
    "depassement": false,
    "jours": 0,
    "heures": 7,
    "minutes": 30,
    "total_minutes": 450
  }
}
```

---

## 🎨 Intégration Frontend

Le frontend affiche les compteurs avec des couleurs selon le statut :

### Affichage des statuts

```javascript
// Exemple React/Vue.js
const getStatusColor = (status) => {
  return status === 'respecte' ? 'green' : 'red';
};

// Affichage du compteur
<div className={`compteur ${getStatusColor(incident.sla_prise_en_charge_status)}`}>
  {incident.temps_restant_prise_en_charge.jours}j 
  {incident.temps_restant_prise_en_charge.heures}h 
  {incident.temps_restant_prise_en_charge.minutes}min
</div>
```

### États possibles

| Statut | Couleur Frontend | Description |
|--------|-----------------|-------------|
| `respecte` | 🟢 Vert | Dans les temps |
| `depasse` | 🔴 Rouge | Hors délai |

---

## 📊 Statuts des Tickets

Les incidents peuvent avoir les statuts suivants :

| Statut | Couleur | Description |
|--------|---------|-------------|
| `nouveau` | 🔵 Bleu | Nouveau ticket non pris en charge |
| `en_cours` | 🟠 Orange | En cours de traitement |
| `en_pause` | ⚪ Gris | Mis en pause (en attente) |
| `en_arbitrage` | 🟣 Violet | En arbitrage |
| `resolu` | 🟢 Vert | Résolu, en attente de validation |
| `ferme` | ⚫ Noir | Fermé définitivement |

---

## 🔔 Indicateurs de Performance (KPI)

### Taux de respect des SLA

```python
# Calculer le % d'incidents résolus dans les délais
def get_sla_compliance_rate(date_range):
    total = Incident.query.filter(
        Incident.created_at.between(date_range['start'], date_range['end'])
    ).count()
    
    respected = Incident.query.filter(
        Incident.created_at.between(date_range['start'], date_range['end']),
        Incident.sla_resolution_status == 'respecte',
        Incident.resolved_at != None
    ).count()
    
    return (respected / total) * 100 if total > 0 else 0
```

### Délai moyen de résolution

```python
# Calculer le délai moyen par priorité
def get_average_resolution_time(priority):
    incidents = Incident.query.filter(
        Incident.priority == priority,
        Incident.resolved_at != None
    ).all()
    
    total_time = sum([
        (i.resolved_at - i.created_at).total_seconds() / 3600 
        for i in incidents
    ])
    
    return total_time / len(incidents) if incidents else 0
```

---

## 📝 Exemples d'API

### Créer un incident avec SLA

```bash
POST /incidents
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Serveur inaccessible",
  "description": "Le serveur de production ne répond plus",
  "priority": "P1",
  "impact": "arret_service",
  "domain": "infrastructure",
  "declarant_name": "Jean Dupont",
  "project_id": 1
}
```

**Réponse:**
```json
{
  "status": "success",
  "data": {
    "id": 42,
    "incident_number": "INC-2025-00042",
    "title": "Serveur inaccessible",
    "priority": "P1",
    "sla_prise_en_charge_deadline": "2025-10-12T16:30:00Z",
    "sla_resolution_deadline": "2025-10-12T20:00:00Z",
    "sla_prise_en_charge_status": "respecte",
    "sla_resolution_status": "respecte",
    "temps_restant_prise_en_charge": {
      "status": "respecte",
      "minutes": 28,
      "total_minutes": 28
    }
  }
}
```

### Prendre en charge un incident

```bash
PATCH /incidents/42
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "en_cours",
  "taken_at": "2025-10-12T16:15:00Z",
  "assigned_to": 3
}
```

### Résoudre un incident

```bash
PATCH /incidents/42
Content-Type: application/json
Authorization: Bearer {token}

{
  "status": "resolu",
  "resolved_at": "2025-10-12T19:45:00Z",
  "resolved_by": 3,
  "resolution_notes": "Serveur redémarré, problème de mémoire corrigé"
}
```

---

## 🔧 Migration SQL

Pour ajouter les champs SLA à une base existante :

```bash
mysql -u root -p datalys_consulting < src/migrations/add_sla_fields_to_incidents.sql
```

---

## ✅ Checklist d'Implémentation

### Backend ✅
- [x] Ajout des champs SLA au modèle `Incident`
- [x] Méthode `calculate_sla_deadlines()` pour calculer les deadlines
- [x] Méthode `calculate_time_remaining()` pour le temps restant
- [x] Méthode `update_sla_status()` pour mettre à jour les statuts
- [x] Calcul automatique des deadlines lors de la création
- [x] Migration SQL pour ajouter les champs
- [x] Index sur les champs SLA pour les performances

### Frontend ⏳ (à faire)
- [ ] Affichage du compteur de prise en charge
- [ ] Affichage du compteur de résolution
- [ ] Couleurs dynamiques (vert/rouge) selon le statut
- [ ] Dashboard KPI avec taux de respect SLA
- [ ] Graphiques de performance par priorité
- [ ] Alertes visuelles pour les dépassements

---

## 📚 Références

- **Modèle:** `src/models/incident.py`
- **Service:** `src/services/incident_service.py`
- **Migration:** `src/migrations/add_sla_fields_to_incidents.sql`
- **Routes:** `src/routes/incidents.py`

---

**Créé le:** 12 octobre 2025  
**Auteur:** Équipe Datalys Consulting  
**Statut:** ✅ Implémenté

