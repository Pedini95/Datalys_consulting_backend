from models import Partner
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils.file_upload import file_upload_manager

logger = logging.getLogger(__name__)


class PartnerService:
    """
    Service pour la gestion des partners
    """
    
    def __init__(self):
        self.model_class = Partner
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Partner], bool, str]:
        """
        Créer un nouveau partner
        
        Args:
            data: Données du partner à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (partner, succès, message)
        """
        try:
            # Validation des doublons avant création
            has_duplicates, error_msg = self.model_class.check_duplicates(
                email=data.get('email'),
                phone=data.get('phone'),
                name=data.get('name'),
                address=data.get('address')
            )
            
            if has_duplicates:
                logger.warning(f"Tentative de création d'un partenaire en doublon: {error_msg}")
                return None, False, error_msg
            
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            partner = self.model_class(**data)
            db.session.add(partner)
            db.session.commit()
            
            return partner, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, partner_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Partner], bool, str]:
        """
        Mettre à jour un partner
        
        Args:
            partner_id: ID du partner à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (partner, succès, message)
        """
        try:
            # Vérifier si le partner existe
            partners, _ = self.model_class.get_by_criteria({'id': partner_id}, 0, 1)
            if not partners:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            partner = partners[0]
            
            # Validation des doublons avant mise à jour (exclure le partenaire actuel)
            has_duplicates, error_msg = self.model_class.check_duplicates(
                email=data.get('email'),
                phone=data.get('phone'), 
                name=data.get('name'),
                address=data.get('address'),
                exclude_id=partner_id
            )
            
            if has_duplicates:
                logger.warning(f"Tentative de mise à jour d'un partenaire avec des doublons: {error_msg}")
                return None, False, error_msg
            
            # Gérer la suppression de l'ancien logo si un nouveau est fourni
            if 'logo_url' in data and data['logo_url'] and partner.logo_url:
                # Supprimer l'ancien logo
                file_upload_manager.delete_file(partner.logo_url)
                logger.info(f"Ancien logo supprimé pour le partner {partner_id}: {partner.logo_url}")
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(partner, key):
                    setattr(partner, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(partner, 'updated_by'):
                partner.updated_by = user_id
            
            db.session.commit()
            
            return partner, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, partner_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un partner (soft delete par défaut)
        
        Args:
            partner_id: ID du partner à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le partner existe
            partners, _ = self.model_class.get_by_criteria({'id': partner_id}, 0, 1)
            if not partners:
                return False, f"{self.model_class.__name__} non trouvé"
            
            partner = partners[0]
            
            # Supprimer le logo si il existe
            if partner.logo_url:
                file_upload_manager.delete_file(partner.logo_url)
                logger.info(f"Logo supprimé pour le partner {partner_id}: {partner.logo_url}")
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(partner)
            else:
                # Soft delete
                if hasattr(partner, 'is_deleted'):
                    partner.is_deleted = True
                    if user_id and hasattr(partner, 'updated_by'):
                        partner.updated_by = user_id
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(partner)
            
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
        Récupérer des partners selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des partners, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
