from flask import Blueprint, request
from services.user_service import UserService
from utils.notification import EmailService
import logging
import utils.functional_error as functional_error
import utils.utilities as utilities
from flask_cors import cross_origin
from routes.auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('users', __name__)



user_service = UserService()

@bp.route('/users/getByCriteria', methods=['POST'])
@cross_origin()
@require_auth
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
        
        processed_data = {
            'name': data.get('name', ''),
            'email': data.get('email'),
            'password': data.get('password'),
            'role_name': data.get('role_name'),
            'is_active': data.get('is_active', True)
        }
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = user_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        
        # Envoyer l'email de bienvenue
        if success and item:
            try:
                email_service = EmailService()
                login_url = f"https://applicationweb.datalysconsulting.com/connexion"
                # Calculer le nom complet pour l'email
                user_name = item.name if hasattr(item, 'name') else f"{item.first_name or ''} {item.last_name or ''}".strip() or item.username
                email_sent = email_service.send_welcome_email(
                    user_email=item.email,
                    user_name=user_name,
                    login_url=login_url
                )
                if email_sent:
                    logging.info(f"Email de bienvenue envoyé à {item.email}")
                else:
                    logging.warning(f"Échec de l'envoi de l'email de bienvenue à {item.email}")
            except Exception as e:
                logging.error(f"Erreur lors de l'envoi de l'email de bienvenue: {str(e)}")
        
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

 