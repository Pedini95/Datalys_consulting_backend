from flask import Blueprint, request
from services import PermissionService, RolePermissionService
import logging
from utils import functional_error
from .auth import require_auth
from middleware.role_security import require_permission

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('permissions', __name__)

permission_service = PermissionService()
role_permission_service = RolePermissionService()


@bp.route('/permissions/getByCriteria', methods=['POST'])
@require_auth
def get_permissions():
    """
    Liste le catalogue des permissions disponibles (référentiel en lecture,
    utilisé pour afficher les cases à cocher dans l'interface d'administration des rôles).
    """
    logging.info("**** Begin get_permissions ****")
    logging.info("/permissions/getByCriteria")
    r = request.get_json() or {}
    index = r.get('index', 0)
    size = r.get('size', 100)
    criteria = r.get('data', {})

    permissions, total_items = permission_service.getByCriteria(criteria, index, size)
    if permissions:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()

    response = {"items": [permission.as_dict() for permission in permissions], "count": total_items, "message": message, "code": 200}
    logging.info("**** End get_permissions ****")
    return response


@bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
@require_auth
@require_permission('roles.manage')
def get_role_permissions(role_id):
    """
    Liste les clés de permission accordées à un rôle donné.
    """
    logging.info(f"**** Begin get_role_permissions (role_id={role_id}) ****")
    permission_keys = role_permission_service.get_permission_keys_for_role(role_id)
    response = {"role_id": role_id, "permission_keys": permission_keys, "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    logging.info("**** End get_role_permissions ****")
    return response


@bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
@require_auth
@require_permission('roles.manage')
def set_role_permissions(role_id):
    """
    Remplace l'ensemble des permissions accordées à un rôle.

    Body:
    {
        "user": {"id": 1},
        "permission_keys": ["users.view", "users.create", ...]
    }
    """
    logging.info(f"**** Begin set_role_permissions (role_id={role_id}) ****")
    r = request.get_json() or {}
    user = r.get('user', {})
    permission_keys = r.get('permission_keys')

    if permission_keys is None or not isinstance(permission_keys, list):
        return {"status": "error", "message": "Le champ permission_keys (liste) est obligatoire"}, 400

    success, message = role_permission_service.set_permissions_for_role(role_id, permission_keys, user.get('id'))
    if not success:
        return {"status": "error", "message": message}, 400

    updated_keys = role_permission_service.get_permission_keys_for_role(role_id)
    response = {"role_id": role_id, "permission_keys": updated_keys, "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    logging.info("**** End set_role_permissions ****")
    return response
