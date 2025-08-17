from flask import Blueprint, request, g
from services.incident_service import IncidentService
import logging
from utils import functional_error
from flask_cors import cross_origin
from .auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('communication', __name__)

incident_service = IncidentService()

# ===============================
# ROUTES POUR MESSAGES
# ===============================

@bp.route('/messages/send', methods=['POST'])
@cross_origin()
@require_auth
def send_message():
    """
    Envoyer un message aux admins (utilisé par les partenaires)
    """
    logging.info("**** Begin send_message ****")
    try:
        data = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(data)
        
        # Valider les champs requis
        if not data.get('title'):
            return {"status": "error", "message": "Le titre est requis"}, 400
        if not data.get('description'):
            return {"status": "error", "message": "La description est requise"}, 400
        
        # Créer le message
        message, success, message_text = incident_service.create_message(data, g.current_user.id)
        
        if success and message:
            response = {
                "code": 200,
                "items": [message.as_dict()],
                "message": functional_error.MESSAGE_SUCCESS()
            }
        else:
            response = {"status": "error", "message": message_text}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End send_message ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans send_message: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/messages/my-messages', methods=['POST'])
@cross_origin()
@require_auth
def get_my_messages():
    """
    Récupérer mes messages (pour partenaires)
    """
    logging.info("**** Begin get_my_messages ****")
    try:
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 10)
        
        # Récupérer les messages de l'utilisateur connecté
        messages, total_items = incident_service.get_messages_for_user(g.current_user.id, index, size)
        
        if messages:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()
        
        response = {
            "items": [msg.as_dict() for msg in messages],
            "count": total_items,
            "message": message,
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End get_my_messages ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_my_messages: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/messages/reply', methods=['POST'])
@cross_origin()
@require_auth
def reply_to_message():
    """
    Répondre à un message
    """
    logging.info("**** Begin reply_to_message ****")
    try:
        data = request.get_json() or {}
        parent_id = data.get('parent_id')
        
        if not parent_id:
            return {"status": "error", "message": "L'ID du message parent est requis"}, 400
        
        if not data.get('description'):
            return {"status": "error", "message": "La réponse ne peut pas être vide"}, 400
        
        # Créer la réponse
        reply, success, message_text = incident_service.reply_to_message(parent_id, data, g.current_user.id)
        
        if success and reply:
            response = {
                "code": 200,
                "items": [reply.as_dict()],
                "message": functional_error.MESSAGE_SUCCESS()
            }
        else:
            response = {"status": "error", "message": message_text}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End reply_to_message ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans reply_to_message: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

# ===============================
# ROUTES POUR SUPPORT
# ===============================

@bp.route('/support/request', methods=['POST'])
@cross_origin()
@require_auth
def create_support_request():
    """
    Créer une demande de support technique
    """
    logging.info("**** Begin create_support_request ****")
    try:
        data = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(data)
        
        # Valider les champs requis
        if not data.get('title'):
            return {"status": "error", "message": "Le titre est requis"}, 400
        if not data.get('description'):
            return {"status": "error", "message": "La description est requise"}, 400
        
        # Créer la demande de support
        support_req, success, message_text = incident_service.create_support_request(data, g.current_user.id)
        
        if success and support_req:
            response = {
                "code": 200,
                "items": [support_req.as_dict()],
                "message": functional_error.MESSAGE_SUCCESS()
            }
        else:
            response = {"status": "error", "message": message_text}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End create_support_request ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans create_support_request: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/support/requests', methods=['POST'])
@cross_origin()
@require_auth
def get_support_requests():
    """
    Récupérer les demandes de support (pour admins)
    """
    logging.info("**** Begin get_support_requests ****")
    try:
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 10)
        status = r.get('data', {}).get('status')
        
        # Récupérer les demandes de support
        requests, total_items = incident_service.get_support_requests(status, index, size)
        
        if requests:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()
        
        response = {
            "items": [req.as_dict() for req in requests],
            "count": total_items,
            "message": message,
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End get_support_requests ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_support_requests: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

# ===============================
# ROUTES POUR NOTIFICATIONS
# ===============================

@bp.route('/notifications/send', methods=['POST'])
@cross_origin()
@require_auth
def send_notification():
    """
    Envoyer une notification officielle (admins seulement)
    """
    logging.info("**** Begin send_notification ****")
    try:
        data = request.get_json() or {}
        
        # Vérifier que l'utilisateur est admin (vous pouvez adapter selon votre logique de rôles)
        # if g.current_user.role.name != 'admin':
        #     return {"status": "error", "message": "Action non autorisée"}, 403
        
        # Valider les champs requis
        if not data.get('title'):
            return {"status": "error", "message": "Le titre est requis"}, 400
        if not data.get('description'):
            return {"status": "error", "message": "La description est requise"}, 400
        
        # Créer la notification
        notification, success, message_text = incident_service.create_notification(data, g.current_user.id)
        
        if success and notification:
            response = {
                "code": 200,
                "items": [notification.as_dict()],
                "message": functional_error.MESSAGE_SUCCESS()
            }
        else:
            response = {"status": "error", "message": message_text}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End send_notification ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans send_notification: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/notifications/unread', methods=['POST'])
@cross_origin()
@require_auth
def get_unread_notifications():
    """
    Récupérer les notifications non lues
    """
    logging.info("**** Begin get_unread_notifications ****")
    try:
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 10)
        
        # Récupérer les notifications non lues pour l'utilisateur connecté
        notifications, total_items = incident_service.get_unread_notifications(g.current_user.id, index, size)
        
        if notifications:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()
        
        response = {
            "items": [notif.as_dict() for notif in notifications],
            "count": total_items,
            "message": message,
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End get_unread_notifications ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_unread_notifications: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/notifications/mark-read', methods=['POST'])
@cross_origin()
@require_auth
def mark_notification_read():
    """
    Marquer une notification comme lue
    """
    logging.info("**** Begin mark_notification_read ****")
    try:
        data = request.get_json() or {}
        notification_id = data.get('id')
        
        if not notification_id:
            return {"status": "error", "message": "L'ID de la notification est requis"}, 400
        
        # Marquer comme lu
        notification, success, message_text = incident_service.mark_as_read(notification_id, g.current_user.id)
        
        if success and notification:
            response = {
                "code": 200,
                "items": [notification.as_dict()],
                "message": functional_error.MESSAGE_SUCCESS()
            }
        else:
            response = {"status": "error", "message": message_text}, 500
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End mark_notification_read ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans mark_notification_read: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

# ===============================
# ROUTES POUR CONVERSATIONS
# ===============================

@bp.route('/conversations/thread', methods=['POST'])
@cross_origin()
@require_auth
def get_conversation_thread():
    """
    Récupérer une conversation complète (message + réponses)
    """
    logging.info("**** Begin get_conversation_thread ****")
    try:
        r = request.get_json() or {}
        parent_id = r.get('parent_id')
        index = r.get('index', 0)
        size = r.get('size', 50)
        
        if not parent_id:
            return {"status": "error", "message": "L'ID du message parent est requis"}, 400
        
        # Récupérer la conversation
        messages, total_items = incident_service.get_conversation_thread(parent_id, index, size)
        
        if messages:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()
        
        response = {
            "items": [msg.as_dict() for msg in messages],
            "count": total_items,
            "message": message,
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End get_conversation_thread ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_conversation_thread: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500 