import redis
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from flask import request
from config import Config

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Gestionnaire de sessions avec Redis
    """
    
    def __init__(self):
        """Initialiser la connexion Redis"""
        try:
            # Vérifier que les configurations Redis existent
            redis_host = getattr(Config, 'REDIS_HOST', 'localhost')
            redis_port = int(getattr(Config, 'REDIS_PORT', 6379))
            redis_db = int(getattr(Config, 'REDIS_DB', 0))
            redis_password = getattr(Config, 'REDIS_PASSWORD', None)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=30,  # Augmenté de 5 à 30 secondes
                socket_timeout=60,          # Augmenté de 5 à 60 secondes
                retry_on_timeout=True,      # Ajout de retry automatique
                health_check_interval=30    # Vérification de santé toutes les 30s
            )
            # Test de connexion
            self.redis_client.ping()
            logger.info(" Connexion Redis établie avec succès")
        except Exception as e:
            logger.error(f" Erreur de connexion Redis: {str(e)}")
            self.redis_client = None
    
    def create_session(self, user_id: int, user_data: Dict[str, Any], token: str, 
                      expires_in: int = 7200) -> bool:
        """
        Créer une nouvelle session utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            user_data: Données de l'utilisateur
            token: Token JWT
            expires_in: Durée de validité en secondes (2h par défaut)
            
        Returns:
            bool: True si la session a été créée avec succès
        """
        try:
            if not self.redis_client:
                return False
            
            session_data = {
                'user_id': user_id,
                'user_data': user_data,
                'token': token,
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
            
            # Stocker la session avec le token comme clé
            session_key = f"session:{token}"
            self.redis_client.setex(
                session_key, 
                expires_in, 
                json.dumps(session_data)
            )
            
            logger.info(f" Session créée pour l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f" Erreur lors de la création de session: {str(e)}")
            return False
    
    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer une session par token
        
        Args:
            token: Token JWT
            
        Returns:
            Dict ou None: Données de la session
        """
        try:
            if not self.redis_client:
                return None
            
            session_key = f"session:{token}"
            session_data = self.redis_client.get(session_key)
            
            if session_data and isinstance(session_data, str):
                session = json.loads(session_data)
                # Mettre à jour la dernière activité
                session['last_activity'] = datetime.utcnow().isoformat()
                # Remettre la session avec le même TTL
                self.redis_client.setex(
                    session_key,
                    7200,  # 2 heures
                    json.dumps(session)
                )
                return session
            
            return None
            
        except Exception as e:
            logger.error(f" Erreur lors de la récupération de session: {str(e)}")
            return None
    
    def delete_session(self, token: str) -> bool:
        """
        Supprimer une session
        
        Args:
            token: Token JWT
            
        Returns:
            bool: True si la session a été supprimée
        """
        try:
            if not self.redis_client:
                return False
            
            # Supprimer la session
            session_key = f"session:{token}"
            self.redis_client.delete(session_key)
            
            logger.info(f" Session supprimée pour le token {token[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f" Erreur lors de la suppression de session: {str(e)}")
            return False
    
    def is_session_valid(self, token: str) -> bool:
        """
        Vérifier si une session est valide
        
        Args:
            token: Token JWT
            
        Returns:
            bool: True si la session est valide
        """
        try:
            if not self.redis_client:
                return False
            
            session_key = f"session:{token}"
            result = self.redis_client.exists(session_key)
            return bool(result)
            
        except Exception as e:
            logger.error(f" Erreur lors de la vérification de session: {str(e)}")
            return False

# Instance globale du gestionnaire de sessions
session_manager = SessionManager()

# Fonctions utilitaires pour compatibilité
def create_user_session(user_id: int, user_data: Dict[str, Any], token: str) -> bool:
    """Créer une session utilisateur (fonction utilitaire)"""
    return session_manager.create_session(user_id, user_data, token)

def get_user_session(token: str) -> Optional[Dict[str, Any]]:
    """Récupérer une session utilisateur (fonction utilitaire)"""
    return session_manager.get_session(token)

def delete_user_session(token: str) -> bool:
    """Supprimer une session utilisateur (fonction utilitaire)"""
    return session_manager.delete_session(token)

def is_user_session_valid(token: str) -> bool:
    """Vérifier si une session utilisateur est valide (fonction utilitaire)"""
    return session_manager.is_session_valid(token)

def create_reset_token_session(reset_token: str, user_id: int, expires_in: int = 3600) -> bool:
    """
    Créer une session pour un token de reset de mot de passe
    
    Args:
        reset_token: Token de reset
        user_id: ID de l'utilisateur
        expires_in: Durée de validité en secondes (1h par défaut)
        
    Returns:
        bool: True si la session a été créée avec succès
    """
    try:
        if not session_manager.redis_client:
            return False
        
        reset_data = {
            'user_id': user_id,
            'token': reset_token,
            'created_at': datetime.utcnow().isoformat(),
            'type': 'password_reset'
        }
        
        # Stocker le token de reset avec le token comme clé
        reset_key = f"reset_token:{reset_token}"
        session_manager.redis_client.setex(
            reset_key, 
            expires_in, 
            json.dumps(reset_data)
        )
        
        logger.info(f" Token de reset créé pour l'utilisateur {user_id}")
        return True
        
    except Exception as e:
        logger.error(f" Erreur lors de la création du token de reset: {str(e)}")
        return False

def delete_reset_token_session(reset_token: str) -> bool:
    """
    Supprimer une session de token de reset
    
    Args:
        reset_token: Token de reset
        
    Returns:
        bool: True si la session a été supprimée
    """
    try:
        if not session_manager.redis_client:
            return False
        
        # Supprimer le token de reset
        reset_key = f"reset_token:{reset_token}"
        session_manager.redis_client.delete(reset_key)
        
        logger.info(f" Token de reset supprimé: {reset_token[:20]}...")
        return True
        
    except Exception as e:
        logger.error(f" Erreur lors de la suppression du token de reset: {str(e)}")
        return False

def is_reset_token_valid(reset_token: str) -> bool:
    """
    Vérifier si un token de reset est valide
    
    Args:
        reset_token: Token de reset
        
    Returns:
        bool: True si le token est valide
    """
    try:
        if not session_manager.redis_client:
            return False
        
        reset_key = f"reset_token:{reset_token}"
        result = session_manager.redis_client.exists(reset_key)
        return bool(result)
        
    except Exception as e:
        logger.error(f" Erreur lors de la vérification du token de reset: {str(e)}")
        return False
