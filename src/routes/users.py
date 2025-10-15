from flask import Blueprint, request
from services.user_service import UserService
from utils.notification import EmailService
import logging
from utils import functional_error, utilities
from flask_cors import cross_origin
from .auth import require_auth
from middleware.role_security import require_role

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('users', __name__)



user_service = UserService()

@bp.route('/users/getByCriteria', methods=['POST'])
@cross_origin()
@require_auth
@require_role(['admin', 'manager'])  # Seuls admins et managers peuvent voir la liste des utilisateurs
def get_users():
    logging.info("**** Begin get_users ****")
    logging.info("/users/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    users, total_items = user_service.model_class.get_by_criteria(criteria, index, size)
    if users:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [user.as_dict() for user in users], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_users ****")
    return response

@bp.route('/users/create', methods=['POST'])
@cross_origin()
@require_auth
@require_role('admin')  # Seuls les admins peuvent créer des utilisateurs
def create_users():
    logging.info("**** Begin create_users ****")
    logging.info("/users/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)

    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['email', 'password', 'role_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        # Note: Pour créer un utilisateur avec mot de passe temporaire auto-généré,
        # utilisez l'endpoint /users/create-with-temp-password
        
        # VÉRIFICATION : Cette API est dédiée uniquement aux utilisateurs admin/manager
        role_name = data.get('role_name')
        if role_name.lower() not in ['admin', 'manager', 'user']:
            return {"status": "error", "message": f"Rôle invalide: {role_name}"}, 400
        
        processed_data = {
            'name': data.get('name', ''),
            'email': data.get('email'),
            'password': data.get('password'),
            'role_name': data.get('role_name'),
            'is_active': True  # Toujours initialisé à true lors de la création
        }
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        # Sauvegarder le mot de passe en clair avant la création (il sera hashé par le service)
        plain_password = data.get('password')
        
        item, success, message = user_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        
        # Envoyer l'email avec les credentials
        if success and item:
            try:
                email_service = EmailService()
                import os
                app_url = os.getenv('APP_URL', 'https://applicationweb.datalysconsulting.com')
                login_url = f"{app_url}/connexion"
                
                # Utiliser le nom de l'utilisateur pour l'email
                user_name = item.name or item.email
                
                # Envoyer l'email avec le mot de passe
                email_sent = email_service.send_partner_credentials_email(
                    partner_email=item.email,
                    partner_name=user_name,
                    email=item.email,
                    password=plain_password,
                    app_url=login_url
                )
                
                if email_sent:
                    logging.info(f"Email avec credentials envoyé à {item.email}")
                else:
                    logging.warning(f"Échec de l'envoi de l'email à {item.email}")
            except Exception as e:
                logging.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        
        items.append(item)
    
    if success and items:
        response = {"items": [user.as_dict() for user in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucun utilisateur créé"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_users ****")
    return response

@bp.route('/users/update', methods=['POST'])
@cross_origin()
def update_users():
    logging.info("**** Begin update_users ****")
    logging.info("/users/update")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['id']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {'id': data.get('id')}
        
        if utilities.not_blank(data.get('name')):
            processed_data['name'] = data.get('name')
        if utilities.not_blank(data.get('email')):
            processed_data['email'] = data.get('email')
        if utilities.not_blank(data.get('password')):
            processed_data['password'] = data.get('password')
        if 'role_name' in data:
            processed_data['role_name'] = data.get('role_name')
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        if 'fcm_token' in data:
            processed_data['fcm_token'] = data.get('fcm_token')
        if 'mfa_enabled' in data:
            processed_data['mfa_enabled'] = data.get('mfa_enabled')
        
        # ⚠️ SÉCURITÉ : Le client_code ne peut PAS être modifié (identifiant unique)
        if 'client_code' in data:
            logging.warning(f"⚠️  Tentative de modification du client_code refusée pour l'utilisateur {data.get('id')}")
            # On ignore silencieusement la tentative de modification
        
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = user_service.update(data['id'], data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if success and items:
        response = {"items": [user.as_dict() for user in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucun utilisateur mis à jour"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_users ****")
    return response

@bp.route('/users/delete', methods=['POST'])
@cross_origin()
@require_auth
@require_role('admin')  # Seuls les admins peuvent supprimer des utilisateurs
def delete_users():
    logging.info("**** Begin delete_users ****")
    logging.info("/users/delete")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        if 'id' not in data:
            return {"status": "error", "message": "Field id is missing"}, 400
        processed_datas.append({'id': data.get('id')})
    
    for data in processed_datas:
        success, message = user_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_users ****")
    return response


@bp.route('/users/create-with-temp-password', methods=['POST'])
@cross_origin()
@require_auth
@require_role('admin')  # Seuls les admins peuvent créer des utilisateurs
def create_users_with_temp_password():
    """
    Créer des utilisateurs avec mot de passe temporaire généré automatiquement
    Le mot de passe est envoyé par email à l'utilisateur
    """
    logging.info("**** Begin create_users_with_temp_password ****")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)

    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires (pas de mot de passe requis, il sera généré)
        required_fields = ['email', 'role_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        # Vérification du rôle
        role_name = data.get('role_name')
        if role_name.lower() not in ['admin', 'manager', 'user', 'partner']:
            return {"status": "error", "message": f"Rôle invalide: {role_name}"}, 400
        
        # Générer un mot de passe temporaire
        from utils.utilities import generate_temp_password
        temp_password = generate_temp_password()
        
        processed_data = {
            'name': data.get('name', ''),
            'email': data.get('email'),
            'password': temp_password,
            'role_name': data.get('role_name'),
            'is_active': True,
            'is_temp_password': True  # Marquer comme mot de passe temporaire
        }
        processed_datas.append(processed_data)
    
    items = []
    credentials_list = []
    success = True
    message = ""
    
    for data in processed_datas:
        # Sauvegarder le mot de passe en clair avant la création
        plain_password = data.get('password')
        
        item, success, message = user_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        
        # Envoyer l'email avec les credentials
        email_sent = False
        if success and item:
            try:
                email_service = EmailService()
                import os
                app_url = os.getenv('APP_URL', 'https://applicationweb.datalysconsulting.com')
                login_url = f"{app_url}/connexion"
                
                # Utiliser le nom de l'utilisateur pour l'email
                user_name = item.name or item.email
                
                # Envoyer l'email avec le mot de passe temporaire
                email_sent = email_service.send_partner_credentials_email(
                    partner_email=item.email,
                    partner_name=user_name,
                    email=item.email,
                    password=plain_password,
                    app_url=login_url
                )
                
                if email_sent:
                    logging.info(f"Email avec mot de passe temporaire envoyé à {item.email}")
                else:
                    logging.warning(f"Échec de l'envoi de l'email à {item.email}")
            except Exception as e:
                logging.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        
        items.append(item)
        credentials_list.append({
            'email': item.email,
            'temp_password': plain_password,
            'email_sent': email_sent
        })
    
    if success and items:
        response = {
            "items": [user.as_dict() for user in items],
            "credentials": credentials_list,
            "message": functional_error.MESSAGE_SUCCESS(),
            "code": 200
        }
    else:
        response = {"status": "error", "message": message or "Aucun utilisateur créé"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_users_with_temp_password ****")
    return response

 