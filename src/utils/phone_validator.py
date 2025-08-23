"""
Utilitaire pour la validation et le formatage des numéros de téléphone par pays
"""

import re
from typing import Tuple, Optional, Dict, Any


class PhoneValidator:
    """Classe pour valider et formater les numéros de téléphone internationaux"""
    
    # Codes pays supportés avec leurs formats et exemples
    COUNTRY_CODES = {
        '+237': {
            'name': 'Cameroun',
            'format': r'^\+237[0-9]{9}$',
            'example': '+237612345678',
            'description': '9 chiffres après +237'
        },
        '+33': {
            'name': 'France',
            'format': r'^\+33[0-9]{9}$',
            'example': '+33123456789',
            'description': '9 chiffres après +33'
        },
        '+1': {
            'name': 'États-Unis/Canada',
            'format': r'^\+1[0-9]{10}$',
            'example': '+12345678901',
            'description': '10 chiffres après +1'
        },
        '+32': {
            'name': 'Belgique',
            'format': r'^\+32[0-9]{9}$',
            'example': '+32123456789',
            'description': '9 chiffres après +32'
        },
        '+41': {
            'name': 'Suisse',
            'format': r'^\+41[0-9]{9}$',
            'example': '+41123456789',
            'description': '9 chiffres après +41'
        },
        '+225': {
            'name': 'Côte d\'Ivoire',
            'format': r'^\+225[0-9]{10}$',
            'example': '+2250123456789',
            'description': '10 chiffres après +225'
        },
        '+226': {
            'name': 'Burkina Faso',
            'format': r'^\+226[0-9]{8}$',
            'example': '+22612345678',
            'description': '8 chiffres après +226'
        },
        '+223': {
            'name': 'Mali',
            'format': r'^\+223[0-9]{8}$',
            'example': '+22312345678',
            'description': '8 chiffres après +223'
        },
        '+224': {
            'name': 'Guinée',
            'format': r'^\+224[0-9]{9}$',
            'example': '+224123456789',
            'description': '9 chiffres après +224'
        },
        '+242': {
            'name': 'Congo',
            'format': r'^\+242[0-9]{9}$',
            'example': '+242123456789',
            'description': '9 chiffres après +242'
        },
        '+221': {
            'name': 'Sénégal',
            'format': r'^\+221[0-9]{9}$',
            'example': '+221123456789',
            'description': '9 chiffres après +221'
        },
        '+234': {
            'name': 'Nigeria',
            'format': r'^\+234[0-9]{10}$',
            'example': '+2341234567890',
            'description': '10 chiffres après +234'
        },
        '+254': {
            'name': 'Kenya',
            'format': r'^\+254[0-9]{9}$',
            'example': '+254123456789',
            'description': '9 chiffres après +254'
        },
        '+27': {
            'name': 'Afrique du Sud',
            'format': r'^\+27[0-9]{9}$',
            'example': '+27123456789',
            'description': '9 chiffres après +27'
        },
        '+212': {
            'name': 'Maroc',
            'format': r'^\+212[0-9]{9}$',
            'example': '+212123456789',
            'description': '9 chiffres après +212'
        },
        '+216': {
            'name': 'Tunisie',
            'format': r'^\+216[0-9]{8}$',
            'example': '+21612345678',
            'description': '8 chiffres après +216'
        },
        '+213': {
            'name': 'Algérie',
            'format': r'^\+213[0-9]{9}$',
            'example': '+213123456789',
            'description': '9 chiffres après +213'
        },
        '+20': {
            'name': 'Égypte',
            'format': r'^\+20[0-9]{10}$',
            'example': '+201234567890',
            'description': '10 chiffres après +20'
        }
    }
    
    @classmethod
    def get_supported_countries(cls) -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des pays supportés"""
        return cls.COUNTRY_CODES
    
    @classmethod
    def normalize_phone(cls, phone: str, country_code: str = '+237') -> Tuple[str, str]:
        """
        Normalise un numéro de téléphone
        
        Args:
            phone: Le numéro de téléphone à normaliser
            country_code: Le code pays par défaut
            
        Returns:
            Tuple (numéro_normalisé, code_pays)
        """
        if not phone:
            return '', country_code
        
        # Supprimer tous les caractères non numériques sauf +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Si le numéro commence déjà par un code pays supporté
        for code in cls.COUNTRY_CODES.keys():
            if cleaned.startswith(code):
                return cleaned[len(code):], code
        
        # Sinon, utiliser le code pays par défaut
        return cleaned, country_code
    
    @classmethod
    def validate_phone(cls, phone: str, country_code: str) -> Tuple[bool, str]:
        """
        Valide un numéro de téléphone selon le pays
        
        Args:
            phone: Le numéro de téléphone
            country_code: Le code pays
            
        Returns:
            Tuple (est_valide, message_erreur)
        """
        if not phone:
            return True, "Numéro optionnel"
        
        if country_code not in cls.COUNTRY_CODES:
            return False, f"Code pays non supporté: {country_code}"
        
        # Normaliser le numéro
        normalized_phone, detected_country = cls.normalize_phone(phone, country_code)
        
        # Vérifier que le code pays détecté correspond à celui attendu
        if detected_country != country_code:
            return False, f"Le numéro correspond au code pays {detected_country}, pas {country_code}"
        
        # Formater le numéro complet
        formatted_phone = f"{country_code}{normalized_phone}"
        
        # Valider le format
        country_info = cls.COUNTRY_CODES[country_code]
        if not re.match(country_info['format'], formatted_phone):
            return False, f"Format invalide pour {country_info['name']}. {country_info['description']}. Exemple: {country_info['example']}"
        
        return True, "Numéro valide"
    
    @classmethod
    def format_phone(cls, phone: str, country_code: str = '+237') -> str:
        """
        Formate un numéro de téléphone avec le code pays
        
        Args:
            phone: Le numéro de téléphone
            country_code: Le code pays
            
        Returns:
            Le numéro formaté
        """
        if not phone:
            return ""
        
        # Si le numéro commence déjà par +, le retourner tel quel
        if phone.startswith('+'):
            return phone
        
        # Normaliser et formater
        normalized_phone, detected_country = cls.normalize_phone(phone, country_code)
        return f"{detected_country}{normalized_phone}"
    
    @classmethod
    def detect_country_from_phone(cls, phone: str) -> Optional[str]:
        """
        Détecte le code pays à partir d'un numéro de téléphone
        
        Args:
            phone: Le numéro de téléphone
            
        Returns:
            Le code pays détecté ou None
        """
        if not phone:
            return None
        
        # Supprimer les caractères non numériques sauf +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Chercher un code pays au début
        for code in cls.COUNTRY_CODES.keys():
            if cleaned.startswith(code):
                return code
        
        return None
    
    @classmethod
    def get_country_info(cls, country_code: str) -> Optional[Dict[str, Any]]:
        """
        Retourne les informations d'un pays
        
        Args:
            country_code: Le code pays
            
        Returns:
            Les informations du pays ou None
        """
        return cls.COUNTRY_CODES.get(country_code)


# Fonctions utilitaires pour faciliter l'utilisation
def validate_phone_number(phone: str, country_code: str = '+237') -> Tuple[bool, str]:
    """Fonction utilitaire pour valider un numéro de téléphone"""
    return PhoneValidator.validate_phone(phone, country_code)


def format_phone_number(phone: str, country_code: str = '+237') -> str:
    """Fonction utilitaire pour formater un numéro de téléphone"""
    return PhoneValidator.format_phone(phone, country_code)


def get_supported_countries() -> Dict[str, Dict[str, Any]]:
    """Fonction utilitaire pour obtenir la liste des pays supportés"""
    return PhoneValidator.get_supported_countries()
