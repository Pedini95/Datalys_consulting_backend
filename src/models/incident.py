from extensions import db
from sqlalchemy import and_
from datetime import datetime


class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # ✅ NOUVEAU : Numéro d'incident auto-généré (INC-2025-00001)
    incident_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Amélioration : Ajouter des champs pour la communication
    type = db.Column(db.String(50), default='incident')  # 'incident', 'message', 'support', 'notification'
    
    priority = db.Column(db.String(20), default='P3')  # 'P0', 'P1', 'P2', 'P3', 'P4'
    # P0 : Arrêt de service (prise en charge immédiate)
    # P1 : Forte dégradation de service
    # P2 : Dégradation de service
    # P3 : Incident ordinaire sans impact
    # P4 : Incident mineur
    
    # ✅ NOUVEAU : Impact de l'incident
    impact = db.Column(db.String(50), nullable=True)  # 'arret_service', 'service_degrade', 'majeur', 'mineur'
    
    # ✅ NOUVEAU : Domaine concerné
    domain = db.Column(db.String(50), nullable=True)  # 'reseau', 'infrastructure', 'cloud', 'energie'
    
    # ✅ NOUVEAU : Nom du déclarant
    declarant_name = db.Column(db.String(255), nullable=True)
    
    status = db.Column(db.String(20), default='nouveau')  # 'nouveau', 'en_cours', 'en_attente', 'en_arbitrage', 'resolu', 'ferme'
    
    motif_attente = db.Column(db.Text, nullable=True)
    
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
    
    # Relations avec users (spécifier les foreign_keys pour éviter l'ambiguïté)
    creator = db.relationship('User', foreign_keys=[user_id])
    assignee = db.relationship('User', foreign_keys=[assigned_to])

    def as_dict(self):
        data = {}
        columns = [
            'id', 'incident_number', 'title', 'description', 'type', 'priority', 'status', 'category',
            'impact', 'domain', 'declarant_name', 'motif_attente', 
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
        
        # ✅ Ajouter des métadonnées utiles
        if self.priority:
            data['priority_label'] = self.get_priority_label()
        if self.status:
            data['status_color'] = self.get_status_color()
        if self.impact:
            data['impact_label'] = self.get_impact_label()
        
        return data
    
    def get_priority_label(self):
        """Retourne le label descriptif de la priorité"""
        labels = {
            'P0': 'Arrêt de service (immédiat)',
            'P1': 'Forte dégradation de service',
            'P2': 'Dégradation de service',
            'P3': 'Incident ordinaire',
            'P4': 'Incident mineur'
        }
        return labels.get(self.priority, self.priority)
    
    def get_status_color(self):
        """Retourne la couleur associée au statut"""
        colors = {
            'nouveau': 'blue',
            'en_cours': 'orange',
            'en_attente': 'gray',
            'en_arbitrage': 'purple',
            'resolu': 'green',
            'ferme': 'black'
        }
        return colors.get(self.status, 'gray')
    
    def get_impact_label(self):
        """Retourne le label descriptif de l'impact"""
        labels = {
            'arret_service': 'Arrêt de service',
            'service_degrade': 'Service dégradé',
            'majeur': 'Impact majeur',
            'mineur': 'Impact mineur'
        }
        return labels.get(self.impact, self.impact)

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
        
        # ✅ Nouveaux critères de recherche
        if 'impact' in criteria:
            conditions.append(Incident.impact == criteria['impact'])
        if 'domain' in criteria:
            conditions.append(Incident.domain == criteria['domain'])
        if 'declarant_name' in criteria:
            conditions.append(Incident.declarant_name.like(f"%{criteria['declarant_name']}%"))
        
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
    
    @classmethod
    def get_priority_mapping(cls):
        """Retourne le mapping entre impact et priorité recommandée"""
        return {
            'arret_service': 'P0',
            'service_degrade': 'P1',
            'majeur': 'P2',
            'mineur': 'P3'
        }
    
    @classmethod
    def get_valid_priorities(cls):
        """Retourne la liste des priorités valides"""
        return ['P0', 'P1', 'P2', 'P3', 'P4']
    
    @classmethod
    def get_valid_statuses(cls):
        """Retourne la liste des statuts valides"""
        return ['nouveau', 'en_cours', 'en_attente', 'en_arbitrage', 'resolu', 'ferme']
    
    @classmethod
    def get_valid_impacts(cls):
        """Retourne la liste des impacts valides"""
        return ['arret_service', 'service_degrade', 'majeur', 'mineur']
    
    @classmethod
    def get_valid_domains(cls):
        """Retourne la liste des domaines valides"""
        return ['reseau', 'infrastructure', 'cloud', 'energie']
    
    @classmethod
    def generate_incident_number(cls):
        """
        Génère un numéro d'incident unique et séquentiel
        Format : INC-YYYY-NNNNN (ex: INC-2025-00001)
        
        Utilise un verrouillage de ligne pour garantir l'unicité
        même en cas de créations simultanées
        """
        year = datetime.now().year
        
        # Verrouiller la dernière ligne pour éviter les doublons (FOR UPDATE)
        last_incident = cls.query.filter(
            cls.incident_number.like(f'INC-{year}-%')
        ).order_by(cls.id.desc()).with_for_update().first()
        
        if last_incident:
            # Extraire le numéro de la dernière entrée
            last_num = int(last_incident.incident_number.split('-')[-1])
            new_num = last_num + 1
        else:
            # Premier incident de l'année
            new_num = 1
        
        return f'INC-{year}-{new_num:05d}'

    def __repr__(self):
        return f'<Incident {self.incident_number}: {self.title}>' 