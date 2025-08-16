from flask import Blueprint, request, jsonify, g
from services.auth_service import AuthService
import logging
from flask_cors import cross_origin
from functools import wraps
from middleware.rate_limiter import login_rate_limit, rate_limit

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('auth', __name__)

auth_service = AuthService()


def require_auth(f):
    """
    Décorateur pour protéger les routes qui nécessitent une authentification
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Récupérer le token depuis les headers
        auth_header = request.headers.get('Authorization')
        logger.info(f"Auth header reçu: {auth_header}")
        
        if not auth_header:
            logger.warning("Token d'authentification manquant")
            return {"status": "error", "message": "Token d'authentification manquant"}, 401
        
        # Extraire le token (format: "Bearer <token>")
        try:
            token = auth_header.split(" ")[1]
            logger.info(f"Token extrait: {token[:20]}...")
        except IndexError:
            logger.warning("Format de token invalide")
            return {"status": "error", "message": "Format de token invalide"}, 401
        
        # Vérifier le token et récupérer l'utilisateur
        logger.info("Vérification du token...")
        user, success, message = auth_service.get_current_user(token)
        logger.info(f"Résultat de vérification: success={success}, message={message}")
        
        if not success:
            logger.warning(f"Échec de vérification du token: {message}")
            return {"status": "error", "message": message}, 401
        
        # Ajouter l'utilisateur à Flask's g object
        g.current_user = user
        logger.info(f"Utilisateur authentifié: {user.email if user else 'None'}")
        return f(*args, **kwargs)
    
    return decorated_function


@bp.route('/auth/login', methods=['POST'])
@cross_origin()
@login_rate_limit()
def login():
    """
    Route pour la connexion utilisateur
    """
    try:
        logging.info("**** login input ****")
        data = request.get_json()
        logging.info(data)
        
        if not data:
            return {"status": "error", "message": "Données manquantes"}, 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return {"status": "error", "message": "Email et mot de passe requis"}, 400
        
        # Authentifier l'utilisateur
        user_data, success, message = auth_service.login(email, password)
        
        if success:
            response = {
                "status": "success",
                "message": message,
                "data": user_data
            }
            logging.info("**** login response ****")
            logging.info(response)
            return jsonify(response), 200
        else:
            return {"status": "error", "message": message}, 401
            
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500


@bp.route('/auth/logout', methods=['POST'])
@cross_origin()
@require_auth
def logout():
    """
    Route pour la déconnexion utilisateur
    """
    try:
        logging.info("**** logout input ****")
        data = request.get_json()
        logging.info(data)
        
        # Récupérer l'utilisateur depuis le décorateur
        user = g.current_user
        
        # Récupérer le token depuis les headers
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
        else:
            return {"status": "error", "message": "Token d'authentification manquant"}, 401
        
        # Déconnecter l'utilisateur
        success, message = auth_service.logout(user.id, token)
        
        if success:
            response = {
                "status": "success",
                "message": message
            }
            logging.info("**** logout response ****")
            logging.info(response)
            return jsonify(response), 200
        else:
            return {"status": "error", "message": message}, 400
            
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500


@bp.route('/auth/reset-password-request', methods=['POST'])
@cross_origin()
@rate_limit(max_requests=10, window=300)  # 10 tentatives par 5 minutes
def reset_password_request():
    """
    Route pour demander un reset de mot de passe
    """
    try:
        logging.info("**** reset password request input ****")
        data = request.get_json()
        logging.info(data)
        
        if not data:
            return {"status": "error", "message": "Données manquantes"}, 400
        
        email = data.get('email')
        
        if not email:
            return {"status": "error", "message": "Email requis"}, 400
        
        # Demander le reset de mot de passe
        success, message = auth_service.reset_password_request(email)
        
        if success:
            response = {
                "status": "success",
                "message": message
            }
            logging.info("**** reset password request response ****")
            logging.info(response)
            return jsonify(response), 200
        else:
            return {"status": "error", "message": message}, 400
            
    except Exception as e:
        logger.error(f"Erreur lors de la demande de reset: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500 