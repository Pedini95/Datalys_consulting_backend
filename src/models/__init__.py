import os
import sys

# Ajouter le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Imports robustes avec gestion d'erreur
try:
    from .Role import Role
except ImportError:
    # Fallback pour import absolu
    from models.Role import Role

try:
    from .User import User
except ImportError:
    from models.User import User

try:
    from .Partner import Partner
except ImportError:
    from models.Partner import Partner

try:
    from .Project import Project
except ImportError:
    from models.Project import Project

try:
    from .Incident import Incident
except ImportError:
    from models.Incident import Incident

try:
    from .Folder import Folder
except ImportError:
    from models.Folder import Folder

try:
    from .File import File
except ImportError:
    from models.File import File

try:
    from .UserProjectPermission import UserProjectPermission
except ImportError:
    from models.UserProjectPermission import UserProjectPermission

try:
    from .ActionHistory import ActionHistory
except ImportError:
    from models.ActionHistory import ActionHistory

__all__ = [
    'Role',
    'User',
    'Partner',
    'Project',
    'Incident',
    'Folder',
    'File',
    'UserProjectPermission',
    'ActionHistory'
] 