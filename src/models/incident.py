from extensions import db
from sqlalchemy import and_
from datetime import datetime


class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Amélioration : Ajouter des champs pour la communication
    type = db.Column(db.String(50), default='incident')  # 'incident', 'message', 'support', 'notification'
    priority = db.Column(db.String(20), default='moyenne')  # 'basse', 'moyenne', 'haute', 'critique'
    status = db.Column(db.String(20), default='ouvert')  # 'ouvert', 'en_cours', 'resolu', 'ferme'
    category = db.Column(db.String(50), nullable=True)  # 'technique', 'fonctionnel', 'support', 'question'
    
    # Relations existantes
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Qui a créé
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # Projet concerné
    
    # Nouveau : Assignation et réponses
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin assigné
    parent_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=True)  # Pour les réponses
    
    # Nouveaux champs pour la communication
    resolution_notes = db.Column(db.Text, nullable=True)  # Notes de résolution
    is_read = db.Column(db.Boolean, default=False)  # Lu par le destinataire
    read_at = db.Column(db.DateTime, nullable=True)  # Date de lecture
    
    # Champs existants
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations améliorées
    children = db.relationship('Incident', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def as_dict(self):
        data = {}
        columns = [
            'id', 'title', 'description', 'type', 'priority', 'status', 'category',
            'user_id', 'project_id', 'assigned_to', 'parent_id', 
            'resolution_notes', 'is_read', 'read_at',
            'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by'
        ]
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
        query = Incident.query
        conditions = [Incident.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(Incident.id == criteria['id'])
        if 'title' in criteria:
            conditions.append(Incident.title.like(f"%{criteria['title']}%"))
        if 'description' in criteria:
            conditions.append(Incident.description.like(f"%{criteria['description']}%"))
        if 'type' in criteria:
            conditions.append(Incident.type == criteria['type'])
        if 'priority' in criteria:
            conditions.append(Incident.priority == criteria['priority'])
        if 'status' in criteria:
            conditions.append(Incident.status == criteria['status'])
        if 'category' in criteria:
            conditions.append(Incident.category == criteria['category'])
        if 'user_id' in criteria:
            conditions.append(Incident.user_id == criteria['user_id'])
        if 'project_id' in criteria:
            conditions.append(Incident.project_id == criteria['project_id'])
        if 'assigned_to' in criteria:
            conditions.append(Incident.assigned_to == criteria['assigned_to'])
        if 'parent_id' in criteria:
            conditions.append(Incident.parent_id == criteria['parent_id'])
        if 'is_read' in criteria:
            conditions.append(Incident.is_read == criteria['is_read'])
        if 'is_active' in criteria:
            conditions.append(Incident.is_active == criteria['is_active'])

        query = query.filter(and_(*conditions))
        query = query.order_by(Incident.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<Incident {self.title}>'
