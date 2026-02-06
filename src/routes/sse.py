"""
Server-Sent Events (SSE) pour les notifications en temps réel
"""
from flask import Blueprint, Response, g, request
from flask_cors import cross_origin
import json
import time
import logging
from .auth import require_auth
from services.incident_service import IncidentService
from queue import Queue
from threading import Lock

logger = logging.getLogger(__name__)

bp = Blueprint('sse', __name__)

# Stockage des connexions SSE actives par utilisateur
# Structure: {user_id: [queue1, queue2, ...]}
active_connections = {}
connections_lock = Lock()

def add_connection(user_id: int, queue: Queue):
    """Ajouter une connexion SSE pour un utilisateur"""
    with connections_lock:
        if user_id not in active_connections:
            active_connections[user_id] = []
        active_connections[user_id].append(queue)
        logger.info(f"SSE: Connexion ajoutée pour user {user_id}. Total: {len(active_connections[user_id])}")

def remove_connection(user_id: int, queue: Queue):
    """Retirer une connexion SSE"""
    with connections_lock:
        if user_id in active_connections:
            try:
                active_connections[user_id].remove(queue)
                logger.info(f"SSE: Connexion retirée pour user {user_id}. Restant: {len(active_connections[user_id])}")
                if not active_connections[user_id]:
                    del active_connections[user_id]
            except ValueError:
                pass

def notify_user(user_id: int, event_type: str, data: dict):
    """
    Envoyer une notification à un utilisateur spécifique
    Appelée depuis d'autres parties du code quand un événement se produit
    """
    with connections_lock:
        if user_id in active_connections:
            message = format_sse(event_type, data)
            for queue in active_connections[user_id]:
                try:
                    queue.put_nowait(message)
                except:
                    pass
            logger.info(f"SSE: Notification '{event_type}' envoyée à user {user_id}")
            return True
    return False

def notify_admins(event_type: str, data: dict):
    """Envoyer une notification à tous les admins connectés"""
    from models import User, Role

    # Récupérer les IDs des admins
    admins = User.query.join(Role).filter(
        Role.name.in_(['Admin', 'Manager']),
        User.is_active == True
    ).all()

    count = 0
    for admin in admins:
        if notify_user(admin.id, event_type, data):
            count += 1

    logger.info(f"SSE: Notification '{event_type}' envoyée à {count} admins")
    return count

def format_sse(event: str, data: dict) -> str:
    """Formater un message SSE"""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@bp.route('/events/stream', methods=['GET'])
@cross_origin(supports_credentials=True)
@require_auth
def event_stream():
    """
    Endpoint SSE pour recevoir les notifications en temps réel

    Le client se connecte et reste connecté. Le serveur envoie des événements
    quand il y a des notifications.

    Événements envoyés:
    - 'connected': Confirmation de connexion
    - 'new_message': Nouveau message reçu
    - 'new_notification': Nouvelle notification
    - 'message_deleted': Un message a été supprimé
    - 'heartbeat': Ping toutes les 30 secondes pour garder la connexion active
    """
    user_id = g.current_user.id
    user_queue = Queue()

    def generate():
        add_connection(user_id, user_queue)

        try:
            # Envoyer confirmation de connexion
            yield format_sse('connected', {
                'user_id': user_id,
                'message': 'Connexion SSE établie'
            })

            # Envoyer les notifications non lues existantes
            incident_service = IncidentService()
            notifications, count = incident_service.get_unread_notifications(user_id, 0, 50)
            if notifications:
                yield format_sse('initial_notifications', {
                    'count': count,
                    'items': [n.as_dict() for n in notifications]
                })

            last_heartbeat = time.time()

            while True:
                # Vérifier s'il y a des messages dans la queue
                try:
                    # Attendre un message pendant 1 seconde max
                    message = user_queue.get(timeout=1)
                    yield message
                except:
                    pass

                # Envoyer un heartbeat toutes les 30 secondes
                if time.time() - last_heartbeat > 30:
                    yield format_sse('heartbeat', {'timestamp': int(time.time())})
                    last_heartbeat = time.time()

        except GeneratorExit:
            logger.info(f"SSE: Client {user_id} déconnecté")
        finally:
            remove_connection(user_id, user_queue)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Désactiver le buffering nginx
            'Access-Control-Allow-Origin': '*'
        }
    )


@bp.route('/events/test', methods=['POST'])
@cross_origin()
@require_auth
def test_notification():
    """
    Endpoint de test pour envoyer une notification à soi-même
    Utile pour tester que SSE fonctionne
    """
    user_id = g.current_user.id

    success = notify_user(user_id, 'test', {
        'message': 'Ceci est une notification de test',
        'timestamp': int(time.time())
    })

    return {
        'code': 200,
        'message': 'Notification de test envoyée' if success else 'Aucune connexion SSE active',
        'sse_connected': success
    }
