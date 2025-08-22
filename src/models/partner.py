from extensions import db
from sqlalchemy import and_, Index
from datetime import datetime


class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True, index=True)
    phone = db.Column(db.String(50), nullable=True, index=True)
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
        Index('idx_partner_name_address', 'name', 'address'),
    )

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

    def __repr__(self):
        return f'<Partner {self.name}>' 