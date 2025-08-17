from flask import Blueprint, request, g
from services.action_history_service import ActionHistoryService
import logging
from utils import functional_error
from flask_cors import cross_origin
from .auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('action_history_readonly', __name__)

action_history_service = ActionHistoryService()

@bp.route('/action-history/search', methods=['POST'])
@cross_origin()
@require_auth
def search_action_history():
    """
    Rechercher dans l'historique des actions (LECTURE SEULE)
    Uniquement pour consultation et audit
    """
    logging.info("**** Begin search_action_history ****")
    try:
        r = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(r)
        
        index = r.get('index', 0)
        size = r.get('size', 10)
        criteria = r.get('data', {})
        
        # Filtrer par utilisateur si pas admin (sécurité)
        # Adaptez selon votre logique de rôles
        if not _is_admin(g.current_user):
            criteria['user_id'] = g.current_user.id
        
        action_history, total_items = action_history_service.getByCriteria(criteria, index, size)
        
        if action_history:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()
        
        response = {
            "items": [ah.as_dict() for ah in action_history],
            "count": total_items,
            "message": message,
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End search_action_history ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans search_action_history: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/action-history/user/<int:user_id>', methods=['POST'])
@cross_origin()
@require_auth
def get_user_actions(user_id):
    """
    Récupérer l'historique d'actions d'un utilisateur spécifique
    (Admins seulement ou utilisateur lui-même)
    """
    logging.info(f"**** Begin get_user_actions for user {user_id} ****")
    try:
        # Vérifier autorisation
        if not _is_admin(g.current_user) and g.current_user.id != user_id:
            return {"status": "error", "message": "Accès non autorisé"}, 403
        
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 20)
        
        criteria = {'user_id': user_id}
        
        # Filtres optionnels
        if 'action_type' in r:
            criteria['action_type'] = r['action_type']
        if 'entity_type' in r:
            criteria['entity_type'] = r['entity_type']
        
        action_history, total_items = action_history_service.getByCriteria(criteria, index, size)
        
        response = {
            "items": [ah.as_dict() for ah in action_history],
            "count": total_items,
            "message": functional_error.MESSAGE_SUCCESS(),
            "code": 200,
            "user_id": user_id
        }
        
        logging.info("**** End get_user_actions ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_user_actions: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/action-history/entity/<entity_type>/<int:entity_id>', methods=['POST'])
@cross_origin()
@require_auth
def get_entity_history(entity_type, entity_id):
    """
    Récupérer l'historique d'une entité spécifique
    Ex: /action-history/entity/message/123
    """
    logging.info(f"**** Begin get_entity_history for {entity_type} {entity_id} ****")
    try:
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 50)
        
        criteria = {
            'entity_type': entity_type,
            'entity_id': entity_id
        }
        
        action_history, total_items = action_history_service.getByCriteria(criteria, index, size)
        
        response = {
            "items": [ah.as_dict() for ah in action_history],
            "count": total_items,
            "message": functional_error.MESSAGE_SUCCESS(),
            "code": 200,
            "entity_type": entity_type,
            "entity_id": entity_id
        }
        
        logging.info("**** End get_entity_history ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_entity_history: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/action-history/stats', methods=['POST'])
@cross_origin()
@require_auth
def get_action_stats():
    """
    Statistiques sur les actions (Admins seulement)
    """
    logging.info("**** Begin get_action_stats ****")
    try:
        # Vérifier que l'utilisateur est admin
        if not _is_admin(g.current_user):
            return {"status": "error", "message": "Accès réservé aux administrateurs"}, 403
        
        # TODO: Implémenter les statistiques
        # Exemples: actions par type, actions par utilisateur, actions par jour, etc.
        
        response = {
            "message": "Statistiques non encore implémentées",
            "code": 200
        }
        
        logging.info("**** End get_action_stats ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_action_stats: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

def _is_admin(user):
    """
    Vérifier si l'utilisateur est admin
    Adaptez selon votre logique de rôles
    """
    try:
        # Supposons que role_id = 1 pour admin
        return hasattr(user, 'role_id') and user.role_id == 1
    except:
        return False 