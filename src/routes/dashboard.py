from flask import Blueprint, request, g, jsonify
import logging
from utils import functional_error
from flask_cors import cross_origin
from .auth import require_auth
from middleware.role_security import require_role, filter_data_by_role, get_role_based_criteria, _get_user_role
from services.project_service import ProjectService
from services.incident_service import IncidentService
from services.file_service import FileService
from services.folder_service import FolderService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('dashboard', __name__)

project_service = ProjectService()
incident_service = IncidentService()
file_service = FileService()
folder_service = FolderService()

@bp.route('/dashboard/partner/<int:partner_id>', methods=['GET'])
@cross_origin()
@require_auth
@require_role(['admin', 'partner'])
def get_partner_dashboard(partner_id):
    """
    Interface dashboard pour partenaire
    Affiche un résumé de ses projets, incidents, fichiers, etc.
    """
    logging.info(f"**** Begin get_partner_dashboard for partner {partner_id} ****")
    try:
        user_role = _get_user_role(g.current_user)
        
        # Vérifier autorisation : admin ou le partenaire lui-même
        if user_role != 'admin' and g.current_user.id != partner_id:
            return jsonify({
                "status": "error", 
                "message": "Accès non autorisé à ce dashboard"
            }), 403
        
        # Récupérer les projets du partenaire
        projects_criteria = get_role_based_criteria({}, user_role, g.current_user.id)
        projects, projects_count = project_service.getByCriteria(projects_criteria, 0, 100)
        
        # Récupérer les incidents du partenaire
        incidents_criteria = get_role_based_criteria({}, user_role, g.current_user.id)
        incidents, incidents_count = incident_service.getByCriteria(incidents_criteria, 0, 100)
        
        # Statistiques des incidents par statut
        incident_stats = _get_incident_stats(incidents)
        
        # Récupérer les fichiers récents
        files_criteria = get_role_based_criteria({}, user_role, g.current_user.id)
        recent_files, files_count = file_service.getByCriteria(files_criteria, 0, 10)
        
        # Statistiques générales
        dashboard_data = {
            "partner_id": partner_id,
            "summary": {
                "total_projects": projects_count,
                "total_incidents": incidents_count,
                "total_files": files_count,
                "active_projects": len([p for p in projects if p.is_active]),
                "open_incidents": len([i for i in incidents if i.status == 'ouvert'])
            },
            "projects": [project.as_dict() for project in projects[:5]],  # 5 projets récents
            "recent_incidents": [incident.as_dict() for incident in incidents[:10]],  # 10 incidents récents
            "incident_stats": incident_stats,
            "recent_files": [file.as_dict() for file in recent_files],
            "activity_summary": _get_activity_summary(partner_id, user_role, g.current_user.id)
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

@bp.route('/dashboard/partner/<int:partner_id>/projects', methods=['POST'])
@cross_origin()
@require_auth
@require_role(['admin', 'partner'])
def get_partner_projects(partner_id):
    """
    Récupérer tous les projets d'un partenaire avec pagination
    """
    logging.info(f"**** Begin get_partner_projects for partner {partner_id} ****")
    try:
        user_role = _get_user_role(g.current_user)
        
        # Vérifier autorisation
        if user_role != 'admin' and g.current_user.id != partner_id:
            return jsonify({
                "status": "error", 
                "message": "Accès non autorisé"
            }), 403
        
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 20)
        
        # Critères avec filtrage par rôle
        criteria = get_role_based_criteria(r.get('data', {}), user_role, g.current_user.id)
        
        projects, total_items = project_service.getByCriteria(criteria, index, size)
        
        response = {
            "items": [project.as_dict() for project in projects],
            "count": total_items,
            "message": functional_error.MESSAGE_SUCCESS(),
            "code": 200
        }
        
        logging.info("**** End get_partner_projects ****")
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Erreur dans get_partner_projects: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Erreur interne du serveur"
        }), 500

@bp.route('/dashboard/partner/<int:partner_id>/incidents', methods=['POST'])
@cross_origin()
@require_auth
@require_role(['admin', 'partner'])
def get_partner_incidents(partner_id):
    """
    Récupérer tous les incidents d'un partenaire avec pagination
    """
    logging.info(f"**** Begin get_partner_incidents for partner {partner_id} ****")
    try:
        user_role = _get_user_role(g.current_user)
        
        # Vérifier autorisation
        if user_role != 'admin' and g.current_user.id != partner_id:
            return jsonify({
                "status": "error", 
                "message": "Accès non autorisé"
            }), 403
        
        r = request.get_json() or {}
        index = r.get('index', 0)
        size = r.get('size', 20)
        
        # Critères avec filtrage par rôle
        criteria = get_role_based_criteria(r.get('data', {}), user_role, g.current_user.id)
        
        incidents, total_items = incident_service.getByCriteria(criteria, index, size)
        
        response = {
            "items": [incident.as_dict() for incident in incidents],
            "count": total_items,
            "message": functional_error.MESSAGE_SUCCESS(),
            "code": 200
        }
        
        logging.info("**** End get_partner_incidents ****")
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Erreur dans get_partner_incidents: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Erreur interne du serveur"
        }), 500

@bp.route('/dashboard/admin/overview', methods=['GET'])
@cross_origin()
@require_auth
@require_role('admin')
def get_admin_dashboard():
    """
    Dashboard global pour administrateurs
    Vue d'ensemble de toute la plateforme
    """
    logging.info("**** Begin get_admin_dashboard ****")
    try:
        # Statistiques globales
        all_projects, total_projects = project_service.getByCriteria({}, 0, 10000)
        all_incidents, total_incidents = incident_service.getByCriteria({}, 0, 10000)
        all_files, total_files = file_service.getByCriteria({}, 0, 10000)
        
        # Statistiques par partenaire
        partner_stats = _get_partner_statistics()
        
        # Incidents par priorité
        incident_priority_stats = _get_incident_priority_stats(all_incidents)
        
        # Activité récente
        recent_activity = _get_recent_global_activity()
        
        dashboard_data = {
            "global_summary": {
                "total_projects": total_projects,
                "total_incidents": total_incidents,
                "total_files": total_files,
                "active_projects": len([p for p in all_projects if p.is_active]),
                "open_incidents": len([i for i in all_incidents if i.status == 'ouvert']),
                "critical_incidents": len([i for i in all_incidents if i.priority == 'critique'])
            },
            "partner_stats": partner_stats,
            "incident_priority_stats": incident_priority_stats,
            "recent_projects": [p.as_dict() for p in all_projects[:5]],
            "recent_incidents": [i.as_dict() for i in all_incidents[:10]],
            "recent_activity": recent_activity
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
        # TODO: Implémenter avec action_history
        return {
            "recent_actions": 0,
            "last_login": None,
            "active_sessions": 1
        }
    except:
        return {}

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
        # TODO: Implémenter avec action_history
        return []
    except:
        return [] 