# 🔔 TOUTES LES ROUTES ET PAYLOADS DES NOTIFICATIONS PUSH FCM

Voici la documentation complète de toutes les routes et payloads pour les notifications push FCM dans votre application :

## 📱 **1. ROUTES FCM DIRECTES**

### **1.1 Enregistrer Token FCM**
```http
POST /fcm/register-token
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "token": "dA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6"
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

### **1.2 Supprimer Token FCM**
```http
POST /fcm/unregister-token
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{}
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "user_id": 123,
    "token_unregistered": true
  }
}
```

### **1.3 Test Notification (Admin uniquement)**
```http
POST /fcm/test-notification
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "Test Notification",
  "body": "Ceci est une notification de test",
  "user_id": 1  // Optionnel - si omis, envoie à tous les admins
}
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "notification_sent": true
  }
}
```

### **1.4 Statut du Cache Redis (Admin uniquement)**
```http
GET /fcm/cache/status
Authorization: Bearer YOUR_TOKEN
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "status": "available",
    "fcm_keys_count": 5,
    "fcm_keys": ["fcm:admin_tokens:all", "fcm:user_token:123"],
    "redis_used_memory": "2.5M",
    "redis_connected_clients": 3,
    "redis_uptime": 86400
  }
}
```

### **1.5 Vider le Cache Redis (Admin uniquement)**
```http
POST /fcm/cache/clear
Authorization: Bearer YOUR_TOKEN
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "cache_cleared": true
  }
}
```

### **1.6 Statut Public FCM (Sans authentification)**
```http
GET /fcm/status
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "fcm_enabled": true,
    "status": "available",
    "message": "Service FCM opérationnel"
  }
}
```

### **1.7 Valider Token FCM (Debug Frontend)**
```http
POST /fcm/validate-token
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "token": "dA1B2C3D4E5F6G7H8I9J0K..."
}
```

**Réponse :**
```json
{
  "code": 200,
  "message": {"type": "success"},
  "data": {
    "token_valid": true,
    "test_notification_sent": true,
    "message": "Token FCM validé et notification de test envoyée"
  }
}
```

---

## ⚡ **2. NOTIFICATIONS PUSH AUTOMATIQUES**

### **2.1 Message avec Priorité Haute/Critique**
```http
POST /messages/send
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "🚨 URGENT: Problème serveur",
  "description": "Le serveur principal ne répond plus",
  "project_id": 123,
  "priority": "critique"  // 🚨 Déclenche notification push
}
```

**Notification Push Automatique :**
```json
{
  "notification": {
    "title": "🚨 Message CRITIQUE",
    "body": "Nouveau message: 🚨 URGENT: Problème serveur"
  },
  "data": {
    "incident_id": "789",
    "type": "message",
    "priority": "critique",
    "action": "open_message"
  }
}
```

### **2.2 Demande de Support avec Priorité Haute/Critique**
```http
POST /support/request
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "⚠️ Bug critique application",
  "description": "Les utilisateurs ne peuvent plus se connecter",
  "project_id": 456,
  "priority": "haute"  // ⚠️ Déclenche notification push
}
```

**Notification Push Automatique :**
```json
{
  "notification": {
    "title": "⚠️ Support HAUTE",
    "body": "Demande de support: ⚠️ Bug critique application"
  },
  "data": {
    "incident_id": "790",
    "type": "support",
    "priority": "haute",
    "action": "open_support"
  }
}
```

---

## 📋 **3. PAYLOADS COMPLETS DES NOTIFICATIONS**

### **3.1 Structure Générale**
```json
{
  "notification": {
    "title": "Titre de la notification",
    "body": "Corps de la notification"
  },
  "data": {
    "incident_id": "ID de l'incident",
    "type": "message|support|notification",
    "priority": "basse|moyenne|haute|critique",
    "action": "open_message|open_support|open_notification",
    "timestamp": "2025-08-18T17:30:00"
  }
}
```

### **3.2 Types de Notifications**

| **Type** | **Titre** | **Action** | **Déclencheur** |
|----------|-----------|------------|-----------------|
| **Message Haute** | `⚠️ Message HAUTE` | `open_message` | `priority: "haute"` |
| **Message Critique** | `🚨 Message CRITIQUE` | `open_message` | `priority: "critique"` |
| **Support Haute** | `⚠️ Support HAUTE` | `open_support` | `priority: "haute"` |
| **Support Critique** | `🚨 Support CRITIQUE` | `open_support` | `priority: "critique"` |
| **Test** | `Test Notification` | `open_test` | Endpoint test |

---

## ⚙️ **4. CONFIGURATION DES NOTIFICATIONS**

### **4.1 Variables d'Environnement**
```bash
# Activation FCM
FIREBASE_ENABLED=True

# Notifications automatiques
FCM_AUTO_NOTIFY_HIGH_PRIORITY=True
FCM_AUTO_NOTIFY_CRITICAL_PRIORITY=True

# Configuration Redis (pour le cache FCM)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optionnel
```

### **4.2 Cache Redis FCM**
Le système utilise Redis pour mettre en cache les tokens FCM et améliorer les performances :

- **DB 0** : Sessions utilisateur
- **DB 1** : Cache FCM (tokens, statistiques)
- **TTL Tokens Admin** : 5 minutes
- **TTL Token Utilisateur** : 1 heure
- **TTL Statistiques** : 30 minutes

### **4.3 Destinataires**
- **Messages/Support urgents** → Tous les admins (`role_id = 1`)
- **Tests** → Utilisateur spécifique ou tous les admins
- **Notifications officielles** → Utilisateur assigné

---

## 🚀 **5. EXEMPLES D'UTILISATION COMPLETS**

### **5.1 Scénario Complet : Message Urgent**
```bash
# 1. Enregistrer token FCM (Frontend)
curl -X POST http://localhost:5000/api/fcm/register-token \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{"token": "dA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6"}'

# 2. Envoyer message urgent
curl -X POST http://localhost:5000/api/messages/send \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "🚨 Serveur en panne",
    "description": "Le serveur principal ne répond plus depuis 10 minutes",
    "priority": "critique",
    "project_id": 1
  }'

# → Résultat : Message sauvegardé + Notification push envoyée aux admins
```

### **5.2 Test de Notification**
```bash
# Test notification (Admin uniquement)
curl -X POST http://localhost:5000/api/fcm/test-notification \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Push",
    "body": "Ceci est une notification de test"
  }'
```

---

## 🛡️ **6. SÉCURITÉ ET PERMISSIONS**

### **6.1 Authentification Requise**
- Toutes les routes FCM nécessitent `Authorization: Bearer TOKEN`
- Token FCM lié à l'utilisateur connecté

### **6.2 Permissions Spéciales**
- **Test notifications** : Admin uniquement (`role_id = 1`)
- **Notifications automatiques** : Système interne
- **Enregistrement token** : Utilisateur authentifié

### **6.3 Nettoyage Automatique**
- Tokens invalides supprimés automatiquement
- Gestion des erreurs Firebase
- Mode dégradé si FCM non disponible

---

## 📊 **7. MONITORING ET LOGS**

### **7.1 Logs de Notifications**
```python
# Succès
logger.info("✅ Notification push envoyée pour message 789")

# Échec
logger.warning("⚠️ Échec notification push pour message 789")

# Service non disponible
logger.warning("⚠️ Service push non disponible pour message")
```

### **7.2 Statistiques**
- Nombre de notifications envoyées
- Taux de succès/échec
- Tokens invalides nettoyés
- Temps de réponse

---

## 💻 **8. INTÉGRATION FRONTEND**

### **8.1 JavaScript (Firebase SDK)**
```javascript
// Initialiser Firebase
firebase.initializeApp({
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  messagingSenderId: "123456789",
  appId: "your-app-id"
});

// Demander permission et obtenir token
const messaging = firebase.messaging();
const token = await messaging.getToken();

// Envoyer token au backend
fetch('/api/fcm/register-token', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + userToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ token: token })
});

// Écouter les notifications
messaging.onMessage((payload) => {
  console.log('Notification reçue:', payload);
  // Afficher notification ou naviguer
});
```

### **8.2 React Native (Firebase)**
```javascript
import messaging from '@react-native-firebase/messaging';

// Demander permission
const authStatus = await messaging.requestPermission();
const enabled = authStatus === messaging.AuthorizationStatus.AUTHORIZED;

// Obtenir token
const token = await messaging.getToken();

// Écouter les notifications
messaging.onMessage(async remoteMessage => {
  console.log('Notification reçue:', remoteMessage);
});
```

---

## 🔧 **9. DÉPANNAGE**

### **9.1 Problèmes Courants**

#### **Erreur "Service push non initialisé"**
```bash
# Vérifier la configuration Firebase
ls -la src/config/firebase-service-account.json

# Vérifier les variables d'environnement
echo $FIREBASE_ENABLED
```

#### **Erreur "Token FCM invalide"**
```bash
# Le système nettoie automatiquement les tokens invalides
# Vérifier les logs pour voir les tokens supprimés
tail -f logs/datalys_consulting.log | grep "Token invalide"
```

#### **Notifications non reçues**
```bash
# Tester le service
curl -X POST http://localhost:5000/api/fcm/test-notification \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"title": "Test", "body": "Test"}'
```

#### **Problèmes de Cache Redis**
```bash
# Vérifier le statut du cache
curl -X GET http://localhost:5000/api/fcm/cache/status \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Vider le cache si nécessaire
curl -X POST http://localhost:5000/api/fcm/cache/clear \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Tester la connexion Redis
redis-cli ping
redis-cli info memory
```

### **9.2 Vérification du Service**
```python
# Dans un shell Python
from services.push_notification_service import push_service
print(f"Service disponible: {push_service is not None}")
print(f"Service activé: {push_service.is_enabled() if push_service else False}")

# Vérifier le cache
if push_service and hasattr(push_service, 'fcm_cache'):
    cache_info = push_service.fcm_cache.get_cache_info()
    print(f"Cache status: {cache_info.get('status')}")
```

### **9.3 Test du Cache Redis FCM**
```bash
# Exécuter le script de test complet
cd src/
python test_fcm_cache.py
```

---

## 📈 **10. MÉTRIQUES ET ANALYTICS**

### **10.1 Métriques à Surveiller**
- **Taux de livraison** : % de notifications reçues
- **Temps de réponse** : Délai entre déclenchement et réception
- **Tokens actifs** : Nombre de tokens FCM valides
- **Erreurs Firebase** : Types et fréquences d'erreurs

### **10.2 Logs d'Audit**
```python
# Exemple de log d'audit
{
  "timestamp": "2025-08-18T17:30:00",
  "action": "push_notification_sent",
  "user_id": 123,
  "notification_type": "message_critical",
  "recipients_count": 5,
  "success_count": 4,
  "failure_count": 1
}
```

---

## 🎯 **11. ROADMAP FUTURE**

### **11.1 Fonctionnalités Planifiées**
- [ ] **Notifications par email** pour incidents critiques
- [ ] **Webhooks** pour intégrations tierces (Slack, Teams)
- [ ] **Notifications mobiles** via apps dédiées
- [ ] **Analytics** des communications (temps de réponse, etc.)
- [ ] **Templates** de messages prédéfinis
- [ ] **Escalation automatique** selon la priorité
- [ ] **API GraphQL** pour queries complexes

### **11.2 Améliorations Techniques**
- [x] **Cache Redis** pour les tokens FCM ✅
- [ ] **Batch processing** pour notifications multiples
- [ ] **Retry mechanism** pour échecs temporaires
- [ ] **Rate limiting** pour éviter le spam
- [ ] **A/B testing** pour optimiser les notifications

---

## 📞 **12. SUPPORT**

### **12.1 Ressources**
- **Documentation Firebase** : [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- **Guide d'installation** : `docs/FCM_SETUP_GUIDE.md`
- **APIs de communication** : `docs/COMMUNICATION_APIS.md`

### **12.2 Contact**
Pour toute question ou problème :
1. Consulter les logs de l'application
2. Vérifier la configuration Firebase
3. Tester avec l'endpoint de test
4. Contacter l'équipe technique

---

## 📝 **13. CHANGELOG**

### **Version 1.1.0** (2025-08-18)
- ✅ Cache Redis pour les tokens FCM
- ✅ Optimisation des performances
- ✅ Endpoints de gestion du cache
- ✅ Invalidation automatique du cache
- ✅ Script de test complet

### **Version 1.0.0** (2025-08-18)
- ✅ Implémentation complète FCM
- ✅ Notifications automatiques pour messages/support urgents
- ✅ Endpoints de gestion des tokens
- ✅ Mode dégradé sans Firebase
- ✅ Nettoyage automatique des tokens invalides
- ✅ Documentation complète

---

*Dernière mise à jour : 2025-08-18* 