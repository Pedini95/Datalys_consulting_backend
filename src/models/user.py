from extensions import db
from sqlalchemy import and_
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)  # Changed from username to name
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_temp_password = db.Column(db.Boolean, default=False)  # Gestion des mots de passe temporaires
    fcm_token = db.Column(db.String(255), nullable=True)  # Token Firebase Cloud Messaging pour notifications push

    # ✅ NOUVEAU : Code client unique pour login sans email (évite problèmes de mobilité)
    client_code = db.Column(db.String(50), unique=True, nullable=True, index=True)  # Format: DATALYS-2025-001

    # ✅ NOUVEAU : Champs MFA (Multi-Factor Authentication)
    mfa_enabled = db.Column(db.Boolean, default=True)  # MFA activé par défaut pour la sécurité
    mfa_code = db.Column(db.String(10), nullable=True)  # Code temporaire (6 chiffres)
    mfa_code_expiry = db.Column(db.DateTime, nullable=True)  # Date d'expiration du code (5 minutes)
    mfa_code_attempts = db.Column(db.Integer, default=0)  # Nombre de tentatives échouées

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(255), nullable=True)

    def as_dict(self):
        data = {}
        # Utiliser les attributs de la classe directement
        columns = ['id', 'name', 'email', 'password_hash', 'is_temp_password', 'fcm_token', 'client_code',
                  'role_id', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
        
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value
            elif column in ['fcm_token', 'client_code']:
                # Toujours inclure fcm_token et client_code même si None
                data[column] = value
        
        # Ajouter un champ username pour la compatibilité (alias de name)
        data['username'] = data.get('name', '')
        
        return data

    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = User.query
        conditions = [User.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(User.id == criteria['id'])
        if 'name' in criteria:
            # Rechercher dans name seulement
            conditions.append(User.name.like(f"%{criteria['name']}%"))
        if 'email' in criteria:
            conditions.append(User.email.like(f"%{criteria['email']}%"))
        if 'client_code' in criteria:
            conditions.append(User.client_code == criteria['client_code'])
        if 'role_id' in criteria:
            conditions.append(User.role_id == criteria['role_id'])
        if 'is_active' in criteria:
            conditions.append(User.is_active == criteria['is_active'])
        if 'fcm_token' in criteria:
            conditions.append(User.fcm_token == criteria['fcm_token'])

        query = query.filter(and_(*conditions))
        query = query.order_by(User.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    @classmethod
    def generate_client_code(cls):
        """
        Génère un code client unique au format DTLSXXXXXX (8 caractères alphanumériques)
        Exemple: DTLSA3K9M2, DTLS7BX4P1, DTLSQ8N5R6
        
        Returns:
            str: Code client unique
        """
        import random
        import string
        
        # Caractères autorisés : lettres majuscules et chiffres (sans 0, O, I, 1 pour éviter confusion)
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        
        max_attempts = 100
        for _ in range(max_attempts):
            # Générer 6 caractères aléatoires
            random_part = ''.join(random.choices(chars, k=6))
            code = f'DTLS{random_part}'
            
            # Vérifier que ce code n'existe pas déjà
            existing = cls.query.filter(cls.client_code == code).first()
            if not existing:
                return code
        
        # Si après 100 tentatives on n'a pas trouvé de code unique, lever une exception
        raise Exception("Impossible de générer un code client unique après 100 tentatives")

    def __repr__(self):
        return f'<User {self.email}>'




