#!/usr/bin/env python3
"""
Test script pour vérifier que l'encodage UTF-8 des emails fonctionne correctement
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.notification import EmailService
from config import Config

def test_email_encoding():
    """
    Tester l'encodage UTF-8 des emails
    """
    print("=== Test d'Encodage Email UTF-8 ===")
    
    # Vérifier la configuration
    config = Config()
    if not all([config.MAIL_USERNAME, config.MAIL_PASSWORD, config.MAIL_DEFAULT_SENDER]):
        print("❌ Configuration email incomplète")
        print("Veuillez configurer les variables d'environnement dans .env.local")
        return False
    
    print("✅ Configuration email trouvée")
    
    # Créer le service email
    email_service = EmailService()
    
    # Test avec des caractères français
    test_email = "test@example.com"  # Remplacez par votre email de test
    subject = "Test Encodage UTF-8 - Datalys Consulting"
    
    # Contenu HTML avec caractères français
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Test d'Encodage UTF-8</h1>
        <p>Ceci est un test pour vérifier que l'encodage UTF-8 fonctionne correctement.</p>
        <p>Caractères français : é, è, à, ç, ù, û, î, ô, ï, ë, ü, ÿ</p>
        <p>Accents : àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ</p>
        <p>Si vous voyez ces caractères correctement, l'encodage fonctionne !</p>
    </body>
    </html>
    """
    
    # Contenu texte avec caractères français
    text_content = """
    Test d'Encodage UTF-8
    
    Ceci est un test pour vérifier que l'encodage UTF-8 fonctionne correctement.
    
    Caractères français : é, è, à, ç, ù, û, î, ô, ï, ë, ü, ÿ
    Accents : àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ
    
    Si vous voyez ces caractères correctement, l'encodage fonctionne !
    """
    
    print(f"Envoi d'un email de test à {test_email}...")
    
    try:
        # Envoyer l'email
        success = email_service.send_email(
            to_email=test_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print("✅ Email envoyé avec succès")
            print("Vérifiez votre boîte de réception pour voir si les caractères français s'affichent correctement")
        else:
            print("❌ Échec de l'envoi de l'email")
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {str(e)}")
        return False
    
    return success

def test_welcome_email_encoding():
    """
    Tester spécifiquement l'email de bienvenue
    """
    print("\n=== Test Email de Bienvenue ===")
    
    config = Config()
    if not all([config.MAIL_USERNAME, config.MAIL_PASSWORD, config.MAIL_DEFAULT_SENDER]):
        print("❌ Configuration email incomplète")
        return False
    
    email_service = EmailService()
    test_email = "test@example.com"  # Remplacez par votre email de test
    
    print(f"Envoi d'un email de bienvenue à {test_email}...")
    
    try:
        success = email_service.send_welcome_email(
            user_email=test_email,
            user_name="Jean-François Dupont",  # Nom avec caractères français
            login_url="https://applicationweb.datalysconsulting.com/connexion"
        )
        
        if success:
            print("✅ Email de bienvenue envoyé avec succès")
        else:
            print("❌ Échec de l'envoi de l'email de bienvenue")
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {str(e)}")
        return False
    
    return success

if __name__ == "__main__":
    print("Test d'encodage UTF-8 pour les emails")
    print("=" * 50)
    
    # Test 1: Email basique avec caractères français
    test1_success = test_email_encoding()
    
    # Test 2: Email de bienvenue
    test2_success = test_welcome_email_encoding()
    
    print("\n" + "=" * 50)
    if test1_success and test2_success:
        print("✅ Tous les tests d'encodage ont réussi !")
    else:
        print("❌ Certains tests ont échoué")
        print("Vérifiez la configuration SMTP et les logs pour plus de détails") 