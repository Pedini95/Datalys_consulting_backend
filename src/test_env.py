import os
from dotenv import load_dotenv

# Utiliser un chemin relatif pour charger .env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

# Vérification de l'existence du fichier .env
if not os.path.exists(env_path):
    print(f"❌ Fichier .env introuvable : {env_path}")
else:
    print(f"✅ Chargement du fichier .env depuis : {env_path}")

# Chargez le fichier .env
load_dotenv(env_path, override=True)

# Vérification directe de la variable LOG_FILE_PATH
log_file_path = os.getenv('LOG_FILE_PATH')
print("LOG_FILE_PATH via os.getenv :", log_file_path)

# Afficher toutes les variables d'environnement liées aux logs
for key, value in os.environ.items():
    if 'LOG_FILE_PATH' in key:
        print(f"{key}={value}")
