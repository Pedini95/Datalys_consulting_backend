from flask import Blueprint, request, send_file
from services import IncidentService
import logging
from utils import functional_error, utilities
from flask_cors import cross_origin
from .auth import require_auth
from middleware.role_security import require_role
import io
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Créer le blueprint
bp = Blueprint('incidents', __name__)



incident_service = IncidentService()

@bp.route('/incidents/getByCriteria', methods=['POST'])
@cross_origin()
@require_auth
def get_incidents():
    logging.info("**** Begin get_incidents ****")
    logging.info("/incidents/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index', 0)
    size = r.get('size', 10)
    criteria = r.get('data', {})
    
    incidents, total_items = incident_service.model_class.get_by_criteria(criteria, index, size)
    if incidents:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    
    response = {"items": [incident.as_dict() for incident in incidents], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_incidents ****")
    return response

@bp.route('/incidents/create', methods=['POST'])
@cross_origin()
@require_auth
def create_incidents():
    logging.info("**** Begin create_incidents ****")
    logging.info("/incidents/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['title']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {
            'title': data.get('title'),
            'description': data.get('description'),
            'is_active': data.get('is_active', True)
        }
        
        # Ajouter les nouveaux champs pour la communication
        if 'type' in data and data['type']:
            processed_data['type'] = data.get('type')
        if 'priority' in data and data['priority']:
            processed_data['priority'] = data.get('priority')
        if 'status' in data and data['status']:
            processed_data['status'] = data.get('status')
        if 'category' in data and data['category']:
            processed_data['category'] = data.get('category')
        if 'assigned_to' in data and data['assigned_to']:
            processed_data['assigned_to'] = data.get('assigned_to')
        if 'parent_id' in data and data['parent_id']:
            processed_data['parent_id'] = data.get('parent_id')
        if 'resolution_notes' in data and data['resolution_notes']:
            processed_data['resolution_notes'] = data.get('resolution_notes')
        if 'is_read' in data:
            processed_data['is_read'] = data.get('is_read')
        
        # ✅ NOUVEAUX CHAMPS P0-P4
        if 'impact' in data and data['impact']:
            processed_data['impact'] = data.get('impact')
        if 'domain' in data and data['domain']:
            processed_data['domain'] = data.get('domain')
        if 'declarant_name' in data and data['declarant_name']:
            processed_data['declarant_name'] = data.get('declarant_name')
        if 'motif_attente' in data and data['motif_attente']:
            processed_data['motif_attente'] = data.get('motif_attente')
        
        # Ajouter user_name si fourni (au lieu de user_id)
        if 'user_name' in data and data['user_name']:
            processed_data['user_name'] = data.get('user_name')
        elif 'user_id' in data and data['user_id']:
            processed_data['user_id'] = data.get('user_id')
        
        # Ajouter project_name si fourni (au lieu de project_id)
        if 'project_name' in data and data['project_name']:
            processed_data['project_name'] = data.get('project_name')
        elif 'project_id' in data and data['project_id']:
            processed_data['project_id'] = data.get('project_id')
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = incident_service.create(data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if success and items:
        response = {"items": [incident.as_dict() for incident in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucun incident créé"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_incidents ****")
    return response

@bp.route('/incidents/update', methods=['POST'])
@cross_origin()
@require_auth
def update_incidents():
    logging.info("**** Begin update_incidents ****")
    logging.info("/incidents/update")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    user = r.get('user', {})
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        # Champs obligatoires
        required_fields = ['id']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
        
        processed_data = {'id': data.get('id')}
        
        if utilities.not_blank(data.get('title')):
            processed_data['title'] = data.get('title')
        if utilities.not_blank(data.get('description')):
            processed_data['description'] = data.get('description')
        
        # Ajouter les nouveaux champs pour la communication
        if 'type' in data and data['type']:
            processed_data['type'] = data.get('type')
        if 'priority' in data and data['priority']:
            processed_data['priority'] = data.get('priority')
        if 'status' in data and data['status']:
            processed_data['status'] = data.get('status')
        if 'category' in data and data['category']:
            processed_data['category'] = data.get('category')
        if 'assigned_to' in data and data['assigned_to']:
            processed_data['assigned_to'] = data.get('assigned_to')
        if 'parent_id' in data and data['parent_id']:
            processed_data['parent_id'] = data.get('parent_id')
        if 'resolution_notes' in data and data['resolution_notes']:
            processed_data['resolution_notes'] = data.get('resolution_notes')
        if 'is_read' in data:
            processed_data['is_read'] = data.get('is_read')
        
        # ✅ NOUVEAUX CHAMPS P0-P4
        if 'impact' in data and data['impact']:
            processed_data['impact'] = data.get('impact')
        if 'domain' in data and data['domain']:
            processed_data['domain'] = data.get('domain')
        if 'declarant_name' in data and data['declarant_name']:
            processed_data['declarant_name'] = data.get('declarant_name')
        if 'motif_attente' in data and data['motif_attente']:
            processed_data['motif_attente'] = data.get('motif_attente')
        
        # Ajouter user_name si fourni (au lieu de user_id)
        if 'user_name' in data and data['user_name']:
            processed_data['user_name'] = data.get('user_name')
        elif 'user_id' in data and data['user_id']:
            processed_data['user_id'] = data.get('user_id')
        
        # Ajouter project_name si fourni (au lieu de project_id)
        if 'project_name' in data and data['project_name']:
            processed_data['project_name'] = data.get('project_name')
        elif 'project_id' in data and data['project_id']:
            processed_data['project_id'] = data.get('project_id')
        
        if 'is_active' in data:
            processed_data['is_active'] = data.get('is_active')
        
        processed_datas.append(processed_data)
    
    items = []
    success = True
    message = ""
    
    for data in processed_datas:
        item, success, message = incident_service.update(data['id'], data, user.get('id'))
        if not success:
            return {"status": "error", "message": message}, 400
        items.append(item)
    
    if success and items:
        response = {"items": [incident.as_dict() for incident in items], "message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    else:
        response = {"status": "error", "message": message or "Aucun incident mis à jour"}, 400
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_incidents ****")
    return response

@bp.route('/incidents/delete', methods=['POST'])
@cross_origin()
@require_auth
@require_role(['admin', 'manager'])  # Seuls admins et managers peuvent supprimer
def delete_incidents():
    logging.info("**** Begin delete_incidents ****")
    logging.info("/incidents/delete")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    
    datas = r.get('datas', [])
    
    # Préparer les données pour le service
    processed_datas = []
    for data in datas:
        if 'id' not in data:
            return {"status": "error", "message": "Field id is missing"}, 400
        processed_datas.append({'id': data.get('id')})
    
    for data in processed_datas:
        success, message = incident_service.delete(data['id'])
        if not success:
            return {"status": "error", "message": message}, 400
    
    response = {"message": functional_error.MESSAGE_SUCCESS(), "code": 200}
    
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_incidents ****")
    return response

# ✅ NOUVELLE ROUTE : Obtenir les métadonnées des incidents (P0-P4, domaines, etc.)
@bp.route('/incidents/metadata', methods=['GET'])
@cross_origin()
@require_auth
def get_incidents_metadata():
    """
    Retourne les métadonnées pour les incidents :
    - Priorités valides (P0-P4)
    - Statuts valides
    - Impacts valides
    - Domaines valides
    - Mapping impact → priorité recommandée
    """
    logging.info("**** Begin get_incidents_metadata ****")
    
    from models.incident import Incident
    
    metadata = {
        "priorities": [
            {"value": "P0", "label": "Arrêt de service (immédiat)", "color": "red"},
            {"value": "P1", "label": "Forte dégradation de service", "color": "orange"},
            {"value": "P2", "label": "Dégradation de service", "color": "yellow"},
            {"value": "P3", "label": "Incident ordinaire", "color": "blue"},
            {"value": "P4", "label": "Incident mineur", "color": "green"}
        ],
        "statuses": [
            {"value": "nouveau", "label": "Nouveau", "color": "blue"},
            {"value": "en_cours", "label": "En cours", "color": "orange"},
            {"value": "en_attente", "label": "En attente", "color": "gray"},
            {"value": "en_arbitrage", "label": "En arbitrage", "color": "purple"},
            {"value": "resolu", "label": "Résolu", "color": "green"},
            {"value": "ferme", "label": "Fermé", "color": "black"}
        ],
        "impacts": [
            {"value": "arret_service", "label": "Arrêt de service", "recommended_priority": "P0"},
            {"value": "service_degrade", "label": "Service dégradé", "recommended_priority": "P1"},
            {"value": "majeur", "label": "Impact majeur", "recommended_priority": "P2"},
            {"value": "mineur", "label": "Impact mineur", "recommended_priority": "P3"}
        ],
        "domains": [
            {"value": "reseau", "label": "Réseau"},
            {"value": "infrastructure", "label": "Infrastructure système"},
            {"value": "cloud", "label": "Cloud"},
            {"value": "energie", "label": "Énergie"}
        ],
        "priority_mapping": Incident.get_priority_mapping()
    }
    
    response = {
        "code": 200,
        "message": functional_error.MESSAGE_SUCCESS(),
        "data": metadata
    }

    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_incidents_metadata ****")
    return response


# ✅ NOUVELLE ROUTE : Refuser une solution et réouvrir l'incident
@bp.route('/incidents/<int:incident_id>/refuse-solution', methods=['POST'])
@cross_origin()
@require_auth
def refuse_solution(incident_id):
    """
    Permet au client de refuser la solution proposée et réouvrir l'incident.

    Workflow:
    1. Client refuse la solution proposée (incident doit être 'resolu')
    2. Incident passe de 'resolu' → 'en_cours'
    3. Incrémentation de refusal_count
    4. Enregistrement de refusal_reason
    5. Mise à jour de last_refusal_at
    6. Notification automatique à l'expert assigné
    7. Ajout d'un message dans le fil de discussion

    Body:
    {
        "user": {"id": 123, "email": "...", "name": "..."},
        "refusal_reason": "La solution proposée ne résout pas complètement le problème..."
    }
    """
    logging.info("**** Begin refuse_solution ****")
    logging.info(f"/incidents/{incident_id}/refuse-solution")

    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)

    user = r.get('user', {})
    refusal_reason = r.get('refusal_reason', '').strip()

    # Validation : raison de refus obligatoire
    if not refusal_reason:
        return {
            "status": "error",
            "message": "La raison du refus est obligatoire",
            "code": 400
        }, 400

    from models.incident import Incident
    from models.user import User
    from extensions import db
    from datetime import datetime

    # 1. Vérifier que l'incident existe
    incident = Incident.query.filter_by(id=incident_id, is_deleted=False).first()
    if not incident:
        return {
            "status": "error",
            "message": "Incident non trouvé",
            "code": 404
        }, 404

    # 2. Vérifier que l'incident est résolu (status = 'resolu')
    if incident.status != 'resolu':
        return {
            "status": "error",
            "message": f"Vous ne pouvez refuser la solution que pour un incident résolu. Statut actuel : {incident.status}",
            "code": 400
        }, 400

    # 3. Vérifier que l'utilisateur est bien le créateur de l'incident
    if incident.user_id != user.get('id'):
        return {
            "status": "error",
            "message": "Vous n'êtes pas autorisé à refuser cette solution. Seul le créateur de l'incident peut effectuer cette action.",
            "code": 403
        }, 403

    # 4. Mettre à jour l'incident
    incident.status = 'en_cours'
    incident.refusal_count = (incident.refusal_count or 0) + 1
    incident.refusal_reason = refusal_reason
    incident.last_refusal_at = datetime.utcnow()
    incident.resolved_at = None  # Réinitialiser la date de résolution
    incident.updated_at = datetime.utcnow()
    incident.updated_by = user.get('id')

    try:
        db.session.commit()
        logging.info(f"Incident {incident.incident_number} réouvert après refus de solution (refus #{incident.refusal_count})")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erreur lors de la mise à jour de l'incident : {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors du refus de la solution : {str(e)}",
            "code": 500
        }, 500

    # 5. Envoyer une notification à l'expert assigné (si existant)
    if incident.assigned_to:
        try:
            expert = User.query.filter_by(id=incident.assigned_to).first()
            if expert and expert.email:
                from flask_mail import Message
                from extensions import mail
                import os

                app_url = os.getenv('APP_URL', 'https://datalysconsulting.com')
                sender_name = os.getenv('SENDER_NAME', 'Datalys Consulting')

                msg = Message(
                    subject=f"[REFUS] Solution refusée pour {incident.incident_number}",
                    recipients=[expert.email],
                    sender=(sender_name, os.getenv('MAIL_DEFAULT_SENDER'))
                )

                msg.html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                        <h2 style="color: #d9534f;">Solution refusée pour l'incident {incident.incident_number}</h2>

                        <p>Bonjour {expert.name or 'Expert'},</p>

                        <p>Le client <strong>{user.get('name', 'Inconnu')}</strong> a refusé la solution proposée pour l'incident suivant :</p>

                        <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #d9534f; margin: 20px 0;">
                            <p><strong>Incident :</strong> {incident.incident_number}</p>
                            <p><strong>Titre :</strong> {incident.title}</p>
                            <p><strong>Priorité :</strong> {incident.priority}</p>
                            <p><strong>Nombre de refus :</strong> {incident.refusal_count}</p>
                        </div>

                        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                            <p><strong>Raison du refus :</strong></p>
                            <p style="font-style: italic;">{refusal_reason}</p>
                        </div>

                        <p>L'incident a été réouvert et nécessite une nouvelle intervention de votre part.</p>

                        <p style="margin-top: 30px;">
                            <a href="{app_url}/incidents/{incident.id}"
                               style="background-color: #0275d8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Voir l'incident
                            </a>
                        </p>

                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                        <p style="font-size: 12px; color: #777;">
                            Cet email a été envoyé automatiquement par {sender_name}. Merci de ne pas y répondre.
                        </p>
                    </div>
                </body>
                </html>
                """

                mail.send(msg)
                logging.info(f"Email de notification envoyé à {expert.email}")
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'email à l'expert : {str(e)}")
            # Ne pas bloquer la réponse si l'email échoue

    # 6. Ajouter un message automatique dans le fil de discussion
    try:
        # Créer un message incident de type "refus de solution"
        refusal_message = Incident(
            title=f"Solution refusée (#{incident.refusal_count})",
            description=f"**Raison du refus :**\n\n{refusal_reason}",
            type='message',
            status='nouveau',
            priority=incident.priority,
            user_id=user.get('id'),
            project_id=incident.project_id,
            assigned_to=incident.assigned_to,
            parent_id=incident.id,  # Lier au incident parent
            is_active=True,
            is_deleted=False,
            created_at=datetime.utcnow(),
            created_by=user.get('id')
        )

        # Générer un numéro pour ce message
        refusal_message.incident_number = Incident.generate_incident_number()

        db.session.add(refusal_message)
        db.session.commit()
        logging.info(f"Message de refus créé : {refusal_message.incident_number}")
    except Exception as e:
        logging.error(f"Erreur lors de la création du message de refus : {str(e)}")
        # Ne pas bloquer la réponse si le message échoue

    # 7. Retourner la réponse avec l'incident mis à jour
    response = {
        "code": 200,
        "message": "Solution refusée avec succès. L'incident a été réouvert.",
        "data": {
            "incident": incident.as_dict(),
            "refusal_count": incident.refusal_count,
            "status": incident.status
        }
    }

    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End refuse_solution ****")
    return response


# ✅ NOUVELLE ROUTE : Exporter les incidents (PDF, Excel, CSV)
@bp.route('/incidents/export', methods=['POST'])
@cross_origin()
@require_auth
@require_role(['admin', 'manager'])  # Réservé aux admins et managers
def export_incidents():
    """
    Exporter les incidents dans différents formats (PDF, Excel, CSV)

    Réservé aux administrateurs et managers.

    Body:
    {
        "user": {"id": 1, "email": "admin@datalys.com"},
        "format": "pdf|excel|csv",
        "criteria": {
            "status": "en_cours",
            "priority": "P1",
            ...
        },
        "date_from": "2025-01-01",  # Optionnel
        "date_to": "2025-12-31",    # Optionnel
        "include_stats": true        # Optionnel (défaut: false)
    }

    Returns:
        Fichier téléchargeable (PDF/Excel/CSV)
    """
    logging.info("**** Begin export_incidents ****")
    logging.info("/incidents/export")

    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)

    # Paramètres
    export_format = r.get('format', 'csv').lower()
    criteria = r.get('criteria', {})
    date_from = r.get('date_from')
    date_to = r.get('date_to')
    include_stats = r.get('include_stats', False)

    # Validation du format
    if export_format not in ['pdf', 'excel', 'csv']:
        return {
            "status": "error",
            "message": "Format invalide. Formats acceptés : pdf, excel, csv",
            "code": 400
        }, 400

    from models.incident import Incident
    from datetime import datetime as dt

    # Ajouter les filtres de date si fournis
    if date_from:
        try:
            date_from_obj = dt.strptime(date_from, '%Y-%m-%d')
            criteria['created_at_from'] = date_from_obj
        except ValueError:
            return {
                "status": "error",
                "message": "Format de date invalide pour date_from. Format attendu : YYYY-MM-DD",
                "code": 400
            }, 400

    if date_to:
        try:
            date_to_obj = dt.strptime(date_to, '%Y-%m-%d')
            criteria['created_at_to'] = date_to_obj
        except ValueError:
            return {
                "status": "error",
                "message": "Format de date invalide pour date_to. Format attendu : YYYY-MM-DD",
                "code": 400
            }, 400

    # Récupérer les incidents selon les critères (max 10000 pour éviter les surcharges)
    try:
        incidents, total_items = Incident.get_by_criteria(criteria, 0, 10000)

        if not incidents:
            return {
                "status": "error",
                "message": "Aucun incident trouvé pour les critères spécifiés",
                "code": 404
            }, 404

        logging.info(f"Export de {len(incidents)} incidents au format {export_format}")

        # Générer le rapport selon le format
        from utils.report_generator import ReportGenerator
        generator = ReportGenerator()

        if export_format == 'csv':
            content = generator.generate_csv(incidents, include_stats)
            mimetype = 'text/csv'
            filename = f'incidents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            file_data = io.BytesIO(content.encode('utf-8'))

        elif export_format == 'excel':
            content = generator.generate_excel(incidents, include_stats)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'incidents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            file_data = io.BytesIO(content)

        elif export_format == 'pdf':
            content = generator.generate_pdf(incidents, include_stats)
            mimetype = 'application/pdf'
            filename = f'incidents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            file_data = io.BytesIO(content)

        file_data.seek(0)

        logging.info(f"Rapport généré avec succès : {filename}")
        logging.info("**** End export_incidents ****")

        return send_file(
            file_data,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logging.error(f"Erreur lors de l'export des incidents : {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la génération du rapport : {str(e)}",
            "code": 500
        }, 500 