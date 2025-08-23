from flask import jsonify, render_template, current_app
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
from flask_mail import Message
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def send_email(to_email, subject, body):
    from_email = current_app.config['MAIL_USERNAME']
    from_password = current_app.config['MAIL_PASSWORD']
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Content-Type'] = 'text/plain; charset=UTF-8'
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        # Utiliser SMTP_SSL pour le port 465
        server = smtplib.SMTP_SSL(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.login(from_email, from_password)
        text = msg.as_string()
        # Convertir en bytes UTF-8 si nécessaire
        if isinstance(text, str):
            text = text.encode('utf-8')
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        return jsonify({'message': 'ERROR', 'details': str(e)}), 500



def send_mail_registration(datas, emails):
    msg = Message("REGISTRATION FIBER",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=emails)
    # Définir l'encodage UTF-8 pour Flask-Mail
    msg.charset = 'utf-8'
    current_app.extensions['mail'].send(msg)

def send_mail_login(emails, password):
    msg = Message("IDENTIFIER",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=emails)
    # Définir l'encodage UTF-8 pour Flask-Mail
    msg.charset = 'utf-8'
    current_app.extensions['mail'].send(msg)


class EmailService:
    """
    Service pour l'envoi d'emails via SMTP
    Compatible avec Hostinger VPS
    """
    
    def __init__(self):
        # Configuration SMTP depuis config.py
        from config import Config
        config = Config()
        
        self.smtp_server = config.MAIL_SERVER
        self.smtp_port = config.MAIL_PORT
        self.smtp_username = config.MAIL_USERNAME
        self.smtp_password = config.MAIL_PASSWORD
        self.sender_email = config.MAIL_DEFAULT_SENDER
        self.sender_name = config.SENDER_NAME
        
        # Vérifier la configuration
        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            logger.warning("Configuration SMTP incomplète. Les emails ne seront pas envoyés.")
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: Optional[str] = None, attachments: Optional[List[Dict]] = None) -> bool:
        """
        Envoyer un email
        
        Args:
            to_email: Email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML
            text_content: Contenu texte (optionnel)
            attachments: Liste des pièces jointes (optionnel)
            
        Returns:
            True si l'email a été envoyé avec succès
        """
        try:
            # Créer le message avec encodage UTF-8
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            message['Content-Type'] = 'text/html; charset=UTF-8'
            
            # Ajouter le contenu texte
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(text_part)
            
            # Ajouter le contenu HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # Ajouter les pièces jointes
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Envoyer l'email
            return self._send_smtp(message)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
            return False
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """
        Ajouter une pièce jointe au message
        
        Args:
            message: Message MIME
            attachment: Dictionnaire avec 'filename', 'content', 'content_type'
        """
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['content'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            message.attach(part)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la pièce jointe: {str(e)}")
    
    def _send_smtp(self, message: MIMEMultipart) -> bool:
        """
        Envoyer l'email via SMTP avec TLS sur le port 587
        
        Args:
            message: Message MIME à envoyer
            
        Returns:
            True si l'envoi a réussi
        """
        try:
            # Utiliser SMTP avec TLS pour le port 587
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(self.smtp_username, self.smtp_password)
                
                # Envoyer l'email avec encodage UTF-8 explicite
                text = message.as_string()
                # Convertir en bytes UTF-8 si nécessaire
                if isinstance(text, str):
                    text = text.encode('utf-8')
                server.sendmail(self.sender_email, message['To'], text)
                
                logger.info(f"Email envoyé avec succès à {message['To']}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur SMTP TLS: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str, login_url: str) -> bool:
        """
        Envoyer un email de bienvenue
        
        Args:
            user_email: Email de l'utilisateur
            user_name: Nom de l'utilisateur
            login_url: URL de connexion
            
        Returns:
            True si l'email a été envoyé
        """
        subject = f"Bienvenue sur {self.sender_name}"
        
        # Utiliser le template Flask
        #         logo_url = "https://datalysconsulting.com/static/image/logo.png"  # URL absolue
        html_content = render_template('email_welcome.html',
            user_name=user_name,
            login_url=login_url,
            sender_name=self.sender_name,
        )
        
        return self.send_email(user_email, subject, html_content)
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_url: str, 
                                 expires_in: str = "1 heure") -> bool:
        """
        Envoyer un email de réinitialisation de mot de passe
        
        Args:
            user_email: Email de l'utilisateur
            user_name: Nom de l'utilisateur
            reset_url: URL de réinitialisation
            expires_in: Durée de validité du lien
            
        Returns:
            True si l'email a été envoyé
        """
        subject = f"Réinitialisation de votre mot de passe - {self.sender_name}"
        
        # Utiliser le template Flask
        #         logo_url = "https://datalysconsulting.com/static/image/logo.png"  # URL absolue
        html_content = render_template('email_password_reset.html',
            user_name=user_name,
            reset_url=reset_url,
            expires_in=expires_in,
            sender_name=self.sender_name,
        )
        
        return self.send_email(user_email, subject, html_content)
    
    def send_partner_credentials_email(self, partner_email: str, partner_name: str, email: str, 
                                     password: str, app_url: str) -> bool:
        """
        Envoyer un email avec les credentials d'un partenaire
        
        Args:
            partner_email: Email du partenaire
            partner_name: Nom du partenaire
            email: Email de connexion
            password: Mot de passe temporaire
            app_url: URL de l'application
            
        Returns:
            True si l'email a été envoyé
        """
        subject = f"Vos identifiants de connexion - {self.sender_name}"
        
        # Utiliser le template Flask
        #         logo_url = "https://datalysconsulting.com/static/image/logo.png"  # URL absolue
        html_content = render_template('email_partner_credentials.html',
            partner_name=partner_name,
            email=email,
            password=password,
            app_url=app_url,
            sender_name=self.sender_name,
            sender_email=self.sender_email,
        )
        
        return self.send_email(partner_email, subject, html_content)
    

    
    def send_incident_alert(self, to_email: str, partner_name: str, email_data: Dict[str, Any]) -> bool:
        """
        Envoyer un email d'alerte d'incident aux partenaires
        
        Args:
            to_email: Email du partenaire
            partner_name: Nom du partenaire
            email_data: Données de l'incident
            
        Returns:
            True si l'email a été envoyé
        """
        subject = f"🚨 ALERTE INCIDENT - Projet {email_data.get('project_title', 'N/A')}"
        
        # Créer le contenu HTML de l'alerte
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; border-radius: 5px; text-align: center; margin-bottom: 20px; }}
                .alert-icon {{ font-size: 48px; margin-bottom: 10px; }}
                .incident-details {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #495057; }}
                .value {{ color: #212529; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="alert-icon">🚨</div>
                    <h1>ALERTE INCIDENT</h1>
                    <p>Un incident a été signalé sur votre projet</p>
                </div>
                
                <div class="incident-details">
                    <div class="detail-row">
                        <span class="label">Partenaire :</span>
                        <span class="value">{email_data.get('partner_name', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Projet :</span>
                        <span class="value">{email_data.get('project_title', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Titre de l'incident :</span>
                        <span class="value">{email_data.get('incident_title', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Description :</span>
                        <span class="value">{email_data.get('incident_description', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Signalé par :</span>
                        <span class="value">{email_data.get('creator_name', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Assigné à :</span>
                        <span class="value">{email_data.get('assigned_user', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">ID de l'incident :</span>
                        <span class="value">#{email_data.get('incident_id', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Date de création :</span>
                        <span class="value">{email_data.get('created_at', 'N/A')}</span>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par {self.sender_name}</p>
                    <p>Veuillez contacter l'équipe de support pour plus d'informations.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)
    
    def send_partner_credentials(self, partner_email: str, partner_name: str, username: str, password: str) -> bool:
        """
        Envoyer les identifiants de connexion à un nouveau partenaire
        
        Args:
            partner_email: Email du partenaire
            partner_name: Nom du partenaire
            username: Nom d'utilisateur généré
            password: Mot de passe temporaire
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = f"🚀 Bienvenue dans l'écosystème Datalys Consulting - Accès à votre espace partenaire"
        
        # URL de l'application (configurable via variable d'environnement)
        app_url = current_app.config.get('APP_URL', 'https://applicationweb.datalysconsulting.com/connexion')
        
        # Utiliser le template Flask professionnel
        html_content = render_template('email_partner_credentials.html',
            email=partner_email,
            partner_name=partner_name,
            username=username,
            password=password,
            app_url=app_url,
            sender_email=self.smtp_username,
            sender_name=self.sender_name
        )
        
        return self.send_email(partner_email, subject, html_content)
    


