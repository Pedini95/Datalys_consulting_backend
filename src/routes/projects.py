from flask import Blueprint, request
from services.project_service import ProjectService
import logging
from utils import functional_error, utilities
from flask_cors import cross_origin
from .auth import require_auth
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('projects', __name__)



project_service = ProjectService()

@bp.route('/projects/getByCriteria', methods=['POST'])
@cross_origin()
@require_auth
def get_projects():
    try:
        logging.info("**** Begin get_projects ****")
        logging.info("/projects/getByCriteria")
        r = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(r)
        index = r.get('index', 0)
        size = r.get('size', 10)
        criteria = r.get('data', {})

        projects, total_items = project_service.model_class.get_by_criteria(criteria, index, size)
        if projects:
            message = functional_error.MESSAGE_SUCCESS()
        else:
            message = functional_error.MESSAGE_DATA_EMPTY()

        # Préparer les items avec les informations du partenaire
        items = []
        for project in projects:
            project_dict = project.as_dict()

            # Ajouter les informations du partenaire si disponible
            if project.partner_id:
                try:
                    from models.partner import Partner
                    partner = Partner.query.filter_by(id=project.partner_id, is_deleted=False).first()
                    if partner:
                        project_dict['partner'] = partner.as_dict()
                    else:
                        project_dict['partner'] = None
                except Exception as e:
                    logging.error(f"Erreur lors du chargement du partenaire {project.partner_id}: {e}")
                    project_dict['partner'] = None
            else:
                project_dict['partner'] = None

            items.append(project_dict)

        response = {"items": items, "count": total_items, "message": message, "code": 200}
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End get_projects ****")
        return response
    except Exception as e:
        logging.error(f"Erreur dans get_projects: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Erreur lors de la récupération des projets: {str(e)}", "code": 500}, 500

@bp.route('/projects/create', methods=['POST'])
@cross_origin()
@require_auth
def create_projects():
    logging.info("**** Begin create_projects ****")
    logging.info("/projects/create")
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
            'title': data.get('title')
        }
        
        # Ajouter partner_name si fourni (au lieu de partner_id)
        if 'partner_name' in data and data['partner_name']:
            processed_data['partner_name'] = data.get('partner_name')
        elif 'partner_id' in data and data['partner_id']:
            processed_data['partner_id'] = data.get('partner_id')
        
        # is_active sera géré automatiquement par le service
        processed_datas.append(processed_data)
    
    items = []
    all_success = True
    for data in processed_datas:
        item, success, message = project_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if all_success and items:
        response = {"items": [project.as_dict() for project in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": "Erreur lors de la création"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_projects ****")
    return response

@bp.route('/projects/update', methods=['POST'])
@cross_origin()
@require_auth
def update_projects():
    logging.info("**** Begin update_projects ****")
    logging.info("/projects/update")
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
        if 'partner_id' in data:
            processed_data['partner_id'] = data.get('partner_id')
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    all_success = True
    for data in processed_datas:
        item, success, message = project_service.update(data['id'], data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if all_success and items:
        response = {"items": [project.as_dict() for project in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": "Erreur lors de la mise à jour"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_projects ****")
    return response

@bp.route('/projects/<int:project_id>/close', methods=['POST'])
@cross_origin()
@require_auth
def close_project(project_id):
    """
    Clôture manuelle d'un projet.

    Body:
    {
        "user": {"id": 1},
        "closure_reason": "Projet terminé avec succès."
    }
    """
    logging.info(f"**** Begin close_project (id={project_id}) ****")
    r = request.get_json() or {}
    user = r.get('user', {})
    closure_reason = (r.get('closure_reason') or '').strip()

    if not closure_reason:
        return {"status": "error", "message": "Le motif de clôture est obligatoire.", "code": 400}, 400

    from models.project import Project
    from extensions import db

    project = Project.query.filter_by(id=project_id, is_deleted=False).first()
    if not project:
        return {"status": "error", "message": "Projet non trouvé.", "code": 404}, 404

    if not project.is_active:
        return {"status": "error", "message": "Le projet est déjà clôturé.", "code": 400}, 400

    project.is_active = False
    project.closed_at = datetime.utcnow()
    project.closed_by = user.get('id')
    project.closure_reason = closure_reason
    project.updated_at = datetime.utcnow()
    project.updated_by = user.get('id')

    try:
        db.session.commit()
        logging.info(f"Projet {project_id} clôturé par user {user.get('id')}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur clôture projet {project_id}: {str(e)}")
        return {"status": "error", "message": f"Erreur lors de la clôture : {str(e)}", "code": 500}, 500

    return {"code": 200, "message": functional_error.MESSAGE_SUCCESS(), "data": project.as_dict()}


@bp.route('/projects/<int:project_id>/reopen', methods=['POST'])
@cross_origin()
@require_auth
def reopen_project(project_id):
    """
    Réouverture manuelle d'un projet clôturé.

    Body:
    {
        "user": {"id": 1}
    }
    """
    logging.info(f"**** Begin reopen_project (id={project_id}) ****")
    r = request.get_json() or {}
    user = r.get('user', {})

    from models.project import Project
    from extensions import db

    project = Project.query.filter_by(id=project_id, is_deleted=False).first()
    if not project:
        return {"status": "error", "message": "Projet non trouvé.", "code": 404}, 404

    if project.is_active:
        return {"status": "error", "message": "Le projet est déjà actif.", "code": 400}, 400

    project.is_active = True
    project.reopened_at = datetime.utcnow()
    project.reopened_by = user.get('id')
    project.updated_at = datetime.utcnow()
    project.updated_by = user.get('id')

    try:
        db.session.commit()
        logging.info(f"Projet {project_id} réouvert par user {user.get('id')}")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur réouverture projet {project_id}: {str(e)}")
        return {"status": "error", "message": f"Erreur lors de la réouverture : {str(e)}", "code": 500}, 500

    return {"code": 200, "message": functional_error.MESSAGE_SUCCESS(), "data": project.as_dict()}


@bp.route('/projects/delete', methods=['POST'])
@cross_origin()
@require_auth
def delete_projects():
    logging.info("**** Begin delete_projects ****")
    logging.info("/projects/delete")
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
        success, message = project_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_projects ****")
    return response 