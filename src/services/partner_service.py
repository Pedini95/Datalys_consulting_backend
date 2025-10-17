from models import Partner
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils.file_upload import file_upload_manager
from utils.utilities import generate_temp_password
from utils.audit_utils import set_audit_fields, update_audit_field

logger = logging.getLogger(__name__)


class PartnerService:
    """
    Service pour la gestion des partners
    """
    
    def __init__(self):
        self.model_class = Partner

    def _check_duplicates(self, email=None, phone=None, name=None, address=None, exclude_id=None):
        """
        Logique métier : Vérifier s'il existe des doublons pour les champs uniques
        
        Args:
            email: Email à vérifier
            phone: Téléphone à vérifier  
            name: Nom à vérifier (avec adresse)
            address: Adresse à vérifier (avec nom)
            exclude_id: ID à exclure de la recherche (pour les updates)
            
        Returns:
            Tuple (has_duplicates, error_message)
        """
        # Vérifier email unique
        if email:
            existing_email = self.model_class.find_by_email(email, exclude_id)
            if existing_email:
                return True, f"Un partenaire avec l'email '{email}' existe déjà"
        
        # Vérifier téléphone unique
        if phone:
            existing_phone = self.model_class.find_by_phone(phone, exclude_id)
            if existing_phone:
                return True, f"Un partenaire avec le téléphone '{phone}' existe déjà"
        
        # Vérifier combinaison nom + adresse
        if name and address:
            existing_combo = self.model_class.find_by_name_and_address(name, address, exclude_id)
            if existing_combo:
                return True, f"Un partenaire avec le nom '{name}' à l'adresse '{address}' existe déjà"
        
        return False, ""
    
    def create_with_user(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Partner], Optional[str], Optional[str], bool, str]:
        """
        Créer un nouveau partner avec un utilisateur associé

        Args:
            data: Données du partner à créer
            user_id: ID de l'utilisateur qui crée

        Returns:
            Tuple (partner, username, temp_password, succès, message)
        """
        try:
            # Validation des doublons avant création
            has_duplicates, error_msg = self._check_duplicates(
                email=data.get('email'),
                phone=data.get('phone'),
                name=data.get('name'),
                address=data.get('address')
            )

            if has_duplicates:
                logger.warning(f"Tentative de création d'un partenaire en doublon: {error_msg}")
                return None, None, None, False, error_msg

            # Vérifier qu'un email est fourni (obligatoire pour créer l'utilisateur)
            if not data.get('email'):
                return None, None, None, False, "L'email est obligatoire pour créer un compte utilisateur"

            # Vérifier si l'email existe déjà dans la table users
            from models import User
            existing_user = User.query.filter_by(email=data.get('email')).first()
            if existing_user:
                return None, None, None, False, f"Un utilisateur avec l'email '{data.get('email')}' existe déjà"
            
            # Générer un mot de passe temporaire
            temp_password = generate_temp_password()
            
            # Créer le partenaire
            partner_data = data.copy()
            set_audit_fields(partner_data, user_id)
            
            partner = self.model_class(**partner_data)
            db.session.add(partner)
            db.session.flush()  # Pour obtenir l'ID du partenaire
            
            # Créer l'utilisateur associé
            from models import User, Role
            from utils.utilities import encrypt
            
            # 1. Trouver ou créer le rôle 'partner'
            partner_role = Role.query.filter(Role.name == 'partner').first()
            if not partner_role:
                logger.info("Création du rôle 'partner' car il n'existe pas")
                partner_role = Role()
                partner_role.name = 'partner'
                partner_role.is_active = True
                if user_id:
                    set_audit_fields(partner_role.__dict__, user_id)
                db.session.add(partner_role)
                db.session.flush()
            
            # Générer un nom d'utilisateur basé sur l'email
            username = data.get('email', '').lower()

            # Générer un code client unique pour le partenaire
            client_code = User.generate_client_code()

            # Créer l'utilisateur avec la structure existante
            user_data = {
                'name': data.get('name', ''),  # Utiliser name au lieu de username
                'email': data.get('email', ''),
                'password_hash': encrypt(temp_password),  # Utiliser password_hash
                'is_temp_password': True,  # Marquer le mot de passe comme temporaire
                'client_code': client_code,  # Code client unique pour la connexion
                'role_id': partner_role.id,  # Assigner le rôle 'partner'
                'is_active': True
            }
            
            if user_id:
                set_audit_fields(user_data, user_id)
            
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Partenaire et utilisateur créés avec succès: {partner.name} (ID: {partner.id}) avec rôle 'partner'")
            return partner, username, temp_password, True, f"Partenaire créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création du partenaire avec utilisateur: {str(e)}")
            return None, None, None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création du partenaire avec utilisateur: {str(e)}")
            return None, None, None, False, f"Erreur inattendue: {str(e)}"
    
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
            has_duplicates, error_msg = self._check_duplicates(
                email=data.get('email'),
                phone=data.get('phone'),
                name=data.get('name'),
                address=data.get('address')
            )
            
            if has_duplicates:
                logger.warning(f"Tentative de création d'un partenaire en doublon: {error_msg}")
                return None, False, error_msg
            
            # Ajouter les champs d'audit
            set_audit_fields(data, user_id)
            
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
            has_duplicates, error_msg = self._check_duplicates(
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
            update_audit_field(partner, user_id)
            
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
                        update_audit_field(partner, user_id)
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
