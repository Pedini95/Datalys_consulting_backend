from extensions import db
from sqlalchemy import and_
from datetime import datetime


class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations
    projects = db.relationship('Project', backref='partner', lazy=True)

    def as_dict(self):
        data = {}
        columns = ['id', 'name', 'email', 'phone', 'address', 'logo_url', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
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
        query = Partner.query
        conditions = [Partner.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(Partner.id == criteria['id'])
        if 'name' in criteria:
            conditions.append(Partner.name.like(f"%{criteria['name']}%"))
        if 'is_active' in criteria:
            conditions.append(Partner.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(Partner.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<Partner {self.name}>' 