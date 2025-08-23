import os
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Tuple
import mimetypes
from PIL import Image

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
        
        # Restrictions de résolution pour les logos
        self.logo_resolution_limits = {
            'min_width': 100,    # Largeur minimale en pixels
            'max_width': 2000,   # Largeur maximale en pixels
            'min_height': 100,   # Hauteur minimale en pixels
            'max_height': 2000,  # Hauteur maximale en pixels
            'max_aspect_ratio': 5.0,  # Ratio largeur/hauteur maximum
            'min_aspect_ratio': 0.2   # Ratio largeur/hauteur minimum
        }
        
        # Restrictions de résolution pour les images génériques
        self.image_resolution_limits = {
            'min_width': 50,     # Largeur minimale en pixels
            'max_width': 5000,   # Largeur maximale en pixels
            'min_height': 50,    # Hauteur minimale en pixels
            'max_height': 5000,  # Hauteur maximale en pixels
            'max_aspect_ratio': 10.0, # Ratio largeur/hauteur maximum
            'min_aspect_ratio': 0.1   # Ratio largeur/hauteur minimum
        }
    
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
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Générer un nom de fichier unique avec timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = self.get_file_extension(original_filename)
        
        if extension:
            return f"{timestamp}_{unique_id}.{extension}"
        else:
            return f"{timestamp}_{unique_id}"
    
    def create_upload_path(self, subfolder: str = '') -> str:
        """Créer le chemin d'upload avec sous-dossier"""
        try:
            # Utiliser le dossier d'upload configuré dans Flask
            base_path = current_app.config.get('UPLOAD_FOLDER', self.upload_folder)
            
            if subfolder:
                base_path = os.path.join(base_path, subfolder)
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(base_path, exist_ok=True)
            return str(base_path)
        except Exception as e:
            logger.error(f"Erreur création chemin upload: {e}")
            # Fallback vers le dossier par défaut
            base_path = os.path.join(self.upload_folder, subfolder)
            os.makedirs(base_path, exist_ok=True)
            return str(base_path)
    
    def validate_image_resolution(self, file, is_logo: bool = False) -> Tuple[bool, str]:
        """
        Valider la résolution d'une image
        
        Args:
            file: Fichier Flask
            is_logo: Si True, applique les restrictions de logo
            
        Returns:
            Tuple (valide, message)
        """
        try:
            # Lire l'image avec PIL
            file.seek(0)
            image = Image.open(file)
            file.seek(0)  # Remettre le curseur au début
            
            width, height = image.size
            
            # Choisir les limites selon le type
            limits = self.logo_resolution_limits if is_logo else self.image_resolution_limits
            
            # Vérifier les dimensions
            if width < limits['min_width']:
                return False, f"Largeur trop petite. Minimum: {limits['min_width']}px, actuel: {width}px"
            
            if width > limits['max_width']:
                return False, f"Largeur trop grande. Maximum: {limits['max_width']}px, actuel: {width}px"
            
            if height < limits['min_height']:
                return False, f"Hauteur trop petite. Minimum: {limits['min_height']}px, actuel: {height}px"
            
            if height > limits['max_height']:
                return False, f"Hauteur trop grande. Maximum: {limits['max_height']}px, actuel: {height}px"
            
            # Vérifier le ratio d'aspect
            aspect_ratio = width / height
            if aspect_ratio > limits['max_aspect_ratio']:
                return False, f"Ratio d'aspect trop large. Maximum: {limits['max_aspect_ratio']}, actuel: {aspect_ratio:.2f}"
            
            if aspect_ratio < limits['min_aspect_ratio']:
                return False, f"Ratio d'aspect trop étroit. Minimum: {limits['min_aspect_ratio']}, actuel: {aspect_ratio:.2f}"
            
            return True, f"Résolution valide: {width}x{height}px"
            
        except Exception as e:
            logger.error(f"Erreur validation résolution: {e}")
            return False, f"Erreur lors de la validation de la résolution: {str(e)}"
    
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
            
            # Valider la résolution si c'est une image
            if image_only:
                is_logo = subfolder == 'logos'
                resolution_valid, resolution_message = self.validate_image_resolution(file, is_logo)
                if not resolution_valid:
                    return False, resolution_message, ""
                logger.info(f"Résolution validée: {resolution_message}")
            
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
            relative_path = os.path.join(subfolder, filename)
            
            logger.info(f"Fichier sauvegardé: {file_path}")
            return True, "Fichier sauvegardé avec succès", relative_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False, f"Erreur lors de la sauvegarde: {str(e)}", ""
    
    def delete_file(self, file_path: str) -> bool:
        """Supprimer un fichier"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Fichier supprimé: {file_path}")
                return True
            else:
                logger.warning(f"Fichier non trouvé: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """Générer l'URL d'accès au fichier"""
        try:
            # Construire l'URL de base
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            
            # Nettoyer le chemin
            relative_path = file_path.replace('\\', '/').lstrip('/')
            
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