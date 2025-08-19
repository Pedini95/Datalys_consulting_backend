import redis
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class FCMCacheManager:
    """
    Gestionnaire de cache Redis pour les tokens FCM
    Optimise les performances en évitant les requêtes DB répétées
    """
    
    def __init__(self):
        """Initialiser la connexion Redis pour le cache FCM"""
        try:
            # Configuration Redis depuis Config
            redis_host = getattr(Config, 'REDIS_HOST', 'localhost')
            redis_port = int(getattr(Config, 'REDIS_PORT', 6379))
            redis_password = getattr(Config, 'REDIS_PASSWORD', None)
            
            # Utiliser une DB Redis différente pour le cache FCM (DB 1)
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=1,  # DB 1 pour le cache FCM (DB 0 pour les sessions)
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=30,
                socket_timeout=60,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test de connexion
            self.redis_client.ping()
            logger.info(" Cache Redis FCM initialisé avec succès")
            
        except Exception as e:
            logger.error(f" Erreur initialisation cache Redis FCM: {str(e)}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Vérifier si le cache Redis est disponible"""
        return self.redis_client is not None
    
    def _get_cache_key(self, key_type: str, identifier: str) -> str:
        """
        Générer une clé de cache standardisée
        
        Args:
            key_type: Type de clé ('admin_tokens', 'user_token', 'stats')
            identifier: Identifiant (user_id, 'all', etc.)
            
        Returns:
            str: Clé de cache formatée
        """
        return f"fcm:{key_type}:{identifier}"
    
    def cache_admin_tokens(self, tokens: List[str], ttl: int = 300) -> bool:
        """
        Mettre en cache les tokens des administrateurs
        
        Args:
            tokens: Liste des tokens FCM des admins
            ttl: Time to live en secondes (défaut: 5 minutes)
            
        Returns:
            bool: True si mis en cache avec succès
        """
        if not self.is_available():
            return False
            
        try:
            cache_key = self._get_cache_key('admin_tokens', 'all')
            cache_data = {
                'tokens': tokens,
                'count': len(tokens),
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.info(f" {len(tokens)} tokens admin mis en cache (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f" Erreur mise en cache tokens admin: {e}")
            return False
    
    def get_cached_admin_tokens(self) -> Optional[List[str]]:
        """
        Récupérer les tokens admin depuis le cache
        
        Returns:
            List[str] ou None: Liste des tokens ou None si non trouvé/expiré
        """
        if not self.is_available():
            return None
            
        try:
            cache_key = self._get_cache_key('admin_tokens', 'all')
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data and isinstance(cached_data, str):
                data = json.loads(cached_data)
                tokens = data.get('tokens', [])
                cached_at = data.get('cached_at')
                
                logger.info(f" {len(tokens)} tokens admin récupérés du cache (caché: {cached_at})")
                return tokens
            
            return None
            
        except Exception as e:
            logger.error(f" Erreur récupération cache tokens admin: {e}")
            return None
    
    def cache_user_token(self, user_id: int, token: str, ttl: int = 3600) -> bool:
        """
        Mettre en cache le token d'un utilisateur spécifique
        
        Args:
            user_id: ID de l'utilisateur
            token: Token FCM de l'utilisateur
            ttl: Time to live en secondes (défaut: 1 heure)
            
        Returns:
            bool: True si mis en cache avec succès
        """
        if not self.is_available():
            return False
            
        try:
            cache_key = self._get_cache_key('user_token', str(user_id))
            cache_data = {
                'user_id': user_id,
                'token': token,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.info(f" Token utilisateur {user_id} mis en cache (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f" Erreur mise en cache token utilisateur {user_id}: {e}")
            return False
    
    def get_cached_user_token(self, user_id: int) -> Optional[str]:
        """
        Récupérer le token d'un utilisateur depuis le cache
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            str ou None: Token FCM ou None si non trouvé/expiré
        """
        if not self.is_available():
            return None
            
        try:
            cache_key = self._get_cache_key('user_token', str(user_id))
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data and isinstance(cached_data, str):
                data = json.loads(cached_data)
                token = data.get('token')
                cached_at = data.get('cached_at')
                
                logger.info(f" Token utilisateur {user_id} récupéré du cache (caché: {cached_at})")
                return token
            
            return None
            
        except Exception as e:
            logger.error(f" Erreur récupération cache token utilisateur {user_id}: {e}")
            return None
    
    def cache_partner_tokens(self, tokens: List[str], project_id: Optional[int] = None, ttl: int = 300) -> bool:
        """
        Mettre en cache les tokens des partenaires
        
        Args:
            tokens: Liste des tokens FCM des partenaires
            project_id: ID du projet (optionnel - si spécifié, cache spécifique au projet)
            ttl: Time to live en secondes (défaut: 5 minutes)
            
        Returns:
            bool: True si mis en cache avec succès
        """
        if not self.is_available():
            return False
            
        try:
            cache_key = self._get_cache_key('partner_tokens', f"project_{project_id}" if project_id else "all")
            cache_data = {
                'tokens': tokens,
                'count': len(tokens),
                'project_id': project_id,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.info(f" {len(tokens)} tokens partenaires mis en cache (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f" Erreur mise en cache tokens partenaires: {e}")
            return False
    
    def get_cached_partner_tokens(self, project_id: Optional[int] = None) -> Optional[List[str]]:
        """
        Récupérer les tokens des partenaires depuis le cache
        
        Args:
            project_id: ID du projet (optionnel - si spécifié, récupère les tokens du projet)
            
        Returns:
            List[str] ou None: Liste des tokens ou None si non trouvé/expiré
        """
        if not self.is_available():
            return None
            
        try:
            cache_key = self._get_cache_key('partner_tokens', f"project_{project_id}" if project_id else "all")
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data and isinstance(cached_data, str):
                data = json.loads(cached_data)
                tokens = data.get('tokens', [])
                cached_at = data.get('cached_at')
                
                logger.info(f" {len(tokens)} tokens partenaires récupérés du cache (caché: {cached_at})")
                return tokens
            
            return None
            
        except Exception as e:
            logger.error(f" Erreur récupération cache tokens partenaires: {e}")
            return None
    
    def invalidate_user_token(self, user_id: int) -> bool:
        """
        Invalider le cache du token d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si invalidé avec succès
        """
        if not self.is_available():
            return False
            
        try:
            cache_key = self._get_cache_key('user_token', str(user_id))
            result = self.redis_client.delete(cache_key)
            
            if result:
                logger.info(f" Cache token utilisateur {user_id} invalidé")
            else:
                logger.info(f"ℹ Cache token utilisateur {user_id} non trouvé")
            
            return True
            
        except Exception as e:
            logger.error(f" Erreur invalidation cache token utilisateur {user_id}: {e}")
            return False
    
    def invalidate_admin_tokens(self) -> bool:
        """
        Invalider le cache des tokens admin
        
        Returns:
            bool: True si invalidé avec succès
        """
        if not self.is_available():
            return False
            
        try:
            cache_key = self._get_cache_key('admin_tokens', 'all')
            result = self.redis_client.delete(cache_key)
            
            if result:
                logger.info(" Cache tokens admin invalidé")
            else:
                logger.info("ℹ Cache tokens admin non trouvé")
            
            return True
            
        except Exception as e:
            logger.error(f" Erreur invalidation cache tokens admin: {e}")
            return False
    
    def cache_notification_stats(self, stats: Dict[str, Any], ttl: int = 1800) -> bool:
        """
        Mettre en cache les statistiques de notifications
        
        Args:
            stats: Dictionnaire des statistiques
            ttl: Time to live en secondes (défaut: 30 minutes)
            
        Returns:
            bool: True si mis en cache avec succès
        """
        if not self.is_available():
            return False
            
        try:
            cache_key = self._get_cache_key('stats', 'notifications')
            cache_data = {
                'stats': stats,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.info(f" Statistiques notifications mises en cache (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f" Erreur mise en cache stats notifications: {e}")
            return False
    
    def get_cached_notification_stats(self) -> Optional[Dict[str, Any]]:
        """
        Récupérer les statistiques de notifications depuis le cache
        
        Returns:
            Dict ou None: Statistiques ou None si non trouvé/expiré
        """
        if not self.is_available():
            return None
            
        try:
            cache_key = self._get_cache_key('stats', 'notifications')
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data and isinstance(cached_data, str):
                data = json.loads(cached_data)
                stats = data.get('stats', {})
                cached_at = data.get('cached_at')
                
                logger.info(f" Statistiques notifications récupérées du cache (caché: {cached_at})")
                return stats
            
            return None
            
        except Exception as e:
            logger.error(f" Erreur récupération cache stats notifications: {e}")
            return None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Obtenir des informations sur l'état du cache
        
        Returns:
            Dict: Informations sur le cache
        """
        if not self.is_available():
            return {
                'status': 'unavailable',
                'message': 'Cache Redis non disponible'
            }
        
        try:
            # Compter les clés FCM
            fcm_keys = self.redis_client.keys('fcm:*')
            
            # Statistiques Redis
            info = self.redis_client.info()
            
            # Vérifier que les résultats sont des listes/dicts
            fcm_keys_list = fcm_keys if isinstance(fcm_keys, list) else []
            info_dict = info if isinstance(info, dict) else {}
            
            cache_info = {
                'status': 'available',
                'fcm_keys_count': len(fcm_keys_list),
                'fcm_keys': fcm_keys_list,
                'redis_used_memory': info_dict.get('used_memory_human', 'N/A'),
                'redis_connected_clients': info_dict.get('connected_clients', 0),
                'redis_uptime': info_dict.get('uptime_in_seconds', 0)
            }
            
            return cache_info
            
        except Exception as e:
            logger.error(f" Erreur récupération infos cache: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def clear_all_fcm_cache(self) -> bool:
        """
        Vider tout le cache FCM
        
        Returns:
            bool: True si vidé avec succès
        """
        if not self.is_available():
            return False
            
        try:
            fcm_keys = self.redis_client.keys('fcm:*')
            fcm_keys_list = fcm_keys if isinstance(fcm_keys, list) else []
            
            if fcm_keys_list:
                deleted = self.redis_client.delete(*fcm_keys_list)
                logger.info(f" {deleted} clés FCM supprimées du cache")
            else:
                logger.info("ℹ Aucune clé FCM trouvée dans le cache")
            
            return True
            
        except Exception as e:
            logger.error(f" Erreur vidage cache FCM: {e}")
            return False

# Instance globale du gestionnaire de cache
fcm_cache = FCMCacheManager() 