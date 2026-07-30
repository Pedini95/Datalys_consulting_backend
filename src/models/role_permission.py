from extensions import db
from sqlalchemy import and_
from datetime import datetime


class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )

    permission = db.relationship('Permission')

    def as_dict(self):
        data = {}
        columns = ['id', 'role_id', 'permission_id', 'created_at', 'created_by']
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
        query = RolePermission.query
        conditions = []

        if 'id' in criteria:
            conditions.append(RolePermission.id == criteria['id'])
        if 'role_id' in criteria:
            conditions.append(RolePermission.role_id == criteria['role_id'])
        if 'permission_id' in criteria:
            conditions.append(RolePermission.permission_id == criteria['permission_id'])

        if conditions:
            query = query.filter(and_(*conditions))
        query = query.order_by(RolePermission.id.asc())

        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<RolePermission role_id={self.role_id} permission_id={self.permission_id}>'
