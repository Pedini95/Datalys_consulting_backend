from models import UserProjectPermission
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging

logger = logging.getLogger(__name__)


class UserProjectPermissionService:
    """
    Service pour la gestion des userprojectpermissions
    """
    
    def __init__(self):
        self.model_class = UserProjectPermission
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[UserProjectPermission], bool, str]:
        """
        Créer un nouveau userprojectpermission
        
        Args:
            data: Données du userprojectpermission à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (userprojectpermission, succès, message)
        """
        try:
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            userprojectpermission = self.model_class(**data)
            db.session.add(userprojectpermission)
            db.session.commit()
            
            return userprojectpermission, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, userprojectpermission_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[UserProjectPermission], bool, str]:
        """
        Mettre à jour un userprojectpermission
        
        Args:
            userprojectpermission_id: ID du userprojectpermission à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (userprojectpermission, succès, message)
        """
        try:
            # Vérifier si le userprojectpermission existe
            userprojectpermissions, _ = self.model_class.get_by_criteria({'id': userprojectpermission_id}, 0, 1)
            if not userprojectpermissions:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            userprojectpermission = userprojectpermissions[0]
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(userprojectpermission, key):
                    setattr(userprojectpermission, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(userprojectpermission, 'updated_by'):
                userprojectpermission.updated_by = user_id
            
            db.session.commit()
            
            return userprojectpermission, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, userprojectpermission_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un userprojectpermission (soft delete par défaut)
        
        Args:
            userprojectpermission_id: ID du userprojectpermission à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le userprojectpermission existe
            userprojectpermissions, _ = self.model_class.get_by_criteria({'id': userprojectpermission_id}, 0, 1)
            if not userprojectpermissions:
                return False, f"{self.model_class.__name__} non trouvé"
            
            userprojectpermission = userprojectpermissions[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(userprojectpermission)
            else:
                # Soft delete
                if hasattr(userprojectpermission, 'is_deleted'):
                    userprojectpermission.is_deleted = True
                    if user_id and hasattr(userprojectpermission, 'updated_by'):
                        userprojectpermission.updated_by = user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(userprojectpermission)
            
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
        Récupérer des userprojectpermissions selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des userprojectpermissions, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
