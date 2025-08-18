import logging
from typing import List, Optional, Dict
import os

# Import Firebase avec gestion d'erreur pour développement
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    # Développement sans Firebase installé
    firebase_admin = None
    credentials = None
    messaging = None
    FIREBASE_AVAILABLE = False

logger = logging.getLogger(__name__)

class PushNotificationService:
    """Service pour envoyer les notifications push via Firebase"""
    
    def __init__(self, config=None):
        self.config = config
        self._firebase_initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialiser Firebase Admin SDK"""
        if not FIREBASE_AVAILABLE:
            logger.warning("⚠️ Firebase Admin SDK non disponible (développement)")
            return
            
        try:
            # Vérifier si Firebase est déjà initialisé
            if not firebase_admin._apps:
                # Utiliser le chemin de configuration depuis Config si disponible
                if self.config and hasattr(self.config, 'FIREBASE_CONFIG_PATH'):
                    config_path = self.config.FIREBASE_CONFIG_PATH
                else:
                    # Fallback vers l'ancien chemin
                    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'firebase-service-account.json')
                
                if os.path.exists(config_path):
                    cred = credentials.Certificate(config_path)
                    firebase_admin.initialize_app(cred)
                    self._firebase_initialized = True
                    logger.info(" Firebase initialisé avec succès")
                else:
                    logger.error(f" Fichier de configuration Firebase non trouvé: {config_path}")
                    raise FileNotFoundError(f"Fichier non trouvé: {config_path}")
            else:
                self._firebase_initialized = True
                logger.info(" Firebase déjà initialisé")
                
        except Exception as e:
            logger.error(f" Erreur initialisation Firebase: {e}")
            self._firebase_initialized = False
            # Ne pas lever l'exception pour permettre le mode dégradé
    
    def is_enabled(self) -> bool:
        """Vérifier si le service FCM est activé et fonctionnel"""
        if self.config and hasattr(self.config, 'FIREBASE_ENABLED'):
            return self.config.FIREBASE_ENABLED and FIREBASE_AVAILABLE and self._firebase_initialized
        return FIREBASE_AVAILABLE and self._firebase_initialized
    
    def send_to_admins(self, title: str, body: str, data: Optional[Dict[str, str]] = None) -> bool:
        """
        Envoyer notification push à tous les admins
        
        Args:
            title: Titre de la notification
            body: Corps de la notification  
            data: Données additionnelles (optionnel)
            
        Returns:
            bool: True si envoyé avec succès
        """
        if not self.is_enabled():
            logger.warning(" Service FCM non activé - simulation envoi notification")
            logger.info(f" [SIMULATION] Push aux admins: {title} - {body}")
            return True
            
        try:
            admin_tokens = self._get_admin_tokens()
            
            if not admin_tokens:
                logger.warning(" Aucun token d'admin trouvé pour notifications push")
                return False
            
            # Préparer le message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=admin_tokens
            )
            
            # Envoyer la notification
            response = messaging.send_each_for_multicast(message)
            
            # Logger les résultats
            success_count = response.success_count
            failure_count = response.failure_count
            
            logger.info(f" Notifications envoyées: {success_count}/{len(admin_tokens)} succès")
            
            if failure_count > 0:
                logger.warning(f" {failure_count} notifications échouées")
                self._handle_send_failures(response.responses, admin_tokens)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f" Erreur envoi notifications push: {e}")
            return False
    
    def send_to_user(self, user_token: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> bool:
        """
        Envoyer notification push à un utilisateur spécifique
        
        Args:
            user_token: Token FCM de l'utilisateur
            title: Titre de la notification
            body: Corps de la notification
            data: Données additionnelles (optionnel)
            
        Returns:
            bool: True si envoyé avec succès
        """
        if not self.is_enabled():
            logger.warning(" Service FCM non activé - simulation envoi notification")
            logger.info(f" [SIMULATION] Push à utilisateur: {title} - {body}")
            return True
            
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=user_token
            )
            
            response = messaging.send(message)
            logger.info(f" Notification envoyée à utilisateur: {response}")
            return True
            
        except Exception as e:
            logger.error(f" Erreur envoi notification utilisateur: {e}")
            return False
    
    def send_to_user_by_id(self, user_id: int, title: str, body: str, data: Optional[Dict[str, str]] = None) -> bool:
        """
        Envoyer notification push à un utilisateur par son ID
        
        Args:
            user_id: ID de l'utilisateur
            title: Titre de la notification
            body: Corps de la notification
            data: Données additionnelles (optionnel)
            
        Returns:
            bool: True si envoyé avec succès
        """
        try:
            from models.user import User
            
            users, _ = User.get_by_criteria({'id': user_id, 'is_active': True}, 0, 1)
            if not users or not users[0].fcm_token:
                logger.warning(f" Utilisateur {user_id} sans token FCM valide")
                return False
            
            return self.send_to_user(users[0].fcm_token, title, body, data)
            
        except Exception as e:
            logger.error(f" Erreur envoi notification à utilisateur {user_id}: {e}")
            return False
    
    def _get_admin_tokens(self) -> List[str]:
        """
        Récupérer les tokens FCM des administrateurs depuis la base de données
        
        Returns:
            List[str]: Liste des tokens FCM valides
        """
        try:
            from models.user import User
            
            # Récupérer les utilisateurs admin avec tokens FCM
            # Adaptez selon votre logique de rôles (ex: role_id=1 pour admin)
            admins, _ = User.get_by_criteria({'role_id': 1, 'is_active': True}, 0, 100)
            
            # Filtrer seulement ceux qui ont un token FCM
            tokens = [admin.fcm_token for admin in admins if hasattr(admin, 'fcm_token') and admin.fcm_token]
            
            logger.info(f"📱 {len(tokens)} tokens d'admin trouvés")
            return tokens
            
        except Exception as e:
            logger.error(f" Erreur récupération tokens admin: {e}")
            return []
    
    def _handle_send_failures(self, responses: List, tokens: List[str]):
        """
        Gérer les échecs d'envoi (tokens invalides, etc.)
        
        Args:
            responses: Réponses de Firebase
            tokens: Tokens utilisés
        """
        try:
            for idx, response in enumerate(responses):
                if not response.success:
                    token = tokens[idx]
                    error_code = response.exception.code if response.exception else "UNKNOWN"
                    
                    logger.warning(f"⚠️ Échec notification token {token[:20]}...: {error_code}")
                    
                    # Si le token est invalide, le supprimer de la DB
                    if error_code in ['UNREGISTERED', 'INVALID_ARGUMENT']:
                        self._remove_invalid_token(token)
                        
        except Exception as e:
            logger.error(f" Erreur gestion échecs: {e}")
    
    def _remove_invalid_token(self, token: str):
        """
        Supprimer un token invalide de la base de données
        
        Args:
            token: Token FCM à supprimer
        """
        try:
            from models.user import User
            from extensions import db
            
            # Trouver l'utilisateur avec ce token et le nettoyer
            users, _ = User.get_by_criteria({'fcm_token': token}, 0, 1)
            if users:
                user = users[0]
                user.fcm_token = None
                db.session.commit()
                logger.info(f"🧹 Token invalide supprimé pour utilisateur {user.id}")
                
        except Exception as e:
            logger.error(f" Erreur suppression token invalide: {e}")

# Fonction pour créer l'instance avec configuration
def create_push_service(config=None):
    """Créer une instance du service push avec configuration"""
    return PushNotificationService(config)

# Instance globale du service (sera initialisée par l'app)
push_service = None 