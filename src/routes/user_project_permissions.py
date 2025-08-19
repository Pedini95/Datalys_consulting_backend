from flask import Blueprint, request
from services import UserProjectPermissionService
import logging
from utils import functional_error
from flask_cors import cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('user_project_permissions', __name__)



permission_service = UserProjectPermissionService()

@bp.route('/user_project_permissions/getByCriteria', methods=['POST'])
@cross_origin()
def get_user_project_permissions():
    logging.info("**** Begin get_user_project_permissions ****")
    logging.info("/user_project_permissions/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    permissions, total_items = permission_service.model_class.get_by_criteria(criteria, index, size)
    if permissions:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [permission.as_dict() for permission in permissions], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_user_project_permissions ****")
    return response

@bp.route('/user_project_permissions/create', methods=['POST'])
@cross_origin()
def create_user_project_permissions():
    logging.info("**** Begin create_user_project_permissions ****")
    logging.info("/user_project_permissions/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['user_id', 'project_id', 'role_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {
            'user_id': data.get('user_id'),
            'project_id': data.get('project_id'),
            'role_id': data.get('role_id'),
            'is_active': data.get('is_active', True)
        }
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = permission_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        

        
        items.append(item)
    
    if success and items:
        response = {"items": [permission.as_dict() for permission in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucune permission créée"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_user_project_permissions ****")
    return response

@bp.route('/user_project_permissions/update', methods=['POST'])
@cross_origin()
def update_user_project_permissions():
    logging.info("**** Begin update_user_project_permissions ****")
    logging.info("/user_project_permissions/update")
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
        
        if 'user_id' in data:
            processed_data['user_id'] = data.get('user_id')
        if 'project_id' in data:
            processed_data['project_id'] = data.get('project_id')
        if 'role_id' in data:
            processed_data['role_id'] = data.get('role_id')
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = permission_service.update(data['id'], data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if success and items:
        response = {"items": [permission.as_dict() for permission in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucune permission mise à jour"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_user_project_permissions ****")
    return response

@bp.route('/user_project_permissions/delete', methods=['POST'])
@cross_origin()
def delete_user_project_permissions():
    logging.info("**** Begin delete_user_project_permissions ****")
    logging.info("/user_project_permissions/delete")
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
        success, message = permission_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_user_project_permissions ****")
    return response 