import os
from dotenv import load_dotenv

# Charger le fichier .env.local seulement en développement
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env.local')

# Vérifier si on est en production (Kubernetes/Docker)
is_production = os.getenv('ENV') == 'production' or os.getenv('FLASK_ENV') == 'production'

if is_production:
    print("✅ Mode production: utilisation des variables d'environnement système")
    # En production, ne pas charger de fichier .env pour éviter les conflits
elif os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f"✅ Variables d'environnement chargées depuis: {env_path}")
else:
    print(f"⚠️  Fichier .env.local non trouvé: {env_path}")

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')
    SESSION_EXPIRE_MINUTES = 30
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # MySQL
    SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration Redis
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB')

    TIME_OUT = int(os.getenv('TIME_OUT', 30))

    ENV = os.getenv('ENV', 'local')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

    # LOG_FILE_PATH=os.getenv('LOG_FILE_PATH')
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/datalys_consulting.log")
    
    # Configuration des emails (SMTP Hostinger)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.hostinger.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@votredomaine.com')
    
    # Configuration Flask-Mail pour UTF-8
    MAIL_ASCII_ATTACHMENTS = False
    MAIL_SUPPRESS_SEND = False
    
    # Configuration email supplémentaire
    SENDER_NAME = os.getenv('SENDER_NAME', 'Datalys Consulting')
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    
    # Configuration Flask pour url_for
    SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:5000')
    APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')
    PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'http')


  