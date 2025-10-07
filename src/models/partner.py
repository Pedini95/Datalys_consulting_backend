from extensions import db
from sqlalchemy import and_, Index
from datetime import datetime
import re


class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True, index=True)
    phone = db.Column(db.String(50), nullable=True, index=True)
    country_code = db.Column(db.String(10), nullable=True, default='+237')  # Code pays par défaut (Cameroun)
    address = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    projects = db.relationship('Project', lazy=True)

    __table_args__ = (
        Index('idx_partner_name_address', 'name', db.text('address(255)')),
        Index('idx_partner_phone_country', 'phone', 'country_code'),
    )

    # Codes pays supportés avec leurs formats
    COUNTRY_CODES = {
        '+237': {'name': 'Cameroun', 'format': r'^\+237[0-9]{9}$', 'example': '+237612345678'},
        '+33': {'name': 'France', 'format': r'^\+33[0-9]{9}$', 'example': '+33123456789'},
        '+1': {'name': 'États-Unis/Canada', 'format': r'^\+1[0-9]{10}$', 'example': '+12345678901'},
        '+32': {'name': 'Belgique', 'format': r'^\+32[0-9]{9}$', 'example': '+32123456789'},
        '+41': {'name': 'Suisse', 'format': r'^\+41[0-9]{9}$', 'example': '+41123456789'},
        '+225': {'name': 'Côte d\'Ivoire', 'format': r'^\+225[0-9]{10}$', 'example': '+2250123456789'},
        '+226': {'name': 'Burkina Faso', 'format': r'^\+226[0-9]{8}$', 'example': '+22612345678'},
        '+223': {'name': 'Mali', 'format': r'^\+223[0-9]{8}$', 'example': '+22312345678'},
        '+224': {'name': 'Guinée', 'format': r'^\+224[0-9]{9}$', 'example': '+224123456789'},
        '+242': {'name': 'Congo', 'format': r'^\+242[0-9]{9}$', 'example': '+242123456789'},
        '+221': {'name': 'Sénégal', 'format': r'^\+221[0-9]{9}$', 'example': '+221123456789'},
        '+234': {'name': 'Nigeria', 'format': r'^\+234[0-9]{10}$', 'example': '+2341234567890'},
        '+254': {'name': 'Kenya', 'format': r'^\+254[0-9]{9}$', 'example': '+254123456789'},
        '+27': {'name': 'Afrique du Sud', 'format': r'^\+27[0-9]{9}$', 'example': '+27123456789'},
    }

    def as_dict(self):
        data = {}
        columns = ['id', 'name', 'email', 'phone', 'country_code', 'address', 'logo_url', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value
        
        # Ajouter le numéro formaté complet et les informations du pays
        if self.phone and self.country_code:
            data['phone_formatted'] = self.get_formatted_phone()
            if self.country_code in self.COUNTRY_CODES:
                data['country_name'] = self.COUNTRY_CODES[self.country_code]['name']
        
        return data

    def get_formatted_phone(self):
        """Retourne le numéro de téléphone formaté avec le code pays"""
        if not self.phone:
            return None
        
        # Si le numéro commence déjà par +, le retourner tel quel
        if self.phone.startswith('+'):
            return self.phone
        
        # Sinon, ajouter le code pays
        return f"{self.country_code}{self.phone}"

    def validate_phone(self):
        """Valide le format du numéro de téléphone selon le pays"""
        if not self.phone or not self.country_code:
            return True  # Numéro optionnel
        
        if self.country_code not in self.COUNTRY_CODES:
            return False, f"Code pays non supporté: {self.country_code}"
        
        country_info = self.COUNTRY_CODES[self.country_code]
        formatted_phone = self.get_formatted_phone()
        
        if not formatted_phone or not re.match(country_info['format'], formatted_phone):
            return False, f"Format invalide pour {country_info['name']}. Exemple: {country_info['example']}"
        
        return True, "Numéro valide"

    def normalize_phone(self):
        """Normalise le numéro de téléphone (supprime espaces, tirets, etc.)"""
        if not self.phone:
            return
        
        # Supprimer tous les caractères non numériques sauf +
        cleaned = re.sub(r'[^\d+]', '', self.phone)
        
        # Si le numéro commence par le code pays, l'extraire
        for code in self.COUNTRY_CODES.keys():
            if cleaned.startswith(code):
                self.country_code = code
                self.phone = cleaned[len(code):]
                return
        
        # Sinon, utiliser le code pays par défaut
        self.phone = cleaned

    @classmethod
    def get_by_criteria(cls, criteria, index, size):
        query = cls.query
        conditions = [cls.is_deleted == False]

        if 'id' in criteria:
            conditions.append(cls.id == criteria['id'])
        if 'name' in criteria:
            conditions.append(cls.name.like(f"%{criteria['name']}%"))
        if 'email' in criteria:
            conditions.append(cls.email == criteria['email'])
        if 'phone' in criteria:
            conditions.append(cls.phone == criteria['phone'])
        if 'country_code' in criteria:
            conditions.append(cls.country_code == criteria['country_code'])
        if 'is_active' in criteria:
            conditions.append(cls.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(cls.id.desc())

        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    @classmethod
    def find_by_email(cls, email, exclude_id=None):
        """Méthode d'accès aux données - rechercher par email"""
        query = cls.query.filter(cls.is_deleted == False, cls.email == email)
        if exclude_id:
            query = query.filter(cls.id != exclude_id)
        return query.first()

    @classmethod
    def find_by_phone(cls, phone, exclude_id=None):
        """Méthode d'accès aux données - rechercher par téléphone"""
        query = cls.query.filter(cls.is_deleted == False, cls.phone == phone)
        if exclude_id:
            query = query.filter(cls.id != exclude_id)
        return query.first()

    @classmethod
    def find_by_phone_and_country(cls, phone, country_code, exclude_id=None):
        """Méthode d'accès aux données - rechercher par téléphone et code pays"""
        query = cls.query.filter(
            cls.is_deleted == False, 
            cls.phone == phone,
            cls.country_code == country_code
        )
        if exclude_id:
            query = query.filter(cls.id != exclude_id)
        return query.first()

    @classmethod
    def find_by_name_and_address(cls, name, address, exclude_id=None):
        """Méthode d'accès aux données - rechercher par nom et adresse"""
        query = cls.query.filter(
            cls.is_deleted == False,
            cls.name == name,
            cls.address == address
        )
        if exclude_id:
            query = query.filter(cls.id != exclude_id)
        return query.first()

    @classmethod
    def get_supported_countries(cls):
        """Retourne la liste des pays supportés avec leurs formats"""
        return cls.COUNTRY_CODES

    def __repr__(self):
        return f'<Partner {self.name}>' 