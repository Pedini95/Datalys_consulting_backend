#!/usr/bin/env python3
"""
Test spécifique pour l'email de réinitialisation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config

def test_reset_email_direct():
    """
    Test direct de l'email de réinitialisation
    """
    print("=== Test Direct Email de Réinitialisation ===")
    
    config = Config()
    
    if not all([config.MAIL_USERNAME, config.MAIL_PASSWORD, config.MAIL_DEFAULT_SENDER]):
        print("❌ Configuration email incomplète")
        return False
    
    # Email de test
    test_email = "nonssekone@gmail.com"
    
    try:
        # Créer le message
        message = MIMEMultipart('alternative')
        message['From'] = f"{config.SENDER_NAME} <{config.MAIL_DEFAULT_SENDER}>"
        message['To'] = test_email
        message['Subject'] = "Test Réinitialisation - Datalys Consulting"
        message['Content-Type'] = 'text/html; charset=UTF-8'
        
        # Contenu HTML avec caractères français
        html_content = """
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>Test Email de Réinitialisation</h1>
            <p>Bonjour,</p>
            <p>Ceci est un test d'email de réinitialisation de mot de passe.</p>
            <p>Caractères français : é, è, à, ç, ù, û, î, ô, ï, ë, ü, ÿ</p>
            <p>Si vous recevez cet email, la configuration SMTP fonctionne correctement !</p>
            <p>Lien de réinitialisation : <a href="https://applicationweb.datalysconsulting.com/mot-de-passe-oublie?token=test123">Réinitialiser mon mot de passe</a></p>
            <p>Ce lien expire dans 1 heure.</p>
            <p>Date d'envoi : """ + str(__import__('datetime').datetime.now()) + """</p>
        </body>
        </html>
        """
        
        # Ajouter le contenu HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        # Envoyer l'email
        context = ssl.create_default_context()
        
        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
            server.starttls(context=context)
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            
            # Envoyer avec encodage UTF-8
            text = message.as_string()
            if isinstance(text, str):
                text = text.encode('utf-8')
            server.sendmail(config.MAIL_DEFAULT_SENDER, test_email, text)
            
            print(f"✅ Email de test envoyé avec succès à {test_email}")
            print("Vérifiez votre boîte de réception (et le dossier spam)")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Test Direct Email de Réinitialisation - Datalys Consulting")
    print("=" * 60)
    
    success = test_reset_email_direct()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test réussi !")
        print("Si vous ne recevez pas l'email, vérifiez :")
        print("1. Le dossier spam/indésirable")
        print("2. Les filtres Gmail")
        print("3. Ajoutez l'expéditeur à vos contacts")
    else:
        print("❌ Test échoué")
        print("Vérifiez la configuration SMTP") 