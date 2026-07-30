import os
import sys

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Imports avec noms de fichiers en minuscules
from .role import Role
from .permission import Permission
from .role_permission import RolePermission
from .user import User
from .partner import Partner
from .project import Project
from .incident import Incident
from .folder import Folder
from .file import File
from .user_project_permission import UserProjectPermission
from .action_history import ActionHistory
from .incident_history import IncidentHistory
from .incident_note import IncidentNote
from .incident_attachment import IncidentAttachment

__all__ = [
    'Role',
    'Permission',
    'RolePermission',
    'User',
    'Partner',
    'Project',
    'Incident',
    'Folder',
    'File',
    'UserProjectPermission',
    'ActionHistory',
    'IncidentHistory',
    'IncidentNote',
    'IncidentAttachment'
]