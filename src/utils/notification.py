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
import threading
import time

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

        self.smtp_server = Config.MAIL_SERVER
        self.smtp_port = Config.MAIL_PORT
        self.smtp_username = Config.MAIL_USERNAME
        self.smtp_password = Config.MAIL_PASSWORD
        self.sender_email = Config.MAIL_DEFAULT_SENDER
        self.sender_name = Config.SENDER_NAME
        
        # Vérifier la configuration
        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            logger.warning("Configuration SMTP incomplète. Les emails ne seront pas envoyés.")

    def get_logo_base64(self) -> str:
        """
        Lire le logo et l'encoder en base64 pour l'intégrer dans les emails

        Returns:
            String base64 du logo au format data URI ou string vide si erreur
        """
        import base64
        import os

        try:
            # Chemin vers le logo (relatif au fichier notification.py)
            logo_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'static', 'image', 'logodatalys_email.jpg'
            )

            # Lire le fichier et encoder en base64
            with open(logo_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_string}"
        except Exception as e:
            logger.error(f"Erreur lors de l'encodage du logo: {str(e)}")
            return ""

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
    
    def send_email_async(self, to_email: str, subject: str, html_content: str, 
                        text_content: Optional[str] = None, attachments: Optional[List[Dict]] = None):
        """
        Envoyer un email de manière asynchrone (non-bloquante)
        
        Cette méthode lance l'envoi de l'email dans un thread séparé et retourne immédiatement.
        Idéal pour les emails MFA, notifications, etc. où on ne veut pas bloquer la réponse HTTP.
        
        Args:
            to_email: Email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML
            text_content: Contenu texte (optionnel)
            attachments: Liste des pièces jointes (optionnel)
        """
        def _send_in_background():
            """Fonction exécutée dans le thread en arrière-plan"""
            try:
                start_time = time.time()
                logger.info(f"📧 [Thread] Envoi asynchrone d'email à {to_email} - Sujet: {subject[:50]}...")
                
                # Créer le message MIME directement (pas besoin du contexte Flask)
                message = MIMEMultipart('alternative')
                message['From'] = f"{self.sender_name} <{self.sender_email}>"
                message['To'] = to_email
                message['Subject'] = subject

                # Ajouter le contenu texte si fourni
                if text_content:
                    text_part = MIMEText(text_content, 'plain', 'utf-8')
                    message.attach(text_part)
                
                # Ajouter le contenu HTML
                html_part = MIMEText(html_content, 'html', 'utf-8')
                message.attach(html_part)
                
                # Ajouter les pièces jointes si fournies
                if attachments:
                    for attachment in attachments:
                        self._add_attachment(message, attachment)
                
                # Envoyer via SMTP
                success = self._send_smtp(message)
                
                elapsed_time = time.time() - start_time
                if success:
                    logger.info(f"✅ [Thread] Email envoyé avec succès à {to_email} en {elapsed_time:.2f}s")
                else:
                    logger.error(f"❌ [Thread] Échec de l'envoi de l'email à {to_email} après {elapsed_time:.2f}s")
                    
            except Exception as e:
                logger.error(f"❌ [Thread] Erreur dans le thread d'envoi d'email à {to_email}: {str(e)}")
        
        # Lancer l'envoi dans un thread séparé (daemon=True pour qu'il se termine avec l'app)
        thread = threading.Thread(target=_send_in_background, daemon=True)
        thread.start()
        logger.info(f"⚡ Thread d'envoi d'email lancé pour {to_email} (non-bloquant)")
    
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
        Envoyer l'email via SMTP avec SSL (port 465) ou TLS (port 587)
        
        Args:
            message: Message MIME à envoyer
            
        Returns:
            True si l'envoi a réussi
        """
        try:
            # Utiliser SMTP_SSL pour le port 465 (Hostinger)
            if self.smtp_port == 465:
                logger.info(f"📧 Connexion SMTP_SSL au serveur {self.smtp_server}:{self.smtp_port}")
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=ssl.create_default_context()) as server:
                    server.login(self.smtp_username, self.smtp_password)
                    logger.info(f"✅ Authentification SMTP réussie")
                    
                    # Envoyer l'email avec encodage UTF-8 explicite
                    text = message.as_string()
                    if isinstance(text, str):
                        text = text.encode('utf-8')
                    server.sendmail(self.sender_email, message['To'], text)
                    
                    logger.info(f"✅ Email envoyé avec succès à {message['To']}")
                    return True
            
            # Utiliser SMTP avec STARTTLS pour le port 587
            else:
                logger.info(f"📧 Connexion SMTP+STARTTLS au serveur {self.smtp_server}:{self.smtp_port}")
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(self.smtp_username, self.smtp_password)
                    logger.info(f"✅ Authentification SMTP réussie")
                    
                    # Envoyer l'email avec encodage UTF-8 explicite
                    text = message.as_string()
                    if isinstance(text, str):
                        text = text.encode('utf-8')
                    server.sendmail(self.sender_email, message['To'], text)
                    
                    logger.info(f"✅ Email envoyé avec succès à {message['To']}")
                    return True
                
        except Exception as e:
            logger.error(f"❌ Erreur SMTP lors de l'envoi à {message['To']}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
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
                                     password: str, app_url: str, client_code: Optional[str] = None) -> bool:
        """
        Envoyer un email avec les credentials d'un partenaire

        Args:
            partner_email: Email du partenaire (destinataire)
            partner_name: Nom du partenaire
            email: Email de connexion (peut être le même que partner_email ou différent)
            password: Mot de passe temporaire
            app_url: URL de l'application
            client_code: Code client optionnel pour la connexion

        Returns:
            True si l'email a été envoyé
        """
        subject = f"Vos identifiants de connexion - {self.sender_name}"

        # Utiliser le template Flask
        # Construire l'URL de connexion
        login_url = f"{app_url}/connexion" if app_url else "https://applicationweb.datalysconsulting.com/connexion"

        html_content = render_template('email_partner_credentials.html',
            partner_name=partner_name,
            partner_email=email,
            client_code=client_code,
            password=password,
            login_url=login_url,
            app_url=app_url,
            sender_name=self.sender_name,
            sender_email=self.sender_email,
        )
        
        return self.send_email(partner_email, subject, html_content)
    
    def send_mfa_code_email(self, user_email: str, user_name: str, mfa_code: str) -> bool:
        """
        Envoyer un email avec le code MFA (Multi-Factor Authentication)
        
        Args:
            user_email: Email de l'utilisateur
            user_name: Nom de l'utilisateur
            mfa_code: Code MFA à 6 chiffres
            
        Returns:
            True si l'email a été envoyé avec succès
        """
        try:
            from flask import render_template
            from datetime import datetime
            
            subject = f"Code de verification - Datalys Consulting"
            
            # Préparer les données pour le template
            now = datetime.now()
            template_data = {
                'user_name': user_name,
                'user_email': user_email,
                'mfa_code': mfa_code,
                'login_date': now.strftime('%d/%m/%Y'),
                'login_time': now.strftime('%H:%M:%S')
            }
            
            # Rendre le template HTML
            html_content = render_template('email_mfa_code.html', **template_data)
            
            # ⚡ Envoyer l'email de manière ASYNCHRONE (non-bloquante)
            # Cela permet de retourner la réponse HTTP immédiatement sans attendre l'envoi de l'email
            self.send_email_async(user_email, subject, html_content)
            
            # Retourner True immédiatement (l'email sera envoyé en arrière-plan)
            logger.info(f"⚡ Email MFA programmé pour envoi asynchrone à {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de l'email MFA pour {user_email}: {str(e)}")
            return False

    def send_temp_password_email(self, user_email: str, user_name: str, temp_password: str) -> bool:
        """
        Envoyer un email avec le mot de passe temporaire

        Args:
            user_email: Email de l'utilisateur
            user_name: Nom de l'utilisateur
            temp_password: Mot de passe temporaire

        Returns:
            True si l'email a été envoyé avec succès
        """
        try:
            from datetime import datetime

            subject = "Votre nouveau mot de passe temporaire - Datalys Consulting"

            now = datetime.now()
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .password-box {{ background-color: #e8f4f8; border: 2px solid #3498db; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px; }}
                    .password {{ font-size: 24px; font-weight: bold; color: #2c3e50; letter-spacing: 2px; }}
                    .warning {{ background-color: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin-top: 15px; }}
                    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Datalys Consulting</h1>
                    </div>
                    <div class="content">
                        <p>Bonjour <strong>{user_name}</strong>,</p>
                        <p>Un administrateur a reinitialise votre mot de passe. Voici votre nouveau mot de passe temporaire :</p>
                        <div class="password-box">
                            <span class="password">{temp_password}</span>
                        </div>
                        <div class="warning">
                            <strong>Important :</strong> Ce mot de passe est temporaire. Vous serez invite a le changer lors de votre prochaine connexion.
                        </div>
                        <p>Date de reinitialisation : {now.strftime('%d/%m/%Y a %H:%M')}</p>
                    </div>
                    <div class="footer">
                        <p>Cet email a ete envoye automatiquement. Merci de ne pas y repondre.</p>
                        <p>&copy; {now.year} Datalys Consulting - Tous droits reserves</p>
                    </div>
                </div>
            </body>
            </html>
            """

            self.send_email_async(user_email, subject, html_content)
            logger.info(f"Email mot de passe temporaire programme pour {user_email}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email mot de passe temporaire pour {user_email}: {str(e)}")
            return False

    def send_incident_notification_to_experts(self, expert_email: str, expert_name: str, incident_data: Dict[str, Any]) -> bool:
        """
        Envoyer un email de notification aux experts (Admin/Manager) lors de la création d'un incident
        
        Args:
            expert_email: Email de l'expert
            expert_name: Nom de l'expert
            incident_data: Données de l'incident (incident_number, title, priority, etc.)
            
        Returns:
            True si l'email a été envoyé avec succès
        """
        try:
            from flask import render_template
            from config import Config
            
            # Préparer le sujet avec le numéro d'incident et la priorité
            # ⚠️ IMPORTANT: Pas d'emoji dans le sujet pour éviter le blocage par Gmail
            priority = incident_data.get('priority', 'P3')
            incident_number = incident_data.get('incident_number', 'N/A')
            subject = f"Nouvel incident {priority} - {incident_number} - Datalys Consulting"
            
            # Mapper les labels
            priority_labels = {
                'P0': 'Arrêt de service (immédiat)',
                'P1': 'Forte dégradation de service',
                'P2': 'Dégradation de service',
                'P3': 'Incident ordinaire',
                'P4': 'Incident mineur'
            }
            
            impact_labels = {
                'arret_service': 'Arrêt de service',
                'service_degrade': 'Service dégradé',
                'majeur': 'Impact majeur',
                'mineur': 'Impact mineur'
            }
            
            domain_labels = {
                'reseau': 'Réseau',
                'infrastructure': 'Infrastructure système',
                'cloud': 'Cloud',
                'energie': 'Énergie'
            }
            
            # Préparer les données pour le template
            template_data = {
                'expert_name': expert_name,
                'incident_number': incident_number,
                'incident_title': incident_data.get('incident_title', 'N/A'),
                'incident_description': incident_data.get('incident_description', 'Aucune description'),
                'priority': priority,
                'priority_label': priority_labels.get(priority, priority),
                'impact_label': impact_labels.get(incident_data.get('impact', ''), 'Non spécifié'),
                'domain_label': domain_labels.get(incident_data.get('domain', ''), 'Non spécifié'),
                'declarant_name': incident_data.get('declarant_name', 'Non spécifié'),
                'partner_name': incident_data.get('partner_name', 'N/A'),
                'project_title': incident_data.get('project_title', 'N/A'),
                'created_at': incident_data.get('created_at', 'Maintenant'),
                'incident_id': incident_data.get('incident_id', ''),
                'app_url': Config.APP_URL or 'https://app.datalysconsulting.com'
            }
            
            # Rendre le template HTML
            html_content = render_template('email_incident_notification_experts.html', **template_data)
            
            # ⚡ Envoyer l'email de manière ASYNCHRONE (non-bloquante)
            self.send_email_async(expert_email, subject, html_content)
            
            # Retourner True immédiatement (l'email sera envoyé en arrière-plan)
            logger.info(f"⚡ Email de notification d'incident programmé pour envoi asynchrone à {expert_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de l'email de notification pour {expert_email}: {str(e)}")
            return False
    
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
        subject = f"ALERTE INCIDENT - Projet {email_data.get('project_title', 'N/A')}"
        
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
        subject = f"Bienvenue dans l'écosystème Datalys Consulting - Accès à votre espace partenaire"

        # URL de l'application (configurable via variable d'environnement)
        app_url = current_app.config.get('APP_URL', 'https://applicationweb.datalysconsulting.com')
        login_url = f"{app_url}/connexion"

        # Utiliser le template Flask professionnel
        html_content = render_template('email_partner_credentials.html',
            email=partner_email,
            partner_name=partner_name,
            username=username,
            password=password,
            login_url=login_url,
            app_url=app_url,
            sender_email=self.smtp_username,
            sender_name=self.sender_name
        )
        
        return self.send_email(partner_email, subject, html_content)
    


