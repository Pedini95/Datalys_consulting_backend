# 📧 Envoi d'Email avec Credentials pour les Partenaires

## 🎯 Vue d'ensemble

Cette fonctionnalité permet d'envoyer automatiquement un email contenant les identifiants de connexion lorsqu'un administrateur crée un nouveau partenaire dans la plateforme.

## ✨ Fonctionnalités

### ✅ **Fonctionnalités Implémentées**

- ✅ **Création automatique** d'un compte utilisateur pour chaque partenaire
- ✅ **Génération sécurisée** de mot de passe temporaire
- ✅ **Assignation automatique** du rôle 'partner'
- ✅ **Envoi d'email** avec les credentials de connexion
- ✅ **Template HTML** professionnel et responsive
- ✅ **Instructions de sécurité** incluses
- ✅ **Compatibilité** avec les modes JSON et multipart
- ✅ **Gestion d'erreurs** complète

### 🔧 **Workflow Automatique**

1. **Admin crée un partenaire** via l'API `/partners/create`
2. **Système génère** un mot de passe temporaire sécurisé
3. **Création automatique** d'un utilisateur avec le rôle 'partner'
4. **Envoi d'email** avec les credentials au partenaire
5. **Partenaire peut se connecter** immédiatement

## 📡 API Endpoints

### **POST /partners/create**

**URL :** `http://localhost:5000/partners/create`

**Headers requis :**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## 🔄 Modes de Fonctionnement

### **Mode 1 : JSON Classique**

**Content-Type :** `application/json`

**Payload :**
```json
{
  "user": {"id": 1},
  "datas": [{
    "name": "TechCorp",
    "email": "contact@techcorp.com",
    "phone": "+1234567890",
    "address": "123 Tech Street, City",
    "is_active": true
  }]
}
```

### **Mode 2 : Multipart avec Logo**

**Content-Type :** `multipart/form-data`

**Payload :**
```
data: {"name": "TechCorp", "email": "contact@techcorp.com", "phone": "+1234567890", "address": "123 Tech Street, City", "is_active": true}
user: {"id": 1}
logo: [fichier image]
```

## 📧 Contenu de l'Email

### **Sujet :**
```
🎉 Bienvenue chez Datalys Consulting - Vos identifiants de connexion
```

### **Contenu :**
- **En-tête** : Logo et message de bienvenue
- **Identifiants** : Email, nom d'utilisateur, mot de passe temporaire
- **Bouton de connexion** : Lien direct vers la page de connexion
- **Instructions de sécurité** : Recommandations importantes
- **Fonctionnalités** : Liste des possibilités une fois connecté

### **Sécurité :**
- Mot de passe temporaire généré automatiquement
- Recommandation de changement lors de la première connexion
- Avertissements de sécurité inclus

## 🗄️ Structure de Base de Données

### **Création Automatique :**

```sql
-- 1. Création du partenaire
INSERT INTO partners (name, email, phone, address, is_active, ...)
VALUES ('TechCorp', 'contact@techcorp.com', '+1234567890', '123 Tech Street', true, ...);

-- 2. Création du rôle 'partner' (si n'existe pas)
INSERT INTO roles (name, is_active) VALUES ('partner', true);

-- 3. Création de l'utilisateur associé
INSERT INTO users (name, email, password_hash, role_id, is_active, ...)
VALUES ('TechCorp', 'contact@techcorp.com', 'encrypted_temp_password', 
        (SELECT id FROM roles WHERE name = 'partner'), true, ...);
```

## 🔐 Gestion des Rôles

### **Rôle 'partner' :**
- **Création automatique** si n'existe pas
- **Assignation automatique** à l'utilisateur partenaire
- **Permissions** : Accès au dashboard partenaire, projets, incidents

### **Sécurité :**
- **Middleware de sécurité** compatible avec le rôle 'partner'
- **Filtrage automatique** des données selon le rôle
- **Accès restreint** aux projets du partenaire uniquement

## 🛠️ Configuration

### **Variables d'Environnement Requises :**

```env
# Configuration SMTP - SSL sur port 465
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=appweb@datalysconsulting.com
MAIL_PASSWORD=votre_mot_de_passe
MAIL_DEFAULT_SENDER=appweb@datalysconsulting.com

# Configuration de l'application
SENDER_NAME=Datalys Consulting
APP_URL=https://applicationweb.datalysconsulting.com
```

## 📋 Tests

### **Script de Test :**

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le test
python test_partner_role.py
```

### **Test Manuel :**

```bash
# Test avec cURL
curl -X POST http://localhost:5000/partners/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"id": 1},
    "datas": [{
      "name": "Test Partner",
      "email": "test@example.com",
      "phone": "+1234567890",
      "address": "123 Test Street",
      "is_active": true
    }]
  }'
```

## 🚀 Avantages

### **Pour les Administrateurs :**
- **Workflow simplifié** : Une seule action pour créer partenaire + compte
- **Moins d'erreurs** : Pas de création manuelle de comptes
- **Traçabilité** : Logs complets des créations

### **Pour les Partenaires :**
- **Accès immédiat** : Credentials reçus par email
- **Interface dédiée** : Dashboard partenaire personnalisé
- **Sécurité** : Mot de passe temporaire sécurisé

### **Pour le Système :**
- **Cohérence** : Chaque partenaire a un compte utilisateur
- **Sécurité** : Contrôle d'accès basé sur les rôles
- **Évolutivité** : Architecture prête pour de nouvelles fonctionnalités

## 🔍 Dépannage

### **Problèmes Courants :**

1. **Email non envoyé** : Vérifier la configuration SMTP
2. **Rôle non créé** : Vérifier les permissions de base de données
3. **Mot de passe non généré** : Vérifier les dépendances Python

### **Logs :**
- **Création réussie** : `"Partenaire et utilisateur créés avec succès"`
- **Email envoyé** : `"Email avec credentials envoyé au partenaire"`
- **Erreurs** : Logs détaillés dans les fichiers de log

## 📝 Notes Techniques

### **Compatibilité :**
- ✅ **Code existant** : Aucun impact sur les fonctionnalités existantes
- ✅ **Base de données** : Pas de migration requise
- ✅ **API** : Rétrocompatible avec les anciennes versions

### **Sécurité :**
- ✅ **Mots de passe** : Génération cryptographiquement sécurisée
- ✅ **Encryption** : Mots de passe hashés avant stockage
- ✅ **Rôles** : Contrôle d'accès granulaire

### **Performance :**
- ✅ **Transaction** : Création atomique (partenaire + utilisateur)
- ✅ **Rollback** : Gestion automatique des erreurs
- ✅ **Logs** : Traçabilité complète 