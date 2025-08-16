from extensions import db
from datetime import datetime


class ActionHistory(db.Model):
    __tablename__ = 'action_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self):
        data = {}
        # Utiliser les attributs de la classe directement
        columns = ['id', 'user_id', 'action_type', 'entity_type', 'entity_id', 
                  'description', 'ip_address', 'user_agent', 'created_at']
        
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
        query = ActionHistory.query
        
        if 'id' in criteria:
            query = query.filter(ActionHistory.id == criteria['id'])
        if 'user_id' in criteria:
            query = query.filter(ActionHistory.user_id == criteria['user_id'])
        if 'action_type' in criteria:
            query = query.filter(ActionHistory.action_type == criteria['action_type'])
        if 'entity_type' in criteria:
            query = query.filter(ActionHistory.entity_type == criteria['entity_type'])
        if 'entity_id' in criteria:
            query = query.filter(ActionHistory.entity_id == criteria['entity_id'])
        if 'ip_address' in criteria:
            query = query.filter(ActionHistory.ip_address == criteria['ip_address'])

        query = query.order_by(ActionHistory.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<ActionHistory {self.action_type} on {self.entity_type} by user {self.user_id}>' 