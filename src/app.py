from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
swagger = Swagger(app)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler(
            app.config['LOG_FILE_PATH'], 
            when='midnight', 
            interval=1, 
            backupCount=7, 
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
# handler = logging.getLogger().handlers[0]
# if isinstance(handler, TimedRotatingFileHandler):
#     handler.doRollover()

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Importer les routes ici pour éviter les imports circulaires
from routes import fonctionalite
from routes import kyc_api