# 🔔 Guide d'Installation FCM (Firebase Cloud Messaging)

Ce guide vous accompagne dans l'installation et la configuration complète du système de notifications push pour Datalys Consulting.

## 📋 Vue d'ensemble

Le système FCM permet d'envoyer des notifications push automatiques aux administrateurs lors de :
- Messages avec priorité **haute** ou **critique**
- Demandes de support avec priorité **haute** ou **critique**
- Tests de notifications (endpoint de debug)

## 🚀 Installation Automatique

### Option 1: Script de Migration Automatique

```bash
cd src/
python -c "from utils.fcm_migration import setup_fcm_complete; setup_fcm_complete()"
```

Ce script va automatiquement :
- ✅ Ajouter le champ `fcm_token` à la table `users`
- ✅ Installer Firebase Admin SDK si manquant
- ✅ Vérifier tous les prérequis
- ✅ Créer les index nécessaires

### Option 2: Installation Manuelle

#### 1. Installer Firebase Admin SDK

```bash
pip install firebase-admin
```

#### 2. Exécuter la migration SQL

```sql
-- Ajouter le champ FCM token
ALTER TABLE users 
ADD COLUMN fcm_token VARCHAR(255) NULL 
COMMENT 'Token Firebase Cloud Messaging pour notifications push';

-- Ajouter l'index pour les performances
CREATE INDEX idx_users_fcm_token ON users (fcm_token);
```

## 🔧 Configuration

### 1. Configuration Firebase

1. **Créer un projet Firebase** :
   - Aller sur [Firebase Console](https://console.firebase.google.com/)
   - Créer un nouveau projet ou utiliser un existant
   - Activer **Cloud Messaging**

2. **Générer la clé de service** :
   - Project Settings → Service Accounts
   - "Generate new private key"
   - Télécharger le fichier JSON

3. **Placer le fichier de configuration** :
   ```bash
   # Copier le fichier téléchargé vers :
   src/config/firebase-service-account.json
   ```

### 2. Variables d'Environnement

Ajouter à votre fichier `.env` :

```bash
# Firebase Cloud Messaging (FCM) - Notifications Push
FIREBASE_ENABLED=True

# Notifications push automatiques
FCM_AUTO_NOTIFY_HIGH_PRIORITY=True
FCM_AUTO_NOTIFY_CRITICAL_PRIORITY=True
```

### 3. Redémarrer l'Application

```bash
# Redémarrer votre serveur Flask
python app.py
```

## 📱 Utilisation des APIs

### 1. Enregistrer un Token FCM

**Endpoint :** `POST /fcm/register-token`

```json
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
    "user_id": 123,
    "token_registered": true
  }
}
```

### 2. Supprimer un Token FCM

**Endpoint :** `POST /fcm/unregister-token`

```json
{}
```

### 3. Tester les Notifications

**Endpoint :** `POST /fcm/test-notification`

```json
{
  "title": "Test Notification",
  "body": "Ceci est un test",
  "user_id": 1  // Optionnel - si omis, envoie à tous les admins
}
```

## 🔄 Notifications Automatiques

Le système envoie automatiquement des notifications pour :

### Messages Urgents
```http
POST /messages/send
{
  "title": "Serveur en panne",
  "description": "Le serveur principal ne répond plus",
  "priority": "critique"  // 🚨 Déclenche une notification push
}
```

### Support Urgent
```http
POST /support/request
{
  "title": "Problème critique",
  "description": "Base de données inaccessible",
  "priority": "haute"     // ⚠️ Déclenche une notification push
}
```

## 🐛 Dépannage

### Vérifier le Status FCM

```python
from utils.fcm_migration import check_fcm_requirements

# Dans un context Flask
with app.app_context():
    status = check_fcm_requirements()
    print(status)
```

### Problèmes Courants

#### 1. Erreur "firebase-service-account.json non trouvé"
```bash
# Vérifier le chemin
ls -la src/config/firebase-service-account.json

# Si manquant, télécharger depuis Firebase Console
```

#### 2. Erreur "Firebase Admin SDK non disponible"
```bash
# Installer la dépendance
pip install firebase-admin

# Ou réinstaller toutes les dépendances
pip install -r requirements.txt
```

#### 3. Erreur "Token FCM invalide"
```
Le système nettoie automatiquement les tokens invalides.
Les utilisateurs doivent se reconnecter et re-enregistrer leur token.
```

#### 4. Mode Simulation (Développement)
```
Si Firebase n'est pas configuré, le système fonctionne en mode simulation.
Les logs montrent [SIMULATION] au lieu d'envoyer réellement.
```

## 📊 Logs et Monitoring

### Logs Utiles

```bash
# Filtrer les logs FCM
tail -f logs/datalys_consulting.log | grep -i fcm

# Logs d'initialisation
grep "Firebase" logs/datalys_consulting.log

# Logs de notifications
grep "notification" logs/datalys_consulting.log
```

### Messages de Status

- ✅ `Firebase initialisé avec succès`
- ⚠️ `Firebase non disponible - simulation`
- 📤 `Notification envoyée: X/Y succès`
- 🧹 `Token invalide supprimé`

## 🔒 Sécurité

### Bonnes Pratiques

1. **Fichier de Configuration** :
   - Garder `firebase-service-account.json` privé
   - Ne pas commiter dans Git
   - Utiliser des variables d'environnement en production

2. **Tokens FCM** :
   - Nettoyage automatique des tokens invalides
   - Expiration automatique si non utilisés
   - Un token par utilisateur/appareil

3. **Permissions** :
   - Seuls les utilisateurs authentifiés peuvent enregistrer des tokens
   - Seuls les admins reçoivent les notifications urgentes

## 📈 Performance

### Optimisations

- **Index Base de Données** : Index automatique sur `fcm_token`
- **Lazy Loading** : Service FCM chargé uniquement si nécessaire
- **Batch Notifications** : Notifications multiples en une seule requête
- **Nettoyage Automatique** : Suppression tokens invalides

### Métriques

- **Notifications Envoyées** : Compteur dans les logs
- **Taux de Succès** : Ratio succès/échecs
- **Tokens Actifs** : Nombre d'utilisateurs avec tokens valides

## 🚀 Prochaines Étapes

1. **Intégration Frontend** :
   - Implémenter Firebase SDK côté client
   - Enregistrer token au login
   - Gérer les notifications reçues

2. **Notifications Étendues** :
   - Notifications personnalisées par utilisateur
   - Notifications de projets spécifiques
   - Notifications programmées

3. **Analytics** :
   - Dashboard des notifications
   - Statistiques d'engagement
   - Rapports de performance

---

## 🆘 Support

Pour toute question ou problème :
1. Consulter les logs de l'application
2. Vérifier la configuration Firebase
3. Tester avec l'endpoint de test
4. Contacter l'équipe technique

**Fichiers importants :**
- `src/routes/fcm_routes.py` - Endpoints API
- `src/services/push_notification_service.py` - Service métier
- `src/utils/fcm_migration.py` - Migration et setup
- `src/config/firebase-service-account.json` - Configuration Firebase 