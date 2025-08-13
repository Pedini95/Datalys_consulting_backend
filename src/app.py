from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configuration du dossier d'upload
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/var/www/html/uploads')
swagger = Swagger(app)

# Determine if in development environment
is_dev = app.config.get('ENV', 'local') == 'local'
logging.info(f"is_dev: {is_dev}")

# Dossier et fichier log
log_file_path = app.config['LOG_FILE_PATH']
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

# Format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Handler fichier
file_handler = TimedRotatingFileHandler(
    log_file_path, when='midnight', interval=1, backupCount=7, encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Handler console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Nettoyage des handlers existants
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configuration du root logger
logging.root.setLevel(logging.INFO)
logging.root.addHandler(file_handler)
logging.root.addHandler(console_handler)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
CORS(app)

# Importer tous les modèles pour que SQLAlchemy les reconnaisse
from models import *



# Importer les routes ici pour éviter les imports circulaires
from routes import roles, users, partners, projects, incidents, folders, files, user_project_permissions, action_history, auth, health_check, session_routes

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

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=seamfix_treatment.create_seamfix_treatment_job, trigger="interval", seconds=120, id="create_seamfix_treatment_job", replace_existing=True)
# if not scheduler.running:
#     scheduler.start()


