import os
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Tuple
import mimetypes

logger = logging.getLogger(__name__)

class FileUploadManager:
    """
    Gestionnaire d'upload de fichiers
    """
    
    def __init__(self, upload_folder: str = 'uploads'):
        self.upload_folder = upload_folder
        # Extensions autorisées pour les images (logos)
        self.image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
        # Extensions autorisées pour tous les fichiers (upload générique)
        self.allowed_extensions = {
            # Images
            'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'tiff',
            # Documents
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf',
            # Archives
            'zip', 'rar', '7z', 'tar', 'gz',
            # Code
            'py', 'js', 'html', 'css', 'json', 'xml', 'sql',
            # Autres
            'csv', 'tsv', 'log', 'md'
        }
        self.max_file_size = 50 * 1024 * 1024  # 50MB (augmenté pour être cohérent avec Flask)
    
    def allowed_file(self, filename: str, image_only: bool = False) -> bool:
        """Vérifier si l'extension du fichier est autorisée"""
        if not '.' in filename:
            return False
        
        # Extraire l'extension et nettoyer les caractères parasites
        extension = filename.rsplit('.', 1)[1].lower()
        # Nettoyer l'extension des caractères non-alphanumériques à la fin
        extension = extension.rstrip('_').rstrip('-').rstrip('.')
        
        if image_only:
            return extension in self.image_extensions
        else:
            return extension in self.allowed_extensions
    
    def get_file_extension(self, filename: str) -> str:
        """Obtenir l'extension du fichier"""
        if '.' not in filename:
            return ''
        extension = filename.rsplit('.', 1)[1].lower()
        # Nettoyer l'extension des caractères non-alphanumériques à la fin
        cleaned_extension = str(extension).rstrip('_').rstrip('-').rstrip('.')
        return cleaned_extension if cleaned_extension else ''
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Générer un nom de fichier unique"""
        extension = self.get_file_extension(original_filename)
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{unique_id}.{extension}"
    
    def create_upload_path(self, subfolder: str = '') -> str:
        """Créer le chemin d'upload"""
        try:
            # Utiliser directement la configuration Flask
            config_upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if config_upload_folder is not None:
                base_path = str(config_upload_folder)
            else:
                base_path = './static/files'
            
            # Si le chemin est relatif, le rendre absolu par rapport au répertoire de l'application
            if not os.path.isabs(base_path):
                base_path = os.path.join(current_app.root_path, base_path)
            
            if subfolder and subfolder.strip():
                base_path = os.path.join(base_path, str(subfolder))
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(base_path, exist_ok=True)
            return str(base_path)
        except Exception as e:
            logger.error(f"Erreur lors de la création du chemin d'upload: {str(e)}")
            # Fallback vers le répertoire courant
            base_path = os.path.join(os.getcwd(), self.upload_folder)
            if subfolder and isinstance(subfolder, str) and subfolder.strip():
                base_path = os.path.join(base_path, subfolder)
            os.makedirs(base_path, exist_ok=True)
            return str(base_path)
    
    def save_file(self, file, subfolder: str = 'files', custom_filename: str | None = None, image_only: bool = False) -> Tuple[bool, str, str]:
        """
        Sauvegarder un fichier uploadé
        
        Args:
            file: Fichier Flask
            subfolder: Sous-dossier pour organiser les fichiers
            custom_filename: Nom personnalisé (optionnel)
            image_only: Si True, valide uniquement les images
            
        Returns:
            Tuple (succès, message, chemin_fichier)
        """
        try:
            # Vérifier si le fichier existe
            if not file or file.filename == '':
                return False, "Aucun fichier sélectionné", ""
            
            # Vérifier l'extension selon le type d'upload
            if not self.allowed_file(file.filename, image_only):
                if image_only:
                    return False, f"Type de fichier non autorisé. Extensions autorisées: {', '.join(self.image_extensions)}", ""
                else:
                    return False, f"Type de fichier non autorisé. Extensions autorisées: {', '.join(self.allowed_extensions)}", ""
            
            # Vérifier la taille
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.max_file_size:
                return False, f"Fichier trop volumineux. Taille max: {self.max_file_size // (1024*1024)}MB", ""
            
            # Générer le nom de fichier
            if custom_filename:
                filename = secure_filename(custom_filename)
            else:
                filename = self.generate_unique_filename(file.filename)
            
            # Créer le chemin d'upload
            upload_path = self.create_upload_path(subfolder)
            file_path = os.path.join(upload_path, filename)
            
            # Sauvegarder le fichier
            file.save(file_path)
            
            # Retourner le chemin relatif pour la base de données
            relative_path = os.path.join(self.upload_folder, subfolder, filename)
            
            logger.info(f"Fichier sauvegardé: {file_path}")
            return True, "Fichier sauvegardé avec succès", relative_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
            return False, f"Erreur lors de la sauvegarde: {str(e)}", ""
    
    def delete_file(self, file_path: str) -> bool:
        """
        Supprimer un fichier
        
        Args:
            file_path: Chemin relatif du fichier
            
        Returns:
            bool: True si supprimé avec succès
        """
        try:
            if not file_path:
                return True
            
            # Construire le chemin absolu
            absolute_path = os.path.join(current_app.root_path, file_path)
            
            # Vérifier si le fichier existe
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                logger.info(f"Fichier supprimé: {absolute_path}")
                return True
            else:
                logger.warning(f"Fichier non trouvé: {absolute_path}")
                return True  # Considérer comme succès si le fichier n'existe pas
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Générer l'URL d'accès au fichier via la route /files/serve
        
        Args:
            file_path: Chemin absolu du fichier uploadé
            
        Returns:
            str: URL complète du fichier accessible via /files/serve
        """
        if not file_path:
            return ""
        
        try:
            # Obtenir l'URL de base du serveur
            base_url = None
            
            # Essayer d'obtenir l'URL depuis la requête actuelle
            try:
                from flask import request, has_request_context
                
                if has_request_context() and hasattr(request, 'url_root') and request.url_root:
                    base_url = request.url_root.rstrip('/')
            except (RuntimeError, ImportError):
                # Pas de contexte de requête disponible
                pass
            
            # Fallback depuis la configuration
            if not base_url:
                base_url = current_app.config.get('APP_URL', 'http://82.112.253.137:8082')
            
            # Extraire le nom du fichier relatif depuis le chemin absolu
            # Exemple: /app/src/static/files/logos/image.png -> logos/image.png
            
            # Trouver la partie après 'static/files/'
            if 'static/files/' in file_path:
                relative_path = file_path.split('static/files/', 1)[1]
            else:
                # Fallback: utiliser juste le nom du fichier avec le dossier logos/
                filename = os.path.basename(file_path)
                # Détecter le type de fichier pour le sous-dossier approprié
                if any(ext in filename.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                    relative_path = f"logos/{filename}"
                else:
                    relative_path = f"files/{filename}"
            
            # Construire l'URL avec la route /files/serve
            file_url = f"{base_url}/files/serve/{relative_path}"
            
            logger.info(f"Generated file URL: {file_url} from path: {file_path}")
            return file_url
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'URL: {str(e)}")
            # Fallback d'urgence avec une URL statique
            filename = os.path.basename(file_path)
            if any(ext in filename.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                return f"http://82.112.253.137:8082/files/serve/logos/{filename}"
            else:
                return f"http://82.112.253.137:8082/files/serve/files/{filename}"
    
    def validate_image_file(self, file) -> Tuple[bool, str]:
        """
        Valider un fichier image
        
        Args:
            file: Fichier Flask
            
        Returns:
            Tuple (valide, message)
        """
        try:
            if not file:
                return False, "Aucun fichier fourni"
            
            # Vérifier le type MIME
            mime_type, _ = mimetypes.guess_type(file.filename)
            if not mime_type or not mime_type.startswith('image/'):
                return False, "Le fichier doit être une image"
            
            # Vérifier l'extension
            if not self.allowed_file(file.filename, image_only=True):
                return False, f"Format d'image non supporté. Formats autorisés: {', '.join(self.image_extensions)}"
            
            return True, "Fichier image valide"
            
        except Exception as e:
            return False, f"Erreur de validation: {str(e)}"

# Instance globale
file_upload_manager = FileUploadManager() 