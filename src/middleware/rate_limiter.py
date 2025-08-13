from functools import wraps
from flask import request
import time
import logging
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

# Stockage en mémoire des tentatives (dans un vrai projet, utiliser Redis)
login_attempts = defaultdict(list)
ip_attempts = defaultdict(list)
lock = threading.Lock()


class RateLimiter:
    """
    Classe pour gérer le rate limiting
    """
    
    def __init__(self):
        self.max_login_attempts = 5  # Max tentatives de connexion
        self.max_requests_per_minute = 60  # Max requêtes par minute par IP
        self.block_duration = 300  # Durée de blocage en secondes (5 minutes)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """
        Vérifier si une IP est bloquée
        
        Args:
            ip_address: Adresse IP à vérifier
            
        Returns:
            True si l'IP est bloquée
        """
        with lock:
            attempts = ip_attempts.get(ip_address, [])
            current_time = time.time()
            
            # Nettoyer les anciennes tentatives
            attempts = [attempt for attempt in attempts if current_time - attempt < self.block_duration]
            ip_attempts[ip_address] = attempts
            
            # Vérifier si l'IP a trop de tentatives récentes
            if len(attempts) >= self.max_requests_per_minute:
                return True
            
            return False
    
    def is_login_blocked(self, identifier: str) -> bool:
        """
        Vérifier si un identifiant (email/IP) est bloqué pour la connexion
        
        Args:
            identifier: Email ou IP à vérifier
            
        Returns:
            True si l'identifiant est bloqué
        """
        with lock:
            attempts = login_attempts.get(identifier, [])
            current_time = time.time()
            
            # Nettoyer les anciennes tentatives
            attempts = [attempt for attempt in attempts if current_time - attempt < self.block_duration]
            login_attempts[identifier] = attempts
            
            # Vérifier si l'identifiant a trop de tentatives récentes
            if len(attempts) >= self.max_login_attempts:
                return True
            
            return False
    
    def record_login_attempt(self, identifier: str, success: bool):
        """
        Enregistrer une tentative de connexion
        
        Args:
            identifier: Email ou IP
            success: True si la connexion a réussi
        """
        with lock:
            current_time = time.time()
            
            if success:
                # Si la connexion réussit, nettoyer les tentatives
                login_attempts[identifier] = []
            else:
                # Ajouter la tentative échouée
                login_attempts[identifier].append(current_time)
    
    def record_request(self, ip_address: str):
        """
        Enregistrer une requête
        
        Args:
            ip_address: Adresse IP
        """
        with lock:
            current_time = time.time()
            ip_attempts[ip_address].append(current_time)
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Obtenir le nombre de tentatives restantes
        
        Args:
            identifier: Email ou IP
            
        Returns:
            Nombre de tentatives restantes
        """
        with lock:
            attempts = login_attempts.get(identifier, [])
            current_time = time.time()
            
            # Nettoyer les anciennes tentatives
            attempts = [attempt for attempt in attempts if current_time - attempt < self.block_duration]
            login_attempts[identifier] = attempts
            
            return max(0, self.max_login_attempts - len(attempts))


# Instance globale du rate limiter
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, window: int = 60):
    """
    Décorateur pour limiter le nombre de requêtes par IP
    
    Args:
        max_requests: Nombre maximum de requêtes
        window: Fenêtre de temps en secondes
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.remote_addr
            
            # Vérifier si l'IP est valide
            if not ip_address:
                return {
                    "status": "error",
                    "message": "Impossible de déterminer l'adresse IP."
                }, 400
            
            # Vérifier si l'IP est bloquée
            if rate_limiter.is_ip_blocked(ip_address):
                return {
                    "status": "error",
                    "message": "Trop de requêtes. Veuillez réessayer plus tard."
                }, 429
            
            # Enregistrer la requête
            rate_limiter.record_request(ip_address)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def login_rate_limit():
    """
    Décorateur spécifique pour limiter les tentatives de connexion
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return {"status": "error", "message": "Données manquantes"}, 400
            
            email = data.get('email')
            ip_address = request.remote_addr
            
            # Vérifier si l'email est valide
            if not email:
                return {"status": "error", "message": "Email manquant"}, 400
            
            # Vérifier si l'IP est valide
            if not ip_address:
                return {"status": "error", "message": "Impossible de déterminer l'adresse IP."}, 400
            
            # Vérifier si l'email ou l'IP est bloqué
            if rate_limiter.is_login_blocked(email) or rate_limiter.is_login_blocked(ip_address):
                remaining_time = rate_limiter.block_duration
                return {
                    "status": "error",
                    "message": f"Trop de tentatives de connexion. Réessayez dans {remaining_time} secondes."
                }, 429
            
            # Exécuter la fonction de connexion
            response = f(*args, **kwargs)
            
            # Enregistrer la tentative
            success = response[1] == 200  # Vérifier le code de statut
            rate_limiter.record_login_attempt(email, success)
            rate_limiter.record_login_attempt(ip_address, success)
            
            # Ajouter le nombre de tentatives restantes à la réponse
            if not success and response[1] == 401:
                remaining_attempts = rate_limiter.get_remaining_attempts(email)
                if isinstance(response[0], dict):
                    response[0]["remaining_attempts"] = remaining_attempts
            
            return response
        
        return decorated_function
    return decorator


def get_rate_limit_info(identifier: str) -> dict:
    """
    Obtenir les informations de rate limiting pour un identifiant
    
    Args:
        identifier: Email ou IP
        
    Returns:
        Dictionnaire avec les informations de rate limiting
    """
    remaining_attempts = rate_limiter.get_remaining_attempts(identifier)
    is_blocked = rate_limiter.is_login_blocked(identifier)
    
    return {
        "remaining_attempts": remaining_attempts,
        "is_blocked": is_blocked,
        "max_attempts": rate_limiter.max_login_attempts,
        "block_duration": rate_limiter.block_duration
    } 