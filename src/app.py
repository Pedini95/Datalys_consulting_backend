from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flasgger import Swagger
from flask_cors import CORS

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
swagger = Swagger(app)

# Determine if in development environment
is_dev = app.config.get('ENV', 'local') == 'local'
logging.info("is_dev:", is_dev)

log_dir = "/app/logs"
log_file = os.path.join(log_dir, "com.fusion_kyc_kya.log")
# Création automatique du dossier si manquant
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# # Configure logging handlers based on environment
# handlers = [logging.StreamHandler()]

# handlers.append(
#     TimedRotatingFileHandler(
#         app.config['LOG_FILE_PATH'],
#         when='midnight',
#         interval=1,
#         backupCount=7,
#         encoding='utf-8'
#     )
# )

# # Set up logging configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=handlers
# )

# # Récupération du chemin du fichier log depuis .env
# log_file_path = app.config['LOG_FILE_PATH']
# log_dir = os.path.dirname(log_file_path)

# # Assurer l'existence du dossier
# os.makedirs(log_dir, exist_ok=True)

# # Handler fichier (rotation quotidienne)
# file_handler = TimedRotatingFileHandler(
#     log_file_path,
#     when='midnight',
#     interval=1,
#     backupCount=7,
#     encoding='utf-8'
# )
# file_handler.setLevel(logging.INFO)

# # Handler console
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)

# # Format des logs
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# # Configuration globale du logging
# logging.basicConfig(
#     level=logging.INFO,
#     handlers=[file_handler, console_handler]
# )

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Importer les routes ici pour éviter les imports circulaires
from routes import fonctionalite
from routes import kyc_api
from routes import role
from routes import user
from routes import timm_config
from routes import seamfix_api
from routes import seamfix_treatment

scheduler = BackgroundScheduler()
# scheduler.add_job(seamfix_treatment.create_seamfix_treatment_job, 'interval', minutes=5, max_instances=1)
if not scheduler.running:
    scheduler.start()


