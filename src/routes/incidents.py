from flask import Blueprint, request
from services import IncidentService
import logging
from utils import functional_error, utilities
from flask_cors import cross_origin
from .auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('incidents', __name__)



incident_service = IncidentService()

@bp.route('/incidents/getByCriteria', methods=['POST'])
@cross_origin()
@require_auth
def get_incidents():
    logging.info("**** Begin get_incidents ****")
    logging.info("/incidents/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    incidents, total_items = incident_service.model_class.get_by_criteria(criteria, index, size)
    if incidents:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [incident.as_dict() for incident in incidents], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_incidents ****")
    return response

@bp.route('/incidents/create', methods=['POST'])
@cross_origin()
@require_auth
def create_incidents():
    logging.info("**** Begin create_incidents ****")
    logging.info("/incidents/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['title']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'is_active': data.get('is_active', True)
        }
        
        # Ajouter user_name si fourni (au lieu de user_id)
        if 'user_name' in data and data['user_name']:
            processed_data['user_name'] = data.get('user_name')
        elif 'user_id' in data and data['user_id']:
            processed_data['user_id'] = data.get('user_id')
        
        # Ajouter project_name si fourni (au lieu de project_id)
        if 'project_name' in data and data['project_name']:
            processed_data['project_name'] = data.get('project_name')
        elif 'project_id' in data and data['project_id']:
            processed_data['project_id'] = data.get('project_id')
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = incident_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if success and items:
        response = {"items": [incident.as_dict() for incident in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucun incident créé"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_incidents ****")
    return response

@bp.route('/incidents/update', methods=['POST'])
@cross_origin()
@require_auth
def update_incidents():
    logging.info("**** Begin update_incidents ****")
    logging.info("/incidents/update")
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
        
        if utilities.not_blank(data.get('title')):
            processed_data['title'] = data.get('title')
        if utilities.not_blank(data.get('description')):
            processed_data['description'] = data.get('description')
        
        # Ajouter user_name si fourni (au lieu de user_id)
        if 'user_name' in data and data['user_name']:
            processed_data['user_name'] = data.get('user_name')
        elif 'user_id' in data and data['user_id']:
            processed_data['user_id'] = data.get('user_id')
        
        # Ajouter project_name si fourni (au lieu de project_id)
        if 'project_name' in data and data['project_name']:
            processed_data['project_name'] = data.get('project_name')
        elif 'project_id' in data and data['project_id']:
            processed_data['project_id'] = data.get('project_id')
        
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = incident_service.update(data['id'], data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if success and items:
        response = {"items": [incident.as_dict() for incident in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucun incident mis à jour"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_incidents ****")
    return response

@bp.route('/incidents/delete', methods=['POST'])
@cross_origin()
@require_auth
def delete_incidents():
    logging.info("**** Begin delete_incidents ****")
    logging.info("/incidents/delete")
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
        success, message = incident_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_incidents ****")
    return response 