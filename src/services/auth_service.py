from models import User
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils import utilities
from utils import session_utils
from utils.audit_utils import set_audit_fields, update_audit_field
from utils.error_handler import handle_sqlalchemy_error, handle_general_error
import jwt
import datetime
from config import Config

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service pour la gestion des users
    """
    
    def __init__(self):
        self.model_class = User
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[User], bool, str]:
        """
        Créer un nouveau user
        
        Args:
            data: Données du user à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (user, succès, message)
        """
        try:
            # Ajouter les champs d'audit
            set_audit_fields(data, user_id)
            
            user = self.model_class(**data)
            db.session.add(user)
            db.session.commit()
            
            return user, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            error_msg = handle_sqlalchemy_error(e, "la création de l'utilisateur", data)
            return None, False, error_msg
        except Exception as e:
            db.session.rollback()
            error_msg = handle_general_error(e, "la création de l'utilisateur")
            return None, False, error_msg
    
    def update(self, user_id: int, data: Dict[str, Any], current_user_id: Optional[int] = None) -> Tuple[Optional[User], bool, str]:
        """
        Mettre à jour un user
        
        Args:
            user_id: ID du user à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (user, succès, message)
        """
        try:
            # Vérifier si le user existe
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            user = users[0]
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            # Mettre à jour les champs d'audit
            update_audit_field(user, current_user_id)
            
            db.session.commit()
            
            return user, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            error_msg = handle_sqlalchemy_error(e, "la mise à jour de l'utilisateur", data)
            return None, False, error_msg
        except Exception as e:
            db.session.rollback()
            error_msg = handle_general_error(e, "la mise à jour de l'utilisateur")
            return None, False, error_msg
    
    def delete(self, user_id: int, current_user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un user (soft delete par défaut)
        
        Args:
            user_id: ID du user à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le user existe
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return False, f"{self.model_class.__name__} non trouvé"
            
            user = users[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(user)
            else:
                # Soft delete
                if hasattr(user, 'is_deleted'):
                    user.is_deleted = True
                    update_audit_field(user, current_user_id)
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(user)
            
            db.session.commit()
            
            return True, f"{self.model_class.__name__} supprimé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            error_msg = handle_sqlalchemy_error(e, "la suppression de l'utilisateur")
            return False, error_msg
        except Exception as e:
            db.session.rollback()
            error_msg = handle_general_error(e, "la suppression de l'utilisateur")
            return False, error_msg
    
    def getByCriteria(self, criteria: Dict[str, Any], index: int = 0, size: int = 10) -> Tuple[list, int]:
        """
        Récupérer des users selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des users, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0

    def login(self, identifier: str, password: str) -> Tuple[Optional[Dict], bool, str]:
        """
        Authentifier un utilisateur avec email/code client et mot de passe
        
        Args:
            identifier: Email OU code client de l'utilisateur (ex: "user@example.com" ou "DATALYS-2025-001")
            password: Mot de passe en clair
            
        Returns:
            Tuple (données utilisateur avec token, succès, message)
        """
        try:
            # Rechercher l'utilisateur par email OU code client
            from sqlalchemy import or_
            from utils import utilities
            
            user = self.model_class.query.filter(
                or_(
                    self.model_class.email == identifier,
                    self.model_class.client_code == identifier
                ),
                self.model_class.is_deleted == False
            ).first()
            
            if not user:
                return None, False, "Identifiant ou mot de passe incorrect"
            
            # Vérifier le mot de passe avec la même méthode de hashage que lors de la création (SHA1)
            if user.password_hash != utilities.encrypt(password):
                return None, False, "Identifiant ou mot de passe incorrect"
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                return None, False, "Compte désactivé"
            
            # Vérifier si le mot de passe est temporaire (avec fallback pour compatibilité)
            is_temp_password = getattr(user, 'is_temp_password', False)
            if is_temp_password:
                # Retourner une réponse spéciale pour forcer le changement de mot de passe
                return {
                    'user_id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'requires_password_change': True,
                    'message': 'Vous devez changer votre mot de passe temporaire'
                }, True, "Changement de mot de passe requis"
            
            # ✅ NOUVEAU : Vérifier si MFA est activé
            mfa_enabled = getattr(user, 'mfa_enabled', True)  # Par défaut activé
            if mfa_enabled:
                # Générer un code MFA à 6 chiffres
                mfa_code = utilities.generate_numeric_code(6)
                
                # Sauvegarder le code et sa date d'expiration (5 minutes)
                user.mfa_code = mfa_code
                user.mfa_code_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                user.mfa_code_attempts = 0
                db.session.commit()
                
                # Envoyer le code par email
                from utils.notification import EmailService
                email_service = EmailService()
                email_sent = email_service.send_mfa_code_email(
                    user_email=user.email,
                    user_name=user.name,
                    mfa_code=mfa_code
                )
                
                if email_sent:
                    logger.info(f"Code MFA envoyé à {user.email}")
                else:
                    logger.error(f"Échec de l'envoi du code MFA à {user.email}")
                
                # Retourner une réponse indiquant que le MFA est requis
                return {
                    'requires_mfa': True,
                    'user_id': user.id,
                    'email': user.email,
                    'message': 'Code de vérification envoyé par email'
                }, True, "MFA requis"
            
            # Si MFA désactivé, générer le token JWT directement
            token_data = {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }
            
            secret_key = Config.SECRET_KEY or 'default-secret-key'
            token = jwt.encode(token_data, secret_key, algorithm='HS256')
            
            # Créer la session Redis
            user_data_for_session = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role_name': user.role.name if user.role else None
            }
            
            session_created = session_utils.create_user_session(
                user_id=user.id,
                user_data=user_data_for_session,
                token=token
            )
            
            if not session_created:
                logger.error(f"ERREUR CRITIQUE: Impossible de créer la session Redis pour l'utilisateur {user.id}")
                # En production, on peut soit échouer soit continuer en mode dégradé
                # Pour l'instant, on continue mais on log l'erreur
                logger.error("Mode dégradé activé - authentification sans session Redis")
            else:
                logger.info(f"Session Redis créée avec succès pour l'utilisateur {user.id}")

            # Préparer la réponse
            user_data = user.as_dict()
            user_data['token'] = token
            
            return user_data, True, "Connexion réussie"
            
        except Exception as e:
            error_msg = handle_general_error(e, "l'authentification")
            return None, False, error_msg

    def verify_token(self, token: str) -> Tuple[Optional[Dict], bool, str]:
        """
        Vérifier un token JWT avec validation de session Redis
        
        Args:
            token: Token JWT à vérifier
            
        Returns:
            Tuple (données utilisateur, succès, message)
        """
        try:
            # Vérifier d'abord si la session existe dans Redis
            redis_session_valid = session_utils.is_user_session_valid(token)
            
            # Si Redis fonctionne mais la session n'est pas trouvée, le token est invalide
            if not redis_session_valid:
                try:
                    from utils.session_utils import session_manager
                    if session_manager.redis_client is None:
                        # Redis non disponible - mode dégradé temporaire pour développement
                        logger.warning("Redis non disponible - mode dégradé temporaire activé")
                        # Continuer avec JWT seulement en mode dégradé
                    else:
                        # Redis fonctionne mais session pas trouvée = token invalide (logout ou expiration)
                        logger.warning(f"Session Redis non trouvée pour le token - probablement logout ou expiration")
                        return None, False, "Session expirée ou invalide (logout effectué)"
                except Exception as e:
                    logger.warning(f"Erreur lors de la vérification Redis: {e} - mode dégradé temporaire activé")
                    # Continuer avec JWT seulement en mode dégradé
            
            # Décoder le token JWT
            secret_key = Config.SECRET_KEY or 'default-secret-key'
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Récupérer l'utilisateur
            users, _ = self.model_class.get_by_criteria({'id': payload['user_id']}, 0, 1)
            if not users:
                return None, False, "Utilisateur non trouvé"
            
            user = users[0]
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                return None, False, "Compte désactivé"
            
            if not redis_session_valid:
                logger.info(f"Authentification réussie en mode dégradé pour l'utilisateur {user.id}")
            
            return user.as_dict(), True, "Token valide"
            
        except jwt.ExpiredSignatureError:
            return None, False, "Token expiré"
        except jwt.InvalidTokenError:
            return None, False, "Token invalide"
        except Exception as e:
            error_msg = handle_general_error(e, "la vérification du token")
            return None, False, error_msg

    def logout(self, user_id: int, token: str) -> Tuple[bool, str]:
        """
        Déconnecter un utilisateur et supprimer sa session
        
        Args:
            user_id: ID de l'utilisateur
            token: Token JWT à invalider
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Supprimer la session Redis
            session_deleted = session_utils.delete_user_session(token)
            
            if session_deleted:
                logger.info(f"Session supprimée pour l'utilisateur {user_id}")
                return True, "Déconnexion réussie"
            else:
                logger.warning(f"Session non trouvée pour l'utilisateur {user_id}")
                return True, "Déconnexion réussie (session déjà expirée)"
                
        except Exception as e:
            error_msg = handle_general_error(e, "la déconnexion")
            return False, error_msg

    def get_current_user(self, token: str) -> Tuple[Optional[User], bool, str]:
        """
        Récupérer l'utilisateur actuel à partir du token

        Args:
            token: Token JWT

        Returns:
            Tuple (utilisateur, succès, message)
        """
        try:
            # Vérifier le token et récupérer les données utilisateur
            user_data, success, message = self.verify_token(token)

            if not success or not user_data:
                return None, False, message

            # Récupérer l'objet utilisateur complet
            user_id = user_data.get('id')
            if not user_id:
                return None, False, "ID utilisateur manquant"

            # Utiliser une requête directe avec eager loading pour charger le role
            from sqlalchemy.orm import joinedload
            user = self.model_class.query.options(joinedload(self.model_class.role)).filter_by(
                id=user_id,
                is_deleted=False
            ).first()

            if not user:
                return None, False, "Utilisateur non trouvé"

            return user, True, "Utilisateur récupéré avec succès"

        except Exception as e:
            error_msg = handle_general_error(e, "la récupération de l'utilisateur")
            return None, False, error_msg

    def reset_password_request(self, email: str) -> Tuple[bool, str]:
        """
        Demander un reset de mot de passe
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Rechercher l'utilisateur par email
            users, _ = self.model_class.get_by_criteria({'email': email}, 0, 1)
            if not users:
                return True, "Si l'email existe, un lien de réinitialisation a été envoyé"
            
            user = users[0]
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                return True, "Si l'email existe, un lien de réinitialisation a été envoyé"
            
            # Générer un token de reset (expire dans 1 heure)
            reset_token_data = {
                'user_id': user.id,
                'email': user.email,
                'type': 'password_reset',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            
            secret_key = Config.SECRET_KEY or 'default-secret-key'
            reset_token = jwt.encode(reset_token_data, secret_key, algorithm='HS256')
            
            # Stocker le token dans Redis (optionnel, pour invalidation)
            session_utils.create_reset_token_session(reset_token, user.id)
            
            # Envoyer l'email de réinitialisation
            try:
                logger.info(f"Tentative d'envoi d'email de réinitialisation à {user.email}")
                from utils.notification import EmailService
                logger.info("EmailService importé avec succès")
                
                email_service = EmailService()
                logger.info("EmailService créé avec succès")
                
                reset_url = f"https://applicationweb.datalysconsulting.com/reset-mot-de-passe?token={reset_token}"
                logger.info(f"URL de reset générée: {reset_url}")
                
                email_sent = email_service.send_password_reset_email(
                    user_email=user.email,
                    user_name=user.name,
                    reset_url=reset_url,
                    expires_in="1 heure"
                )
                
                logger.info(f"Résultat de l'envoi d'email: {email_sent}")
                
                if email_sent:
                    logger.info(f"Email de réinitialisation envoyé à {user.email}")
                else:
                    logger.warning(f"Échec de l'envoi de l'email de réinitialisation à {user.email}")
                    
            except Exception as email_error:
                logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {str(email_error)}")
                import traceback
                logger.error(f"Traceback complet: {traceback.format_exc()}")
            
            return True, "Si l'email existe, un lien de réinitialisation a été envoyé"
            
        except Exception as e:
            logger.error(f"Erreur lors de la demande de reset: {str(e)}")
            return True, "Si l'email existe, un lien de réinitialisation a été envoyé"

    def reset_password_confirm(self, reset_token: str, new_password: str) -> Tuple[bool, str]:
        """
        Confirmer le reset de mot de passe
        
        Args:
            reset_token: Token de reset
            new_password: Nouveau mot de passe
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier le token de reset
            secret_key = Config.SECRET_KEY or 'default-secret-key'
            payload = jwt.decode(reset_token, secret_key, algorithms=['HS256'])
            
            # Vérifier le type de token
            if payload.get('type') != 'password_reset':
                return False, "Token de reset invalide"
            
            user_id = payload.get('user_id')
            if not user_id:
                return False, "Token de reset invalide"
            
            # Récupérer l'utilisateur
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return False, "Utilisateur non trouvé"
            
            user = users[0]
            
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                return False, "Compte désactivé"
            
            # Mettre à jour le mot de passe
            user.password_hash = utilities.encrypt(new_password)
            db.session.commit()
            
            # Supprimer le token de reset de Redis
            session_utils.delete_reset_token_session(reset_token)
            
            return True, "Mot de passe mis à jour avec succès"
            
        except jwt.ExpiredSignatureError:
            return False, "Token de reset expiré"
        except jwt.InvalidTokenError:
            return False, "Token de reset invalide"
        except Exception as e:
            error_msg = handle_general_error(e, "la confirmation de réinitialisation")
            return False, error_msg

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Changer le mot de passe d'un utilisateur connecté
        
        Args:
            user_id: ID de l'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Récupérer l'utilisateur
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return False, "Utilisateur non trouvé"
            
            user = users[0]
            
            # Vérifier le mot de passe actuel
            if user.password_hash != utilities.encrypt(current_password):
                return False, "Mot de passe actuel incorrect"
            
            # Mettre à jour le mot de passe
            user.password_hash = utilities.encrypt(new_password)
            db.session.commit()
            
            return True, "Mot de passe mis à jour avec succès"
            
        except Exception as e:
            error_msg = handle_general_error(e, "le changement de mot de passe")
            return False, error_msg

    def generate_token(self, user_id: int, email: str) -> str:
        """
        Générer un nouveau token JWT

        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur

        Returns:
            Token JWT
        """
        try:
            # Récupérer l'utilisateur pour obtenir le nom
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                raise Exception("Utilisateur non trouvé")

            user = users[0]

            # Générer le token JWT
            token_data = {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }

            secret_key = Config.SECRET_KEY or 'default-secret-key'
            token = jwt.encode(token_data, secret_key, algorithm='HS256')

            return token

        except Exception as e:
            logger.error(f"Erreur lors de la génération du token: {str(e)}")
            raise e

    def resend_mfa_code(self, identifier: str) -> Tuple[bool, str]:
        """
        Renvoyer le code MFA pour un utilisateur

        Args:
            identifier: Email OU code client de l'utilisateur

        Returns:
            Tuple (succès, message)
        """
        try:
            # Rechercher l'utilisateur par email OU code client
            from sqlalchemy import or_
            from utils import utilities

            user = self.model_class.query.filter(
                or_(
                    self.model_class.email == identifier,
                    self.model_class.client_code == identifier
                ),
                self.model_class.is_deleted == False
            ).first()

            if not user:
                # Pour des raisons de sécurité, ne pas révéler si l'utilisateur existe
                return False, "Aucune demande de code MFA en attente pour cet identifiant"

            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                return False, "Compte désactivé"

            # Vérifier si MFA est activé pour cet utilisateur
            mfa_enabled = getattr(user, 'mfa_enabled', True)
            if not mfa_enabled:
                return False, "L'authentification multi-facteurs n'est pas activée pour ce compte"

            # Générer un nouveau code MFA à 6 chiffres
            mfa_code = utilities.generate_numeric_code(6)

            # Sauvegarder le nouveau code et sa date d'expiration (5 minutes)
            user.mfa_code = mfa_code
            user.mfa_code_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            user.mfa_code_attempts = 0  # Réinitialiser le compteur de tentatives
            db.session.commit()

            # Envoyer le code par email
            from utils.notification import EmailService
            email_service = EmailService()
            email_sent = email_service.send_mfa_code_email(
                user_email=user.email,
                user_name=user.name,
                mfa_code=mfa_code
            )

            if email_sent:
                logger.info(f"Code MFA renvoyé à {user.email}")
                return True, "Un nouveau code de vérification a été envoyé à votre adresse email"
            else:
                logger.error(f"Échec du renvoi du code MFA à {user.email}")
                return False, "Erreur lors de l'envoi du code. Veuillez réessayer."

        except Exception as e:
            error_msg = handle_general_error(e, "le renvoi du code MFA")
            return False, error_msg
