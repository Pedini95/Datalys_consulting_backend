from flask import Blueprint, request, jsonify, send_from_directory, g
from services.file_service import FileService
from utils.file_upload import file_upload_manager
import logging
import utils.functional_error as functional_error
import utils.utilities as utilities
import os
from app import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('files', __name__)

file_service = FileService()

@bp.route('/files/getByCriteria', methods=['POST'])
@require_auth
def get_files():
    logging.info("**** Begin get_files ****")
    logging.info("/files/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    files, total_items = file_service.model_class.get_by_criteria(criteria, index, size)
    if files:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [file.as_dict() for file in files], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_files ****")
    return response

@bp.route('/files/update', methods=['POST'])
@require_auth
def update_files():
    logging.info("**** Begin update_files ****")
    logging.info("/files/update")
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
        if utilities.not_blank(data.get('file_url')):
            processed_data['file_url'] = data.get('file_url')
        if 'folder_id' in data:
            processed_data['folder_id'] = data.get('folder_id')
        if 'is_public' in data:
            processed_data['is_public'] = data.get('is_public')
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    for data in processed_datas:
        item, item_success, item_message = file_service.update(data['id'], data, user.get('id'))
        if not item_success:
            return {"status": "error", "message": item_message}, 400
        items.append(item)
    
    if success:
        response = {"items": [file.as_dict() for file in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_files ****")
    return response

@bp.route('/files/delete', methods=['POST'])
@require_auth
def delete_files():
    logging.info("**** Begin delete_files ****")
    logging.info("/files/delete")
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
        success, message = file_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_files ****")
    return response

# Routes pour l'upload de fichiers
@bp.route('/files/upload/logo', methods=['POST'])
@require_auth
def upload_logo():
    """
    Upload d'un logo pour un partner
    """
    try:
        logger.info("**** Begin upload_logo ****")
        
        # Vérifier si un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        
        # Vérifier si le fichier est valide
        is_valid, message = file_upload_manager.validate_image_file(file)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
        
        # Sauvegarder le fichier (upload logo - images uniquement)
        success, message, file_path = file_upload_manager.save_file(file, subfolder='logos', image_only=True)
        
        if success:
            # Générer l'URL d'accès
            file_url = file_upload_manager.get_file_url(file_path)
            
            response = {
                'status': 'success',
                'message': 'Logo uploadé avec succès',
                'data': {
                    'file_path': file_path,
                    'file_url': file_url,
                    'filename': os.path.basename(file_path)
                }
            }
            
            logger.info(f"**** Logo uploadé: {file_path} ****")
            return jsonify(response), 200
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de l'upload du logo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'upload: {str(e)}'
        }), 500

@bp.route('/files/upload', methods=['POST'])
@require_auth
def upload_file():
    """
    Upload générique de fichier avec création d'enregistrement DB
    """
    try:
        logger.info("**** Begin upload_file ****")
        
        # Vérifier si un fichier a été envoyé
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        subfolder = request.form.get('subfolder', 'files')
        
        # Récupérer les paramètres optionnels
        folder_id = request.form.get('folder_id')
        folder_name = request.form.get('folder_name')
        project_name = request.form.get('project_name')
        is_public = request.form.get('is_public', 'false').lower() == 'true'
        
        # Sauvegarder le fichier (upload générique - tous types acceptés)
        success, message, file_path = file_upload_manager.save_file(file, subfolder=subfolder, image_only=False)
        
        if success:
            # Générer l'URL d'accès
            file_url = file_upload_manager.get_file_url(file_path)
            
            # Créer l'enregistrement dans la base de données
            file_data = {
                'name': file.filename,
                'file_url': file_path,
                'is_public': is_public,
                'is_active': True
            }
            
            # Ajouter folder_id si fourni
            if folder_id:
                file_data['folder_id'] = int(folder_id)
            elif folder_name:
                # Rechercher le dossier par nom
                from models import Folder
                folders, _ = Folder.get_by_criteria({'name': folder_name}, 0, 1)
                if folders:
                    file_data['folder_id'] = folders[0].id
                    logger.info(f"Dossier trouvé: {folder_name} (ID: {folders[0].id})")
                else:
                    logger.warning(f"Dossier non trouvé: {folder_name}")
            
            # Créer l'enregistrement en base
            file_record, create_success, create_message = file_service.create(file_data, g.current_user.id)
            
            if create_success and file_record:
            response = {
                'status': 'success',
                'message': 'Fichier uploadé avec succès',
                'data': {
                    'file_path': file_path,
                    'file_url': file_url,
                        'filename': os.path.basename(file_path),
                        'file_id': file_record.id,
                        'db_record': file_record.as_dict()
                }
            }
            
                logger.info(f"**** Fichier uploadé et enregistré en DB: {file_path} (ID: {file_record.id}) ****")
            return jsonify(response), 200
            else:
                # Supprimer le fichier physique si l'enregistrement DB échoue
                file_upload_manager.delete_file(file_path)
                return jsonify({
                    'status': 'error',
                    'message': f'Fichier uploadé mais erreur DB: {create_message}'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de l'upload du fichier: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de l\'upload: {str(e)}'
        }), 500

@bp.route('/files/upload/delete', methods=['POST'])
@require_auth
def delete_uploaded_file():
    """
    Supprimer un fichier uploadé
    """
    try:
        logger.info("**** Begin delete_uploaded_file ****")
        
        data = request.get_json() or {}
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'status': 'error',
                'message': 'Chemin du fichier requis'
            }), 400
        
        # Supprimer le fichier
        success = file_upload_manager.delete_file(file_path)
        
        if success:
            response = {
                'status': 'success',
                'message': 'Fichier supprimé avec succès'
            }
            
            logger.info(f"**** Fichier supprimé: {file_path} ****")
            return jsonify(response), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Erreur lors de la suppression du fichier'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du fichier: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la suppression: {str(e)}'
        }), 500

# Route pour servir les fichiers statiques
@bp.route('/files/serve/<path:filename>')
def serve_file(filename):
    """
    Servir les fichiers uploadés
    """
    try:
        # Utiliser la configuration Flask pour le chemin d'upload
        from flask import current_app
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        
        if not upload_folder:
            # Fallback vers le répertoire de travail + static/files
            upload_folder = os.path.join(os.getcwd(), 'static', 'files')
        
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        logger.error(f"Erreur lors du service du fichier {filename}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Fichier non trouvé'
        }), 404 

@bp.route('/files/download/<int:file_id>', methods=['GET'])
@require_auth
def download_file(file_id):
    """
    Télécharger un fichier par son ID (API sécurisée)
    """
    try:
        logger.info(f"**** Begin download_file - ID: {file_id} ****")
        
        # Récupérer le fichier en base de données
        files, _ = file_service.model_class.get_by_criteria({'id': file_id}, 0, 1)
        if not files:
            return jsonify({
                'status': 'error',
                'message': 'Fichier non trouvé'
            }), 404
        
        file_record = files[0]
        
        # Vérifier si le fichier est actif
        if not file_record.is_active or file_record.is_deleted:
            return jsonify({
                'status': 'error',
                'message': 'Fichier non disponible'
            }), 404
        
        # Vérifier les permissions (optionnel)
        if not file_record.is_public:
            # Ici vous pouvez ajouter une logique de vérification des permissions
            pass
        
        # Construire le chemin du fichier physique
        file_path = file_record.file_url
        
        # Vérifier si le fichier existe physiquement
        if not os.path.exists(file_path):
            logger.error(f"Fichier physique non trouvé: {file_path}")
            return jsonify({
                'status': 'error',
                'message': 'Fichier physique non trouvé'
            }), 404
        
        # Incrémenter le compteur de téléchargements (optionnel)
        try:
            file_record.download_count = getattr(file_record, 'download_count', 0) + 1
            db.session.commit()
        except:
            pass
        
        # Servir le fichier
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        logger.info(f"**** Fichier téléchargé: {file_path} ****")
        
        return send_from_directory(
            directory, 
            filename, 
            as_attachment=True,  # Force le téléchargement
            download_name=file_record.name  # Nom du fichier pour le téléchargement
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement du fichier {file_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du téléchargement: {str(e)}'
        }), 500 