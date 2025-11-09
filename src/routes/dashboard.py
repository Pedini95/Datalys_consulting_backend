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
        # Étape 1: Récupérer les informations de l'utilisateur connecté
        logging.debug("Étape 1: Récupération des infos utilisateur")
        logging.debug(f"g.current_user: {g.current_user}")
        logging.debug(f"g.current_user.id: {g.current_user.id}")
        logging.debug(f"hasattr(g.current_user, 'role'): {hasattr(g.current_user, 'role')}")

        user_role = g.current_user.role.name if hasattr(g.current_user, 'role') and g.current_user.role else 'user'
        user_id = g.current_user.id

        logging.debug(f"user_role: {user_role}")
        logging.debug(f"user_id: {user_id}")

        # Si l'utilisateur n'est pas admin, vérifier les permissions
        # Note: Pour l'instant, tous les users peuvent voir n'importe quel partenaire
        # À améliorer : ajouter un système de permissions plus fin si nécessaire
        if user_role.lower() not in ['admin', 'manager']:
            # Les utilisateurs simples peuvent uniquement accéder via leur propre contexte
            # Pour le moment, on ne bloque pas mais on pourrait ajouter des restrictions
            pass

        # Étape 2: Récupérer les données du partenaire
        logging.debug(f"Étape 2: Récupération du partenaire ID={partner_id}")
        partners, _ = partner_service.getByCriteria({'id': partner_id}, 0, 1)
        logging.debug(f"Nombre de partenaires trouvés: {len(partners)}")

        partner = partners[0] if partners else None
        if not partner:
            logging.warning(f"Partenaire non trouvé: ID={partner_id}")
            return jsonify({
                "status": "error",
                "message": "Partenaire non trouvé"
            }), 404

        logging.debug(f"Partenaire trouvé: {partner.name}")

        # Étape 3: Récupérer les projets du partenaire
        logging.debug(f"Étape 3: Récupération des projets pour partner_id={partner_id}")
        projects, _ = project_service.getByCriteria({'partner_id': partner_id}, 0, 100)
        logging.debug(f"Nombre de projets trouvés: {len(projects)}")

        # Étape 4: Récupérer les incidents liés aux projets du partenaire
        logging.debug("Étape 4: Récupération des incidents")
        project_ids = [p.id for p in projects]
        logging.debug(f"IDs de projets: {project_ids}")

        all_incidents = []
        for project_id in project_ids:
            logging.debug(f"Récupération des incidents pour project_id={project_id}")
            incidents_for_project, _ = incident_service.getByCriteria({'project_id': project_id}, 0, 1000)
            logging.debug(f"Incidents trouvés pour project_id={project_id}: {len(incidents_for_project)}")
            all_incidents.extend(incidents_for_project)

        incidents = all_incidents
        logging.debug(f"Total incidents: {len(incidents)}")

        # Étape 5: Calculer les statistiques des projets
        logging.debug("Étape 5: Calcul des statistiques des projets")
        project_stats = {
            "total": len(projects),
            "active": len([p for p in projects if p.is_active]),
            "completed": len([p for p in projects if not p.is_active])
        }
        logging.debug(f"project_stats: {project_stats}")

        # Étape 6: Calculer les statistiques des incidents
        logging.debug("Étape 6: Calcul des statistiques des incidents")
        incident_stats = _get_incident_stats(incidents)
        logging.debug(f"incident_stats: {incident_stats}")

        # Étape 7: Récupérer le résumé d'activité
        logging.debug("Étape 7: Récupération du résumé d'activité")
        activity_summary = _get_activity_summary(partner_id, user_role, user_id)
        logging.debug(f"activity_summary: {activity_summary}")

        # Étape 8: Récupérer les statistiques d'activité détaillées
        logging.debug("Étape 8: Récupération des statistiques d'activité détaillées")
        activity_stats = get_user_activity_stats(user_id)
        logging.debug(f"activity_stats: {activity_stats}")

        # Étape 9: Convertir les objets en dictionnaires
        logging.debug("Étape 9: Conversion du partenaire en dictionnaire")
        partner_dict = partner.as_dict()
        logging.debug(f"partner_dict créé: clés={list(partner_dict.keys())}")

        logging.debug("Étape 10: Conversion des projets en dictionnaires")
        recent_projects = [p.as_dict() for p in projects[:5]]
        logging.debug(f"recent_projects: {len(recent_projects)} projets")

        logging.debug("Étape 11: Conversion des incidents en dictionnaires")
        recent_incidents = [i.as_dict() for i in incidents[:5]]
        logging.debug(f"recent_incidents: {len(recent_incidents)} incidents")

        # Étape 12: Construire la réponse
        logging.debug("Étape 12: Construction de la réponse")
        dashboard_data = {
            "partner": partner_dict,
            "project_stats": project_stats,
            "incident_stats": incident_stats,
            "activity_summary": activity_summary,
            "activity_stats": activity_stats,
            "recent_projects": recent_projects,
            "recent_incidents": recent_incidents
        }

        response = {
            "code": 200,
            "data": dashboard_data,
            "message": functional_error.MESSAGE_SUCCESS()
        }

        logging.info("**** End get_partner_dashboard - SUCCESS ****")
        return jsonify(response)

    except Exception as e:
        logging.error(f"ERREUR dans get_partner_dashboard: {str(e)}")
        logging.error(f"Type d'erreur: {type(e).__name__}")
        import traceback
        logging.error(f"Traceback complet:\n{traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": f"Erreur interne du serveur: {str(e)}"
        }), 500

@bp.route('/dashboard/client', methods=['POST'])
@cross_origin()
@require_auth
def get_client_dashboard():
    """
    Dashboard pour un client (user)
    Affiche une vue globale de SES incidents : nouveau, en cours, en attente
    """
    logging.info("**** Begin get_client_dashboard ****")
    try:
        user_id = g.current_user.id
        user_role = g.current_user.role.name if hasattr(g.current_user, 'role') and g.current_user.role else 'user'

        # Récupérer tous les incidents créés par cet utilisateur
        user_incidents, total_incidents = incident_service.getByCriteria({'user_id': user_id}, 0, 1000)

        # Calculer les statistiques détaillées
        incident_stats = {
            "total": len(user_incidents),
            "nouveau": len([i for i in user_incidents if i.status == 'nouveau']),
            "en_cours": len([i for i in user_incidents if i.status == 'en_cours']),
            "en_attente": len([i for i in user_incidents if i.status == 'en_attente']),
            "en_arbitrage": len([i for i in user_incidents if i.status == 'en_arbitrage']),
            "resolu": len([i for i in user_incidents if i.status == 'resolu']),
            "ferme": len([i for i in user_incidents if i.status == 'ferme']),
        }

        # Compter les incidents actifs (non résolus et non fermés)
        incident_stats["actifs"] = incident_stats["nouveau"] + incident_stats["en_cours"] + incident_stats["en_attente"] + incident_stats["en_arbitrage"]

        # Statistiques par priorité
        priority_stats = {
            "P0": len([i for i in user_incidents if i.priority == 'P0']),
            "P1": len([i for i in user_incidents if i.priority == 'P1']),
            "P2": len([i for i in user_incidents if i.priority == 'P2']),
            "P3": len([i for i in user_incidents if i.priority == 'P3']),
            "P4": len([i for i in user_incidents if i.priority == 'P4']),
        }

        # Statistiques par domaine
        domain_stats = {}
        for incident in user_incidents:
            domain = incident.domain or 'non_specifie'
            domain_stats[domain] = domain_stats.get(domain, 0) + 1

        # Statistiques SLA (incidents en dépassement)
        sla_stats = {
            "prise_en_charge_depasse": len([i for i in user_incidents if i.sla_prise_en_charge_status == 'depasse']),
            "resolution_depasse": len([i for i in user_incidents if i.sla_resolution_status == 'depasse']),
        }

        # Statistiques de refus
        refusal_stats = {
            "total_refus": sum([i.refusal_count or 0 for i in user_incidents]),
            "incidents_with_refusals": len([i for i in user_incidents if (i.refusal_count or 0) > 0])
        }

        # Récupérer les incidents récents (10 derniers)
        recent_incidents = sorted(user_incidents, key=lambda x: x.created_at, reverse=True)[:10]

        # Récupérer les incidents urgents (P0 et P1 non résolus)
        urgent_incidents = [
            i for i in user_incidents
            if i.priority in ['P0', 'P1'] and i.status not in ['resolu', 'ferme']
        ]

        # Récupérer les incidents en attente de réponse (en_attente)
        waiting_incidents = [i for i in user_incidents if i.status == 'en_attente']

        # Résumé d'activité utilisateur
        activity_summary = _get_activity_summary(None, user_role, user_id)

        dashboard_data = {
            "user": {
                "id": g.current_user.id,
                "name": g.current_user.name,
                "email": g.current_user.email,
                "role": user_role
            },
            "incident_stats": incident_stats,
            "priority_stats": priority_stats,
            "domain_stats": domain_stats,
            "sla_stats": sla_stats,
            "refusal_stats": refusal_stats,
            "recent_incidents": [i.as_dict() for i in recent_incidents],
            "urgent_incidents": [i.as_dict() for i in urgent_incidents],
            "waiting_incidents": [i.as_dict() for i in waiting_incidents],
            "activity_summary": activity_summary
        }

        response = {
            "code": 200,
            "data": dashboard_data,
            "message": functional_error.MESSAGE_SUCCESS()
        }

        logging.info("**** End get_client_dashboard ****")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Erreur dans get_client_dashboard: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur interne du serveur: {str(e)}"
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
        user_role = g.current_user.role.name if hasattr(g.current_user, 'role') and g.current_user.role else 'user'
        if user_role.lower() != 'admin':
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