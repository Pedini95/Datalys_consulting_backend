"""
Utilitaires pour les champs d'audit
"""
from typing import Optional
from models import User


def get_user_name_from_id(user_id: int) -> str:
    """
    Récupérer le nom d'un utilisateur à partir de son ID
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Nom de l'utilisateur ou "User_{id}" si non trouvé
    """
    try:
        current_user = User.query.get(user_id)
        return current_user.name if current_user else f"User_{user_id}"
    except:
        return f"User_{user_id}"


def set_audit_fields(data: dict, user_id: Optional[int], created_by_key: str = 'created_by', updated_by_key: str = 'updated_by') -> None:
    """
    Définir les champs d'audit avec l'ID de l'utilisateur (integer)
    
    Args:
        data: Dictionnaire des données
        user_id: ID de l'utilisateur
        created_by_key: Clé pour le champ created_by
        updated_by_key: Clé pour le champ updated_by
    """
    if user_id:
        # ✅ CORRECTION: Utiliser l'ID (integer) au lieu du nom (string)
        data[created_by_key] = str(user_id)  # Convertir en string pour compatibilité
        data[updated_by_key] = str(user_id)


def update_audit_field(obj, user_id: Optional[int], field_name: str = 'updated_by') -> None:
    """
    Mettre à jour un champ d'audit avec l'ID de l'utilisateur (integer)
    
    Args:
        obj: Objet à mettre à jour
        user_id: ID de l'utilisateur
        field_name: Nom du champ à mettre à jour
    """
    if user_id and hasattr(obj, field_name):
        # ✅ CORRECTION: Utiliser l'ID (integer) au lieu du nom (string)
        setattr(obj, field_name, str(user_id))
