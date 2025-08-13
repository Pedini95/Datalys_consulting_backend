from models import ActionHistory
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from app import db
import logging

logger = logging.getLogger(__name__)


class ActionHistoryService:
    """
    Service pour la gestion des actionhistorys
    """
    
    def __init__(self):
        self.model_class = ActionHistory
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[ActionHistory], bool, str]:
        """
        Créer un nouveau actionhistory
        
        Args:
            data: Données du actionhistory à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (actionhistory, succès, message)
        """
        try:
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            actionhistory = self.model_class(**data)
            db.session.add(actionhistory)
            db.session.commit()
            
            return actionhistory, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, actionhistory_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[ActionHistory], bool, str]:
        """
        Mettre à jour un actionhistory
        
        Args:
            actionhistory_id: ID du actionhistory à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (actionhistory, succès, message)
        """
        try:
            # Vérifier si le actionhistory existe
            actionhistorys, _ = self.model_class.get_by_criteria({'id': actionhistory_id}, 0, 1)
            if not actionhistorys:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            actionhistory = actionhistorys[0]
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(actionhistory, key):
                    setattr(actionhistory, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(actionhistory, 'updated_by'):
                actionhistory.updated_by = user_id
            
            db.session.commit()
            
            return actionhistory, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, actionhistory_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un actionhistory (soft delete par défaut)
        
        Args:
            actionhistory_id: ID du actionhistory à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le actionhistory existe
            actionhistorys, _ = self.model_class.get_by_criteria({'id': actionhistory_id}, 0, 1)
            if not actionhistorys:
                return False, f"{self.model_class.__name__} non trouvé"
            
            actionhistory = actionhistorys[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(actionhistory)
            else:
                # Soft delete
                if hasattr(actionhistory, 'is_deleted'):
                    actionhistory.is_deleted = True
                    if user_id and hasattr(actionhistory, 'updated_by'):
                        actionhistory.updated_by = user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(actionhistory)
            
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
        Récupérer des actionhistorys selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des actionhistorys, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
