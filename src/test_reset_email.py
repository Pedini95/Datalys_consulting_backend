#!/usr/bin/env python3
"""
Test de l'email de réinitialisation de mot de passe
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Créer un contexte Flask minimal
from flask import Flask
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialiser Flask-Mail
from flask_mail import Mail
mail = Mail(app)

# Importer après l'initialisation de Flask
from utils.notification import EmailService

def test_reset_email():
    """
    Tester l'email de réinitialisation
    """
    print("=== Test Email de Réinitialisation ===")
    
    with app.app_context():
        try:
            email_service = EmailService()
            
            # Test avec un token fictif
            test_token = "test_reset_token_12345"
            reset_url = f"https://applicationweb.datalysconsulting.com/mot-de-passe-oublie?token={test_token}"
            
            success = email_service.send_password_reset_email(
                user_email="yablaiyablairubenvirgil@gmail.com",
                user_name="yablai",
                reset_url=reset_url,
                expires_in="1 heure"
            )
            
            if success:
                print("✅ Email de réinitialisation envoyé avec succès")
                print("Vérifiez votre boîte de réception")
            else:
                print("❌ Échec de l'envoi de l'email de réinitialisation")
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Test Email de Réinitialisation - Datalys Consulting")
    print("=" * 50)
    
    test_reset_email()
    
    print("\n" + "=" * 50)
    print("Test terminé") 