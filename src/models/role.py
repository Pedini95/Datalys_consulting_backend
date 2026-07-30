from extensions import db
from sqlalchemy import and_
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations
    users = db.relationship('User', backref='role', lazy=True)
    user_project_permissions = db.relationship('UserProjectPermission', backref='role', lazy=True)

    def as_dict(self):
        data = {}
        # Utiliser les attributs de la classe directement
        columns = ['id', 'name', 'is_active', 'is_deleted', 'created_at', 
                  'created_by', 'updated_at', 'updated_by']
        
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value
        return data

    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = Role.query
        conditions = [Role.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(Role.id == criteria['id'])
        if 'name' in criteria:
            conditions.append(Role.name.like(f"%{criteria['name']}%"))
        if 'is_active' in criteria:
            conditions.append(Role.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(Role.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def has_permission(self, permission_key: str) -> bool:
        """
        Vérifie si ce rôle possède la permission donnée (via la table role_permissions).
        """
        from models.permission import Permission
        from models.role_permission import RolePermission

        return db.session.query(RolePermission).join(
            Permission, RolePermission.permission_id == Permission.id
        ).filter(
            RolePermission.role_id == self.id,
            Permission.key == permission_key,
            Permission.is_active == True,
            Permission.is_deleted == False,
        ).first() is not None

    def __repr__(self):
        return f'<Role {self.name}>' 