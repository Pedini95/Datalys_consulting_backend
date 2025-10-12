from extensions import db
from sqlalchemy import and_
from datetime import datetime


class UserProjectPermission(db.Model):
    __tablename__ = 'user_project_permissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)  # Optionnel : peut utiliser can_read/write/delete à la place
    can_read = db.Column(db.Boolean, default=True)
    can_write = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    def as_dict(self):
        data = {}
        columns = ['id', 'user_id', 'project_id', 'role_id', 'can_read', 'can_write', 'can_delete', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
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
        query = UserProjectPermission.query
        conditions = [UserProjectPermission.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(UserProjectPermission.id == criteria['id'])
        if 'user_id' in criteria:
            conditions.append(UserProjectPermission.user_id == criteria['user_id'])
        if 'project_id' in criteria:
            conditions.append(UserProjectPermission.project_id == criteria['project_id'])
        if 'role_id' in criteria:
            conditions.append(UserProjectPermission.role_id == criteria['role_id'])
        if 'is_active' in criteria:
            conditions.append(UserProjectPermission.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(UserProjectPermission.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<UserProjectPermission user_id={self.user_id} project_id={self.project_id} role_id={self.role_id}>' 