from flask import Blueprint, request, jsonify
from extensions import db
from services.partner_service import PartnerService
from utils.file_upload import file_upload_manager
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from flasgger import swag_from
from flask_cors import CORS, cross_origin
from routes.auth import require_auth
import json
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('partners', __name__)



partner_service = PartnerService()

@bp.route('/partners/getByCriteria', methods=['POST'])
@cross_origin()
def get_partners():
    logging.info("**** Begin get_partners ****")
    logging.info("/partners/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    partners, total_items = partner_service.model_class.get_by_criteria(criteria, index, size)
    if partners:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [partner.as_dict() for partner in partners], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_partners ****")
    return response

@bp.route('/partners/create', methods=['POST'])
@cross_origin()
@require_auth
def create_partners():
    """
    Création de partenaires avec upload de logo intégré
    Supporte les formats JSON et multipart/form-data
    """
    try:
        logging.info("**** Begin create_partners ****")
        logging.info("/partners/create")
        
        # Détecter le type de requête
        content_type = request.content_type or ''
        
        if 'multipart/form-data' in content_type:
            # Requête avec fichier logo
            logging.info("Mode multipart/form-data détecté")
            return _create_partners_with_logo()
        else:
            # Requête JSON classique
            logging.info("Mode JSON détecté")
            return _create_partners_json()
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de partenaires: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

def _create_partners_with_logo():
    """
    Création de partenaires avec upload de logo intégré
    """
    try:
        logging.info("**** Begin create_partners_with_logo ****")
        
        # Récupérer les données JSON depuis form-data
        partner_data_str = request.form.get('data', '{}')
        user_data_str = request.form.get('user', '{}')
        
        logging.info(f"Partner data string: {partner_data_str}")
        logging.info(f"User data string: {user_data_str}")
        
        # Parser les données JSON
        try:
            partner_data = json.loads(partner_data_str)
            user_data = json.loads(user_data_str)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {str(e)}")
            return {"status": "error", "message": "Données JSON invalides"}, 400
        
        # Convertir en format attendu par le service
        datas = [partner_data] if isinstance(partner_data, dict) else partner_data
        
        # Récupérer le fichier logo (optionnel)
        logo_file = request.files.get('logo')
        logo_url = None
        
        if logo_file and logo_file.filename:
            logging.info(f"Logo file détecté: {logo_file.filename}")
            
            # Valider le fichier logo
            is_valid, message = file_upload_manager.validate_image_file(logo_file)
            if not is_valid:
                logger.warning(f"Validation logo échouée: {message}")
                return {"status": "error", "message": message}, 400
            
            # Uploader le logo
            success, message, file_path = file_upload_manager.save_file(logo_file, subfolder='logos')
            if success:
                logo_url = file_upload_manager.get_file_url(file_path)
                logging.info(f"Logo uploadé avec succès: {logo_url}")
            else:
                logger.error(f"Échec upload logo: {message}")
                return {"status": "error", "message": f"Erreur upload logo: {message}"}, 500
        else:
            logging.info("Aucun logo fourni")
        
        # Préparer les données pour le service
        processed_datas = []
        for data in datas:
            # Champs obligatoires
            required_fields = ['name']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
            
            processed_data = {
                'name': data.get('name'),
                'logo_url': logo_url or data.get('logo_url'),  # Priorité au logo uploadé
                'is_active': data.get('is_active', True)
            }
            
            # Ajouter les champs optionnels
            if 'email' in data:
                processed_data['email'] = data.get('email')
            if 'phone' in data:
                processed_data['phone'] = data.get('phone')
            if 'address' in data:
                processed_data['address'] = data.get('address')
            
            processed_datas.append(processed_data)
        
        # Créer les partenaires
        items = []
        for data in processed_datas:
            item, success, message = partner_service.create(data, user_data.get('id'))
            if not success:
                # En cas d'échec, supprimer le logo uploadé
                if logo_url:
                    try:
                        file_upload_manager.delete_file(logo_url)
                        logging.info(f"Logo supprimé après échec création: {logo_url}")
                    except Exception as e:
                        logger.error(f"Erreur suppression logo: {str(e)}")
                
                return {"status": "error", "message": message}, 400
            items.append(item)
        
        response = {
            "items": [partner.as_dict() for partner in items], 
            "message": functional_error.MESSAGE_SUCCESS(), 
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End create_partners_with_logo ****")
        return response
        
    except Exception as e:
        logger.error(f"Erreur dans _create_partners_with_logo: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

def _create_partners_json():
    """
    Création de partenaires en mode JSON (compatibilité)
    """
    try:
        logging.info("**** Begin create_partners_json ****")
        
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
                'name': data.get('name'),
                'logo_url': data.get('logo_url'),
                'is_active': data.get('is_active', True)
            }
            
            # Ajouter les champs optionnels
            if 'email' in data:
                processed_data['email'] = data.get('email')
            if 'phone' in data:
                processed_data['phone'] = data.get('phone')
            if 'address' in data:
                processed_data['address'] = data.get('address')
            
            processed_datas.append(processed_data)
        
        items = []
        for data in processed_datas:
            item, success, message = partner_service.create(data, user.get('id'))
            if not success:
                return {"status": "error", "message": message}, 400
            items.append(item)
        
        response = {
            "items": [partner.as_dict() for partner in items], 
            "message": functional_error.MESSAGE_SUCCESS(), 
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End create_partners_json ****")
        return response
        
    except Exception as e:
        logger.error(f"Erreur dans _create_partners_json: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500

@bp.route('/partners/update', methods=['POST'])
@cross_origin()
def update_partners():
    logging.info("**** Begin update_partners ****")
    logging.info("/partners/update")
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
        if utilities.not_blank(data.get('phone')):
            processed_data['phone'] = data.get('phone')
        if utilities.not_blank(data.get('address')):
            processed_data['address'] = data.get('address')
        if utilities.not_blank(data.get('logo_url')):
            processed_data['logo_url'] = data.get('logo_url')
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    all_success = True
    for data in processed_datas:
        item, success, message = partner_service.update(data['id'], data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if all_success and items:
        response = {"items": [partner.as_dict() for partner in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": "Erreur lors de la mise à jour"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_partners ****")
    return response



@bp.route('/partners/delete', methods=['POST'])
@cross_origin()
def delete_partners():
    logging.info("**** Begin delete_partners ****")
    logging.info("/partners/delete")
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
        success, message = partner_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_partners ****")
    return response 