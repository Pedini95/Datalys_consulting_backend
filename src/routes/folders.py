from flask import Blueprint, request
from services.folder_service import FolderService
import logging
from utils import functional_error, utilities
from flask_cors import cross_origin
from .auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('folders', __name__)

folder_service = FolderService()

@bp.route('/folders/getByCriteria', methods=['POST'])
@cross_origin()
@require_auth
def get_folders():
    try:
        logging.info("**** Begin get_folders ****")
        logging.info("/folders/getByCriteria")
        r = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(r)
        index = r.get('index', 0)
        size = r.get('size', 10)
        criteria = r.get('data', {})

        folders, total_items = folder_service.model_class.get_by_criteria(criteria, index, size)
        if folders:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()

        response = {"items": [folder.as_dict() for folder in folders], "count": total_items, "message": message, "code": 200}
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End get_folders ****")
        return response
    except Exception as e:
        logging.error(f"Erreur dans get_folders: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Erreur lors de la récupération des dossiers: {str(e)}", "code": 500}, 500

@bp.route('/folders/create', methods=['POST'])
@cross_origin()
@require_auth
def create_folders():
    logging.info("**** Begin create_folders ****")
    logging.info("/folders/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['name']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {
            'name': data.get('name')
        }
        
        # Ajouter project_name si fourni (au lieu de project_id)
        if 'project_name' in data and data['project_name']:
            processed_data['project_name'] = data.get('project_name')
        elif 'project_id' in data and data['project_id']:
            processed_data['project_id'] = data.get('project_id')
        
        # Ajouter parent_folder_name si fourni (au lieu de parent_folder_id)
        if 'parent_folder_name' in data and data['parent_folder_name']:
            processed_data['parent_folder_name'] = data.get('parent_folder_name')
        elif 'parent_folder_id' in data and data['parent_folder_id']:
            processed_data['parent_folder_id'] = data.get('parent_folder_id')
        
        # is_active sera géré automatiquement par le service
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    for data in processed_datas:
        logging.info(f"Tentative de création de dossier avec les données: {data}")
        item, item_success, item_message = folder_service.create(data, user.get('id'))
        logging.info(f"Résultat: success={item_success}, message={item_message}")
        if not item_success:
            return {"status": "error", "message": item_message}, 400
        items.append(item)
    
    if success:
        response = {"items": [folder.as_dict() for folder in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_folders ****")
    return response

@bp.route('/folders/update', methods=['POST'])
@cross_origin()
@require_auth
def update_folders():
    logging.info("**** Begin update_folders ****")
    logging.info("/folders/update")
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
        
        # Ajouter project_name si fourni (au lieu de project_id)
        if 'project_name' in data and data['project_name']:
            processed_data['project_name'] = data.get('project_name')
        elif 'project_id' in data and data['project_id']:
            processed_data['project_id'] = data.get('project_id')
        
        # Ajouter parent_folder_name si fourni (au lieu de parent_folder_id)
        if 'parent_folder_name' in data and data['parent_folder_name']:
            processed_data['parent_folder_name'] = data.get('parent_folder_name')
        elif 'parent_folder_id' in data and data['parent_folder_id']:
            processed_data['parent_folder_id'] = data.get('parent_folder_id')
        
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    for data in processed_datas:
        item, item_success, item_message = folder_service.update(data['id'], data, user.get('id'))
        if not item_success:
            return {"status": "error", "message": item_message}, 400
        items.append(item)
    
    if success:
        response = {"items": [folder.as_dict() for folder in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_folders ****")
    return response

@bp.route('/folders/delete', methods=['POST'])
@cross_origin()
@require_auth
def delete_folders():
    logging.info("**** Begin delete_folders ****")
    logging.info("/folders/delete")
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
        success, message = folder_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_folders ****")
    return response 