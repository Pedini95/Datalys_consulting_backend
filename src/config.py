import os
from dotenv import load_dotenv

# Charger le fichier .env.local seulement en développement
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env.local')

# Vérifier si on est en production (Kubernetes/Docker)
is_production = os.getenv('ENV') == 'production' or os.getenv('FLASK_ENV') == 'production'

if is_production:
    print(" Mode production: utilisation des variables d'environnement système")
    # En production, ne pas charger de fichier .env pour éviter les conflits
elif os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f" Variables d'environnement chargées depuis: {env_path}")
else:
    print(f"  Fichier .env.local non trouvé: {env_path}")

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

    TIME_OUT = int(os.getenv('TIME_OUT', 60))  # Augmenté de 30 à 60 secondes
    
    # Timeouts spécifiques pour les connexions
    DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', 30))
    DB_READ_TIMEOUT = int(os.getenv('DB_READ_TIMEOUT', 60))
    REDIS_CONNECT_TIMEOUT = int(os.getenv('REDIS_CONNECT_TIMEOUT', 30))
    REDIS_READ_TIMEOUT = int(os.getenv('REDIS_READ_TIMEOUT', 60))
    
    # Configuration pour les requêtes HTTP
    HTTP_TIMEOUT = int(os.getenv('HTTP_TIMEOUT', 30))
    HTTP_CONNECT_TIMEOUT = int(os.getenv('HTTP_CONNECT_TIMEOUT', 10))

    ENV = os.getenv('ENV', 'local')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

    # LOG_FILE_PATH=os.getenv('LOG_FILE_PATH')
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/datalys_consulting.log")
    
    # Configuration des emails (SMTP Hostinger - TLS sur port 587)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.hostinger.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))  # Port TLS au lieu de 465 SSL
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'  # SSL désactivé par défaut
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'  # TLS activé par défaut
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'appweb@datalysconsulting.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'appweb@datalysconsulting.com')
    
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
    
    # Configuration Firebase Cloud Messaging (FCM)
    # Le fichier firebase-service-account.json doit être présent dans src/config/
    FIREBASE_ENABLED = os.getenv('FIREBASE_ENABLED', 'True').lower() == 'true'
    FIREBASE_CONFIG_PATH = os.path.join(current_dir, 'config', 'firebase-service-account.json')
    
    # Configuration pour les notifications push automatiques
    FCM_AUTO_NOTIFY_HIGH_PRIORITY = os.getenv('FCM_AUTO_NOTIFY_HIGH_PRIORITY', 'True').lower() == 'true'
    FCM_AUTO_NOTIFY_CRITICAL_PRIORITY = os.getenv('FCM_AUTO_NOTIFY_CRITICAL_PRIORITY', 'True').lower() == 'true'


  