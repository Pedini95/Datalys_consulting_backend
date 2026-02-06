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
from services.auth_service import AuthService
from queue import Queue
from threading import Lock

logger = logging.getLogger(__name__)

bp = Blueprint('sse', __name__)

# Stockage des connexions SSE actives par utilisateur
# Structure: {user_id: [queue1, queue2, ...]}
active_connections = {}
connections_lock = Lock()

auth_service = AuthService()


def validate_token_from_query():
    """
    Valider le token depuis les query parameters
    Utilisé pour SSE car EventSource ne supporte pas les headers personnalisés

    Returns:
        Tuple (user, success, error_message)
    """
    token = request.args.get('token')

    if not token:
        return None, False, "Token manquant. Utilisez ?token=<votre_token>"

    # Valider le token
    user, success, message = auth_service.get_current_user(token)

    if not success:
        return None, False, message

    return user, True, None


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
def event_stream():
    """
    Endpoint SSE pour recevoir les notifications en temps réel

    Le client se connecte via:
    GET /events/stream?token=<JWT_TOKEN>

    Le token est passé en query parameter car EventSource ne supporte pas
    les headers personnalisés.

    Événements envoyés:
    - 'connected': Confirmation de connexion
    - 'initial_notifications': Notifications non lues existantes
    - 'new_message': Nouveau message reçu
    - 'new_notification': Nouvelle notification
    - 'message_deleted': Un message a été supprimé
    - 'heartbeat': Ping toutes les 30 secondes pour garder la connexion active
    - 'error': Erreur d'authentification
    """
    # Valider le token depuis les query params
    user, success, error_message = validate_token_from_query()

    if not success:
        # Retourner une erreur SSE au lieu d'un JSON
        def error_generator():
            yield format_sse('error', {
                'message': error_message,
                'code': 401
            })

        return Response(
            error_generator(),
            mimetype='text/event-stream',
            status=401,
            headers={
                'Cache-Control': 'no-cache',
                'Access-Control-Allow-Origin': '*'
            }
        )

    user_id = user.id
    user_queue = Queue()

    def generate():
        add_connection(user_id, user_queue)

        try:
            # Envoyer confirmation de connexion
            yield format_sse('connected', {
                'user_id': user_id,
                'user_name': user.name,
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
            else:
                yield format_sse('initial_notifications', {
                    'count': 0,
                    'items': []
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


@bp.route('/events/status', methods=['GET'])
@cross_origin()
@require_auth
def sse_status():
    """
    Vérifier le statut des connexions SSE
    Retourne le nombre de connexions actives
    """
    with connections_lock:
        total_connections = sum(len(queues) for queues in active_connections.values())
        user_count = len(active_connections)

    return {
        'code': 200,
        'data': {
            'total_connections': total_connections,
            'connected_users': user_count,
            'current_user_connected': g.current_user.id in active_connections
        }
    }
