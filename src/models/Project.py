from app import db
from sqlalchemy import and_
from datetime import datetime


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations
    incidents = db.relationship('Incident', backref='project', lazy=True)
    folders = db.relationship('Folder', backref='project', lazy=True)
    user_project_permissions = db.relationship('UserProjectPermission', backref='project', lazy=True)

    def as_dict(self):
        data = {}
        columns = ['id', 'title', 'partner_id', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
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
        query = Project.query
        conditions = [Project.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(Project.id == criteria['id'])
        if 'title' in criteria:
            conditions.append(Project.title.like(f"%{criteria['title']}%"))
        if 'partner_id' in criteria:
            conditions.append(Project.partner_id == criteria['partner_id'])
        if 'is_active' in criteria:
            conditions.append(Project.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(Project.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<Project {self.title}>' 