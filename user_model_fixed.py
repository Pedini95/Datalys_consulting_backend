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
        columns = ['id', 'name', 'email', 'password_hash', 'is_temp_password', 'fcm_token', 'role_id', 
                  'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
        
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value
            elif column == 'fcm_token':
                # Toujours inclure fcm_token même si None
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

    def __repr__(self):
        return f'<User {self.email}>'
