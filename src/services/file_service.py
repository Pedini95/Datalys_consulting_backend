from models import File
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from app import db
import logging

logger = logging.getLogger(__name__)


class FileService:
    """
    Service pour la gestion des files
    """
    
    def __init__(self):
        self.model_class = File
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[File], bool, str]:
        """
        Créer un nouveau file
        
        Args:
            data: Données du file à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (file, succès, message)
        """
        try:
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            file = self.model_class(**data)
            db.session.add(file)
            db.session.commit()
            
            return file, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, file_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[File], bool, str]:
        """
        Mettre à jour un file
        
        Args:
            file_id: ID du file à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (file, succès, message)
        """
        try:
            # Vérifier si le file existe
            files, _ = self.model_class.get_by_criteria({'id': file_id}, 0, 1)
            if not files:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            file = files[0]
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(file, key):
                    setattr(file, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(file, 'updated_by'):
                file.updated_by = user_id
            
            db.session.commit()
            
            return file, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, file_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un file (soft delete par défaut)
        
        Args:
            file_id: ID du file à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le file existe
            files, _ = self.model_class.get_by_criteria({'id': file_id}, 0, 1)
            if not files:
                return False, f"{self.model_class.__name__} non trouvé"
            
            file = files[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(file)
            else:
                # Soft delete
                if hasattr(file, 'is_deleted'):
                    file.is_deleted = True
                    if user_id and hasattr(file, 'updated_by'):
                        file.updated_by = user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(file)
            
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
        Récupérer des files selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des files, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
