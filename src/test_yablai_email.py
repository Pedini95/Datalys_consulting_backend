#!/usr/bin/env python3
"""
Test spécifique pour l'email yablai
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config

def test_yablai_email():
    """
    Tester l'envoi d'un email à yablai
    """
    print("=== Test Email pour yablai ===")
    
    config = Config()
    
    if not all([config.MAIL_USERNAME, config.MAIL_PASSWORD, config.MAIL_DEFAULT_SENDER]):
        print("❌ Configuration email incomplète")
        return False
    
    # Email de test
    test_email = "yablaiyablairubenvirgil@gmail.com"
    
    try:
        # Créer le message
        message = MIMEMultipart('alternative')
        message['From'] = f"{config.SENDER_NAME} <{config.MAIL_DEFAULT_SENDER}>"
        message['To'] = test_email
        message['Subject'] = "Test Email - Datalys Consulting (yablai)"
        message['Content-Type'] = 'text/html; charset=UTF-8'
        
        # Contenu HTML avec caractères français
        html_content = """
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>Test Email - Datalys Consulting</h1>
            <p>Bonjour yablai,</p>
            <p>Ceci est un test d'envoi d'email avec encodage UTF-8.</p>
            <p>Caractères français : é, è, à, ç, ù, û, î, ô, ï, ë, ü, ÿ</p>
            <p>Si vous recevez cet email, la configuration SMTP fonctionne correctement !</p>
            <p>URL de connexion : <a href="https://applicationweb.datalysconsulting.com/connexion">Se connecter</a></p>
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
            
            print(f"✅ Email envoyé avec succès à {test_email}")
            print("Vérifiez votre boîte de réception (et le dossier spam)")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {str(e)}")
        return False

if __name__ == "__main__":
    print("Test Email pour yablai - Datalys Consulting")
    print("=" * 50)
    
    success = test_yablai_email()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test réussi !")
    else:
        print("❌ Test échoué") 