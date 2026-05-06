from extensions import db
from sqlalchemy import and_
from datetime import datetime


class Incident(db.Model):
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    #  NOUVEAU : Numéro d'incident auto-généré (INC-2025-00001)
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
    
    #  NOUVEAU : Impact de l'incident
    impact = db.Column(db.String(50), nullable=True)  # 'arret_service', 'service_degrade', 'majeur', 'mineur'
    
    #  NOUVEAU : Domaine concerné
    domain = db.Column(db.String(50), nullable=True)  # 'reseau', 'infrastructure', 'cloud', 'energie'
    
    #  NOUVEAU : Nom du déclarant
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
    
    # Champs de résolution
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Qui a résolu
    resolved_at = db.Column(db.DateTime, nullable=True)  # Date de résolution

    #  NOUVEAU : Champs de refus de solution
    refusal_count = db.Column(db.Integer, default=0)  # Nombre de fois que le client a refusé la solution
    refusal_reason = db.Column(db.Text, nullable=True)  # Raison du dernier refus
    last_refusal_at = db.Column(db.DateTime, nullable=True)  # Date du dernier refus

    #  NOUVEAU : Champs SLA (Service Level Agreement)
    taken_at = db.Column(db.DateTime, nullable=True)  # Date de prise en charge
    sla_prise_en_charge_deadline = db.Column(db.DateTime, nullable=True)  # Deadline prise en charge
    sla_resolution_deadline = db.Column(db.DateTime, nullable=True)  # Deadline résolution
    sla_prise_en_charge_status = db.Column(db.String(20), default='respecte')  # 'respecte' ou 'depasse'
    sla_resolution_status = db.Column(db.String(20), default='respecte')  # 'respecte' ou 'depasse'
    
    # Champs existants
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    # Suppression individuelle pour messages (expéditeur/destinataire)
    deleted_by_sender = db.Column(db.Boolean, default=False)
    deleted_by_recipient = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, nullable=True)

    # Relations améliorées
    children = db.relationship('Incident', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    # Relations avec users (spécifier les foreign_keys pour éviter l'ambiguïté)
    creator = db.relationship('User', foreign_keys=[user_id])
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    resolver = db.relationship('User', foreign_keys=[resolved_by])

    def as_dict(self):
        data = {}
        columns = [
            'id', 'incident_number', 'title', 'description', 'type', 'priority', 'status', 'category',
            'impact', 'domain', 'declarant_name', 'motif_attente',
            'user_id', 'project_id', 'assigned_to', 'parent_id',
            'resolution_notes', 'is_read', 'read_at', 'resolved_by', 'resolved_at',
            'refusal_count', 'refusal_reason', 'last_refusal_at',
            'taken_at', 'sla_prise_en_charge_deadline', 'sla_resolution_deadline',
            'sla_prise_en_charge_status', 'sla_resolution_status',
            'is_active', 'is_deleted', 'deleted_by_sender', 'deleted_by_recipient',
            'created_at', 'created_by', 'updated_at', 'updated_by'
        ]
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value

        #  Ajouter des métadonnées utiles
        if self.priority:
            data['priority_label'] = self.get_priority_label()
        if self.status:
            data['status_color'] = self.get_status_color()
        if self.impact:
            data['impact_label'] = self.get_impact_label()

        #  Ajouter les délais SLA calculés
        if self.sla_prise_en_charge_deadline and not self.taken_at:
            data['temps_restant_prise_en_charge'] = self.calculate_time_remaining(self.sla_prise_en_charge_deadline)
        if self.sla_resolution_deadline and not self.resolved_at:
            data['temps_restant_resolution'] = self.calculate_time_remaining(self.sla_resolution_deadline)

        #  Ajouter le numéro de ticket parent pour les réponses/messages
        if self.parent_id:
            parent_ticket = self.get_parent_ticket()
            if parent_ticket:
                data['parent_ticket_number'] = parent_ticket.incident_number
                data['parent_ticket_title'] = parent_ticket.title
                data['thread_ticket_number'] = parent_ticket.incident_number  # Numéro du ticket du thread
        else:
            # Si c'est le message principal, son propre numéro est le numéro du thread
            data['thread_ticket_number'] = self.incident_number

        # Compter le nombre de réponses
        data['replies_count'] = len(self.children) if self.children else 0

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

    def get_parent_ticket(self):
        """
        Récupère le ticket parent (le message principal du thread)
        Remonte la chaîne des parents jusqu'au message principal
        """
        if not self.parent_id:
            return self

        parent = Incident.query.get(self.parent_id)
        if not parent:
            return None

        # Si le parent a lui-même un parent, on continue de remonter
        if parent.parent_id:
            return parent.get_parent_ticket()

        return parent

    def get_thread_messages(self, include_self=True):
        """
        Récupère tous les messages d'un thread (le message principal + toutes les réponses)
        Retourne une liste ordonnée chronologiquement
        """
        # Si c'est une réponse, remonter au parent
        parent_ticket = self.get_parent_ticket()

        # Récupérer tous les messages du thread
        if include_self and parent_ticket.id == self.id:
            # On est déjà le parent
            messages = [parent_ticket]
        elif include_self:
            messages = [parent_ticket, self]
        else:
            messages = [parent_ticket]

        # Ajouter toutes les réponses récursivement
        def get_all_children(incident):
            children = []
            for child in incident.children:
                if not child.is_deleted:
                    children.append(child)
                    children.extend(get_all_children(child))
            return children

        all_children = get_all_children(parent_ticket)
        messages.extend(all_children)

        # Enlever les doublons et trier par date de création
        unique_messages = list({msg.id: msg for msg in messages}.values())
        unique_messages.sort(key=lambda x: x.created_at)

        return unique_messages

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
        
        #  Nouveaux critères de recherche
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
    def get_sla_config(cls):
        """
        Configuration SLA par priorité
        Retourne les délais de prise en charge et de résolution
        """
        return {
            'P1': {
                'prise_en_charge_minutes': 30,  # 30 minutes (24/7)
                'resolution_hours': 4  # 4 heures ouvrées
            },
            'P2': {
                'prise_en_charge_hours': 1,  # 1 heure ouvrée
                'resolution_hours': 8  # 1 jour ouvré (8h)
            },
            'P3': {
                'prise_en_charge_hours': 4,  # 4 heures ouvrées
                'resolution_hours': 24  # 3 jours ouvrés (3x8h)
            },
            'P4': {
                'prise_en_charge_hours': 8,  # 1 jour ouvré
                'resolution_hours': 40  # 5 jours ouvrés (5x8h)
            }
        }
    
    @classmethod
    def calculate_sla_deadlines(cls, priority, created_at=None):
        """
        Calcule les deadlines SLA en fonction de la priorité
        Retourne un dict avec les deux deadlines
        """
        from datetime import timedelta
        
        if not created_at:
            created_at = datetime.utcnow()
        
        sla_config = cls.get_sla_config()
        
        # P1 n'est pas dans la config car priorité P0 n'a pas de SLA défini
        if priority not in sla_config:
            return {
                'sla_prise_en_charge_deadline': None,
                'sla_resolution_deadline': None
            }
        
        config = sla_config[priority]
        
        # Calcul deadline prise en charge
        if 'prise_en_charge_minutes' in config:
            prise_en_charge_deadline = created_at + timedelta(minutes=config['prise_en_charge_minutes'])
        else:
            prise_en_charge_deadline = created_at + timedelta(hours=config['prise_en_charge_hours'])
        
        # Calcul deadline résolution
        resolution_deadline = created_at + timedelta(hours=config['resolution_hours'])
        
        return {
            'sla_prise_en_charge_deadline': prise_en_charge_deadline,
            'sla_resolution_deadline': resolution_deadline
        }
    
    def calculate_time_remaining(self, deadline):
        """
        Calcule le temps restant jusqu'à la deadline
        Retourne un dict avec jours, heures, minutes et le statut (respecte/depasse)
        """
        if not deadline:
            return None
        
        now = datetime.utcnow()
        delta = deadline - now
        
        # Si la deadline est dépassée
        if delta.total_seconds() < 0:
            total_minutes = int(abs(delta.total_seconds()) / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            days = hours // 24
            hours = hours % 24
            
            return {
                'status': 'depasse',
                'depassement': True,
                'jours': days,
                'heures': hours,
                'minutes': minutes,
                'total_minutes': -total_minutes  # Négatif pour indiquer le dépassement
            }
        
        # Si la deadline n'est pas encore atteinte
        total_minutes = int(delta.total_seconds() / 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        days = hours // 24
        hours = hours % 24
        
        return {
            'status': 'respecte',
            'depassement': False,
            'jours': days,
            'heures': hours,
            'minutes': minutes,
            'total_minutes': total_minutes
        }
    
    def update_sla_status(self):
        """
        Met à jour les statuts SLA (respecte/depasse) en fonction de l'état actuel
        À appeler périodiquement ou lors de la récupération
        """
        now = datetime.utcnow()
        
        # Vérifier le statut de prise en charge
        if self.sla_prise_en_charge_deadline and not self.taken_at:
            if now > self.sla_prise_en_charge_deadline:
                self.sla_prise_en_charge_status = 'depasse'
            else:
                self.sla_prise_en_charge_status = 'respecte'
        
        # Vérifier le statut de résolution
        if self.sla_resolution_deadline and not self.resolved_at:
            if now > self.sla_resolution_deadline:
                self.sla_resolution_status = 'depasse'
            else:
                self.sla_resolution_status = 'respecte'
    
    @classmethod
    def generate_incident_number(cls, ticket_type='incident'):
        """
        Génère un numéro de ticket unique et séquentiel.
        Format : INC-YYYY-NNNNN pour les incidents, SUPP-YYYY-NNNNN pour le support.
        """
        year = datetime.now().year
        prefix = 'SUPP' if ticket_type == 'support' else 'INC'

        last_ticket = cls.query.filter(
            cls.incident_number.like(f'{prefix}-{year}-%')
        ).order_by(cls.id.desc()).with_for_update().first()

        if last_ticket:
            last_num = int(last_ticket.incident_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f'{prefix}-{year}-{new_num:05d}'

    def __repr__(self):
        return f'<Incident {self.incident_number}: {self.title}>' 