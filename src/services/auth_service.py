from models import User
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils import utilities
from utils import session_utils
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
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            user = self.model_class(**data)
            db.session.add(user)
            db.session.commit()
            
            return user, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
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
            if current_user_id and hasattr(user, 'updated_by'):
                user.updated_by = current_user_id
            
            db.session.commit()
            
            return user, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
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
                    if current_user_id and hasattr(user, 'updated_by'):
                        user.updated_by = current_user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(user)
            
            db.session.commit()
            
            return True, f"{self.model_class.__name__} supprimé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression de {self.model_class.__name__}: {str(e)}")
            return False, f"Erreur lors de la suppression: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la suppression de {self.model_class.__name__}: {str(e)}")
            return False, f"Erreur inattendue: {str(e)}"
    
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

    def login(self, email: str, password: str) -> Tuple[Optional[Dict], bool, str]:
        """
        Authentifier un utilisateur
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Tuple (données utilisateur avec token, succès, message)
        """
        try:
            # Rechercher l'utilisateur par email
            users, _ = self.model_class.get_by_criteria({'email': email}, 0, 1)
            if not users:
                return None, False, "Email ou mot de passe incorrect"
            
            user = users[0]
            
            # Vérifier le mot de passe
            if user.password_hash != utilities.encrypt(password):
                return None, False, "Email ou mot de passe incorrect"
            
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
            
            # Générer le token JWT
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
            logger.error(f"Erreur lors de l'authentification: {str(e)}")
            return None, False, f"Erreur lors de l'authentification: {str(e)}"

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
            
            if not redis_session_valid:
                # Mode dégradé : si Redis n'est pas disponible, on continue avec JWT seulement
                logger.warning("Session Redis non trouvée - tentative de vérification JWT seule (mode dégradé)")
                
                # Vérifier si Redis est complètement down
                try:
                    from utils.session_utils import session_manager
                    if session_manager.redis_client is None:
                        logger.warning("Redis non disponible - mode dégradé activé")
                    else:
                        # Redis fonctionne mais session pas trouvée = vraiment expirée
                        return None, False, "Session expirée ou invalide"
                except Exception as e:
                    logger.warning(f"Erreur lors de la vérification Redis: {e} - mode dégradé activé")
            
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
            logger.error(f"Erreur lors de la vérification du token: {str(e)}")
            return None, False, f"Erreur lors de la vérification du token: {str(e)}"

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
            logger.error(f"Erreur lors de la déconnexion: {str(e)}")
            return False, f"Erreur lors de la déconnexion: {str(e)}"

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
                
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return None, False, "Utilisateur non trouvé"
            
            return users[0], True, "Utilisateur récupéré avec succès"
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
            return None, False, f"Erreur lors de la récupération de l'utilisateur: {str(e)}"

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
                
                reset_url = f"https://applicationweb.datalysconsulting.com/mot-de-passe-oublie?token={reset_token}"
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
            logger.error(f"Erreur lors de la confirmation de reset: {str(e)}")
            return False, f"Erreur lors de la confirmation de reset: {str(e)}"

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
            logger.error(f"Erreur lors du changement de mot de passe: {str(e)}")
            return False, f"Erreur lors du changement de mot de passe: {str(e)}"

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
