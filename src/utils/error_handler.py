"""
Utilitaires pour gérer les erreurs de manière sécurisée et user-friendly
"""
import logging

logger = logging.getLogger(__name__)


def handle_sqlalchemy_error(e, operation: str = "opération", data: dict = None) -> str:
    """
    Transforme une erreur SQLAlchemy en message user-friendly

    Args:
        e: L'exception SQLAlchemy
        operation: Type d'opération ("création", "mise à jour", "suppression")
        data: Données de la requête (pour extraire des infos si nécessaire)

    Returns:
        Message d'erreur user-friendly
    """
    error_str = str(e)

    # Erreurs de duplication (Duplicate entry)
    if 'Duplicate entry' in error_str:
        # Extraire le champ concerné
        if 'users.email' in error_str or 'email' in error_str:
            email = data.get('email', '') if data else ''
            if email:
                return f"Un utilisateur avec l'email '{email}' existe déjà"
            return "Cet email est déjà utilisé"

        elif 'phone' in error_str:
            return "Ce numéro de téléphone est déjà utilisé"

        elif 'client_code' in error_str:
            return "Ce code client existe déjà"

        elif 'incident_number' in error_str:
            return "Ce numéro d'incident existe déjà"

        else:
            return "Cette entrée existe déjà dans la base de données"

    # Erreurs de clé étrangère (Foreign key constraint)
    elif 'foreign key constraint' in error_str.lower() or 'cannot delete' in error_str.lower():
        if 'delete' in operation.lower() or 'suppression' in operation.lower():
            return "Impossible de supprimer cet élément car il est utilisé par d'autres données"
        return "Cette opération viole une contrainte de base de données"

    # Erreurs de valeur NULL non autorisée
    elif 'cannot be null' in error_str.lower() or 'not null' in error_str.lower():
        return "Certains champs obligatoires sont manquants"

    # Erreurs de type de données
    elif 'data too long' in error_str.lower() or 'too long' in error_str.lower():
        return "Une des valeurs est trop longue"

    elif 'incorrect' in error_str.lower() and 'value' in error_str.lower():
        return "Une des valeurs fournies est incorrecte"

    # Erreur générique (ne pas exposer les détails)
    else:
        logger.error(f"Erreur SQL non gérée lors de {operation}: {error_str}")
        return f"Une erreur est survenue lors de {operation}. Veuillez réessayer."


def handle_general_error(e, operation: str = "opération") -> str:
    """
    Transforme une erreur générale en message user-friendly

    Args:
        e: L'exception
        operation: Type d'opération

    Returns:
        Message d'erreur user-friendly
    """
    logger.error(f"Erreur inattendue lors de {operation}: {str(e)}")
    return f"Une erreur inattendue s'est produite lors de {operation}. Veuillez réessayer."
