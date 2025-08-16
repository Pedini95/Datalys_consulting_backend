from models import Role
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging

logger = logging.getLogger(__name__)


class RoleService:
    """
    Service pour la gestion des roles
    """
    
    def __init__(self):
        self.model_class = Role
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Role], bool, str]:
        """
        Créer un nouveau role
        
        Args:
            data: Données du role à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (role, succès, message)
        """
        try:
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            role = self.model_class(**data)
            db.session.add(role)
            db.session.commit()
            
            return role, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, role_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Role], bool, str]:
        """
        Mettre à jour un role
        
        Args:
            role_id: ID du role à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (role, succès, message)
        """
        try:
            # Vérifier si le role existe
            roles, _ = self.model_class.get_by_criteria({'id': role_id}, 0, 1)
            if not roles:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            role = roles[0]
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(role, key):
                    setattr(role, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(role, 'updated_by'):
                role.updated_by = user_id
            
            db.session.commit()
            
            return role, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, role_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un role (soft delete par défaut)
        
        Args:
            role_id: ID du role à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le role existe
            roles, _ = self.model_class.get_by_criteria({'id': role_id}, 0, 1)
            if not roles:
                return False, f"{self.model_class.__name__} non trouvé"
            
            role = roles[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(role)
            else:
                # Soft delete
                if hasattr(role, 'is_deleted'):
                    role.is_deleted = True
                    if user_id and hasattr(role, 'updated_by'):
                        role.updated_by = user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(role)
            
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
        Récupérer des roles selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des roles, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
