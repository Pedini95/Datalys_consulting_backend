from functools import wraps
from flask import g, jsonify
import logging

logger = logging.getLogger(__name__)

def require_role(required_roles):
    """
    Décorateur pour restreindre l'accès selon le rôle utilisateur
    
    Args:
        required_roles: Liste des rôles autorisés ['admin', 'partner', 'user']
                       ou rôle unique 'admin'
    
    Usage:
        @require_role(['admin', 'partner'])
        def admin_or_partner_only():
            pass
            
        @require_role('admin')
        def admin_only():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    "status": "error", 
                    "message": "Authentification requise"
                }), 401
            
            user_role = _get_user_role(g.current_user)
            
            # Normaliser required_roles en liste
            if isinstance(required_roles, str):
                allowed_roles = [required_roles]
            else:
                allowed_roles = required_roles
            
            if user_role not in allowed_roles:
                logger.warning(f"Accès refusé: user {g.current_user.id} (rôle: {user_role}) tentative accès à {func.__name__}")
                return jsonify({
                    "status": "error",
                    "message": f"Accès réservé aux rôles: {', '.join(allowed_roles)}"
                }), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def filter_data_by_role(data_list, user_role, user_id=None):
    """
    Filtrer les données selon le rôle de l'utilisateur
    
    Args:
        data_list: Liste des objets à filtrer
        user_role: Rôle de l'utilisateur ('admin', 'partner', 'user')
        user_id: ID de l'utilisateur (pour filtrage partner)
    
    Returns:
        Liste filtrée selon le rôle
    """
    if user_role == 'admin':
        # Admins voient tout
        return data_list
    
    elif user_role == 'partner':
        # Partenaires ne voient que leurs projets/données
        filtered_data = []
        for item in data_list:
            if _partner_can_access(item, user_id):
                filtered_data.append(item)
        return filtered_data
    
    elif user_role == 'user':
        # Utilisateurs ne voient que leurs propres données
        filtered_data = []
        for item in data_list:
            if _user_can_access(item, user_id):
                filtered_data.append(item)
        return filtered_data
    
    else:
        # Rôle inconnu → accès refusé
        return []

def get_role_based_criteria(base_criteria, user_role, user_id=None):
    """
    Ajouter des critères de filtrage basés sur le rôle
    
    Args:
        base_criteria: Critères de base
        user_role: Rôle utilisateur
        user_id: ID utilisateur
    
    Returns:
        Critères enrichis selon le rôle
    """
    if user_role == 'admin':
        # Admins : pas de restriction
        return base_criteria
    
    elif user_role == 'partner':
        # Partenaires : seulement leurs projets
        partner_projects = _get_partner_projects(user_id)
        if partner_projects:
            base_criteria['project_id'] = partner_projects
        else:
            # Si pas de projets, empêcher l'accès
            base_criteria['project_id'] = -1
    
    elif user_role == 'user':
        # Utilisateurs : seulement leurs données
        base_criteria['user_id'] = user_id
    
    return base_criteria

def _get_user_role(user):
    """
    Déterminer le rôle d'un utilisateur
    Adaptez selon votre logique de rôles
    """
    try:
        if hasattr(user, 'role_id'):
            role_mapping = {
                1: 'admin',
                2: 'partner', 
                3: 'user'
            }
            return role_mapping.get(user.role_id, 'user')
        return 'user'
    except:
        return 'user'

def _partner_can_access(item, partner_user_id):
    """
    Vérifier si un partenaire peut accéder à un élément
    """
    try:
        # Logique métier : partenaire accède à ses projets
        if hasattr(item, 'project_id'):
            return _is_partner_project(item.project_id, partner_user_id)
        
        # Si l'item a un user_id, vérifier si c'est le partenaire
        if hasattr(item, 'user_id'):
            return item.user_id == partner_user_id
            
        return False
    except:
        return False

def _user_can_access(item, user_id):
    """
    Vérifier si un utilisateur peut accéder à un élément
    """
    try:
        # Utilisateur accède seulement à ses propres données
        if hasattr(item, 'user_id'):
            return item.user_id == user_id
        if hasattr(item, 'created_by'):
            return item.created_by == user_id
        return False
    except:
        return False

def _get_partner_projects(partner_user_id):
    """
    Récupérer les IDs des projets d'un partenaire
    """
    try:
        from models import Project, Partner, User
        
        # Trouver le partenaire lié à cet utilisateur
        user = User.query.get(partner_user_id)
        if not user:
            return []
        
        # Logique à adapter selon votre structure
        # Option 1: Si user.partner_id existe
        if hasattr(user, 'partner_id') and user.partner_id:
            projects = Project.query.filter(Project.partner_id == user.partner_id).all()
            return [p.id for p in projects]
        
        # Option 2: Si recherche par email/nom
        partners = Partner.query.filter(Partner.email == user.email).all()
        if partners:
            partner = partners[0]
            projects = Project.query.filter(Project.partner_id == partner.id).all()
            return [p.id for p in projects]
        
        return []
    except Exception as e:
        logger.error(f"Erreur récupération projets partenaire: {e}")
        return []

def _is_partner_project(project_id, partner_user_id):
    """
    Vérifier si un projet appartient à un partenaire
    """
    partner_projects = _get_partner_projects(partner_user_id)
    return project_id in partner_projects 