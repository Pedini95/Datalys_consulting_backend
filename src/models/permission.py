from extensions import db
from sqlalchemy import and_
from datetime import datetime


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    label = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    def as_dict(self):
        data = {}
        columns = ['id', 'key', 'label', 'description', 'is_active', 'is_deleted',
                   'created_at', 'created_by', 'updated_at', 'updated_by']
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
        query = Permission.query
        conditions = [Permission.is_deleted == False]

        if 'id' in criteria:
            conditions.append(Permission.id == criteria['id'])
        if 'key' in criteria:
            conditions.append(Permission.key.like(f"%{criteria['key']}%"))
        if 'is_active' in criteria:
            conditions.append(Permission.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(Permission.id.asc())

        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<Permission {self.key}>'
