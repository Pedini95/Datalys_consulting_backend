from functools import wraps
from flask import g
from models import ActionHistory
from extensions import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def audit_action(action_type: str, entity_type: str):
    """
    Décorateur pour enregistrer automatiquement les actions dans l'historique
    
    Args:
        action_type: Type d'action (CREATE, UPDATE, DELETE, etc.)
        entity_type: Type d'entité (message, project, user, etc.)
    
    Usage:
        @audit_action('CREATE', 'message')
        def create_message(data, user_id):
            # ... logique métier ...
            return message, success, message_text
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Exécuter la fonction originale
            result = func(*args, **kwargs)
            
            try:
                # Récupérer l'utilisateur actuel
                user_id = getattr(g, 'current_user', None)
                user_id = user_id.id if user_id else None
                
                # Déterminer si l'action a réussi
                if isinstance(result, tuple) and len(result) >= 2:
                    entity, success = result[0], result[1]
                    
                    if success and entity:
                        # Créer l'entrée d'historique
                        action_history = ActionHistory()
                        action_history.action_type = action_type
                        action_history.entity_type = entity_type
                        action_history.entity_id = entity.id if hasattr(entity, 'id') else None
                        action_history.user_id = user_id
                        action_history.description = f"{action_type} {entity_type} #{entity.id if hasattr(entity, 'id') else 'unknown'}"
                        action_history.ip_address = _get_client_ip()
                        action_history.user_agent = _get_user_agent()
                        
                        db.session.add(action_history)
                        db.session.commit()
                        
                        logger.info(f"📝 Action enregistrée: {action_type} {entity_type} par user {user_id}")
                        
            except Exception as e:
                logger.error(f"❌ Erreur audit automatique: {e}")
                # Ne pas faire échouer l'action principale
                pass
            
            return result
        return wrapper
    return decorator

def _get_client_ip():
    """Récupérer l'IP du client"""
    try:
        from flask import request
        return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    except:
        return None

def _get_user_agent():
    """Récupérer le User-Agent"""
    try:
        from flask import request
        return request.headers.get('User-Agent', '')[:255]  # Limiter la taille
    except:
        return None 