# 🎯 LOGIQUE DES NOTIFICATIONS PUSH

## 📤 QUI ENVOIE LES MESSAGES ?

**Les deux !** Admins ET partenaires peuvent envoyer des messages :

- **Partenaires** → Envoient des messages aux admins
- **Admins** → Envoient des messages aux partenaires ET des notifications officielles

## 📱 QUI REÇOIT LES NOTIFICATIONS PUSH ?

**Les deux !** Admins ET partenaires reçoivent des notifications push automatiques :

| **Qui envoie** | **Qui reçoit** | **Type de notification** |
|----------------|----------------|-------------------------|
| **Partenaire** | **Tous les admins** | `⚠️ Message HAUTE` / `🚨 Message CRITIQUE` |
| **Admin** | **Tous les partenaires du projet** | `📝 Message Admin` / `📢 Message Admin CRITIQUE` |
| **Partenaire** | **Tous les admins** | `⚠️ Support HAUTE` / `🚨 Support CRITIQUE` |
| **Admin** | **Utilisateur assigné** | Notification officielle |

## 🔔 DÉCLENCHEURS DES NOTIFICATIONS PUSH

Les notifications push sont envoyées **automatiquement** quand :

1. **Un partenaire envoie un message** avec priorité `"haute"` ou `"critique"` → Notifications aux admins
2. **Un admin envoie un message** avec priorité `"haute"` ou `"critique"` → Notifications aux partenaires du projet
3. **Un partenaire crée une demande de support** avec priorité `"haute"` ou `"critique"` → Notifications aux admins

## 📋 EXEMPLES CONCRETS

### Exemple 1 : Partenaire alerte les admins
```json
// Un partenaire envoie ce message :
{
  "title": "🚨 URGENT: Problème serveur",
  "description": "Le serveur principal ne répond plus",
  "priority": "critique",  // ← Déclenche notification push
  "project_id": 1
}
```

**Résultat :**
- ✅ Message sauvegardé en base
- 📱 **Notification push envoyée à TOUS les admins** : `🚨 Message CRITIQUE`

### Exemple 2 : Admin informe les partenaires
```json
// Un admin envoie ce message :
{
  "title": "Maintenance programmée",
  "description": "Le système sera en maintenance ce soir",
  "priority": "haute",  // ← Déclenche notification push
  "project_id": 1
}
```

**Résultat :**
- ✅ Message sauvegardé en base
- 📱 **Notification push envoyée aux partenaires du projet** : `📝 Message Admin`

## 🤔 POURQUOI CETTE LOGIQUE ?

1. **Partenaires** → Ont besoin d'alerter rapidement les admins en cas d'urgence
2. **Admins** → Doivent informer les partenaires des réponses et notifications importantes
3. **Communication bidirectionnelle** → Système équilibré pour tous les utilisateurs
4. **Système unifié** → Toutes les communications dans une seule table

## 📊 RÉSUMÉ

- ✅ **Partenaires** : Envoient des messages → Notifications push aux admins
- ✅ **Admins** : Envoient des messages → Notifications push aux partenaires du projet
- ✅ **Système** : Communication bidirectionnelle avec notifications push

Votre système permet maintenant une **communication équilibrée** entre admins et partenaires ! 🚀

---

## 🔧 CONFIGURATION TECHNIQUE

### Variables d'Environnement
```bash
# Activation des notifications automatiques
FCM_AUTO_NOTIFY_HIGH_PRIORITY=True
FCM_AUTO_NOTIFY_CRITICAL_PRIORITY=True
```

### Priorités qui déclenchent les notifications
- `"haute"` → Notification `⚠️` (partenaires) / `📝` (admins)
- `"critique"` → Notification `🚨` (partenaires) / `📢` (admins)

### Destinataires des notifications
- **Messages urgents des partenaires** → Tous les utilisateurs avec `role_id = 1` (admins)
- **Messages urgents des admins** → Tous les partenaires du projet spécifique
- **Support urgent** → Tous les utilisateurs avec `role_id = 1` (admins)
- **Notifications officielles** → Utilisateur spécifique assigné

---

## 🚀 EXEMPLES D'UTILISATION

### Scénario 1 : Partenaire alerte les admins
```http
POST /messages/send
{
  "title": "Problème de connexion",
  "description": "Impossible d'accéder au système depuis 30 minutes",
  "priority": "critique",
  "project_id": 123
}
```
→ **Résultat** : Notification push `🚨 Message CRITIQUE` envoyée à tous les admins

### Scénario 2 : Admin informe les partenaires
```http
POST /messages/send
{
  "title": "Réponse à votre demande",
  "description": "Nous avons résolu le problème de connexion",
  "priority": "haute",
  "project_id": 123
}
```
→ **Résultat** : Notification push `📝 Message Admin` envoyée aux partenaires du projet 123

### Scénario 3 : Demande de support urgente
```http
POST /support/request
{
  "title": "Bug critique",
  "description": "Les utilisateurs ne peuvent plus sauvegarder leurs données",
  "priority": "haute",
  "project_id": 456
}
```
→ **Résultat** : Notification push `⚠️ Support HAUTE` envoyée à tous les admins

---

## 📱 STRUCTURE DES NOTIFICATIONS PUSH

### Format de la notification (Partenaire → Admin)
```json
{
  "notification": {
    "title": "🚨 Message CRITIQUE",
    "body": "Nouveau message: Problème de connexion"
  },
  "data": {
    "incident_id": "789",
    "type": "message",
    "priority": "critique",
    "action": "open_message"
  }
}
```

### Format de la notification (Admin → Partenaire)
```json
{
  "notification": {
    "title": "📝 Message Admin",
    "body": "Message de l'administrateur: Réponse à votre demande"
  },
  "data": {
    "incident_id": "790",
    "type": "message",
    "priority": "haute",
    "action": "open_message"
  }
}
```

### Actions disponibles
- `open_message` → Ouvrir le message dans l'application
- `open_support` → Ouvrir la demande de support
- `open_notification` → Ouvrir la notification officielle

---

## 🔄 NOUVELLES MÉTHODES AJOUTÉES

### Service Push Notifications
- `send_to_partners()` → Envoyer notifications aux partenaires
- `_get_partner_tokens()` → Récupérer tokens des partenaires

### Cache Redis
- `cache_partner_tokens()` → Mettre en cache les tokens partenaires
- `get_cached_partner_tokens()` → Récupérer tokens partenaires du cache

### Logique Intelligente
- **Détection automatique** du type d'utilisateur (admin/partenaire)
- **Notifications ciblées** selon le type d'expéditeur
- **Cache optimisé** pour les performances
