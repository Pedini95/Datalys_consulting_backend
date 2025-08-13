"""
Exemples d'utilisation du service d'email

Ce fichier contient des exemples pour tester l'envoi d'emails.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.notification import EmailService
from config import Config

def test_email_configuration():
    """
    Tester la configuration email
    """
    print("=== Test de Configuration Email ===")
    
    config = Config()
    
    # Vérifier si la configuration est complète
    if not all([config.MAIL_USERNAME, config.MAIL_PASSWORD, config.MAIL_DEFAULT_SENDER]):
        print("❌ Configuration email incomplète")
        print("\nInstructions de configuration :")
        print("""
Configuration SMTP Hostinger VPS :

1. Dans votre panneau de contrôle Hostinger :
   - Allez dans "Email" > "Comptes email"
   - Créez un compte email (ex: noreply@votredomaine.com)
   - Notez le mot de passe

2. Configurez les variables d'environnement dans .env.local :
   MAIL_SERVER=smtp.hostinger.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=noreply@votredomaine.com
   MAIL_PASSWORD=votre_mot_de_passe
   MAIL_DEFAULT_SENDER=noreply@votredomaine.com
   SENDER_NAME=Datalys Consulting
   APP_URL=https://votredomaine.com
        """)
        return False
    
    print("✅ Configuration email complète")
    print(f"SMTP Server: {config.MAIL_SERVER}")
    print(f"SMTP Port: {config.MAIL_PORT}")
    print(f"Sender Email: {config.MAIL_DEFAULT_SENDER}")
    print(f"Sender Name: {config.SENDER_NAME}")
    
    return True

def test_basic_email():
    """
    Tester l'envoi d'un email basique
    """
    print("\n=== Test Email Basique ===")
    
    email_service = EmailService()
    
    # Email de test
    to_email = "test@example.com"  # Remplacez par votre email de test
    subject = "Test Email - Datalys Consulting"
    html_content = """
    <html>
    <body>
        <h1>Test Email</h1>
        <p>Ceci est un test d'envoi d'email via SMTP Hostinger.</p>
        <p>Si vous recevez cet email, la configuration SMTP fonctionne correctement !</p>
    </body>
    </html>
    """
    
    success = email_service.send_email(to_email, subject, html_content)
    
    if success:
        print("✅ Email envoyé avec succès")
    else:
        print("❌ Échec de l'envoi de l'email")
    
    return success

def test_welcome_email():
    """
    Tester l'envoi d'un email de bienvenue
    """
    print("\n=== Test Email de Bienvenue ===")
    
    email_service = EmailService()
    
    # Données de test
    user_email = "nouveau@example.com"  # Remplacez par votre email de test
    user_name = "John Doe"
    login_url = "https://votredomaine.com/login"
    
    success = email_service.send_welcome_email(user_email, user_name, login_url)
    
    if success:
        print("✅ Email de bienvenue envoyé avec succès")
    else:
        print("❌ Échec de l'envoi de l'email de bienvenue")
    
    return success

def test_password_reset_email():
    """
    Tester l'envoi d'un email de réinitialisation de mot de passe
    """
    print("\n=== Test Email de Réinitialisation ===")
    
    email_service = EmailService()
    
    # Données de test
    user_email = "reset@example.com"  # Remplacez par votre email de test
    user_name = "Jane Smith"
    reset_url = "https://votredomaine.com/reset-password?token=abc123"
    
    success = email_service.send_password_reset_email(user_email, user_name, reset_url)
    
    if success:
        print("✅ Email de réinitialisation envoyé avec succès")
    else:
        print("❌ Échec de l'envoi de l'email de réinitialisation")
    
    return success

def test_invitation_email():
    """
    Tester l'envoi d'un email d'invitation
    """
    print("\n=== Test Email d'Invitation ===")
    
    email_service = EmailService()
    
    # Données de test
    user_email = "invite@example.com"  # Remplacez par votre email de test
    user_name = "Alice Johnson"
    invitation_url = "https://votredomaine.com/invitation?token=xyz789"
    inviter_name = "Bob Manager"
    project_name = "Projet Alpha"
    
    success = email_service.send_user_invitation_email(
        user_email, user_name, invitation_url, inviter_name, project_name
    )
    
    if success:
        print("✅ Email d'invitation envoyé avec succès")
    else:
        print("❌ Échec de l'envoi de l'email d'invitation")
    
    return success

def test_email_with_attachment():
    """
    Tester l'envoi d'un email avec pièce jointe
    """
    print("\n=== Test Email avec Pièce Jointe ===")
    
    email_service = EmailService()
    
    # Données de test
    to_email = "attachment@example.com"  # Remplacez par votre email de test
    subject = "Test Email avec Pièce Jointe"
    html_content = """
    <html>
    <body>
        <h1>Test Email avec Pièce Jointe</h1>
        <p>Cet email contient une pièce jointe de test.</p>
    </body>
    </html>
    """
    
    # Pièce jointe de test
    attachment_content = b"Ceci est le contenu d'un fichier de test."
    attachments = [{
        'filename': 'test_file.txt',
        'content': attachment_content,
        'content_type': 'text/plain'
    }]
    
    success = email_service.send_email(to_email, subject, html_content, attachments=attachments)
    
    if success:
        print("✅ Email avec pièce jointe envoyé avec succès")
    else:
        print("❌ Échec de l'envoi de l'email avec pièce jointe")
    
    return success

def run_all_email_tests():
    """
    Exécuter tous les tests d'email
    """
    print("🚀 Démarrage des tests d'email\n")
    
    # Vérifier la configuration
    if not test_email_configuration():
        print("\n❌ Impossible de continuer sans configuration email")
        return
    
    # Tests d'envoi d'emails
    tests = [
        ("Email basique", test_basic_email),
        ("Email de bienvenue", test_welcome_email),
        ("Email de réinitialisation", test_password_reset_email),
        ("Email d'invitation", test_invitation_email),
        ("Email avec pièce jointe", test_email_with_attachment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test '{test_name}': {str(e)}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
    
    successful_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"\nTotal: {successful_tests}/{total_tests} tests réussis")
    
    if successful_tests == total_tests:
        print("🎉 Tous les tests d'email ont réussi !")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration SMTP.")

if __name__ == "__main__":
    run_all_email_tests() 