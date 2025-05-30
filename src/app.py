from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
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
print("is_dev:", is_dev)

# Configure logging handlers based on environment
handlers = [logging.StreamHandler()]  # Always include StreamHandler for console output

if is_dev:
    # Use TimedRotatingFileHandler in development
    handlers.append(
        TimedRotatingFileHandler(
            app.config['LOG_FILE_PATH'],
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
    )

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)

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
scheduler.add_job(seamfix_treatment.create_seamfix_treatment_job, 'interval', minutes=5, max_instances=1)
if not scheduler.running:
    scheduler.start()


