from flask import Blueprint, request, g
from services.action_history_service import ActionHistoryService
import logging
from utils import functional_error
from flask_cors import cross_origin
from .auth import require_auth
from models import ActionHistory
from datetime import datetime, timedelta
from sqlalchemy import func

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('action_history_readonly', __name__)

action_history_service = ActionHistoryService()

# ===============================
# FONCTIONS UTILITAIRES
# ===============================

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

def get_action_statistics():
    """Récupérer les statistiques détaillées sur les actions"""
    try:
        # Statistiques des 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Actions par type
        actions_by_type = ActionHistory.query.filter(
            ActionHistory.created_at >= thirty_days_ago
        ).with_entities(
            ActionHistory.action_type,
            func.count(ActionHistory.id).label('count')
        ).group_by(ActionHistory.action_type).all()
        
        # Actions par entité
        actions_by_entity = ActionHistory.query.filter(
            ActionHistory.created_at >= thirty_days_ago
        ).with_entities(
            ActionHistory.entity_type,
            func.count(ActionHistory.id).label('count')
        ).group_by(ActionHistory.entity_type).all()
        
        # Actions par utilisateur (top 10)
        actions_by_user = ActionHistory.query.filter(
            ActionHistory.created_at >= thirty_days_ago
        ).with_entities(
            ActionHistory.user_id,
            func.count(ActionHistory.id).label('count')
        ).group_by(ActionHistory.user_id).order_by(func.count(ActionHistory.id).desc()).limit(10).all()
        
        # Actions par jour (7 derniers jours)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_actions = ActionHistory.query.filter(
            ActionHistory.created_at >= seven_days_ago
        ).with_entities(
            func.date(ActionHistory.created_at).label('date'),
            func.count(ActionHistory.id).label('count')
        ).group_by(func.date(ActionHistory.created_at)).all()
        
        # Actions par heure (24 dernières heures)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        hourly_actions = ActionHistory.query.filter(
            ActionHistory.created_at >= twenty_four_hours_ago
        ).with_entities(
            func.hour(ActionHistory.created_at).label('hour'),
            func.count(ActionHistory.id).label('count')
        ).group_by(func.hour(ActionHistory.created_at)).all()
        
        # Total des actions
        total_actions = ActionHistory.query.filter(
            ActionHistory.created_at >= thirty_days_ago
        ).count()
        
        # Actions aujourd'hui
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_actions = ActionHistory.query.filter(
            ActionHistory.created_at >= today_start
        ).count()
        
        # Actions cette semaine
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_actions = ActionHistory.query.filter(
            ActionHistory.created_at >= week_start
        ).count()
        
        return {
            "period": "30 derniers jours",
            "total_actions": total_actions,
            "today_actions": today_actions,
            "week_actions": week_actions,
            "actions_by_type": [
                {
                    "action_type": action.action_type,
                    "count": action.count,
                    "percentage": round((action.count / total_actions * 100), 2) if total_actions > 0 else 0
                }
                for action in actions_by_type
            ],
            "actions_by_entity": [
                {
                    "entity_type": entity.entity_type,
                    "count": entity.count,
                    "percentage": round((entity.count / total_actions * 100), 2) if total_actions > 0 else 0
                }
                for entity in actions_by_entity
            ],
            "top_users": [
                {
                    "user_id": user.user_id,
                    "count": user.count,
                    "percentage": round((user.count / total_actions * 100), 2) if total_actions > 0 else 0
                }
                for user in actions_by_user
            ],
            "daily_trend": [
                {
                    "date": str(day.date),
                    "count": day.count
                }
                for day in daily_actions
            ],
            "hourly_distribution": [
                {
                    "hour": hour.hour,
                    "count": hour.count
                }
                for hour in hourly_actions
            ]
        }
    except Exception as e:
        logger.error(f"Erreur récupération statistiques actions: {e}")
        return {
            "period": "30 derniers jours",
            "total_actions": 0,
            "today_actions": 0,
            "week_actions": 0,
            "actions_by_type": [],
            "actions_by_entity": [],
            "top_users": [],
            "daily_trend": [],
            "hourly_distribution": []
        }

# ===============================
# ROUTES
# ===============================

@bp.route('/action-history/search', methods=['POST'])
@cross_origin()
@require_auth
def search_action_history():
    """
    Recherche générale dans l'historique d'actions
    """
    logging.info("**** Begin search_action_history ****")
    try:
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 20)
        criteria = r.get('data', {})
        
        # Filtrage par rôle : non-admin ne voit que ses actions
        if not _is_admin(g.current_user):
            criteria['user_id'] = g.current_user.id
        
        action_history, total_items = action_history_service.getByCriteria(criteria, index, size)
        
        response = {
            "items": [ah.as_dict() for ah in action_history],
            "count": total_items,
            "message": functional_error.MESSAGE_SUCCESS(),
            "code": 200
        }
        
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
    Récupérer l'historique d'un utilisateur spécifique
    """
    logging.info(f"**** Begin get_user_actions for user {user_id} ****")
    try:
        # Vérifier les permissions : admin ou l'utilisateur lui-même
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
        
        # Récupérer les statistiques détaillées
        stats = get_action_statistics()
        
        response = {
            "code": 200,
            "data": stats,
            "message": functional_error.MESSAGE_SUCCESS()
        }
        
        logging.info("**** End get_action_stats ****")
        return response
        
    except Exception as e:
        logging.error(f"Erreur dans get_action_stats: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500 