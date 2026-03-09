from extensions import db
from datetime import datetime


class IncidentHistory(db.Model):
    """
    Historique complet des changements de statut et des actions sur un incident.
    Chaque transition de statut, résolution, refus, mise en attente, etc. est enregistrée.
    """
    __tablename__ = 'incident_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Transition de statut
    old_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=False)

    # Type d'action : 'status_change', 'assignment', 'resolution', 'refusal', 'waiting', 'closure', 'reopening'
    action_type = db.Column(db.String(50), nullable=False, default='status_change')

    # Commentaire ou motif associé à l'action
    comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, nullable=True)

    # Relations
    incident = db.relationship('Incident', backref=db.backref('history', lazy=True, order_by='IncidentHistory.created_at'))
    user = db.relationship('User', foreign_keys=[user_id])

    def as_dict(self):
        data = {}
        columns = ['id', 'incident_id', 'user_id', 'old_status', 'new_status', 'action_type', 'comment', 'created_at', 'created_by']
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value

        # Ajouter le nom de l'utilisateur si disponible
        if self.user:
            data['user_name'] = self.user.name or self.user.email

        return data

    @staticmethod
    def get_by_incident(incident_id):
        return IncidentHistory.query.filter_by(incident_id=incident_id).order_by(IncidentHistory.created_at.asc()).all()

    @staticmethod
    def record(incident_id, new_status, old_status=None, action_type='status_change', comment=None, user_id=None):
        """
        Enregistrer une entrée dans l'historique.
        """
        entry = IncidentHistory(
            incident_id=incident_id,
            user_id=user_id,
            old_status=old_status,
            new_status=new_status,
            action_type=action_type,
            comment=comment,
            created_at=datetime.utcnow(),
            created_by=user_id
        )
        db.session.add(entry)
        return entry

    def __repr__(self):
        return f'<IncidentHistory incident={self.incident_id} {self.old_status}→{self.new_status}>'
