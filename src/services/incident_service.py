from models import Incident
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
import logging
from datetime import datetime
from utils.audit_decorator import audit_action
from utils.audit_utils import set_audit_fields, update_audit_field

logger = logging.getLogger(__name__)


class IncidentService:
    """
    Service pour la gestion des incidents et communication
    """
    
    def __init__(self):
        self.model_class = Incident
        # Import lazy pour éviter les dépendances circulaires
        self._push_service = None
    
    # ===============================
    # NOUVELLES MÉTHODES COMMUNICATION
    # ===============================
    
    @audit_action('CREATE', 'message')
    def create_message(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Créer un message pour communiquer

        Args:
            data: Données du message (title, description, project_id)
            user_id: ID de l'utilisateur qui envoie

        Returns:
            Tuple (message, succès, message)
        """
        # Nettoyer les champs non-valides pour le modèle Incident
        if 'user' in data:
            # Extraire user_id de l'objet user si présent
            if isinstance(data['user'], dict) and 'id' in data['user']:
                if not user_id:
                    user_id = data['user']['id']
            del data['user']

        # Extraire recipient_id si présent (pour assigned_to)
        if 'recipient_id' in data:
            data['assigned_to'] = data.pop('recipient_id')

        # Extraire incident_id si présent (peut être utilisé pour project_id ou parent_id)
        # Par défaut, on l'ignore car on ne sait pas s'il s'agit d'un projet ou d'un incident parent
        if 'incident_id' in data:
            # Si vous voulez lier le message à un incident parent, utilisez parent_id
            # Si vous voulez lier à un projet, utilisez project_id
            # Pour l'instant, on supprime ce champ car il est ambigu
            del data['incident_id']

        data.update({
            'type': 'message',
            'priority': data.get('priority', 'P3'),  # Utiliser P3 au lieu de 'moyenne' pour compatibilité SLA
            'status': 'ouvert',
            'category': 'communication'
        })

        # Ajouter user_id si fourni (pour identifier qui a créé le message)
        if user_id and 'user_id' not in data:
            data['user_id'] = user_id

        # Créer le message
        incident, success, message = self.create(data, user_id)
        
        if success and incident:
            # 🆕 Envoyer notification push selon le type d'utilisateur
            if data.get('priority') in ['P0', 'P1', 'P2']:  # Priorités hautes
                self._send_push_notification_for_message(incident, str(data.get('priority')), user_id)
        
        return incident, success, message
    
    @audit_action('CREATE', 'support')
    def create_support_request(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Créer une demande de support technique

        Args:
            data: Données de la demande (title, description, priority, project_id)
            user_id: ID de l'utilisateur qui demande

        Returns:
            Tuple (demande, succès, message)
        """
        # Nettoyer les champs non-valides pour le modèle Incident
        if 'user' in data:
            if isinstance(data['user'], dict) and 'id' in data['user']:
                if not user_id:
                    user_id = data['user']['id']
            del data['user']

        if 'recipient_id' in data:
            data['assigned_to'] = data.pop('recipient_id')

        if 'incident_id' in data:
            del data['incident_id']

        data.update({
            'type': 'support',
            'priority': data.get('priority', 'P3'),  # Utiliser P3 au lieu de 'moyenne' pour compatibilité SLA
            'status': 'ouvert',
            'category': 'technique'
        })

        # Ajouter user_id si fourni
        if user_id and 'user_id' not in data:
            data['user_id'] = user_id

        # Créer la demande de support
        incident, success, message = self.create(data, user_id)
        
        # 🆕 Envoyer notification push si priorité haute/critique
        if success and incident and data.get('priority') in ['P0', 'P1', 'P2']:  # Priorités hautes
            self._send_push_notification_for_support(incident, str(data.get('priority')))
        
        return incident, success, message
    
    @audit_action('CREATE', 'notification')
    def create_notification(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Créer une notification officielle

        Args:
            data: Données de la notification (title, description, assigned_to)
            user_id: ID de l'admin qui envoie

        Returns:
            Tuple (notification, succès, message)
        """
        # Nettoyer les champs non-valides pour le modèle Incident
        if 'user' in data:
            if isinstance(data['user'], dict) and 'id' in data['user']:
                if not user_id:
                    user_id = data['user']['id']
            del data['user']

        if 'recipient_id' in data:
            data['assigned_to'] = data.pop('recipient_id')

        if 'incident_id' in data:
            del data['incident_id']

        data.update({
            'type': 'notification',
            'priority': data.get('priority', 'P2'),  # Utiliser P2 (haute priorité) au lieu de 'haute'
            'status': 'ouvert',
            'category': 'officiel'
        })

        # Ajouter user_id si fourni
        if user_id and 'user_id' not in data:
            data['user_id'] = user_id

        return self.create(data, user_id)
    
    def reply_to_message(self, parent_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Répondre à un message existant

        Args:
            parent_id: ID du message parent
            data: Données de la réponse (title, description)
            user_id: ID de l'utilisateur qui répond

        Returns:
            Tuple (réponse, succès, message)
        """
        # Nettoyer les champs non-valides pour le modèle Incident
        if 'user' in data:
            if isinstance(data['user'], dict) and 'id' in data['user']:
                if not user_id:
                    user_id = data['user']['id']
            del data['user']

        if 'recipient_id' in data:
            data['assigned_to'] = data.pop('recipient_id')

        if 'incident_id' in data:
            del data['incident_id']

        # Vérifier que le message parent existe
        parent_messages, _ = self.model_class.get_by_criteria({'id': parent_id}, 0, 1)
        if not parent_messages:
            return None, False, "Message parent non trouvé"

        parent = parent_messages[0]

        data.update({
            'parent_id': parent_id,
            'type': parent.type,  # Même type que le parent
            'priority': parent.priority,
            'status': 'ouvert',
            'category': parent.category,
            'project_id': parent.project_id  # Même projet
        })
        
        # Marquer le message parent comme lu
        self.mark_as_read(parent_id, user_id)
        
        return self.create(data, user_id)
    
    def assign_to_admin(self, incident_id: int, admin_id: int, user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Assigner un incident/message à un admin
        
        Args:
            incident_id: ID de l'incident
            admin_id: ID de l'admin assigné
            user_id: ID de l'utilisateur qui assigne
            
        Returns:
            Tuple (incident, succès, message)
        """
        return self.update(incident_id, {
            'assigned_to': admin_id,
            'status': 'en_cours'
        }, user_id)
    
    def mark_as_read(self, incident_id: int, user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Marquer un message comme lu
        
        Args:
            incident_id: ID du message
            user_id: ID de l'utilisateur qui lit
            
        Returns:
            Tuple (incident, succès, message)
        """
        return self.update(incident_id, {
            'is_read': True,
            'read_at': datetime.utcnow()
        }, user_id)
    
    def resolve_incident(self, incident_id: int, resolution_notes: Optional[str] = None, user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Résoudre un incident avec des notes
        
        Args:
            incident_id: ID de l'incident
            resolution_notes: Notes de résolution (optionnel)
            user_id: ID de l'admin qui résout
            
        Returns:
            Tuple (incident, succès, message)
        """
        update_data = {'status': 'resolu'}
        if resolution_notes:
            update_data['resolution_notes'] = resolution_notes
        return self.update(incident_id, update_data, user_id)
    
    def close_incident(self, incident_id: int, user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Fermer définitivement un incident
        
        Args:
            incident_id: ID de l'incident
            user_id: ID de l'utilisateur qui ferme
            
        Returns:
            Tuple (incident, succès, message)
        """
        return self.update(incident_id, {
            'status': 'ferme'
        }, user_id)
    
    # ===============================
    # NOUVELLES MÉTHODES RECHERCHE
    # ===============================
    
    def get_messages_for_user(self, user_id: int, index: int = 0, size: int = 10) -> Tuple[list, int]:
        """
        Récupérer tous les messages pour un utilisateur spécifique
        """
        return self.getByCriteria({
            'created_by': user_id,  # Chercher dans created_by au lieu de user_id
            'type': 'message',
            'is_active': True
        }, index, size)
    
    def get_unread_notifications(self, user_id: int, index: int = 0, size: int = 10) -> Tuple[list, int]:
        """
        Récupérer les notifications non lues pour un utilisateur
        """
        return self.getByCriteria({
            'assigned_to': user_id,
            'type': 'notification',
            'is_read': False,
            'is_active': True
        }, index, size)
    
    def get_support_requests(self, status: Optional[str] = None, index: int = 0, size: int = 10) -> Tuple[list, int]:
        """
        Récupérer les demandes de support
        """
        criteria = {
            'type': 'support',
            'is_active': True
        }
        if status:
            criteria['status'] = status
            
        return self.getByCriteria(criteria, index, size)
    
    def get_conversation_thread(self, parent_id: int, index: int = 0, size: int = 50) -> Tuple[list, int]:
        """
        Récupérer toute la conversation (message + réponses)
        """
        # Récupérer le message parent et tous ses enfants
        all_messages = []
        
        # Message parent
        parent_messages, _ = self.getByCriteria({'id': parent_id}, 0, 1)
        if parent_messages:
            all_messages.extend(parent_messages)
        
        # Messages enfants
        child_messages, _ = self.getByCriteria({
            'parent_id': parent_id,
            'is_active': True
        }, index, size)
        all_messages.extend(child_messages)
        
        return all_messages, len(all_messages)

    # ===============================
    # MÉTHODES EXISTANTES MISES À JOUR
    # ===============================
    
    def create(self, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Créer un nouveau incident et alerter les partenaires
        
        Args:
            data: Données du incident à créer
            user_id: ID de l'utilisateur qui crée
            
        Returns:
            Tuple (incident, succès, message)
        """
        try:
            # ✅ NOUVEAU : Générer automatiquement le numéro d'incident
            if 'incident_number' not in data or not data['incident_number']:
                data['incident_number'] = self.model_class.generate_incident_number()
                logger.info(f"Numéro d'incident généré automatiquement: {data['incident_number']}")
            
            # ✅ NOUVEAU : Calculer automatiquement les deadlines SLA
            priority = data.get('priority', 'P3')
            if priority in ['P1', 'P2', 'P3', 'P4']:
                created_at = data.get('created_at', datetime.utcnow())
                sla_deadlines = self.model_class.calculate_sla_deadlines(priority, created_at)
                data['sla_prise_en_charge_deadline'] = sla_deadlines['sla_prise_en_charge_deadline']
                data['sla_resolution_deadline'] = sla_deadlines['sla_resolution_deadline']
                data['sla_prise_en_charge_status'] = 'respecte'
                data['sla_resolution_status'] = 'respecte'
                logger.info(f"Deadlines SLA calculées pour priorité {priority}: "
                          f"Prise en charge: {sla_deadlines['sla_prise_en_charge_deadline']}, "
                          f"Résolution: {sla_deadlines['sla_resolution_deadline']}")
            
            # Traiter le user_name si fourni (au lieu de user_id)
            if 'user_name' in data and data['user_name']:
                from models import User
                users, _ = User.get_by_criteria({'name': data['user_name']}, 0, 1)
                if users:
                    data['user_id'] = users[0].id
                    logger.info(f"Utilisateur trouvé: {data['user_name']} (ID: {users[0].id})")
                else:
                    logger.warning(f"Utilisateur non trouvé: {data['user_name']}")
                    return None, False, f"Utilisateur non trouvé: {data['user_name']}"
                del data['user_name']
            
            # Traiter le project_name si fourni (au lieu de project_id)
            if 'project_name' in data and data['project_name']:
                from models import Project
                projects, _ = Project.get_by_criteria({'title': data['project_name']}, 0, 1)
                if projects:
                    data['project_id'] = projects[0].id
                    logger.info(f"Projet trouvé: {data['project_name']} (ID: {projects[0].id})")
                else:
                    logger.warning(f"Projet non trouvé: {data['project_name']}")
                    return None, False, f"Projet non trouvé: {data['project_name']}"
                del data['project_name']
            
            # Ajouter les champs d'audit
            set_audit_fields(data, user_id)
            
            incident = self.model_class(**data)
            db.session.add(incident)
            db.session.flush()  # Pour obtenir l'ID de l'incident
            
            # ✅ BIDIRECTIONNALITÉ : Détecter le rôle de l'utilisateur qui crée l'incident
            creator_role = None
            if user_id:
                from models import User, Role
                creator = User.query.get(user_id)
                if creator and creator.role_id:
                    role = Role.query.get(creator.role_id)
                    if role:
                        creator_role = role.name
                        logger.info(f"Incident créé par: {creator.name} (Rôle: {creator_role})")
            
            # Envoyer des notifications selon le rôle du créateur
            if incident.type == 'incident':
                if creator_role in ['Admin', 'Manager']:
                    # SCÉNARIO 1: Admin/Manager → Partenaire
                    # Envoyer notification au partenaire si l'incident est lié à un projet
                    if incident.project_id:
                        logger.info("📧 Notification: Admin/Manager → Partenaire")
                        self._send_incident_alerts(incident, user_id)
                        # Aussi notifier les autres experts
                        self._send_expert_notifications(incident, user_id)
                
                elif creator_role == 'User':
                    # SCÉNARIO 2: Partenaire → Experts (BIDIRECTIONNEL)
                    logger.info("📧 Notification BIDIRECTIONNELLE: Partenaire → Experts")
                    self._send_expert_notifications(incident, user_id)
                
                else:
                    # Rôle inconnu ou non défini, notifier les experts par défaut
                    logger.warning(f"Rôle inconnu pour user_id={user_id}, notification aux experts par défaut")
                    self._send_expert_notifications(incident, user_id)
            
            db.session.commit()
            
            return incident, True, f"{self.model_class.__name__} créé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la création: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la création de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def _send_expert_notifications(self, incident: Incident, user_id: Optional[int] = None):
        """
        Envoyer des notifications par email à tous les experts (Admin/Manager)
        lors de la création d'un nouvel incident
        
        Args:
            incident: L'incident créé
            user_id: ID de l'utilisateur qui a créé l'incident
        """
        try:
            from models import Project, Partner, User, Role
            from utils.notification import EmailService
            
            # Récupérer tous les experts (Admin + Manager)
            experts = User.query.join(Role).filter(
                Role.name.in_(['Admin', 'Manager']),
                User.is_active == True,
                User.is_deleted == False,
                User.email.isnot(None)
            ).all()
            
            if not experts:
                logger.warning("Aucun expert trouvé pour envoyer les notifications")
                return
            
            logger.info(f"Envoi de notifications à {len(experts)} expert(s)")
            
            # Récupérer les informations du projet et du partenaire
            project_title = "N/A"
            partner_name = "N/A"
            
            if incident.project_id:
                projects, _ = Project.get_by_criteria({'id': incident.project_id}, 0, 1)
                if projects:
                    project = projects[0]
                    project_title = project.title
                    
                    if project.partner_id:
                        partners, _ = Partner.get_by_criteria({'id': project.partner_id}, 0, 1)
                        if partners:
                            partner_name = partners[0].name
            
            # Préparer les données de l'incident
            incident_data = {
                'incident_number': incident.incident_number,
                'incident_title': incident.title,
                'incident_description': incident.description or "Aucune description",
                'priority': incident.priority,
                'impact': incident.impact,
                'domain': incident.domain,
                'declarant_name': incident.declarant_name or "Non spécifié",
                'partner_name': partner_name,
                'project_title': project_title,
                'incident_id': incident.id,
                'created_at': incident.created_at.strftime('%d/%m/%Y à %H:%M') if incident.created_at else "Maintenant"
            }
            
            # Envoyer l'email à chaque expert
            email_service = EmailService()
            success_count = 0
            
            for expert in experts:
                try:
                    success = email_service.send_incident_notification_to_experts(
                        expert_email=expert.email,
                        expert_name=expert.name or expert.email,
                        incident_data=incident_data
                    )
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ Email envoyé à l'expert {expert.name} ({expert.email})")
                    else:
                        logger.error(f"❌ Échec de l'envoi à l'expert {expert.name} ({expert.email})")
                        
                except Exception as e:
                    logger.error(f"❌ Erreur lors de l'envoi à l'expert {expert.name}: {str(e)}")
            
            logger.info(f"📧 Notifications envoyées : {success_count}/{len(experts)} experts")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des notifications aux experts: {str(e)}")
            # Ne pas faire échouer la création de l'incident si l'email échoue
    
    def _send_incident_alerts(self, incident: Incident, user_id: Optional[int] = None):
        """
        Envoyer des alertes par email pour un incident (au partenaire/client)
        
        Args:
            incident: L'incident créé
            user_id: ID de l'utilisateur qui a créé l'incident
        """
        try:
            from models import Project, Partner, User
            from utils.notification import EmailService
            
            # Récupérer les informations du projet
            projects, _ = Project.get_by_criteria({'id': incident.project_id}, 0, 1)
            if not projects:
                logger.warning(f"Projet non trouvé pour l'incident {incident.id}")
                return
            
            project = projects[0]
            
            # Récupérer le partenaire du projet
            if project.partner_id:
                partners, _ = Partner.get_by_criteria({'id': project.partner_id}, 0, 1)
                if not partners:
                    logger.warning(f"Partenaire non trouvé pour le projet {project.id}")
                    return
                
                partner = partners[0]
                
                # Récupérer l'utilisateur qui a créé l'incident
                creator_name = "Système"
                if user_id:
                    users, _ = User.get_by_criteria({'id': user_id}, 0, 1)
                    if users:
                        creator_name = users[0].name or users[0].email
                
                # Récupérer l'utilisateur assigné à l'incident
                assigned_user_name = "Non assigné"
                if incident.user_id:
                    assigned_users, _ = User.get_by_criteria({'id': incident.user_id}, 0, 1)
                    if assigned_users:
                        assigned_user_name = assigned_users[0].name or assigned_users[0].email
                
                # Préparer les données pour l'email
                email_data = {
                    'partner_name': partner.name,
                    'project_title': project.title,
                    'incident_title': incident.title,
                    'incident_description': incident.description or "Aucune description",
                    'creator_name': creator_name,
                    'assigned_user': assigned_user_name,
                    'incident_id': incident.id,
                    'created_at': incident.created_at.strftime('%d/%m/%Y à %H:%M') if incident.created_at else "Maintenant"
                }
                
                # Envoyer l'email d'alerte
                email_service = EmailService()
                success = email_service.send_incident_alert(
                    to_email=partner.email,
                    partner_name=partner.name,
                    email_data=email_data
                )
                
                if success:
                    logger.info(f"Email d'alerte envoyé au partenaire {partner.name} ({partner.email})")
                    
                    # Mettre à jour l'email du partenaire avec confirmation
                    try:
                        # Ajouter un champ pour indiquer que l'email a été envoyé
                        partner.email_sent_at = datetime.utcnow()
                        db.session.commit()
                        logger.info(f"Email du partenaire {partner.name} mis à jour avec succès")
                    except Exception as e:
                        logger.warning(f"Impossible de mettre à jour l'email du partenaire: {str(e)}")
                else:
                    logger.error(f"Échec de l'envoi de l'email d'alerte au partenaire {partner.name}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'alerte par email: {str(e)}")
            # Ne pas faire échouer la création de l'incident si l'email échoue
    
    def update(self, incident_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Tuple[Optional[Incident], bool, str]:
        """
        Mettre à jour un incident

        Args:
            incident_id: ID du incident à mettre à jour
            data: Nouvelles données
            user_id: ID de l'utilisateur qui met à jour

        Returns:
            Tuple (incident, succès, message)
        """
        try:
            # Vérifier si le incident existe
            incidents, _ = self.model_class.get_by_criteria({'id': incident_id}, 0, 1)
            if not incidents:
                return None, False, f"{self.model_class.__name__} non trouvé"

            incident = incidents[0]

            # Traiter le user_name si fourni (au lieu de user_id)
            if 'user_name' in data and data['user_name']:
                from models import User
                users, _ = User.get_by_criteria({'name': data['user_name']}, 0, 1)
                if users:
                    data['user_id'] = users[0].id
                    logger.info(f"Utilisateur trouvé: {data['user_name']} (ID: {users[0].id})")
                else:
                    logger.warning(f"Utilisateur non trouvé: {data['user_name']}")
                    return None, False, f"Utilisateur non trouvé: {data['user_name']}"
                del data['user_name']

            # Traiter le project_name si fourni (au lieu de project_id)
            if 'project_name' in data and data['project_name']:
                from models import Project
                projects, _ = Project.get_by_criteria({'title': data['project_name']}, 0, 1)
                if projects:
                    data['project_id'] = projects[0].id
                    logger.info(f"Projet trouvé: {data['project_name']} (ID: {projects[0].id})")
                else:
                    logger.warning(f"Projet non trouvé: {data['project_name']}")
                    return None, False, f"Projet non trouvé: {data['project_name']}"
                del data['project_name']

            # Valider que l'utilisateur assigné existe (assigned_to)
            if 'assigned_to' in data and data['assigned_to']:
                from models import User
                assigned_user = User.query.filter_by(id=data['assigned_to'], is_deleted=False).first()
                if not assigned_user:
                    logger.warning(f"Utilisateur assigné non trouvé: ID={data['assigned_to']}")
                    return None, False, f"L'utilisateur avec l'ID {data['assigned_to']} n'existe pas. Veuillez vérifier l'ID de l'utilisateur à assigner."
                logger.info(f"Utilisateur assigné validé: {assigned_user.name} (ID: {assigned_user.id})")

            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)

            # Mettre à jour les champs d'audit
            update_audit_field(incident, user_id)

            db.session.commit()

            return incident, True, f"{self.model_class.__name__} mis à jour avec succès"

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur lors de la mise à jour: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la mise à jour de {self.model_class.__name__}: {str(e)}")
            return None, False, f"Erreur inattendue: {str(e)}"
    
    def delete(self, incident_id: int, user_id: Optional[int] = None, hard_delete: bool = False) -> Tuple[bool, str]:
        """
        Supprimer un incident (soft delete par défaut)
        
        Args:
            incident_id: ID du incident à supprimer
            user_id: ID de l'utilisateur qui supprime
            hard_delete: Si True, suppression définitive
            
        Returns:
            Tuple (succès, message)
        """
        try:
            # Vérifier si le incident existe
            incidents, _ = self.model_class.get_by_criteria({'id': incident_id}, 0, 1)
            if not incidents:
                return False, f"{self.model_class.__name__} non trouvé"
            
            incident = incidents[0]
            
            if hard_delete:
                # Suppression définitive
                db.session.delete(incident)
            else:
                # Soft delete
                if hasattr(incident, 'is_deleted'):
                    incident.is_deleted = True
                    update_audit_field(incident, user_id)
                else:
                    # Si pas de soft delete, faire une suppression définitive
                    db.session.delete(incident)
            
            db.session.commit()
            
            return True, f"{self.model_class.__name__} supprimé avec succès"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression de {self.model_class.__name__}: {str(e)}")
            return False, f"Erreur lors de la suppression: {str(e)}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inattendue lors de la suppression de {self.model_class.__name__}: {str(e)}")
            return False, f"Erreur inattendue: {str(e)}"
    
    # ===============================
    # MÉTHODES NOTIFICATIONS PUSH
    # ===============================
    
    def _get_push_service(self):
        """Lazy loading du service push pour éviter import circulaire"""
        if self._push_service is None:
            try:
                from services.push_notification_service import push_service
                self._push_service = push_service
            except ImportError as e:
                logger.warning(f"Service push non disponible: {e}")
                self._push_service = None
        return self._push_service
    
    def _send_push_notification_for_message(self, incident: Incident, priority: str, user_id: Optional[int] = None):
        """Envoyer notification push pour nouveau message urgent"""
        push_service = self._get_push_service()
        if not push_service:
            logger.warning("⚠️ Service push non disponible pour message")
            return
        
        # Déterminer le type d'utilisateur qui a envoyé le message
        try:
            from models.user import User
            if user_id:
                users, _ = User.get_by_criteria({'id': user_id}, 0, 1)
                is_admin = users[0].role_id == 1 if users else False
            else:
                is_admin = False
        except:
            is_admin = False
        
        if is_admin:
            # Admin envoie un message → Notifier les partenaires du projet
            emoji = "📢" if priority == 'critique' else "📝"
            title = f"{emoji} Message Admin"
            body = f"Message de l'administrateur: {incident.title}"
            
            data = {
                'incident_id': str(incident.id),
                'type': 'message',
                'priority': priority,
                'action': 'open_message'
            }
            
            success = push_service.send_to_partners(title, body, data, incident.project_id)
            if success:
                logger.info(f"✅ Notification push envoyée aux partenaires pour message admin {incident.id}")
            else:
                logger.warning(f"⚠️ Échec notification push aux partenaires pour message admin {incident.id}")
        else:
            # Partenaire envoie un message → Notifier les admins
            emoji = "🚨" if priority == 'critique' else "⚠️"
            title = f"{emoji} Message {priority.upper()}"
            body = f"Nouveau message: {incident.title}"
            
            data = {
                'incident_id': str(incident.id),
                'type': 'message',
                'priority': priority,
                'action': 'open_message'
            }
            
            success = push_service.send_to_admins(title, body, data)
            if success:
                logger.info(f"✅ Notification push envoyée aux admins pour message {incident.id}")
            else:
                logger.warning(f"⚠️ Échec notification push aux admins pour message {incident.id}")
    
    def _send_push_notification_for_support(self, incident: Incident, priority: str):
        """Envoyer notification push pour demande support urgente"""
        push_service = self._get_push_service()
        if not push_service:
            logger.warning("⚠️ Service push non disponible pour support")
            return
        
        emoji = "🚨" if priority == 'critique' else "⚠️"
        title = f"{emoji} Support {priority.upper()}"
        body = f"Demande de support: {incident.title}"
        
        data = {
            'incident_id': str(incident.id),
            'type': 'support',
            'priority': priority,
            'action': 'open_support'
        }
        
        success = push_service.send_to_admins(title, body, data)
        if success:
            logger.info(f"✅ Notification push envoyée pour support {incident.id}")
        else:
            logger.warning(f"⚠️ Échec notification push pour support {incident.id}")
    
    def getByCriteria(self, criteria: Dict[str, Any], index: int = 0, size: int = 10) -> Tuple[list, int]:
        """
        Récupérer des incidents selon des critères
        
        Args:
            criteria: Critères de recherche
            index: Index de pagination
            size: Taille de la page
            
        Returns:
            Tuple (liste des incidents, nombre total)
        """
        try:
            return self.model_class.get_by_criteria(criteria, index, size)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des {self.model_class.__name__}: {str(e)}")
            return [], 0
