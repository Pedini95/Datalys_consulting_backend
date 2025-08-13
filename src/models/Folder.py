from app import db
from sqlalchemy import and_
from datetime import datetime


class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    path = db.Column(db.String(500), nullable=True)  # Chemin physique du répertoire
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations
    files = db.relationship('File', backref='folder', lazy=True)
    subfolders = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def as_dict(self):
        data = {}
        columns = ['id', 'name', 'project_id', 'parent_folder_id', 'path', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
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
        query = Folder.query
        conditions = [Folder.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(Folder.id == criteria['id'])
        if 'name' in criteria:
            conditions.append(Folder.name.like(f"%{criteria['name']}%"))
        if 'project_id' in criteria:
            conditions.append(Folder.project_id == criteria['project_id'])
        if 'parent_folder_id' in criteria:
            conditions.append(Folder.parent_folder_id == criteria['parent_folder_id'])
        if 'is_active' in criteria:
            conditions.append(Folder.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(Folder.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<Folder {self.name}>' 