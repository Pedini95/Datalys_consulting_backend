from flask import Blueprint, jsonify, g
from services import PartnerService, ProjectService, IncidentService
import logging
from utils import functional_error
from flask_cors import cross_origin
from .auth import require_auth
from models import ActionHistory, User
from datetime import datetime, timedelta
from sqlalchemy import func

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('dashboard', __name__)

partner_service = PartnerService()
project_service = ProjectService()
incident_service = IncidentService()

# ===============================
# FONCTIONS UTILITAIRES
# ===============================

def get_last_login(user_id):
    """Récupérer la dernière connexion d'un utilisateur"""
    try:
        # Chercher la dernière action de login dans action_history
        last_login_action = ActionHistory.query.filter_by(
            user_id=user_id,
            action_type='LOGIN'
        ).order_by(ActionHistory.created_at.desc()).first()
        
        if last_login_action:
            return last_login_action.created_at.isoformat()
        
        # Fallback: chercher dans les actions récentes
        recent_action = ActionHistory.query.filter_by(
            user_id=user_id
        ).order_by(ActionHistory.created_at.desc()).first()
        
        if recent_action:
            return recent_action.created_at.isoformat()
        
        return None
    except Exception as e:
        logger.error(f"Erreur récupération last_login: {e}")
        return None

def get_active_sessions(user_id):
    """Récupérer le nombre de sessions actives d'un utilisateur"""
    try:
        # Calculer les sessions actives (actions dans les dernières 30 minutes)
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        
        recent_actions = ActionHistory.query.filter(
            ActionHistory.user_id == user_id,
            ActionHistory.created_at >= thirty_minutes_ago
        ).count()
        
        # Si l'utilisateur a eu des actions récentes, considérer comme session active
        return 1 if recent_actions > 0 else 0
    except Exception as e:
        logger.error(f"Erreur récupération sessions actives: {e}")
        return 0

def get_user_activity_stats(user_id, days=7):
    """Récupérer les statistiques d'activité d'un utilisateur"""
    try:
        # Date de début pour les statistiques
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Actions par jour
        daily_actions = ActionHistory.query.filter(
            ActionHistory.user_id == user_id,
            ActionHistory.created_at >= start_date
        ).with_entities(
            func.date(ActionHistory.created_at).label('date'),
            func.count(ActionHistory.id).label('count')
        ).group_by(func.date(ActionHistory.created_at)).all()
        
        # Actions par type
        actions_by_type = ActionHistory.query.filter(
            ActionHistory.user_id == user_id,
            ActionHistory.created_at >= start_date
        ).with_entities(
            ActionHistory.action_type,
            func.count(ActionHistory.id).label('count')
        ).group_by(ActionHistory.action_type).all()
        
        return {
            "daily_actions": [{"date": str(day.date), "count": day.count} for day in daily_actions],
            "actions_by_type": [{"type": action.action_type, "count": action.count} for action in actions_by_type],
            "total_actions": len(daily_actions)  # Nombre de jours avec activité
        }
    except Exception as e:
        logger.error(f"Erreur récupération stats activité: {e}")
        return {"daily_actions": [], "actions_by_type": [], "total_actions": 0}

# ===============================
# ROUTES DASHBOARD
# ===============================

@bp.route('/dashboard/partner/<int:partner_id>', methods=['POST'])
@cross_origin()
@require_auth
def get_partner_dashboard(partner_id):
    """
    Dashboard pour un partenaire spécifique
    """
    logging.info(f"**** Begin get_partner_dashboard for partner {partner_id} ****")
    try:
        # Vérifier que l'utilisateur a accès à ce partenaire
        user_role = g.current_user.role.name if hasattr(g.current_user, 'role') else 'user'
        user_id = g.current_user.id
        
        # Si l'utilisateur n'est pas admin, vérifier qu'il appartient au partenaire
        if user_role != 'admin':
            # Vérifier si l'utilisateur appartient au partenaire
            partners, _ = partner_service.getByCriteria({'id': partner_id}, 0, 1)
            partner = partners[0] if partners else None
            if not partner or partner.id != g.current_user.partner_id:
                return jsonify({
                    "status": "error", 
                    "message": "Accès non autorisé à ce partenaire"
                }), 403
        
        # Récupérer les données du partenaire
        partners, _ = partner_service.getByCriteria({'id': partner_id}, 0, 1)
        partner = partners[0] if partners else None
        if not partner:
            return jsonify({
                "status": "error", 
                "message": "Partenaire non trouvé"
            }), 404
        
        # Récupérer les projets du partenaire
        projects, _ = project_service.getByCriteria({'partner_id': partner_id}, 0, 100)
        
        # Récupérer les incidents du partenaire
        incidents, _ = incident_service.getByCriteria({'partner_id': partner_id}, 0, 100)
        
        # Calculer les statistiques
        project_stats = {
            "total": len(projects),
            "active": len([p for p in projects if p.is_active]),
            "completed": len([p for p in projects if not p.is_active])
        }
        
        incident_stats = _get_incident_stats(incidents)
        
        # Récupérer le résumé d'activité
        activity_summary = _get_activity_summary(partner_id, user_role, user_id)
        
        # Récupérer les statistiques d'activité détaillées
        activity_stats = get_user_activity_stats(user_id)
        
        dashboard_data = {
            "partner": partner.as_dict(),
            "project_stats": project_stats,
            "incident_stats": incident_stats,
            "activity_summary": activity_summary,
            "activity_stats": activity_stats,
            "recent_projects": [p.as_dict() for p in projects[:5]],
            "recent_incidents": [i.as_dict() for i in incidents[:5]]
        }
        
        response = {
            "code": 200,
            "data": dashboard_data,
            "message": functional_error.MESSAGE_SUCCESS()
        }
        
        logging.info("**** End get_partner_dashboard ****")
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Erreur dans get_partner_dashboard: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Erreur interne du serveur"
        }), 500

@bp.route('/dashboard/admin', methods=['POST'])
@cross_origin()
@require_auth
def get_admin_dashboard():
    """
    Dashboard global pour les administrateurs
    """
    logging.info("**** Begin get_admin_dashboard ****")
    try:
        # Vérifier que l'utilisateur est admin
        user_role = g.current_user.role.name if hasattr(g.current_user, 'role') else 'user'
        if user_role != 'admin':
            return jsonify({
                "status": "error", 
                "message": "Accès réservé aux administrateurs"
            }), 403
        
        # Récupérer les statistiques globales
        partner_stats = _get_partner_statistics()
        recent_activity = _get_recent_global_activity()
        
        # Récupérer les incidents récents
        recent_incidents, _ = incident_service.getByCriteria({}, 0, 10)
        incident_priority_stats = _get_incident_priority_stats(recent_incidents)
        
        # Récupérer les statistiques d'activité globale
        global_activity_stats = _get_global_activity_stats()
        
        dashboard_data = {
            "partner_stats": partner_stats,
            "recent_activity": recent_activity,
            "incident_priority_stats": incident_priority_stats,
            "global_activity_stats": global_activity_stats,
            "recent_incidents": [i.as_dict() for i in recent_incidents]
        }
        
        response = {
            "code": 200,
            "data": dashboard_data,
            "message": functional_error.MESSAGE_SUCCESS()
        }
        
        logging.info("**** End get_admin_dashboard ****")
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Erreur dans get_admin_dashboard: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Erreur interne du serveur"
        }), 500

# ===============================
# FONCTIONS DE CALCUL DES STATISTIQUES
# ===============================

def _get_incident_stats(incidents):
    """Calculer les statistiques des incidents"""
    stats = {
        "total": len(incidents),
        "by_status": {},
        "by_priority": {},
        "by_type": {}
    }
    
    for incident in incidents:
        # Par statut
        status = incident.status or 'inconnu'
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # Par priorité
        priority = incident.priority or 'moyenne'
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        # Par type
        incident_type = incident.type or 'incident'
        stats["by_type"][incident_type] = stats["by_type"].get(incident_type, 0) + 1
    
    return stats

def _get_activity_summary(partner_id, user_role, user_id):
    """Résumé d'activité pour un partenaire"""
    try:
        # Utiliser action_history pour les vraies données
        recent_actions = ActionHistory.query.filter_by(
            user_id=user_id
        ).order_by(ActionHistory.created_at.desc()).limit(10).all()
        
        return {
            "recent_actions": len(recent_actions),
            "last_login": get_last_login(user_id),
            "active_sessions": get_active_sessions(user_id),
            "actions_details": [
                {
                    "action_type": action.action_type,
                    "entity_type": action.entity_type,
                    "description": action.description,
                    "created_at": action.created_at.isoformat()
                }
                for action in recent_actions[:5]  # Limiter à 5 actions récentes
            ]
        }
    except Exception as e:
        logger.error(f"Erreur activité: {e}")
        return {
            "recent_actions": 0,
            "last_login": None,
            "active_sessions": 0,
            "actions_details": []
        }

def _get_partner_statistics():
    """Statistiques par partenaire pour admins"""
    try:
        from models import Partner, Project
        
        partners = Partner.query.all()
        stats = []
        
        for partner in partners:
            projects = Project.query.filter(Project.partner_id == partner.id).all()
            partner_stat = {
                "partner_id": partner.id,
                "partner_name": partner.name,
                "total_projects": len(projects),
                "active_projects": len([p for p in projects if p.is_active])
            }
            stats.append(partner_stat)
        
        return stats
    except Exception as e:
        logger.error(f"Erreur statistiques partenaires: {e}")
        return []

def _get_incident_priority_stats(incidents):
    """Statistiques incidents par priorité pour admins"""
    stats = {
        "critique": 0,
        "haute": 0,
        "moyenne": 0,
        "basse": 0
    }
    
    for incident in incidents:
        priority = incident.priority or 'moyenne'
        if priority in stats:
            stats[priority] += 1
    
    return stats

def _get_recent_global_activity():
    """Activité récente globale pour admins"""
    try:
        # Récupérer les actions récentes de tous les utilisateurs
        recent_actions = ActionHistory.query.order_by(
            ActionHistory.created_at.desc()
        ).limit(20).all()
        
        activity_list = []
        for action in recent_actions:
            # Récupérer les informations de l'utilisateur
            user = User.query.get(action.user_id)
            user_name = user.name if user else f"User {action.user_id}"
            
            activity_list.append({
                "id": action.id,
                "user_id": action.user_id,
                "user_name": user_name,
                "action_type": action.action_type,
                "entity_type": action.entity_type,
                "entity_id": action.entity_id,
                "description": action.description,
                "created_at": action.created_at.isoformat(),
                "ip_address": action.ip_address
            })
        
        return activity_list
    except Exception as e:
        logger.error(f"Erreur récupération activité globale: {e}")
        return []

def _get_global_activity_stats():
    """Statistiques d'activité globale pour admins"""
    try:
        # Statistiques des 7 derniers jours
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Actions par jour
        daily_actions = ActionHistory.query.filter(
            ActionHistory.created_at >= seven_days_ago
        ).with_entities(
            func.date(ActionHistory.created_at).label('date'),
            func.count(ActionHistory.id).label('count')
        ).group_by(func.date(ActionHistory.created_at)).all()
        
        # Actions par type
        actions_by_type = ActionHistory.query.filter(
            ActionHistory.created_at >= seven_days_ago
        ).with_entities(
            ActionHistory.action_type,
            func.count(ActionHistory.id).label('count')
        ).group_by(ActionHistory.action_type).all()
        
        # Actions par utilisateur
        actions_by_user = ActionHistory.query.filter(
            ActionHistory.created_at >= seven_days_ago
        ).with_entities(
            ActionHistory.user_id,
            func.count(ActionHistory.id).label('count')
        ).group_by(ActionHistory.user_id).order_by(func.count(ActionHistory.id).desc()).limit(10).all()
        
        return {
            "daily_actions": [{"date": str(day.date), "count": day.count} for day in daily_actions],
            "actions_by_type": [{"type": action.action_type, "count": action.count} for action in actions_by_type],
            "top_users": [{"user_id": user.user_id, "count": user.count} for user in actions_by_user],
            "total_actions": len(daily_actions)  # Nombre de jours avec activité
        }
    except Exception as e:
        logger.error(f"Erreur récupération stats globales: {e}")
        return {
            "daily_actions": [],
            "actions_by_type": [],
            "top_users": [],
            "total_actions": 0
        } 