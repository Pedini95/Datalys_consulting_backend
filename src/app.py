# Force rebuild - $(date)
from flask import Flask
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask_restx import Api
from flask_cors import CORS
from extensions import db, migrate, mail
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
# Augmenter la limite pour permettre l'upload de fichiers plus volumineux
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB (augmenté de 16MB)

# Configuration du dossier d'upload
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './static/files')
api = Api(app, doc='/swagger/', title='Datalys Consulting API')

# Determine if in development environment
is_dev = app.config.get('ENV', 'local') == 'local'
logging.info(f"is_dev: {is_dev}")

# Dossier et fichier log
log_file_path = app.config['LOG_FILE_PATH']
# Utiliser un chemin relatif ou s'assurer que le dossier existe
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
# Corriger le chemin du fichier de log
log_file_path = os.path.join(log_dir, 'datalys_consulting.log')

# Format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler fichier (avec gestion d'erreur)
try:
    file_handler = TimedRotatingFileHandler(
        log_file_path, when='midnight', interval=1, backupCount=7, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logging.root.addHandler(file_handler)
except (PermissionError, OSError) as e:
    print(f" Impossible de créer le fichier de log: {e}")
    print(" Logs uniquement en console")

# Handler console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Nettoyage des handlers existants
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configuration du root logger
logging.root.setLevel(logging.INFO)
logging.root.addHandler(console_handler)

# Initialize extensions with the app
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Initialize Firebase/FCM Push Notification Service
try:
    from services.push_notification_service import create_push_service
    import services.push_notification_service as pns
    pns.push_service = create_push_service(app.config)
    logging.info(" Service de notifications push FCM initialisé")
except Exception as e:
    logging.error(f" Erreur initialisation service FCM: {e}")
    logging.warning("🔄 Mode dégradé: notifications push désactivées")

# Configuration CORS pour le frontend
CORS(app,
       origins=[
           # Développement
           "http://localhost:3000",
           "http://localhost:3001",

           # PRODUCTION - URL EXACTE
           "https://applicationweb.datalysconsulting.com",
       ],
       supports_credentials=True,
       methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
       allow_headers=[
           "Content-Type",
           "Authorization",
           "X-Requested-With",
           "Accept",
           "Origin"
       ]
  )

# Importer tous les modèles pour que SQLAlchemy les reconnaisse
from models import *



# Importer les routes ici pour éviter les imports circulaires
from routes import roles, users, partners, projects, incidents, folders, files, user_project_permissions, action_history, auth, health_check, session_routes, communication, fcm_routes, action_history_readonly, dashboard

# Enregistrer les blueprints
app.register_blueprint(roles.bp)
app.register_blueprint(users.bp)
app.register_blueprint(partners.bp)
app.register_blueprint(projects.bp)
app.register_blueprint(incidents.bp)
app.register_blueprint(folders.bp)
app.register_blueprint(files.bp)
app.register_blueprint(user_project_permissions.bp)
app.register_blueprint(action_history.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(health_check.health_bp)
app.register_blueprint(session_routes.session_bp)
app.register_blueprint(communication.bp)
app.register_blueprint(fcm_routes.bp)
app.register_blueprint(action_history_readonly.bp)
app.register_blueprint(dashboard.bp)

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=seamfix_treatment.create_seamfix_treatment_job, trigger="interval", seconds=120, id="create_seamfix_treatment_job", replace_existing=True)
# if not scheduler.running:
#     scheduler.start()


