from extensions import db
from datetime import datetime


class IncidentNote(db.Model):
    """
    Notes de résolution horodatées liées à un incident.
    Plusieurs notes peuvent être ajoutées par les techniciens au fil du temps.
    """
    __tablename__ = 'incident_notes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False, index=True)

    content = db.Column(db.Text, nullable=False)

    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations
    incident = db.relationship('Incident', backref=db.backref('notes', lazy=True, order_by='IncidentNote.created_at'))
    author = db.relationship('User', foreign_keys=[created_by])
    attachments = db.relationship('IncidentAttachment', backref='note', lazy=True, cascade='all, delete-orphan')

    def as_dict(self):
        data = {
            'id': self.id,
            'incident_id': self.incident_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
        }
        if self.author:
            data['author_name'] = self.author.name or self.author.email
        data['attachments'] = [a.as_dict() for a in self.attachments if not a.is_deleted]
        return data

    def __repr__(self):
        return f'<IncidentNote id={self.id} incident={self.incident_id}>'
