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
        
        # Ajouter les nouveaux champs pour la communication
        if 'type' in data and data['type']:
            processed_data['type'] = data.get('type')
        if 'priority' in data and data['priority']:
            processed_data['priority'] = data.get('priority')
        if 'status' in data and data['status']:
            processed_data['status'] = data.get('status')
        if 'category' in data and data['category']:
            processed_data['category'] = data.get('category')
        if 'assigned_to' in data and data['assigned_to']:
            processed_data['assigned_to'] = data.get('assigned_to')
        if 'parent_id' in data and data['parent_id']:
            processed_data['parent_id'] = data.get('parent_id')
        if 'resolution_notes' in data and data['resolution_notes']:
            processed_data['resolution_notes'] = data.get('resolution_notes')
        if 'is_read' in data:
            processed_data['is_read'] = data.get('is_read')
        
        # ✅ NOUVEAUX CHAMPS P0-P4
        if 'impact' in data and data['impact']:
            processed_data['impact'] = data.get('impact')
        if 'domain' in data and data['domain']:
            processed_data['domain'] = data.get('domain')
        if 'declarant_name' in data and data['declarant_name']:
            processed_data['declarant_name'] = data.get('declarant_name')
        if 'motif_attente' in data and data['motif_attente']:
            processed_data['motif_attente'] = data.get('motif_attente')
        
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
        
        # Ajouter les nouveaux champs pour la communication
        if 'type' in data and data['type']:
            processed_data['type'] = data.get('type')
        if 'priority' in data and data['priority']:
            processed_data['priority'] = data.get('priority')
        if 'status' in data and data['status']:
            processed_data['status'] = data.get('status')
        if 'category' in data and data['category']:
            processed_data['category'] = data.get('category')
        if 'assigned_to' in data and data['assigned_to']:
            processed_data['assigned_to'] = data.get('assigned_to')
        if 'parent_id' in data and data['parent_id']:
            processed_data['parent_id'] = data.get('parent_id')
        if 'resolution_notes' in data and data['resolution_notes']:
            processed_data['resolution_notes'] = data.get('resolution_notes')
        if 'is_read' in data:
            processed_data['is_read'] = data.get('is_read')
        
        # ✅ NOUVEAUX CHAMPS P0-P4
        if 'impact' in data and data['impact']:
            processed_data['impact'] = data.get('impact')
        if 'domain' in data and data['domain']:
            processed_data['domain'] = data.get('domain')
        if 'declarant_name' in data and data['declarant_name']:
            processed_data['declarant_name'] = data.get('declarant_name')
        if 'motif_attente' in data and data['motif_attente']:
            processed_data['motif_attente'] = data.get('motif_attente')
        
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

# ✅ NOUVELLE ROUTE : Obtenir les métadonnées des incidents (P0-P4, domaines, etc.)
@bp.route('/incidents/metadata', methods=['GET'])
@cross_origin()
@require_auth
def get_incidents_metadata():
    """
    Retourne les métadonnées pour les incidents :
    - Priorités valides (P0-P4)
    - Statuts valides
    - Impacts valides
    - Domaines valides
    - Mapping impact → priorité recommandée
    """
    logging.info("**** Begin get_incidents_metadata ****")
    
    from models.incident import Incident
    
    metadata = {
        "priorities": [
            {"value": "P0", "label": "Arrêt de service (immédiat)", "color": "red"},
            {"value": "P1", "label": "Forte dégradation de service", "color": "orange"},
            {"value": "P2", "label": "Dégradation de service", "color": "yellow"},
            {"value": "P3", "label": "Incident ordinaire", "color": "blue"},
            {"value": "P4", "label": "Incident mineur", "color": "green"}
        ],
        "statuses": [
            {"value": "nouveau", "label": "Nouveau", "color": "blue"},
            {"value": "en_cours", "label": "En cours", "color": "orange"},
            {"value": "en_attente", "label": "En attente", "color": "gray"},
            {"value": "en_arbitrage", "label": "En arbitrage", "color": "purple"},
            {"value": "resolu", "label": "Résolu", "color": "green"},
            {"value": "ferme", "label": "Fermé", "color": "black"}
        ],
        "impacts": [
            {"value": "arret_service", "label": "Arrêt de service", "recommended_priority": "P0"},
            {"value": "service_degrade", "label": "Service dégradé", "recommended_priority": "P1"},
            {"value": "majeur", "label": "Impact majeur", "recommended_priority": "P2"},
            {"value": "mineur", "label": "Impact mineur", "recommended_priority": "P3"}
        ],
        "domains": [
            {"value": "reseau", "label": "Réseau"},
            {"value": "infrastructure", "label": "Infrastructure système"},
            {"value": "cloud", "label": "Cloud"},
            {"value": "energie", "label": "Énergie"}
        ],
        "priority_mapping": Incident.get_priority_mapping()
    }
    
    response = {
        "code": 200,
        "message": functional_error.MESSAGE_SUCCESS(),
        "data": metadata
    }
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_incidents_metadata ****")
    return response 