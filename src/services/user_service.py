from models import User, Role
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils import utilities
from utils.audit_utils import set_audit_fields, update_audit_field

logger = logging.getLogger(__name__)


class UserService:
    """
    Service pour la gestion des users
    """
    
    def __init__(self):
        self.model_class = User
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[User], bool, str]:
        """
        Créer un nouveau user
        
        Args:
            data: Données du user à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (user, succès, message)
        """
        try:
            # Vérifier s'il existe un utilisateur avec le même email (actif ou supprimé)
            if 'email' in data:
                existing_user = User.query.filter(
                    User.email == data['email']
                ).first()
                
                if existing_user:
                    if existing_user.is_deleted == True:
                        # L'utilisateur existe mais est supprimé (soft delete)
                        return None, False, f"Un utilisateur avec l'email '{data['email']}' existe déjà mais a été supprimé. Utilisez la fonction de réactivation pour le restaurer."
                    else:
                        # L'utilisateur existe et est actif
                        return None, False, f"Un utilisateur avec l'email '{data['email']}' existe déjà"
            
            # Créer un nouvel utilisateur
            # Gérer role_name -> role_id
            if 'role_name' in data:
                role_name = data.pop('role_name')
                roles, _ = Role.get_by_criteria({'name': role_name}, 0, 1)
                if not roles:
                    return None, False, f"Rôle '{role_name}' non trouvé"
                data['role_id'] = roles[0].id
            
            # Le champ name reste tel quel - pas de séparation en first_name/last_name
            # car ces colonnes n'existent pas dans la table
            
            # Hasher le mot de passe
            if 'password' in data:
                password = data.pop('password')
                data['password_hash'] = utilities.encrypt(password)
                # Définir automatiquement is_temp_password à True lors de la création
                # L'utilisateur devra changer son mot de passe à la première connexion
                data['is_temp_password'] = True
                logger.info("🔐 Mot de passe temporaire défini automatiquement")
            
            # Générer automatiquement un code client unique UNIQUEMENT pour les partenaires (rôle "User")
            # Les Admin et Manager n'ont pas besoin de code client car ce sont des employés Datalys
            if 'client_code' not in data or not data['client_code']:
                # Vérifier si c'est un partenaire (rôle "User")
                if 'role_id' in data:
                    role = Role.query.get(data['role_id'])
                    if role and role.name == 'User':
                        data['client_code'] = self.model_class.generate_client_code()
                        logger.info(f"✅ Code client généré pour le partenaire: {data['client_code']}")
                    else:
                        logger.info(f"ℹ️  Pas de code client pour le rôle '{role.name if role else 'inconnu'}' (réservé aux partenaires)")
                        data['client_code'] = None
            
            # MFA activé par défaut pour tous les utilisateurs (sécurité)
            if 'mfa_enabled' not in data:
                data['mfa_enabled'] = True
                logger.info("🔐 MFA activé par défaut")
            
            # Ajouter les champs d'audit
            set_audit_fields(data, user_id)
            
            user = self.model_class(**data)
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID avant commit
            db.session.commit()
            
            if user.client_code:
                logger.info(f"Utilisateur créé avec succès - Email: {user.email}, Code client: {user.client_code}")
            else:
                logger.info(f"Utilisateur créé avec succès - Email: {user.email} (pas de code client)")
            return user, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def update(self, user_id: int, data: Dict[str, Any], current_user_id: Optional[int] = None) -> Tuple[Optional[User], bool, str]:
        """
        Mettre à jour un user
        
        Args:
            user_id: ID du user à mettre à jour
            data: Nouvelles données
            current_user_id: ID de l'utilisateur qui met à jour
            
        Returns:
            Tuple (user, succès, message)
        """
        try:
            # Vérifier si le user existe
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return None, False, f"{self.model_class.__name__} non trouvé"
            
            user = users[0]
            
            # Gérer role_name -> role_id
            if 'role_name' in data:
                role_name = data.pop('role_name')
                roles, _ = Role.get_by_criteria({'name': role_name}, 0, 1)
                if not roles:
                    return None, False, f"Rôle '{role_name}' non trouvé"
                data['role_id'] = roles[0].id
            
            # Le champ name reste tel quel - pas de séparation en first_name/last_name
            # car ces colonnes n'existent pas dans la table
            
            # Hasher le mot de passe si fourni
            if 'password' in data:
                password = data.pop('password')
                data['password_hash'] = utilities.encrypt(password)
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            # Mettre à jour les champs d'audit
            update_audit_field(user, current_user_id)
            
            db.session.commit()
            
            return user, True, f"{self.model_class.__name__} mis à jour avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, user_id: int, current_user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un user (soft delete par défaut)
        
        Args:
            user_id: ID du user à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le user existe
            users, _ = self.model_class.get_by_criteria({'id': user_id}, 0, 1)
            if not users:
                return False, f"{self.model_class.__name__} non trouvé"
            
            user = users[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(user)
            else:
                # Soft delete
                if hasattr(user, 'is_deleted'):
                    user.is_deleted = True
                    if current_user_id and hasattr(user, 'updated_by'):
                        update_audit_field(user, current_user_id)
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(user)
            
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
        Récupérer des users selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des users, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0

    def reactivate_user(self, email: str, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[User], bool, str]:
        """
        Réactiver un utilisateur supprimé (soft delete)
        
        Args:
            email: Email de l'utilisateur à réactiver
            data: Nouvelles données pour l'utilisateur
            user_id: ID de l'utilisateur qui réactive
            
        Returns:
            Tuple (user, succès, message)
        """
        try:
            # Rechercher l'utilisateur supprimé
            existing_user = User.query.filter(
                User.email == email,
                User.is_deleted == True
            ).first()
            
            if not existing_user:
                return None, False, f"Aucun utilisateur supprimé trouvé avec l'email '{email}'"
            
            # Gérer role_name -> role_id
            if 'role_name' in data:
                role_name = data.pop('role_name')
                roles, _ = Role.get_by_criteria({'name': role_name}, 0, 1)
                if not roles:
                    return None, False, f"Rôle '{role_name}' non trouvé"
                data['role_id'] = roles[0].id
            
            # Hasher le mot de passe si fourni
            if 'password' in data:
                password = data.pop('password')
                data['password_hash'] = utilities.encrypt(password)
            
            # Mettre à jour l'utilisateur existant
            for key, value in data.items():
                if hasattr(existing_user, key):
                    setattr(existing_user, key, value)
            
            # Réactiver l'utilisateur
            existing_user.is_deleted = False
            existing_user.is_active = data.get('is_active', True)
            
            # Mettre à jour les champs d'audit
            if user_id:
                existing_user.updated_by = user_id
            
            db.session.commit()
            
            logger.info(f"Utilisateur réactivé avec succès: {email}")
            return existing_user, True, f"Utilisateur réactivé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la réactivation de l'utilisateur: {str(e)}")
            return None, False, f"Erreur lors de la réactivation: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la réactivation: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
