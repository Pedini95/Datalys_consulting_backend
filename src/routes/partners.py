from flask import Blueprint, request, g
from services.partner_service import PartnerService
from utils.file_upload import file_upload_manager
import logging
from utils import functional_error, utilities
from flask_cors import cross_origin
from .auth import require_auth
import json
from utils.notification import EmailService
from middleware.role_security import _get_user_role

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
    Création de partenaires (mode JSON seulement)
    L'upload de logo se fait via l'API dédiée /partners/upload-logo/{id}
    """
    try:
        logging.info("**** Begin create_partners ****")
        logging.info("/partners/create")
        
        r = request.get_json() or {}
        logging.info("**** request input ****")
        logging.info(r)
        
        user = r.get('user', {})
        datas = r.get('datas', [])
        
        # Validation de la structure de base
        if not user or not user.get('id'):
            return {"status": "error", "message": "L'ID de l'utilisateur est requis"}, 400
        
        if not datas or not isinstance(datas, list):
            return {"status": "error", "message": "Le champ 'datas' doit être une liste non vide"}, 400
        
        # Préparer les données pour le service
        processed_datas = []
        for i, data in enumerate(datas):
            # Validation des champs obligatoires
            required_fields = ['name']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {"status": "error", "message": f"Le champ '{field}' est obligatoire pour l'élément {i+1}"}, 400
            
            # Validation du nom
            name = data.get('name', '').strip()
            if len(name) < 2:
                return {"status": "error", "message": f"Le nom doit contenir au moins 2 caractères pour l'élément {i+1}"}, 400
            if len(name) > 255:
                return {"status": "error", "message": f"Le nom ne peut pas dépasser 255 caractères pour l'élément {i+1}"}, 400
            
            # Validation de l'email
            email = data.get('email', '').strip()
            if email:
                if not utilities.is_valid_email(email):
                    return {"status": "error", "message": f"L'email '{email}' n'est pas valide pour l'élément {i+1}"}, 400
                if len(email) > 255:
                    return {"status": "error", "message": f"L'email ne peut pas dépasser 255 caractères pour l'élément {i+1}"}, 400
            
            # Validation du téléphone
            phone = data.get('phone', '').strip()
            if phone:
                # Vérifier que le téléphone contient au moins 10 chiffres
                digits_only = ''.join(filter(str.isdigit, phone))
                if len(digits_only) < 10:
                    return {"status": "error", "message": f"Le téléphone doit contenir au moins 10 chiffres pour l'élément {i+1}"}, 400
                if len(phone) > 50:
                    return {"status": "error", "message": f"Le téléphone ne peut pas dépasser 50 caractères pour l'élément {i+1}"}, 400
            
            # Validation de l'adresse
            address = data.get('address', '').strip()
            if address:
                if len(address) < 5:
                    return {"status": "error", "message": f"L'adresse doit contenir au moins 5 caractères pour l'élément {i+1}"}, 400
                if len(address) > 1000:
                    return {"status": "error", "message": f"L'adresse ne peut pas dépasser 1000 caractères pour l'élément {i+1}"}, 400
            
            processed_data = {
                'name': name,
                'is_active': True  # Toujours initialisé à True lors de la création
            }
            
            # Ajouter les champs optionnels validés
            if email:
                processed_data['email'] = email
            if phone:
                processed_data['phone'] = phone
            if address:
                processed_data['address'] = address
            
            processed_datas.append(processed_data)
        
        items = []
        for data in processed_datas:
            # Utiliser la nouvelle méthode qui crée aussi l'utilisateur
            item, username, temp_password, success, message = partner_service.create_with_user(data, user.get('id'))
            if not success:
                return {"status": "error", "message": message}, 400
            
            # Envoyer l'email avec les credentials
            if success and item and item.email and username and temp_password:
                try:
                    email_service = EmailService()
                    
                    email_sent = email_service.send_partner_credentials(
                        partner_email=item.email,
                        partner_name=item.name,
                        username=username,
                        password=temp_password
                    )
                    
                    if email_sent:
                        logging.info(f"Email avec credentials envoyé au partenaire {item.email}")
                    else:
                        logging.warning(f"Échec de l'envoi de l'email avec credentials à {item.email}")
                except Exception as e:
                    logging.error(f"Erreur lors de l'envoi de l'email avec credentials: {str(e)}")
            
            items.append(item)
        
        response = {
            "items": [partner.as_dict() for partner in items], 
            "message": functional_error.MESSAGE_SUCCESS(), 
            "code": 200
        }
        
        logging.info("**** response output ****")
        logging.info(response)
        logging.info("**** End create_partners ****")
        return response
        
    except Exception as e:
        logger.error(f"Erreur dans create_partners: {str(e)}")
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

@bp.route('/partners/upload-logo/<int:partner_id>', methods=['POST'])
@cross_origin()
@require_auth
def upload_partner_logo(partner_id):
    """
    Upload du logo pour un partenaire existant
    Permet aux admins et partenaires de changer le logo
    """
    try:
        logging.info(f"**** Begin upload_partner_logo for partner {partner_id} ****")
        
        # Vérifier que le partenaire existe
        partners, _ = partner_service.model_class.get_by_criteria({'id': partner_id}, 0, 1)
        if not partners:
            return {"status": "error", "message": "Partenaire non trouvé"}, 404
        
        partner = partners[0]
        
        # Vérifier les permissions (admin ou le partenaire lui-même)
        user_role = _get_user_role(g.current_user)
        if user_role != 'admin' and g.current_user.email != partner.email:
            return {"status": "error", "message": "Accès non autorisé"}, 403
        
        # Récupérer le fichier logo
        logo_file = request.files.get('logo')
        if not logo_file or not logo_file.filename:
            return {"status": "error", "message": "Aucun fichier logo fourni"}, 400
        
        # Upload du logo
        try:
            logo_url = file_upload_manager.upload_file(logo_file, 'logos')
            logging.info(f"Logo uploadé avec succès: {logo_url}")
        except Exception as e:
            logger.error(f"Erreur upload logo: {str(e)}")
            return {"status": "error", "message": f"Erreur upload logo: {str(e)}"}, 400
        
        # Supprimer l'ancien logo si il existe
        old_logo_url = partner.logo_url
        if old_logo_url:
            try:
                file_upload_manager.delete_file(old_logo_url)
                logging.info(f"Ancien logo supprimé: {old_logo_url}")
            except Exception as e:
                logger.warning(f"Impossible de supprimer l'ancien logo: {str(e)}")
        
        # Mettre à jour le partenaire avec le nouveau logo
        update_data = {'logo_url': logo_url}
        updated_partner, success, message = partner_service.update(partner_id, update_data, g.current_user.id)
        
        if not success:
            # En cas d'échec, supprimer le nouveau logo uploadé
            try:
                file_upload_manager.delete_file(logo_url)
                logging.info(f"Nouveau logo supprimé après échec mise à jour: {logo_url}")
            except Exception as e:
                logger.error(f"Erreur suppression nouveau logo: {str(e)}")
            
            return {"status": "error", "message": message}, 400
        
        response = {
            "partner": updated_partner.as_dict(),
            "message": "Logo mis à jour avec succès",
            "code": 200
        }
        
        logging.info(f"**** Logo uploadé avec succès pour le partenaire {partner_id} ****")
        return response
        
    except Exception as e:
        logger.error(f"Erreur dans upload_partner_logo: {str(e)}")
        return {"status": "error", "message": "Erreur interne du serveur"}, 500 

 