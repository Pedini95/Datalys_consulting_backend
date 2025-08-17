# 📝 Système d'Historique d'Actions Automatique

## 🎯 Philosophie

**Action History = AUDIT AUTOMATIQUE, pas API manuelle**

L'historique d'actions doit se générer automatiquement lors de chaque action métier, pas être créé manuellement via des APIs.

## 🔄 Comment ça fonctionne

### ❌ AVANT (Mauvaise pratique)
```python
# API manuelle pour créer action history
POST /action-history/create
{
  "action_type": "CREATE_MESSAGE", 
  "entity_type": "message",
  "entity_id": 123,
  "description": "Message créé"
}
```

### ✅ APRÈS (Bonne pratique)
```python
# Action métier normale
POST /messages/send
{
  "title": "Message urgent",
  "description": "..."
}

# → Automatiquement génère :
# - Sauvegarde du message
# - Entrée action_history
# - Notification push si urgent
```

---

## 🛠️ Implémentation Technique

### 1. **Décorateur d'audit automatique**

```python
from utils.audit_decorator import audit_action

class IncidentService:
    @audit_action('CREATE', 'message')
    def create_message(self, data, user_id):
        # Logique métier normale
        message = create_message_logic(data)
        return message, True, "Succès"
        
    # → L'action est automatiquement loggée !
```

### 2. **Informations capturées automatiquement**

| **Champ** | **Source** | **Exemple** |
|-----------|------------|-------------|
| `action_type` | Décorateur | 'CREATE', 'UPDATE', 'DELETE' |
| `entity_type` | Décorateur | 'message', 'project', 'user' |
| `entity_id` | Objet retourné | 123 |
| `user_id` | `g.current_user` | 456 |
| `description` | Auto-généré | "CREATE message #123" |
| `ip_address` | Request IP | "192.168.1.1" |
| `user_agent` | Request headers | "Mozilla/5.0..." |
| `created_at` | Timestamp | "2025-01-17T15:30:00Z" |

### 3. **Actions auditées automatiquement**

- ✅ `create_message()` → Action: CREATE message
- ✅ `create_support_request()` → Action: CREATE support  
- ✅ `create_notification()` → Action: CREATE notification
- 🔄 `update_*()` → Action: UPDATE (à ajouter)
- 🔄 `delete_*()` → Action: DELETE (à ajouter)

---

## 📋 APIs de Consultation (Lecture seule)

### 1. **Recherche générale**
```http
POST /action-history/search

{
  "index": 0,
  "size": 20,
  "data": {
    "action_type": "CREATE",
    "entity_type": "message",
    "user_id": 123
  }
}
```

### 2. **Historique d'un utilisateur**
```http
POST /action-history/user/123

{
  "index": 0,
  "size": 20,
  "action_type": "CREATE"  // Optionnel
}
```

### 3. **Historique d'une entité**
```http
POST /action-history/entity/message/456

{
  "index": 0,
  "size": 50
}
```

### 4. **Statistiques (Admins)**
```http
POST /action-history/stats
```

---

## 🔒 Sécurité et Permissions

### **Règles d'accès :**
- 👤 **Utilisateurs normaux** : Voient seulement leurs propres actions
- 👑 **Admins** : Voient toutes les actions
- 🚫 **Aucune création/modification manuelle** autorisée

### **Filtrage automatique :**
```python
# Non-admin → filtrage automatique
if not _is_admin(g.current_user):
    criteria['user_id'] = g.current_user.id

# Admin → accès complet
```

---

## 🚀 Exemples Concrets

### **Scénario 1 : Message urgent créé**
```bash
curl -X POST /api/messages/send \
  -d '{"title": "🚨 Serveur en panne", "priority": "critique"}'

# Résultats automatiques :
# 1. ✅ Message sauvegardé 
# 2. ✅ Action history créée :
#    - action_type: "CREATE"
#    - entity_type: "message"  
#    - entity_id: 789
#    - user_id: 123
#    - description: "CREATE message #789"
#    - ip_address: "192.168.1.100"
# 3. ✅ Notification push envoyée
```

### **Scénario 2 : Consultation historique**
```bash
curl -X POST /api/action-history/search \
  -d '{"data": {"entity_type": "message", "action_type": "CREATE"}}'

# Réponse :
{
  "items": [
    {
      "id": 1001,
      "action_type": "CREATE",
      "entity_type": "message",
      "entity_id": 789,
      "user_id": 123,
      "description": "CREATE message #789",
      "ip_address": "192.168.1.100",
      "created_at": "2025-01-17T15:30:00Z"
    }
  ],
  "count": 1
}
```

---

## 📊 Avantages de cette approche

### ✅ **Audit complet et fiable**
- Aucune action n'est oubliée
- Informations cohérentes et complètes
- Impossible de contourner l'audit

### ✅ **Sécurité renforcée**
- Traçabilité de toutes les actions
- Détection d'activités suspectes
- Conformité RGPD/audit

### ✅ **Maintenance simplifiée**
- Pas de code d'audit à maintenir dans chaque endpoint
- Logique centralisée dans le décorateur
- Pas d'erreurs d'oubli

### ✅ **Performance optimisée**
- Une seule transaction pour action + audit
- Pas de requêtes multiples
- Rollback automatique en cas d'erreur

---

## 🔧 Configuration

### **Installation :**
```python
# Dans vos services
from utils.audit_decorator import audit_action

@audit_action('CREATE', 'your_entity')
def your_create_method(self, data, user_id):
    # Votre logique métier
    return entity, success, message
```

### **Enregistrement des routes (app.py) :**
```python
from routes import action_history_readonly
app.register_blueprint(action_history_readonly.bp)
```

---

## 🎯 Roadmap

- [ ] **Étendre aux autres services** (users, projects, files)
- [ ] **Actions UPDATE et DELETE** automatiques
- [ ] **Statistiques avancées** (dashboard admin)
- [ ] **Notifications d'audit** (actions critiques)
- [ ] **Export CSV/Excel** pour compliance
- [ ] **Rétention automatique** (archivage)

---

## 📚 Résumé

**Action History doit être :**
- 🤖 **Automatique** : Généré par décorateurs, pas manuellement
- 👀 **Consultatif** : APIs lecture seule pour audit
- 🔒 **Sécurisé** : Filtrage par rôles et utilisateurs
- 📊 **Informatif** : Capture IP, User-Agent, timestamps

**Ne jamais avoir d'APIs de création/modification manuelle d'action history !** 