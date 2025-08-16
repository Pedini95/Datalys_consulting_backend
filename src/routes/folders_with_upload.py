from flask import Blueprint, request
from services.folder_service import FolderService
import logging
import utils.functional_error as functional_error
import utils.utilities as utilities
import json
import os
from extensions import db
from flask_cors import cross_origin
from routes.auth import require_auth

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('folders', __name__)

folder_service = FolderService()

@bp.route('/folders/getByCriteria', methods=['POST'])
def get_folders():
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

@bp.route('/folders/create', methods=['POST'])
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

@bp.route('/folders/upload', methods=['POST'])
@cross_origin()
@require_auth
def upload_folder():
    """
    Upload de dossier complet (fichiers multiples ou ZIP)
    Supporte:
    - Fichiers multiples (sélection de dossier)
    - Fichier ZIP
    - Drag & Drop
    """
    logging.info("**** Begin upload_folder ****")
    logging.info("/folders/upload")
    
    try:
        # Vérifier l'authentification
        from routes.auth import require_auth
        # require_auth est un décorateur, on ne peut pas l'appeler directement
        # L'authentification sera vérifiée par le décorateur sur la route
        
        # Récupérer les paramètres
        user = request.form.get('user', '{}')
        if isinstance(user, str):
            user = json.loads(user)
        
        project_name = request.form.get('project_name')
        parent_folder_name = request.form.get('parent_folder_name')
        folder_name = request.form.get('folder_name', 'Uploaded Folder')
        
        # Détecter le type d'upload
        if 'files[]' in request.files:
            # Méthode 1: Fichiers multiples (sélection de dossier)
            return upload_multiple_files(user, project_name, parent_folder_name, folder_name)
        elif 'zip_file' in request.files:
            # Méthode 2: Fichier ZIP
            return upload_zip_file(user, project_name, parent_folder_name, folder_name)
        else:
            return {"status": "error", "message": "Aucun fichier détecté"}, 400
            
    except Exception as e:
        logger.error(f"Erreur lors de l'upload de dossier: {str(e)}")
        return {"status": "error", "message": f"Erreur interne: {str(e)}"}, 500

def upload_multiple_files(user, project_name, parent_folder_name, folder_name):
    """Upload de fichiers multiples (sélection de dossier)"""
    logging.info("Upload de fichiers multiples")
    
    files = request.files.getlist('files[]')
    if not files:
        return {"status": "error", "message": "Aucun fichier fourni"}, 400
    
    # Créer le dossier parent
    folder_data = {
        'name': folder_name
    }
    
    if project_name:
        folder_data['project_name'] = project_name
    if parent_folder_name:
        folder_data['parent_folder_name'] = parent_folder_name
    
    # Créer le dossier principal
    folder, success, message = folder_service.create(folder_data, user.get('id'))
    if not success:
        return {"status": "error", "message": message}, 400
    
    # Traiter chaque fichier
    uploaded_files = []
    for file in files:
        if file.filename:
            # Extraire le chemin relatif du fichier
            file_path = file.filename
            relative_path = file_path.replace('\\', '/')  # Normaliser les séparateurs
            
            # Créer la structure de sous-dossiers si nécessaire
            path_parts = relative_path.split('/')
            current_folder = folder
            
            # Créer les sous-dossiers
            for i, part in enumerate(path_parts[:-1]):
                subfolder_name = part
                subfolder_data = {
                    'name': subfolder_name,
                    'project_name': project_name,
                    'parent_folder_name': current_folder.name if current_folder else None
                }
                
                subfolder, sub_success, sub_message = folder_service.create(subfolder_data, user.get('id'))
                if sub_success and subfolder:
                    current_folder = subfolder
                else:
                    logger.warning(f"Impossible de créer le sous-dossier {subfolder_name}: {sub_message}")
            
            # Uploader le fichier
            filename = path_parts[-1]
            if current_folder is None:
                return {"status": "error", "message": "Impossible de créer le dossier parent"}, 400
            file_path = os.path.join(current_folder.path, filename)
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Enregistrer en base de données
            from models import File
            file_record = File(
                name=filename,  # type: ignore
                folder_id=current_folder.id,  # type: ignore
                file_url=file_path,  # type: ignore
                created_by=user.get('id')  # type: ignore
            )
            db.session.add(file_record)
            
            uploaded_files.append({
                'name': filename,
                'path': relative_path,
                'folder_id': current_folder.id
            })
    
    db.session.commit()
    
    if folder is None:
        return {"status": "error", "message": "Impossible de créer le dossier principal"}, 400
    
    return {
        "status": "success",
        "message": f"{len(uploaded_files)} fichiers uploadés avec succès",
        "folder_id": folder.id,
        "folder_name": folder.name,
        "files": uploaded_files
    }

def upload_zip_file(user, project_name, parent_folder_name, folder_name):
    """Upload de fichier ZIP"""
    logging.info("Upload de fichier ZIP")
    
    zip_file = request.files['zip_file']
    if not zip_file or zip_file.filename == '':
        return {"status": "error", "message": "Aucun fichier ZIP fourni"}, 400
    
    # Vérifier l'extension
    if zip_file.filename is None:
        return {"status": "error", "message": "Nom de fichier invalide"}, 400
    if not zip_file.filename.lower().endswith('.zip'):
        return {"status": "error", "message": "Le fichier doit être un ZIP"}, 400
    
    # Créer le dossier parent
    folder_data = {
        'name': folder_name
    }
    
    if project_name:
        folder_data['project_name'] = project_name
    if parent_folder_name:
        folder_data['parent_folder_name'] = parent_folder_name
    
    # Créer le dossier principal
    folder, success, message = folder_service.create(folder_data, user.get('id'))
    if not success:
        return {"status": "error", "message": message}, 400
    
    # Extraire le ZIP
    import zipfile
    import tempfile
    
    uploaded_files = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Sauvegarder le ZIP temporairement
        zip_path = os.path.join(temp_dir, 'upload.zip')
        zip_file.save(zip_path)
        
        # Extraire le contenu
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Parcourir les fichiers extraits
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file != 'upload.zip':  # Ignorer le fichier ZIP lui-même
                    # Calculer le chemin relatif
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, temp_dir)
                    
                    # Créer la structure de dossiers
                    path_parts = relative_path.replace('\\', '/').split('/')
                    current_folder = folder
                    
                    # Créer les sous-dossiers
                    for i, part in enumerate(path_parts[:-1]):
                        subfolder_name = part
                        if current_folder is None:
                            logger.error("current_folder est None, impossible de créer le sous-dossier")
                            continue
                        subfolder_data = {
                            'name': subfolder_name,
                            'project_name': project_name,
                            'parent_folder_name': current_folder.name
                        }
                        
                        subfolder, sub_success, sub_message = folder_service.create(subfolder_data, user.get('id'))
                        if sub_success:
                            current_folder = subfolder
                        else:
                            logger.warning(f"Impossible de créer le sous-dossier {subfolder_name}: {sub_message}")
                    
                    # Copier le fichier vers la destination finale
                    filename = path_parts[-1]
                    if current_folder is None:
                        logger.error("current_folder est None, impossible de continuer")
                        continue
                    final_path = os.path.join(current_folder.path, filename)
                    
                    # Créer le répertoire si nécessaire
                    os.makedirs(os.path.dirname(final_path), exist_ok=True)
                    
                    # Copier le fichier
                    import shutil
                    shutil.copy2(file_path, final_path)
                    
                    # Enregistrer en base de données
                    from models import File
                    file_record = File(
                        name=filename,  # type: ignore
                        folder_id=current_folder.id,  # type: ignore
                        file_url=final_path,  # type: ignore
                        created_by=user.get('id')  # type: ignore
                    )
                    db.session.add(file_record)
                    
                    uploaded_files.append({
                        'name': filename,
                        'path': relative_path,
                        'folder_id': current_folder.id
                    })
    
    db.session.commit()
    
    if folder is None:
        return {"status": "error", "message": "Impossible de créer le dossier principal"}, 400
    
    return {
        "status": "success",
        "message": f"{len(uploaded_files)} fichiers extraits et uploadés avec succès",
        "folder_id": folder.id,
        "folder_name": folder.name,
        "files": uploaded_files
    } 