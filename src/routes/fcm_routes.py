from flask import Blueprint, request, g
import logging
from utils import functional_error
from flask_cors import cross_origin
from .auth import require_auth
from extensions import db
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('fcm', __name__)

@bp.route('/fcm/register-token', methods=['POST'])
@cross_origin()
@require_auth
def register_fcm_token():
    """
    Enregistrer le token FCM d'un utilisateur pour les notifications push
    """
    logging.info("**** Begin register_fcm_token ****")
    try:
        data = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(data)
        
        # Accepter à la fois 'token' et 'fcm_token' pour la compatibilité
        fcm_token = data.get('token') or data.get('fcm_token')
        
        if not fcm_token:
            return {"status": "error", "message": "Token FCM requis"}, 400
        
        # Mettre à jour le token FCM de l'utilisateur connecté
        current_user = g.current_user
        current_user.fcm_token = fcm_token
        
        try:
            db.session.commit()
            
            response = {
                "code": 200,
                "message": functional_error.MESSAGE_SUCCESS(),
                "data": {
                    "user_id": current_user.id,
                    "token_registered": True
                }
            }
            
            logging.info("✅ Token FCM enregistré avec succès")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur sauvegarde token FCM: {e}")
            return {"status": "error", "message": "Erreur lors de l'enregistrement"}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End register_fcm_token ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans register_fcm_token: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/fcm/unregister-token', methods=['POST'])
@cross_origin()
@require_auth
def unregister_fcm_token():
    """
    Supprimer le token FCM d'un utilisateur (logout, désactivation notifications)
    """
    logging.info("**** Begin unregister_fcm_token ****")
    try:
        # Supprimer le token FCM de l'utilisateur connecté
        current_user = g.current_user
        current_user.fcm_token = None
        
        try:
            db.session.commit()
            
            response = {
                "code": 200,
                "message": functional_error.MESSAGE_SUCCESS(),
                "data": {
                    "user_id": current_user.id,
                    "token_unregistered": True
                }
            }
            
            logging.info("✅ Token FCM supprimé avec succès")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erreur suppression token FCM: {e}")
            return {"status": "error", "message": "Erreur lors de la suppression"}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End unregister_fcm_token ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans unregister_fcm_token: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/fcm/test-notification', methods=['POST'])
@cross_origin()
@require_auth
def test_notification():
    """
    Tester l'envoi d'une notification push (pour debug/admin)
    """
    logging.info("**** Begin test_notification ****")
    try:
        data = request.get_json() or {}
        
        # Vérifier si l'utilisateur est admin (SÉCURISÉ POUR PRODUCTION)
        if g.current_user.role_id != 1:  # Seuls les admins peuvent tester
            return {"status": "error", "message": "Action non autorisée - Admin requis"}, 403
        
        # Optionnel: Limiter en production
        from flask import current_app
        if current_app.config.get('ENV') == 'production':
            logging.warning(f"Test FCM demandé en production par admin {g.current_user.id}")
        
        title = data.get('title', 'Test Notification')
        body = data.get('body', 'Ceci est une notification de test')
        user_id = data.get('user_id')  # Si spécifié, envoyer à un utilisateur particulier
        
        try:
            from services.push_notification_service import push_service
            
            # Vérifier que le service push est disponible
            if push_service is None:
                response = {
                    "code": 503,
                    "message": {"type": "error", "text": "Service push non initialisé"},
                    "data": {"notification_sent": False}
                }
            else:
                # Service disponible, envoyer la notification
                if user_id:
                    # Envoyer à un utilisateur spécifique
                    success = push_service.send_to_user_by_id(user_id, title, body, {
                        'type': 'test',
                        'timestamp': str(datetime.now())
                    })
                else:
                    # Envoyer notification de test à tous les admins
                    success = push_service.send_to_admins(title, body, {
                        'type': 'test',
                        'timestamp': str(datetime.now())
                    })
                
                if success:
                    response = {
                        "code": 200,
                        "message": functional_error.MESSAGE_SUCCESS(),
                        "data": {"notification_sent": True}
                    }
                else:
                    response = {
                        "code": 500,
                        "message": {"type": "error", "text": "Échec envoi notification"},
                        "data": {"notification_sent": False}
                    }
                
        except ImportError:
            logging.warning("Service push non disponible")
            response = {
                "code": 503,
                "message": {"type": "error", "text": "Service push non configuré"},
                "data": {"notification_sent": False}
            }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End test_notification ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans test_notification: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500 