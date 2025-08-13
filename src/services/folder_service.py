from models import Folder
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from app import db
import logging

logger = logging.getLogger(__name__)


class FolderService:
    """
    Service pour la gestion des folders
    """
    
    def __init__(self):
        self.model_class = Folder
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Folder], bool, str]:
        """
        Créer un nouveau folder
        
        Args:
            data: Données du folder à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (folder, succès, message)
        """
        try:
            # Traiter le project_name si fourni
            if 'project_name' in data and data['project_name']:
                from models import Project
                # Rechercher le projet par nom
                projects, _ = Project.get_by_criteria({'title': data['project_name']}, 0, 1)
                if projects:
                    data['project_id'] = projects[0].id
                    logger.info(f"Projet trouvé: {data['project_name']} (ID: {projects[0].id})")
                else:
                    logger.warning(f"Projet non trouvé: {data['project_name']}")
                    return None, False, f"Projet non trouvé: {data['project_name']}"
                
                # Supprimer project_name des données
                del data['project_name']
            
            # Traiter le parent_folder_name si fourni
            if 'parent_folder_name' in data and data['parent_folder_name']:
                # Rechercher le dossier parent par nom
                folders, _ = self.model_class.get_by_criteria({'name': data['parent_folder_name']}, 0, 1)
                if folders:
                    data['parent_folder_id'] = folders[0].id
                    logger.info(f"Dossier parent trouvé: {data['parent_folder_name']} (ID: {folders[0].id})")
                else:
                    logger.warning(f"Dossier parent non trouvé: {data['parent_folder_name']}")
                    return None, False, f"Dossier parent non trouvé: {data['parent_folder_name']}"
                
                # Supprimer parent_folder_name des données
                del data['parent_folder_name']
            
            # Définir is_active à True par défaut si non spécifié
            if 'is_active' not in data:
                data['is_active'] = True
                logger.info("is_active défini à True par défaut")
            
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            folder = self.model_class(**data)
            db.session.add(folder)
            db.session.flush()  # Pour obtenir l'ID du dossier
            
            # Créer le répertoire physique
            try:
                import os
                import config
                
                # Construire le chemin du répertoire (structure hybride: ID_Nom)
                upload_folder = getattr(config, 'UPLOAD_FOLDER', './static/files')
                if folder.project_id:
                    # Dossier dans un projet
                    folder_name_safe = folder.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    folder_path = os.path.join(upload_folder, "projects", str(folder.project_id), "folders", f"{folder.id}_{folder_name_safe}")
                else:
                    # Dossier global
                    folder_name_safe = folder.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
                    folder_path = os.path.join(upload_folder, "global", "folders", f"{folder.id}_{folder_name_safe}")
                
                # Créer le répertoire et ses parents
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"Répertoire physique créé: {folder_path}")
                
                # Mettre à jour le chemin dans la base de données
                folder.path = folder_path
                
            except Exception as e:
                logger.error(f"Erreur lors de la création du répertoire physique: {str(e)}")
                db.session.rollback()
                return None, False, f"Erreur lors de la création du répertoire: {str(e)}"
            
            db.session.commit()
            
            return folder, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, folder_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Folder], bool, str]:
        """
        Mettre à jour un folder
        
        Args:
            folder_id: ID du folder à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (folder, succès, message)
        """
        try:
            # Vérifier si le folder existe
            folders, _ = self.model_class.get_by_criteria({'id': folder_id}, 0, 1)
            if not folders:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            folder = folders[0]
            
            # Traiter le project_name si fourni
            if 'project_name' in data and data['project_name']:
                from models import Project
                # Rechercher le projet par nom
                projects, _ = Project.get_by_criteria({'title': data['project_name']}, 0, 1)
                if projects:
                    data['project_id'] = projects[0].id
                    logger.info(f"Projet trouvé pour mise à jour: {data['project_name']} (ID: {projects[0].id})")
                else:
                    logger.warning(f"Projet non trouvé pour mise à jour: {data['project_name']}")
                    return None, False, f"Projet non trouvé: {data['project_name']}"
                
                # Supprimer project_name des données
                del data['project_name']
            
            # Traiter le parent_folder_name si fourni
            if 'parent_folder_name' in data and data['parent_folder_name']:
                # Rechercher le dossier parent par nom
                folders_parent, _ = self.model_class.get_by_criteria({'name': data['parent_folder_name']}, 0, 1)
                if folders_parent:
                    data['parent_folder_id'] = folders_parent[0].id
                    logger.info(f"Dossier parent trouvé pour mise à jour: {data['parent_folder_name']} (ID: {folders_parent[0].id})")
                else:
                    logger.warning(f"Dossier parent non trouvé pour mise à jour: {data['parent_folder_name']}")
                    return None, False, f"Dossier parent non trouvé: {data['parent_folder_name']}"
                
                # Supprimer parent_folder_name des données
                del data['parent_folder_name']
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(folder, key):
                    setattr(folder, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(folder, 'updated_by'):
                folder.updated_by = user_id
            
            db.session.commit()
            
            return folder, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, folder_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un folder (soft delete par défaut)
        
        Args:
            folder_id: ID du folder à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le folder existe
            folders, _ = self.model_class.get_by_criteria({'id': folder_id}, 0, 1)
            if not folders:
                return False, f"{self.model_class.__name__} non trouvé"
            
            folder = folders[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(folder)
            else:
                # Soft delete
                if hasattr(folder, 'is_deleted'):
                    folder.is_deleted = True
                    if user_id and hasattr(folder, 'updated_by'):
                        folder.updated_by = user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(folder)
            
            db.session.commit()
            
            return True, f"{self.model_class.__name__} supprimé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression de {self.model_class.__name__}: {str(e)}")
            return False, f"Erreur lors de la suppression: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la suppression de {self.model_class.__name__}: {str(e)}")
            return False, f"Erreur inattendue: {str(e)}"
    
    def getByCriteria(self, criteria: Dict[str, Any], index: int = 0, size: int = 10) -> Tuple[list, int]:
        """
        Récupérer des folders selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des folders, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
