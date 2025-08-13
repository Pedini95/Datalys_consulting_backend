from flask import Blueprint, jsonify
from utils.session_utils import session_manager
import logging

logger = logging.getLogger(__name__)

session_bp = Blueprint('session', __name__, url_prefix='/api/sessions')

@session_bp.route('/health', methods=['GET'])
def session_health():
    """Vérifier la santé du système de sessions"""
    try:
        # Test de connexion Redis
        if session_manager.redis_client:
            session_manager.redis_client.ping()
            redis_status = "✅ Connecté"
        else:
            redis_status = "❌ Non connecté"
        
        return jsonify({
            'message': 'État du système de sessions',
            'redis_status': redis_status,
            'session_manager_ready': session_manager.redis_client is not None
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de santé: {str(e)}")
        return jsonify({
            'message': 'Erreur lors du test de santé',
            'error': str(e),
            'redis_status': "❌ Erreur de connexion"
        }), 500

@session_bp.route('/stats', methods=['GET'])
def session_stats():
    """Obtenir les statistiques des sessions (Admin uniquement)"""
    try:
        if not session_manager.redis_client:
            return jsonify({
                'message': 'Système de sessions non disponible',
                'stats': {
                    'active_sessions': 0,
                    'redis_connected': False
                }
            }), 503
        
        # Test simple de connexion
        session_manager.redis_client.ping()
        
        return jsonify({
            'message': 'Statistiques des sessions',
            'stats': {
                'redis_connected': True,
                'status': 'Système opérationnel'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des stats: {str(e)}")
        return jsonify({
            'message': 'Erreur lors de la récupération des statistiques',
            'error': str(e)
        }), 500 