import os
import secrets
from dotenv import load_dotenv


# Utiliser un chemin relatif pour charger .env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
# Chargez le fichier .env
load_dotenv(env_path, override=True)

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')
    SESSION_EXPIRE_MINUTES = 30
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Configuration de la base de données
    # Mysql
    # SQLALCHEMY_DATABASE_URI = (f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = (f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration Redis
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB')

    ENV = os.getenv('ENV', 'local')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

    LOG_FILE_PATH=os.getenv('LOG_FILE_PATH')
    
    # Configuration des emails 
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')


    # Configuration Seamfix
    SEAMFIX_PUBLIC_KEY = os.getenv('SEAMFIX_PUBLIC_KEY')
    SEAMFIX_PRIVATE_KEY = os.getenv('SEAMFIX_PRIVATE_KEY')
    SEAMFIX_USER_ID = os.getenv('SEAMFIX_USER_ID')
    SEAMFIX_URL = os.getenv('SEAMFIX_URL')
    SEAMFIX_URL_VERIFY = os.getenv('SEAMFIX_URL_VERIFY')
    SEAMFIX_URL_VALIDATE = os.getenv('SEAMFIX_URL_VALIDATE')
    SEAMFIX_OCR_URL = os.getenv('SEAMFIX_OCR_URL')

    # Configuration TIMM
    TIMM_URL_AUTH = os.getenv('TIMM_URL_AUTH')
