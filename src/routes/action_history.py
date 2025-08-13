from flask import Blueprint, request
from services.action_history_service import ActionHistoryService
import logging
import utils.functional_error as functional_error

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('action_history', __name__)

action_history_service = ActionHistoryService()

@bp.route('/action_history/getByCriteria', methods=['POST'])
def get_action_history():
    logging.info("**** Begin get_action_history ****")
    logging.info("/action_history/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    actions, total_items = action_history_service.model_class.get_by_criteria(criteria, index, size)
    if actions:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [action.as_dict() for action in actions], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_action_history ****")
    return response

@bp.route('/action_history/create', methods=['POST'])
def create_action_history():
    logging.info("**** Begin create_action_history ****")
    logging.info("/action_history/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['user_id', 'action_type', 'entity_type', 'description']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {
            'user_id': data.get('user_id'),
            'action_type': data.get('action_type'),
            'entity_type': data.get('entity_type'),
            'entity_id': data.get('entity_id'),
            'description': data.get('description'),
            'ip_address': data.get('ip_address'),
            'user_agent': data.get('user_agent')
        }
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    for data in processed_datas:
        item, item_success, item_message = action_history_service.create(data)
        if not item_success:
            return {"status": "error", "message": item_message}, 400
        items.append(item)
    
    if success:
        response = {"items": [action.as_dict() for action in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_action_history ****")
    return response

@bp.route('/action_history/log', methods=['POST'])
def log_action():
    logging.info("**** Begin log_action ****")
    logging.info("/action_history/log")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user_id = r.get('user_id')
    action_type = r.get('action_type')
    entity_type = r.get('entity_type')
    entity_id = r.get('entity_id')
    description = r.get('description', '')
    ip_address = r.get('ip_address')
    user_agent = r.get('user_agent')
    
    if not user_id or not action_type or not entity_type:
        return {"status": "error", "message": "user_id, action_type, and entity_type are required"}, 400
    
    # Utiliser la méthode create au lieu de log_action
    action_data = {
        'user_id': user_id,
        'action_type': action_type,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'description': description,
        'ip_address': ip_address,
        'user_agent': user_agent
    }
    
    action, success, message = action_history_service.create(action_data)
    
    if success and action:
        response = {"action": action.as_dict(), "message": message, "code": 200}
    else:
        response = {"status": "error", "message": message}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End log_action ****")
    return response 