# 📝 RÉCAPITULATIF COMPLET - APIs DE COMMUNICATION IMPLÉMENTÉES

## 💬 APIS MESSAGES (Partenaires ↔ Admins)

### 1. Envoyer un message
```http
POST /messages/send
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "Besoin d'assistance",
  "description": "J'ai une question sur le projet Alpha",
  "project_id": 123,
  "priority": "moyenne"  // 🆕 "haute" ou "critique" = notification push !
}
```

**Réponse :**
```json
{
  "code": 200,
  "items": [{"id": 456, "title": "Besoin d'assistance", "type": "message", ...}],
  "message": {"type": "success", "text": "Message créé avec succès"}
}
```

### 2. Récupérer mes messages
```http
POST /messages/my-messages

{
  "index": 0,
  "size": 10
}
```

### 3. Répondre à un message
```http
POST /messages/reply

{
  "parent_id": 456,
  "description": "Voici la réponse à votre question..."
}
```

---

## 🛠️ APIS SUPPORT TECHNIQUE

### 4. Créer demande de support
```http
POST /support/request

{
  "title": "Problème de connexion",
  "description": "Je n'arrive pas à me connecter depuis ce matin",
  "priority": "haute",  // 🆕 "haute" ou "critique" = notification push !
  "project_id": 123
}
```

### 5. Récupérer demandes support (Admins)
```http
POST /support/requests

{
  "index": 0,
  "size": 20,
  "data": {
    "status": "ouvert"
  }
}
```

---

## 📢 APIS NOTIFICATIONS OFFICIELLES

### 6. Envoyer notification (Admins)
```http
POST /notifications/send

{
  "title": "Maintenance programmée",
  "description": "Le système sera en maintenance dimanche de 2h à 4h",
  "assigned_to": 789,
  "priority": "haute"
}
```

### 7. Récupérer notifications non lues
```http
POST /notifications/unread

{
  "index": 0,
  "size": 10
}
```

### 8. Marquer notification comme lue
```http
POST /notifications/mark-read

{
  "id": 123
}
```

---

## 💬 APIS CONVERSATIONS

### 9. Récupérer fil de conversation
```http
POST /conversations/thread

{
  "parent_id": 456,
  "index": 0,
  "size": 50
}
```

---

## 🔔 NOUVELLES APIS NOTIFICATIONS PUSH FCM

### 10. Enregistrer token FCM (Frontend → Backend)
```http
POST /fcm/register-token
Authorization: Bearer YOUR_TOKEN

{
  "fcm_token": "dA1B2C3D4E5F6G7H8I9J0K..."
}
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "user_id": 123,
    "token_registered": true
  }
}
```

### 11. Supprimer token FCM (Logout)
```http
POST /fcm/unregister-token
Authorization: Bearer YOUR_TOKEN
```

### 12. Test notification push (Debug/Admin)
```http
POST /fcm/test-notification
Authorization: Bearer YOUR_TOKEN

{
  "title": "Test Push",
  "body": "Ceci est une notification de test"
}
```

---

## 🔍 API RECHERCHE UNIFIÉE

### 13. Rechercher dans toutes les communications
```http
POST /incidents/getByCriteria

{
  "index": 0,
  "size": 10,
  "data": {
    "type": "message",        // ou "support", "notification", "incident"
    "status": "ouvert",
    "priority": "haute",
    "user_id": 123,
    "project_id": 456,
    "is_read": false
  }
}
```

---

## 🆕 NOUVELLES FONCTIONNALITÉS AUTOMATIQUES

### ⚡ Notifications Push Automatiques :

| **Condition** | **Action** | **Destinataires** |
|---------------|------------|-------------------|
| Message avec `priority: "haute"` | 📤 Push: "⚠️ Message HAUTE" | Tous les admins |
| Message avec `priority: "critique"` | 📤 Push: "🚨 Message CRITIQUE" | Tous les admins |
| Support avec `priority: "haute"` | 📤 Push: "⚠️ Support HAUTE" | Tous les admins |
| Support avec `priority: "critique"` | 📤 Push: "🚨 Support CRITIQUE" | Tous les admins |

### 📱 Exemple de notification push reçue :
```json
{
  "notification": {
    "title": "🚨 Message CRITIQUE",
    "body": "Nouveau message: Serveur en panne"
  },
  "data": {
    "incident_id": "789",
    "type": "message",
    "priority": "critique",
    "action": "open_message"
  }
}
```

---

## 🗄️ STRUCTURE DE BASE DE DONNÉES

### Table `incidents` (unifiée) :
```sql
-- Colonnes existantes
id, title, description, user_id, project_id, is_active, is_deleted, 
created_at, created_by, updated_at, updated_by

-- 🆕 Nouvelles colonnes pour communication
type VARCHAR(50) DEFAULT 'incident'     -- 'message', 'support', 'notification'
priority VARCHAR(20) DEFAULT 'moyenne'  -- 'basse', 'moyenne', 'haute', 'critique'
status VARCHAR(20) DEFAULT 'ouvert'     -- 'ouvert', 'en_cours', 'resolu', 'ferme'
category VARCHAR(50) NULL               -- 'communication', 'technique', 'officiel'
assigned_to INT NULL                    -- Admin assigné
parent_id INT NULL                      -- Pour les réponses/conversations
resolution_notes TEXT NULL              -- Notes de résolution
is_read BOOLEAN DEFAULT FALSE           -- Lu par le destinataire
read_at DATETIME NULL                   -- Date de lecture
```

### Table `users` :
```sql
-- 🆕 Nouvelle colonne pour notifications push
fcm_token VARCHAR(255) NULL             -- Token Firebase Cloud Messaging
```

---

## 📊 AVANTAGES DE CETTE ARCHITECTURE

✅ **Unifiée** : Tous les types de communication dans une seule table  
✅ **Évolutive** : Facile d'ajouter de nouveaux types  
✅ **Temps réel** : Notifications push pour les urgences  
✅ **Historique** : Toutes les communications tracées  
✅ **Flexible** : Recherche dans tous les types  
✅ **Sécurisée** : Tokens FCM gérés côté backend  

---

## 🚀 EXEMPLES D'UTILISATION

### Scénario 1 : Message urgent d'un partenaire
```bash
curl -X POST http://localhost:5000/api/messages/send \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "🚨 URGENT: Problème serveur",
    "description": "Le serveur principal ne répond plus depuis 10 minutes",
    "priority": "critique",
    "project_id": 1
  }'
```
**→ Résultat** : Message sauvegardé + Notification push envoyée à tous les admins

### Scénario 2 : Demande de support technique
```bash
curl -X POST http://localhost:5000/api/support/request \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "⚠️ Bug critique application",
    "description": "Les utilisateurs ne peuvent plus se connecter",
    "priority": "haute",
    "project_id": 2
  }'
```
**→ Résultat** : Demande sauvegardée + Notification push envoyée aux admins

### Scénario 3 : Enregistrement token FCM (Frontend)
```javascript
// Frontend JavaScript
const token = await messaging.getToken({
  vapidKey: 'your-vapid-key'
});

fetch('/api/fcm/register-token', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + userToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ fcm_token: token })
});
```
**→ Résultat** : Token FCM sauvegardé pour l'utilisateur

---

## 🔧 CONFIGURATION REQUISE

### Backend (Python/Flask)
```bash
pip install firebase-admin
```

### Firebase Console
1. Créer projet Firebase
2. Activer Cloud Messaging
3. Télécharger Service Account JSON
4. Placer dans `src/config/firebase-service-account.json`

### Base de données
```sql
-- Appliquer les migrations
ALTER TABLE users ADD COLUMN fcm_token VARCHAR(255) NULL AFTER email;
CREATE INDEX idx_users_fcm_token ON users (fcm_token);

ALTER TABLE incidents ADD COLUMN type VARCHAR(50) DEFAULT 'incident' AFTER description;
-- ... autres colonnes (voir migration complète)
```

---

## 🎯 ROADMAP FUTURS DÉVELOPPEMENTS

- [ ] **Notifications par email** pour incidents critiques
- [ ] **Webhooks** pour intégrations tierces (Slack, Teams)
- [ ] **Notifications mobiles** via apps dédiées
- [ ] **Analytics** des communications (temps de réponse, etc.)
- [ ] **Templates** de messages prédéfinis
- [ ] **Escalation automatique** selon la priorité
- [ ] **API GraphQL** pour queries complexes
- [ ] **WebSockets** pour chat temps réel

---

**Votre système peut maintenant rivaliser avec Slack, Teams ou Discord pour l'engagement temps réel ! 🚀** 