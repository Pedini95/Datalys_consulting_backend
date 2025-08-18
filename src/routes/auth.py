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


@bp.route('/auth/change-temp-password', methods=['POST'])
@cross_origin()
def change_temp_password():
    """
    Route pour changer un mot de passe temporaire
    """
    try:
        data = request.get_json()
        
        if not data:
            return {"status": "error", "message": "Données manquantes"}, 400
        
        email = data.get('email')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not all([email, current_password, new_password]):
            return {"status": "error", "message": "Email, mot de passe actuel et nouveau mot de passe requis"}, 400
        
        # Valider le nouveau mot de passe
        if len(new_password) < 8:
            return {"status": "error", "message": "Le nouveau mot de passe doit contenir au moins 8 caractères"}, 400
        
        # Chercher l'utilisateur
        from models import User
        from utils import utilities
        
        users, _ = User.get_by_criteria({'email': email}, 0, 1)
        if not users:
            return {"status": "error", "message": "Utilisateur non trouvé"}, 404
        
        user = users[0]
        
        # Vérifier le mot de passe actuel
        if user.password_hash != utilities.encrypt(current_password):
            return {"status": "error", "message": "Mot de passe actuel incorrect"}, 401
        
        # Vérifier que c'est bien un mot de passe temporaire
        if not user.is_temp_password:
            return {"status": "error", "message": "Ce compte n'a pas de mot de passe temporaire"}, 400
        
        # Mettre à jour le mot de passe
        user.password_hash = utilities.encrypt(new_password)
        user.is_temp_password = False  # Le mot de passe n'est plus temporaire
        
        from extensions import db
        db.session.commit()
        
        # Maintenant authentifier l'utilisateur normalement
        user_data, success, message = auth_service.login(email, new_password)
        
        if success:
            return {
                "status": "success",
                "message": "Mot de passe changé avec succès",
                "data": user_data
            }, 200
        else:
            return {"status": "error", "message": "Erreur lors de la connexion après changement"}, 500
            
    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe temporaire: {str(e)}")
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