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
        Génère un code client unique au format DATALYS-YYYY-NNN
        Exemple: DATALYS-2025-001, DATALYS-2025-002, etc.
        
        Returns:
            str: Code client unique
        """
        year = datetime.now().year
        
        # Trouver le dernier code client de l'année en cours avec verrouillage
        last_user = cls.query.filter(
            cls.client_code.like(f'DATALYS-{year}-%')
        ).order_by(cls.id.desc()).with_for_update().first()
        
        if last_user and last_user.client_code:
            # Extraire le numéro du dernier code (ex: DATALYS-2025-001 -> 1)
            try:
                last_num = int(last_user.client_code.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                # En cas d'erreur de parsing, recommencer à 1
                new_num = 1
        else:
            # Premier code de l'année
            new_num = 1
        
        return f'DATALYS-{year}-{new_num:03d}'

    def __repr__(self):
        return f'<User {self.email}>'




