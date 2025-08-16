from models import User, Role
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils import utilities

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
            
            # Gérer le champ name -> username, first_name, last_name
            if 'name' in data:
                name = data.pop('name')
                # Si le nom contient un espace, séparer en first_name et last_name
                name_parts = name.strip().split(' ', 1)
                if len(name_parts) > 1:
                    data['first_name'] = name_parts[0]
                    data['last_name'] = name_parts[1]
                    data['username'] = name_parts[0].lower()  # Utiliser first_name comme username
                else:
                    data['username'] = name.lower()
                    data['first_name'] = name
            
            # Hasher le mot de passe
            if 'password' in data:
                password = data.pop('password')
                data['password_hash'] = utilities.encrypt(password)
            
            # Ajouter les champs d'audit
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            user = self.model_class(**data)
            db.session.add(user)
            db.session.commit()
            
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
            
            # Gérer le champ name -> username, first_name, last_name
            if 'name' in data:
                name = data.pop('name')
                # Si le nom contient un espace, séparer en first_name et last_name
                name_parts = name.strip().split(' ', 1)
                if len(name_parts) > 1:
                    data['first_name'] = name_parts[0]
                    data['last_name'] = name_parts[1]
                    data['username'] = name_parts[0].lower()  # Utiliser first_name comme username
                else:
                    data['username'] = name.lower()
                    data['first_name'] = name
            
            # Hasher le mot de passe si fourni
            if 'password' in data:
                password = data.pop('password')
                data['password_hash'] = utilities.encrypt(password)
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            # Mettre à jour les champs d'audit
            if current_user_id and hasattr(user, 'updated_by'):
                user.updated_by = current_user_id
            
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
                        user.updated_by = current_user_id
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
