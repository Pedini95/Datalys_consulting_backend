from functools import wraps
from flask import request, jsonify
from services import AuthService
import logging

logger = logging.getLogger(__name__)

auth_service = AuthService()


def require_role(required_role):
    """
    Décorateur pour vérifier le rôle de l'utilisateur
    
    Args:
        required_role: Nom du rôle requis
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Récupérer le token depuis les headers
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {"status": "error", "message": "Token d'authentification manquant"}, 401
            
            # Extraire le token
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {"status": "error", "message": "Format de token invalide"}, 401
            
            # Vérifier le token et récupérer l'utilisateur
            user, success, message = auth_service.get_current_user(token)
            if not success:
                return {"status": "error", "message": message}, 401
            
            # Vérifier le rôle de l'utilisateur
            if not user.role or user.role.name != required_role:
                return {"status": "error", "message": f"Rôle '{required_role}' requis"}, 403
            
            # Ajouter l'utilisateur à la requête
            request.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permission(required_permission):
    """
    Décorateur pour vérifier une permission spécifique
    
    Args:
        required_permission: Permission requise
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Récupérer le token depuis les headers
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {"status": "error", "message": "Token d'authentification manquant"}, 401
            
            # Extraire le token
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {"status": "error", "message": "Format de token invalide"}, 401
            
            # Vérifier le token et récupérer l'utilisateur
            user, success, message = auth_service.get_current_user(token)
            if not success:
                return {"status": "error", "message": message}, 401
            
            # Vérifier la permission de l'utilisateur
            if not auth_service.has_permission(user, required_permission):
                return {"status": "error", "message": f"Permission '{required_permission}' requise"}, 403
            
            # Ajouter l'utilisateur à la requête
            request.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_any_role(required_roles):
    """
    Décorateur pour vérifier que l'utilisateur a au moins un des rôles requis
    
    Args:
        required_roles: Liste des rôles acceptés
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Récupérer le token depuis les headers
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {"status": "error", "message": "Token d'authentification manquant"}, 401
            
            # Extraire le token
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {"status": "error", "message": "Format de token invalide"}, 401
            
            # Vérifier le token et récupérer l'utilisateur
            user, success, message = auth_service.get_current_user(token)
            if not success:
                return {"status": "error", "message": message}, 401
            
            # Vérifier que l'utilisateur a au moins un des rôles requis
            if not user.role or user.role.name not in required_roles:
                return {"status": "error", "message": f"Un des rôles suivants est requis: {', '.join(required_roles)}"}, 403
            
            # Ajouter l'utilisateur à la requête
            request.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def admin_only(f):
    """
    Décorateur pour restreindre l'accès aux administrateurs uniquement
    """
    return require_role("Admin")(f)


def user_or_admin(f):
    """
    Décorateur pour permettre l'accès aux utilisateurs et administrateurs
    """
    return require_any_role(["User", "Admin"])(f) 