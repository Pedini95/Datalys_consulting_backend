# 📧 Configuration Email - Hostinger VPS

Ce guide explique comment configurer l'envoi d'emails automatiques avec votre serveur VPS Hostinger.

## 🎯 Fonctionnalités Disponibles

- ✅ **Emails de bienvenue** pour les nouveaux utilisateurs
- ✅ **Emails de réinitialisation** de mot de passe
- ✅ **Emails d'invitation** pour rejoindre des projets
- ✅ **Emails personnalisés** avec templates HTML
- ✅ **Pièces jointes** supportées
- ✅ **Configuration SMTP** sécurisée

## 🔧 Configuration SMTP Hostinger

### 1. Créer un Compte Email

1. Connectez-vous à votre **panneau de contrôle Hostinger**
2. Allez dans **"Email"** > **"Comptes email"**
3. Cliquez sur **"Créer un compte email"**
4. Configurez :
   - **Adresse email** : `noreply@votredomaine.com`
   - **Mot de passe** : Choisissez un mot de passe fort
   - **Quota** : 1 GB minimum
5. Cliquez sur **"Créer"**

### 2. Configuration des Variables d'Environnement

Configurez les variables d'environnement dans le fichier `.env.local` :

```env
# Configuration SMTP Hostinger - SSL sur port 465
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=datalysconsultingapp@datalysconsulting.com
MAIL_PASSWORD=votre_mot_de_passe
MAIL_DEFAULT_SENDER=datalysconsultingapp@datalysconsulting.com

# Configuration de l'expéditeur
SENDER_NAME=Datalys Consulting

# URL de l'application
APP_URL=https://votredomaine.com
```

### 3. Vérification de la Configuration

Testez votre configuration :

```bash
cd src
python examples/email_examples.py
```

## 📧 Types d'Emails Disponibles

### 1. Email de Bienvenue

Envoyé automatiquement lors de la création d'un compte utilisateur.

```python
from utils.notification import EmailService

email_service = EmailService()
email_service.send_welcome_email(
    user_email="nouveau@example.com",
    user_name="John Doe",
    login_url="https://votredomaine.com/login"
)
```

### 2. Email de Réinitialisation de Mot de Passe

Envoyé automatiquement lors d'une demande de reset.

```python
email_service.send_password_reset_email(
    user_email="user@example.com",
    user_name="Jane Smith",
    reset_url="https://votredomaine.com/reset-password?token=abc123",
    expires_in="1 heure"
)
```

### 3. Email d'Invitation

Pour inviter des utilisateurs à rejoindre des projets.

```python
email_service.send_user_invitation_email(
    user_email="invite@example.com",
    user_name="Alice Johnson",
    invitation_url="https://votredomaine.com/invitation?token=xyz789",
    inviter_name="Bob Manager",
    project_name="Projet Alpha"
)
```

### 4. Email Personnalisé

Pour envoyer des emails personnalisés.

```python
email_service.send_email(
    to_email="destinataire@example.com",
    subject="Sujet de l'email",
    html_content="<h1>Contenu HTML</h1><p>Message personnalisé</p>",
    text_content="Version texte du message",
    attachments=[
        {
            'filename': 'document.pdf',
            'content': pdf_content,
            'content_type': 'application/pdf'
        }
    ]
)
```

## 🎨 Templates d'Emails

L'application utilise des templates Flask HTML pour les emails. Les templates sont situés dans `src/templates/` :

### Templates Disponibles

- **`email_welcome.html`** - Email de bienvenue pour les nouveaux utilisateurs
- **`email_password_reset.html`** - Email de réinitialisation de mot de passe
- **`email_invitation.html`** - Email d'invitation pour rejoindre des projets
- **`email_template_identifiant.html`** - Template existant pour les identifiants

### Structure des Templates

Tous les templates suivent le même style que le template existant :

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .email-container {
            margin: auto;
        }
        .footer {
            width: 100%;
            text-align: left;
            font-family: Arial, sans-serif;
            font-size: 12px;
            color: #666;
        }
        .footer img {
            float: right;
            width: 100px;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="email-container" style="border: 1px solid #ddd; padding: 20px; font-family: Arial, sans-serif;">
        <!-- Contenu de l'email -->
        <div class="footer">
            <p>Envoyé par {{ sender_name }} <img src="{{ logo_url }}" alt="Logo" style="width: 50px;"></p>
        </div>
    </div>
</body>
</html>
```

### Variables Disponibles

- `{{ user_name }}` - Nom de l'utilisateur
- `{{ sender_name }}` - Nom de l'expéditeur
- `{{ logo_url }}` - URL du logo (générée automatiquement)
- `{{ login_url }}` - URL de connexion
- `{{ reset_url }}` - URL de réinitialisation
- `{{ invitation_url }}` - URL d'invitation
- `{{ inviter_name }}` - Nom de l'inviteur
- `{{ project_name }}` - Nom du projet (optionnel)
- `{{ expires_in }}` - Durée de validité du lien

## 🔒 Sécurité

### Bonnes Pratiques

1. **Utilisez HTTPS** en production
2. **Changez régulièrement** le mot de passe du compte email
3. **Limitez les permissions** du compte email
4. **Monitorer** les envois d'emails
5. **Utilisez des templates** sécurisés (pas d'injection HTML)

### Configuration Sécurisée

```python
# Configuration recommandée
SMTP_PORT=465  # SSL
SMTP_SERVER=smtp.hostinger.com
# Utilisez un mot de passe fort pour le compte email
```

## 🚨 Dépannage

### Erreurs Courantes

#### 1. "Authentication failed"

**Cause** : Mauvais nom d'utilisateur ou mot de passe
**Solution** : Vérifiez les identifiants dans le panneau Hostinger

#### 2. "Connection refused"

**Cause** : Port SMTP incorrect ou pare-feu
**Solution** : Utilisez le port 465 avec SSL

#### 3. "Sender address rejected"

**Cause** : Adresse d'expéditeur non autorisée
**Solution** : Utilisez l'adresse email du compte créé

### Test de Connexion

```python
from config import Config
import smtplib
import ssl

# Test de connexion SMTP SSL
config = Config()
try:
    server = smtplib.SMTP_SSL(config.MAIL_SERVER, config.MAIL_PORT)
    server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
    print("✅ Connexion SMTP SSL réussie")
    server.quit()
except Exception as e:
    print(f"❌ Erreur SMTP SSL: {e}")
```

## 📊 Monitoring

### Logs d'Envoi

L'application enregistre automatiquement :
- Tentatives d'envoi d'emails
- Succès/échecs d'envoi
- Erreurs SMTP
- Adresses des destinataires

### Métriques

- Nombre d'emails envoyés par jour
- Taux de succès d'envoi
- Types d'emails les plus envoyés
- Temps de livraison moyen

## 🔄 Intégration avec l'Application

### Dans les Services

```python
from utils.notification import EmailService

class UserService:
    def create_user(self, user_data):
        # Créer l'utilisateur
        user = self._create_user_in_db(user_data)
        
        # Envoyer l'email de bienvenue
        email_service = EmailService()
        email_service.send_welcome_email(
            user.email, 
            user.name, 
            "https://votredomaine.com/login"
        )
        
        return user
```

### Dans les Routes

```python
@app.route('/auth/reset-password-request', methods=['POST'])
def reset_password_request():
    # Logique de reset
    # L'email sera envoyé automatiquement par AuthService
    pass
```

---

**Note** : Cette configuration permet d'envoyer des emails professionnels via votre serveur VPS Hostinger. Assurez-vous de respecter les limites d'envoi de votre hébergeur. 