from models import Project
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils.audit_utils import set_audit_fields, update_audit_field

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service pour la gestion des projects
    """
    
    def __init__(self):
        self.model_class = Project
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Project], bool, str]:
        """
        Créer un nouveau project
        
        Args:
            data: Données du project à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (project, succès, message)
        """
        try:
            # Traiter le partner_name si fourni
            if 'partner_name' in data and data['partner_name']:
                from models import Partner
                # Rechercher le partenaire par nom
                partners, _ = Partner.get_by_criteria({'name': data['partner_name']}, 0, 1)
                if partners:
                    data['partner_id'] = partners[0].id
                    logger.info(f"Partenaire trouvé: {data['partner_name']} (ID: {partners[0].id})")
                else:
                    logger.warning(f"Partenaire non trouvé: {data['partner_name']}")
                    return None, False, f"Partenaire non trouvé: {data['partner_name']}"
                
                # Supprimer partner_name des données
                del data['partner_name']
            
            # Définir is_active à True par défaut si non spécifié
            if 'is_active' not in data:
                data['is_active'] = True
                logger.info("is_active défini à True par défaut")
            
            # Ajouter les champs d'audit
            set_audit_fields(data, user_id)
            
            project = self.model_class(**data)
            db.session.add(project)
            db.session.commit()
            
            return project, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, project_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Project], bool, str]:
        """
        Mettre à jour un project
        
        Args:
            project_id: ID du project à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (project, succès, message)
        """
        try:
            # Vérifier si le project existe
            projects, _ = self.model_class.get_by_criteria({'id': project_id}, 0, 1)
            if not projects:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            project = projects[0]
            
            # Traiter le partner_name si fourni
            if 'partner_name' in data and data['partner_name']:
                from models import Partner
                # Rechercher le partenaire par nom
                partners, _ = Partner.get_by_criteria({'name': data['partner_name']}, 0, 1)
                if partners:
                    data['partner_id'] = partners[0].id
                    logger.info(f"Partenaire trouvé pour mise à jour: {data['partner_name']} (ID: {partners[0].id})")
                else:
                    logger.warning(f"Partenaire non trouvé pour mise à jour: {data['partner_name']}")
                    return None, False, f"Partenaire non trouvé: {data['partner_name']}"
                
                # Supprimer partner_name des données
                del data['partner_name']
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            # Mettre à jour les champs d'audit
            update_audit_field(project, user_id)
            
            db.session.commit()
            
            return project, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, project_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un project (soft delete par défaut)
        
        Args:
            project_id: ID du project à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le project existe
            projects, _ = self.model_class.get_by_criteria({'id': project_id}, 0, 1)
            if not projects:
                return False, f"{self.model_class.__name__} non trouvé"
            
            project = projects[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(project)
            else:
                # Soft delete
                if hasattr(project, 'is_deleted'):
                    project.is_deleted = True
                    update_audit_field(project, user_id)
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(project)
            
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
        Récupérer des projects selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des projects, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
