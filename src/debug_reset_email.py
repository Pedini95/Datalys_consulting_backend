#!/usr/bin/env python3
"""
Debug script pour tester l'email de réinitialisation étape par étape
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

def debug_reset_email():
    """
    Debug de l'email de réinitialisation
    """
    print("=== Debug Email de Réinitialisation ===")
    
    with app.app_context():
        try:
            # Test 1: Import EmailService
            print("1. Test import EmailService...")
            from utils.notification import EmailService
            print("✅ Import EmailService réussi")
            
            # Test 2: Création de l'instance
            print("2. Test création EmailService...")
            email_service = EmailService()
            print("✅ EmailService créé")
            
            # Test 3: Test de la méthode send_password_reset_email
            print("3. Test send_password_reset_email...")
            
            test_token = "debug_test_token_12345"
            reset_url = f"https://applicationweb.datalysconsulting.com/mot-de-passe-oublie?token={test_token}"
            
            success = email_service.send_password_reset_email(
                user_email="nonssekone@gmail.com",
                user_name="Test User",
                reset_url=reset_url,
                expires_in="1 heure"
            )
            
            print(f"✅ Résultat: {success}")
            
            if success:
                print("✅ Email de réinitialisation envoyé avec succès")
            else:
                print("❌ Échec de l'envoi de l'email de réinitialisation")
                
        except Exception as e:
            print(f"❌ Erreur lors du debug: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("Debug Email de Réinitialisation - Datalys Consulting")
    print("=" * 60)
    
    debug_reset_email()
    
    print("\n" + "=" * 60)
    print("Debug terminé") 