from extensions import db
from datetime import datetime


class IncidentAttachment(db.Model):
    """
    Pièces jointes (fichiers) liées à une note d'incident.
    """
    __tablename__ = 'incident_attachments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.Integer, db.ForeignKey('incident_notes.id'), nullable=False, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False, index=True)

    file_name = db.Column(db.String(255), nullable=False)   # Nom original du fichier
    file_url = db.Column(db.String(500), nullable=False)    # URL d'accès
    file_type = db.Column(db.String(100), nullable=True)    # MIME type
    file_size = db.Column(db.Integer, nullable=True)        # Taille en octets

    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    author = db.relationship('User', foreign_keys=[created_by])

    def as_dict(self):
        data = {
            'id': self.id,
            'note_id': self.note_id,
            'incident_id': self.incident_id,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
        }
        if self.author:
            data['author_name'] = self.author.name or self.author.email
        return data

    def __repr__(self):
        return f'<IncidentAttachment id={self.id} note={self.note_id} file={self.file_name}>'
