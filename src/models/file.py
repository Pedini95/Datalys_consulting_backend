from extensions import db
from sqlalchemy import and_
from datetime import datetime


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=True)
    file_url = db.Column(db.String(255), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    def as_dict(self):
        data = {}
        columns = ['id', 'name', 'folder_id', 'incident_id', 'file_url', 'is_public', 'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
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
        query = File.query
        conditions = [File.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(File.id == criteria['id'])
        if 'name' in criteria:
            conditions.append(File.name.like(f"%{criteria['name']}%"))
        if 'folder_id' in criteria:
            conditions.append(File.folder_id == criteria['folder_id'])
        if 'incident_id' in criteria:
            conditions.append(File.incident_id == criteria['incident_id'])
        if 'is_public' in criteria:
            conditions.append(File.is_public == criteria['is_public'])
        if 'is_active' in criteria:
            conditions.append(File.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(File.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<File {self.name}>' 