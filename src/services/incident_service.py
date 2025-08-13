from models import Incident
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from app import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IncidentService:
    """
    Service pour la gestion des incidents
    """
    
    def __init__(self):
        self.model_class = Incident
    
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
            if user_id:
                data['created_by'] = user_id
                data['updated_by'] = user_id
            
            incident = self.model_class(**data)
            db.session.add(incident)
            db.session.flush()  # Pour obtenir l'ID de l'incident
            
            # Envoyer des alertes par email si l'incident est lié à un projet
            if incident.project_id:
                self._send_incident_alerts(incident, user_id)
            
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
    
    def _send_incident_alerts(self, incident: Incident, user_id: Optional[int] = None):
        """
        Envoyer des alertes par email pour un incident
        
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
            
            # Mettre à jour les champs
            for key, value in data.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)
            
            # Mettre à jour les champs d'audit
            if user_id and hasattr(incident, 'updated_by'):
                incident.updated_by = user_id
            
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
                    if user_id and hasattr(incident, 'updated_by'):
                        incident.updated_by = user_id
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
