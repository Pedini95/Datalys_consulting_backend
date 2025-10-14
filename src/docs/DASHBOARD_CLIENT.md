# Dashboard Client - Documentation

## Vue d'ensemble

La route `/dashboard/client` fournit au client une vue globale de tous ses incidents avec des statistiques détaillées.

## Route

```
POST /dashboard/client
```

### Authentification

Requiert un JWT token valide dans le header `Authorization: Bearer <token>`.

### Request Body

```json
{
  "user": {
    "id": 123,
    "email": "client@example.com",
    "name": "Nom du Client"
  }
}
```

### Response

```json
{
  "code": 200,
  "message": "Opération réussie",
  "data": {
    "user": {
      "id": 123,
      "name": "Nom du Client",
      "email": "client@example.com",
      "role": "user"
    },
    "incident_stats": {
      "total": 45,
      "nouveau": 5,
      "en_cours": 12,
      "en_attente": 3,
      "en_arbitrage": 2,
      "resolu": 20,
      "ferme": 3,
      "actifs": 22
    },
    "priority_stats": {
      "P0": 1,
      "P1": 5,
      "P2": 10,
      "P3": 20,
      "P4": 9
    },
    "domain_stats": {
      "reseau": 15,
      "infrastructure": 10,
      "cloud": 12,
      "energie": 5,
      "non_specifie": 3
    },
    "sla_stats": {
      "prise_en_charge_depasse": 2,
      "resolution_depasse": 5
    },
    "refusal_stats": {
      "total_refus": 8,
      "incidents_with_refusals": 5
    },
    "recent_incidents": [
      {
        "id": 123,
        "incident_number": "INC-2025-00123",
        "title": "Problème réseau",
        "status": "en_cours",
        "priority": "P1",
        "created_at": "2025-10-14T10:30:00",
        ...
      }
    ],
    "urgent_incidents": [
      {
        "id": 125,
        "incident_number": "INC-2025-00125",
        "title": "Arrêt service critique",
        "status": "nouveau",
        "priority": "P0",
        ...
      }
    ],
    "waiting_incidents": [
      {
        "id": 124,
        "incident_number": "INC-2025-00124",
        "title": "En attente information",
        "status": "en_attente",
        "priority": "P2",
        ...
      }
    ],
    "activity_summary": {
      "recent_actions": 15,
      "last_login": "2025-10-14T08:00:00",
      "active_sessions": 1,
      "actions_details": [...]
    }
  }
}
```

## Statistiques Fournies

### 1. **incident_stats** - Vue d'ensemble des incidents
- `total`: Nombre total d'incidents créés par le client
- `nouveau`: Incidents nouvellement créés
- `en_cours`: Incidents en cours de traitement
- `en_attente`: Incidents en attente d'information client
- `en_arbitrage`: Incidents en arbitrage
- `resolu`: Incidents résolus (en attente validation client)
- `ferme`: Incidents fermés définitivement
- `actifs`: Total des incidents non résolus (nouveau + en_cours + en_attente + en_arbitrage)

### 2. **priority_stats** - Répartition par priorité
Compte des incidents par niveau de priorité (P0 à P4) :
- `P0`: Arrêt de service (immédiat)
- `P1`: Forte dégradation de service
- `P2`: Dégradation de service
- `P3`: Incident ordinaire
- `P4`: Incident mineur

### 3. **domain_stats** - Répartition par domaine
Compte des incidents par domaine technique :
- `reseau`: Problèmes réseau
- `infrastructure`: Infrastructure système
- `cloud`: Services cloud
- `energie`: Énergie
- `non_specifie`: Domaine non spécifié

### 4. **sla_stats** - État des SLA
- `prise_en_charge_depasse`: Nombre d'incidents dont le délai de prise en charge est dépassé
- `resolution_depasse`: Nombre d'incidents dont le délai de résolution est dépassé

### 5. **refusal_stats** - Statistiques de refus
- `total_refus`: Nombre total de fois que le client a refusé des solutions
- `incidents_with_refusals`: Nombre d'incidents ayant au moins un refus

### 6. **recent_incidents** - Derniers incidents
Liste des 10 derniers incidents créés (triés par date de création décroissante).

### 7. **urgent_incidents** - Incidents urgents
Liste des incidents P0 et P1 non résolus nécessitant une attention immédiate.

### 8. **waiting_incidents** - Incidents en attente
Liste des incidents en statut "en_attente" nécessitant une action du client.

### 9. **activity_summary** - Résumé d'activité
- `recent_actions`: Nombre d'actions récentes
- `last_login`: Date de dernière connexion
- `active_sessions`: Nombre de sessions actives
- `actions_details`: Détails des 5 dernières actions

## Cas d'utilisation

### Interface Client

Le client peut utiliser ce dashboard pour :

1. **Vue globale** : Voir rapidement le nombre total d'incidents (nouveau, en cours, en attente)
2. **Incidents actifs** : Nombre total d'incidents nécessitant une attention
3. **Incidents urgents** : Voir les incidents P0/P1 nécessitant une action immédiate
4. **Incidents en attente** : Voir les incidents nécessitant son intervention
5. **Historique** : Consulter les incidents récents et les statistiques globales
6. **SLA** : Surveiller les dépassements de délais
7. **Refus** : Voir combien de fois il a refusé des solutions

### Exemple d'affichage

```
┌─────────────────────────────────────────────┐
│        DASHBOARD - Mes Incidents            │
├─────────────────────────────────────────────┤
│ Total: 45           Actifs: 22              │
│ Nouveau: 5          En cours: 12            │
│ En attente: 3       Résolus: 20             │
├─────────────────────────────────────────────┤
│ ⚠️  URGENTS (P0/P1): 6                      │
│ ⏳ EN ATTENTE: 3                             │
│ 🚨 SLA DÉPASSÉS: 5                          │
└─────────────────────────────────────────────┘
```

## Sécurité

- ✅ Authentification requise (@require_auth)
- ✅ Chaque client voit uniquement **ses propres incidents** (filtre sur `user_id`)
- ✅ Pas d'accès aux incidents d'autres utilisateurs

## Architecture de l'application

### Entités
- **Partner** : Entreprise cliente (ex: "Société ABC")
- **Project** : Projet lié à un Partner
- **User** : Utilisateur de l'application
  - `role="user"` : Employé du Partner (client)
  - `role="admin"` ou `"manager"` : Expert Datalys
- **Incident** : Créé par un User, peut être lié à un Project

### Différence avec les autres dashboards

| Dashboard | Public | Données |
|-----------|--------|---------|
| `/dashboard/client` | User avec role="user" | **Incidents créés par cet utilisateur spécifique** |
| `/dashboard/partner/<id>` | Admins/Managers | **Incidents liés aux projets du Partner (entreprise)** |
| `/dashboard/admin` | Admins | **Vue globale de tous les incidents** |

### Exemples de cas d'usage

**Scénario 1 : Utilisateur Client (User role="user")**
- Jean travaille pour la Société ABC
- Jean se connecte et appelle `/dashboard/client`
- Il voit uniquement **ses propres incidents** qu'il a créés

**Scénario 2 : Vue Partner (Admin/Manager)**
- Un admin Datalys veut voir tous les incidents de la Société ABC
- Il appelle `/dashboard/partner/123` (où 123 = ID du Partner "Société ABC")
- Il voit **tous les incidents liés aux projets** de la Société ABC

**Scénario 3 : Vue Admin**
- Un admin Datalys veut une vue globale
- Il appelle `/dashboard/admin`
- Il voit **tous les incidents** de tous les partners

## Codes d'erreur

- `200`: Succès
- `401`: Non authentifié (token manquant ou invalide)
- `500`: Erreur serveur

## Exemple de code (Frontend)

```javascript
async function getClientDashboard() {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch('https://api.datalysconsulting.com/dashboard/client', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      user: {
        id: currentUser.id,
        email: currentUser.email,
        name: currentUser.name
      }
    })
  });

  const data = await response.json();

  if (data.code === 200) {
    console.log('Incidents actifs:', data.data.incident_stats.actifs);
    console.log('Incidents urgents:', data.data.urgent_incidents.length);
    console.log('Incidents en attente:', data.data.waiting_incidents.length);
  }
}
```
