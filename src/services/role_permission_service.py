from models import Permission, RolePermission
from typing import List, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging

logger = logging.getLogger(__name__)


class RolePermissionService:
    """
    Service pour gérer l'association entre rôles et permissions
    """

    def get_permission_keys_for_role(self, role_id: int) -> List[str]:
        """
        Liste les clés de permission accordées à un rôle
        """
        rows = db.session.query(Permission.key).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).filter(
            RolePermission.role_id == role_id,
            Permission.is_deleted == False,
        ).all()
        return [row[0] for row in rows]

    def set_permissions_for_role(self, role_id: int, permission_keys: List[str], user_id: int = None) -> Tuple[bool, str]:
        """
        Remplace l'ensemble des permissions accordées à un rôle par `permission_keys`
        (ajoute celles qui manquent, retire celles qui ne sont plus demandées).
        """
        try:
            permissions = Permission.query.filter(
                Permission.key.in_(permission_keys),
                Permission.is_deleted == False,
            ).all()
            found_keys = {p.key for p in permissions}

            unknown_keys = set(permission_keys) - found_keys
            if unknown_keys:
                return False, f"Permissions inconnues: {', '.join(sorted(unknown_keys))}"

            current = RolePermission.query.filter(RolePermission.role_id == role_id).all()
            current_by_permission_id = {rp.permission_id: rp for rp in current}
            wanted_permission_ids = {p.id for p in permissions}

            # Retirer les permissions qui ne sont plus demandées
            for permission_id, rp in current_by_permission_id.items():
                if permission_id not in wanted_permission_ids:
                    db.session.delete(rp)

            # Ajouter les permissions manquantes
            for permission in permissions:
                if permission.id not in current_by_permission_id:
                    db.session.add(RolePermission(
                        role_id=role_id,
                        permission_id=permission.id,
                        created_by=user_id,
                    ))

            db.session.commit()
            return True, "Permissions mises à jour avec succès"

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour des permissions du rôle {role_id}: {str(e)}")
            return False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour des permissions du rôle {role_id}: {str(e)}")
            return False, f"Erreur inattendue: {str(e)}"
