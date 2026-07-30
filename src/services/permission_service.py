from models import Permission
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from utils.audit_utils import set_audit_fields, update_audit_field

logger = logging.getLogger(__name__)


class PermissionService:
    """
    Service pour la gestion du catalogue de permissions
    """

    def __init__(self):
        self.model_class = Permission

    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Permission], bool, str]:
        try:
            set_audit_fields(data, user_id)

            permission = self.model_class(**data)
            db.session.add(permission)
            db.session.commit()

            return permission, True, f"{self.model_class.__name__} créé avec succès"

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"

    def update(self, permission_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Permission], bool, str]:
        try:
            permissions, _ = self.model_class.get_by_criteria({'id': permission_id}, 0, 1)
            if not permissions:
                return None, False, f"{self.model_class.__name__} non trouvé"

            permission = permissions[0]

            for key, value in data.items():
                if hasattr(permission, key):
                    setattr(permission, key, value)

            update_audit_field(permission, user_id)

            db.session.commit()

            return permission, True, f"{self.model_class.__name__} mis à jour avec succès"

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"

    def delete(self, permission_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        try:
            permissions, _ = self.model_class.get_by_criteria({'id': permission_id}, 0, 1)
            if not permissions:
                return False, f"{self.model_class.__name__} non trouvé"

            permission = permissions[0]

            if hard_delete:
                db.session.delete(permission)
            else:
                permission.is_deleted = True
                update_audit_field(permission, user_id)

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
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
