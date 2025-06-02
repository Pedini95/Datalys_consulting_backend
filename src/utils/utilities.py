from typing import Dict
from app import app, db
import random
import re
import hashlib
from datetime import datetime, date
import unicodedata
import base64
from PIL import Image
from io import BytesIO
import os
import shutil
import string
import json
from werkzeug.utils import secure_filename
from flask import request, jsonify
import utils.functional_error as functional_error
from models.timm_config import TimmConfig

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from models.user import User
from Crypto.Cipher import AES
from Cryptodome.Cipher import AES

import requests
from requests.exceptions import RequestException, ConnectionError, Timeout, SSLError
import socket

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')

def check_password_requirements(password: str, data: Dict) -> bool:
    """
        1. Must be at least eight (8) characters in length
        2. Must not include any of the user names (First, Last and Middle)
        3. Must include at least one of these symbols (@#$&()*)
        4. Must include at least one lowercase character
        5. Must include at least one upper-case character
        6. Must include at least one numeric character
    """
    if len(password) < 8:
        return False
    if data['first_name'] in password:
        return False
    if data['last_name'] in password:
        return False
    if not any(symbol in password for symbol in ['@', '#', '$', '&', '(', ')', '*']):
        return False
    if not any(ch in password for ch in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']):
        return False
    if not any(ch in password for ch in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']):
        return False
    if not any(ch in password for ch in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
        return False
    return True

def generate_code():
    secure_random = random.SystemRandom()  # Utilisation de SystemRandom pour plus de sécurité
    num = secure_random.randint(0, 99999999)  # Générer un nombre entre 0 et 99999999
    formatted = "{:05d}".format(num)  # Formater le nombre avec 5 chiffres, complétés par des zéros
    return formatted

def is_true(b):
    return b is not None and b

def is_false(b):
    return not is_true(b)

def is_numeric(string):
    try:
        float(string)  # Utilisation de float pour gérer les nombres entiers et flottants
        return True
    except ValueError:
        return False

def is_string(i):
    try:
        int(str(i))
        return False
    except ValueError:
        return True
    
def is_valid_email(email):
    regex = r'^(.+)@(.+)$'
    pattern = re.compile(regex)
    matcher = pattern.match(email)
    return matcher is not None

def convert_byte_array_to_hex_string(byte_array):
    return ''.join(['{:02x}'.format(byte) for byte in byte_array])

def encrypt(string):
    sha1 = hashlib.sha1()
    sha1.update(string.encode('utf-8'))
    hashed_bytes = sha1.digest()
    return convert_byte_array_to_hex_string(hashed_bytes)

def is_date_valid(date):
    try:
        if '-' in date:
            simple_date_format = '%d-%m-%Y'
        elif '/' in date:
            simple_date_format = '%d/%m/%Y'
        else:
            return False

        datetime.strptime(date, simple_date_format)
        return True
    except ValueError:
        return False
    
def get_age(date_naissance):
    if date_naissance is None:
        return 0

    today = date.today()
    age = today.year - date_naissance.year

    if today < date_naissance.replace(year=today.year):
        age -= 1

    return age

def normalize_file_name(file_name):
    # Trim whitespace
    file_normalize = file_name.strip()
    # Replace whitespace with underscore
    file_normalize = re.sub(r'\s+', '_', file_normalize)
    # Remove apostrophes
    file_normalize = file_normalize.replace("'", "")
    # Normalize unicode characters
    file_normalize = unicodedata.normalize('NFD', file_normalize)
    # Remove non-ASCII characters
    file_normalize = re.sub(r'[^\x00-\x7F]', '', file_normalize)
    return file_normalize

def decode_to_image(base64_string):
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None
    
def save_image(base64_string, nom_complet_image, extension):
    image = decode_to_image(base64_string)
    if image is None:
        return False
    try:
        image.save(nom_complet_image, format=extension.upper())
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False
    
def save_video(base64_string, nom_complet_video):
    try:
        decoded_bytes = base64.b64decode(base64_string)
        with open(nom_complet_video, 'wb') as video_file:
            video_file.write(decoded_bytes)
        return True
    except Exception as e:
        print(f"Error saving video: {e}")
        return False
    
def decode_to_image(image_string):
    try:
        image_bytes = base64.b64decode(image_string)
        image = Image.open(BytesIO(image_bytes))
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def encode_to_string(image, image_type):
    try:
        buffered = BytesIO()
        image.save(buffered, format=image_type)
        image_bytes = buffered.getvalue()
        image_string = base64.b64encode(image_bytes).decode('utf-8')
        return image_string
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def convert_file_to_base64(file_path):
    try:
        with open(file_path, 'rb') as file:
            file_bytes = file.read()
            encoded_base64 = base64.b64encode(file_bytes).decode('utf-8')
            return encoded_base64
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def get_image_extension(file_path):
    _, extension = os.path.splitext(file_path)
    if extension:
        return extension[1:]  # Remove the dot
    return None

def file_is_image(file_name):
    image_pattern = re.compile(r'([^\\s]+(\\.(?i)(jpg|png|gif|bmp|jpeg))$)')
    return bool(image_pattern.match(file_name))

def file_is_video(file_name):
    video_pattern = re.compile(r'([^\\s]+(\\.(?i)(mp4|avi|camv|dvx|mpeg|mpg|wmv|3gp|mkv))$)')
    return bool(video_pattern.match(file_name))

def delete_folder(chemin):
    try:
        if os.path.exists(chemin) and os.path.isdir(chemin):
            shutil.rmtree(chemin)
            print(f"Folder {chemin} deleted successfully.")
        else:
            print(f"The path {chemin} does not exist or is not a directory.")
    except Exception as e:
        print(f"Error deleting folder {chemin}: {e}")

def delete_file(chemin):
    try:
        if os.path.exists(chemin) and os.path.isfile(chemin):
            os.remove(chemin)
            print(f"File {chemin} deleted successfully.")
        else:
            print(f"The file {chemin} does not exist.")
    except Exception as e:
        print(f"Error deleting file {chemin}: {e}")

def not_blank(string):
    return string is not None and string.strip() != ''

def not_empty(lst):
    return lst is not None and len(lst) > 0 and all(s.strip() != '' for s in lst)

def is_not_empty(lst):
    return lst is not None and len(lst) > 0

def generate_alphanumeric_code(nbre_caractere):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=nbre_caractere))

def check_password_hash(hashed_password, plain_password):
    return hashed_password == hashlib.sha256(plain_password.encode()).hexdigest()

def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verifier_email(email):
    email_pattern = re.compile(r".+@.+\.[a-z]+")
    return bool(email_pattern.match(email))

def convert_object_to_json(obj):
    try:
        return json.dumps(obj)
    except TypeError as e:
        print(f"Error converting object to JSON: {e}")
        return None

def parse_date_string(date_str):
    date_format = "%d/%m/%Y"
    return datetime.strptime(date_str, date_format)

def parse_datetime_string(datetime_str):
    datetime_format = "%d/%m/%Y %H:%M:%S"
    return datetime.strptime(datetime_str, datetime_format)

# method to verify pasword throught api request
@basic_auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user

def save_base64_image(base64_str, file_name, extension):
    logging.info("***** Begin save_base64_image ****")
    try:
        # Decode the base64 string
        image_data = base64.b64decode(base64_str)
        # Convert binary data to an image
        image = Image.open(BytesIO(image_data))
        # Create a secure filename
        filename = secure_filename(f"{file_name}_{datetime.now()}.{extension}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Save the image
        image.save(file_path)
        logging.info("***** End save_base64_image %s****", file_path)
        # Return the file path
        return file_path
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

@token_auth.verify_token
def check_token_and_get_user(auth_header):
    # auth_header = request.headers.get('token')
    message = True
    logging.debug('***** message %s****', message)
    if not auth_header:
        message = False
        return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_ACCESS_DENIED()}), 401
    logging.debug('***** header **** %s', auth_header)
    user = User.find_by_token(auth_header, False)
    logging.debug('***** user **** %s', user)
    if not user or user == None:
        message = message = False
        return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_ACCESS_DENIED()}), 401

def generate_numeric_code(nbre_caractere):
    formatted = ''.join(random.choices('0123456789', k=nbre_caractere))
    return formatted

def calculate_minutes_between_dates(date1_str, date2_str, date_format="%Y-%m-%d %H:%M:%S"):
    """
    Calcule le nombre de minutes entre deux dates.
    
    :param date1_str: La première date sous forme de chaîne de caractères.
    :param date2_str: La deuxième date sous forme de chaîne de caractères.
    :param date_format: Le format des dates fournies (par défaut : "%Y-%m-%d %H:%M:%S").
    :return: Le nombre de minutes entre les deux dates.
    """
    try:
        date1 = datetime.strptime(date1_str, date_format)
        # date1 = date1.strftime("%Y-%m-%d %H:%M:%S")
        date2 = datetime.strptime(date2_str, date_format)
        # date2 = date2.strftime("%Y-%m-%d %H:%M:%S")
        delta = date1 - date2
        minutes = delta.total_seconds() / 60
        return minutes
    except ValueError as e:
        print(f"Error parsing dates: {e}")
        return None
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in  app.config['ALLOWED_EXTENSIONS']

def upload_file(request):
    # Vérifie si la partie fichier est présente dans la requête
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # Si l'utilisateur n'a pas sélectionné de fichier, le navigateur envoie un fichier vide sans nom
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        app.logger.debug('***** filename %s****', filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    else:
        return 'File type not allowed'

def generate_alphanumeric_code_lite(nbre_caractere):
    """Génère une chaîne alphanumérique de longueur spécifiée."""
    if nbre_caractere <= 0:
        raise ValueError("La longueur doit être un nombre entier positif.")
    # Crée une chaîne contenant les caractères alphanumériques
    characters = string.ascii_letters + string.digits
    # Génère la chaîne aléatoire
    formatted = ''.join(random.choices(characters, k=nbre_caractere))
    return formatted

def build_search_string(data):
    # Liste des champs à ignorer
    image_fields = {'timm_password','contract_image','id_document_image','id_document_image_back','customer_image','customer_image_ocr','agent_signature'}
    # Concaténer les valeurs des champs, en ignorant les champs d'images et en filtrant les champs non vides
    search_string = ', '.join(str(data.get(field, '')).strip() 
                    for field in data 
                    if field not in image_fields and data.get(field))
    return search_string

def get_timm_user_password(projet_name):
    timm_config = TimmConfig.find_by_projet_name(projet_name, False)
    if not timm_config:
        return None
    return timm_config.timm_user, timm_config.timm_password, timm_config.timm_url


def encrypt_password_lite(password):
    """ Chiffre un mot de passe en utilisant AES avec un tag d'intégrité """
    SECRET_KEY = base64.b64decode(app.config['SECRET_KEY'])  # Convertir la clé en bytes
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce  # Génère un nonce unique
    ciphertext, tag = cipher.encrypt_and_digest(password.encode('utf-8'))  # Chiffrement + Tag
    # Stocker nonce + tag + ciphertext ensemble (encodé en Base64)
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')


def decrypt_password_lite(encrypted_password):
    """ Déchiffre un mot de passe chiffré avec AES et vérifie l'intégrité """
    SECRET_KEY = base64.b64decode(app.config['SECRET_KEY'])  # Convertir la clé en bytes
    encrypted_data = base64.b64decode(encrypted_password)  # Décoder le Base64
    nonce = encrypted_data[:16]  # Extraire le nonce (16 bytes)
    tag = encrypted_data[16:32]  # Extraire le tag (16 bytes)
    ciphertext = encrypted_data[32:]  # Extraire le texte chiffré
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)  # Déchiffreur avec nonce
    decrypted_password = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')  # Vérification du tag
    return decrypted_password

def save_base64_image_lite(base64_str, prefix="image"):
    # try:
    logging.info("***** app.config['UPLOAD_FOLDER'] %s****", app.config['UPLOAD_FOLDER'])
    filename = f"{prefix}.jpg"
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(base64_str))
    logging.info("***** End save_base64_image_lite %s****", filepath)
    return filepath
    # except Exception as e:
    #     raise RuntimeError(f"Erreur lors de la sauvegarde de l’image : {e}")


def check_service_connection(url: str, timeout: int = None) -> dict:
    """
    Teste la connectivité vers un service donné et retourne un résultat détaillé.

    :param url: URL complète du service à tester
    :param timeout: Délai d'attente en secondes
    :return: Dictionnaire avec les champs : success, message, ip (si dispo), status_code (si dispo)
    """
    result = {
        "success": False,
        "message": "",
        "ip": None,
        "status_code": None
    }

    try:
        # Résolution DNS
        host = url.split("//")[-1].split("/")[0]
        ip = socket.gethostbyname(host)
        result["ip"] = ip

        # Requête test
        response = requests.get(url, timeout=timeout, verify=False)
        logging.info("**** response : {}".format(response))
        result["status_code"] = response.status_code
        result["success"] = response.status_code < 500
        result["message"] = f"Connexion réussie avec code {response.status_code}"

    except socket.gaierror:
        logging.error("Échec de résolution DNS")
        result["message"] = "DNS resolution failed"
    except SSLError:
        logging.error("Erreur SSL : certificat invalide ou refusé")
        result["message"] = "SSL error: invalid or untrusted certificate"
    except Timeout:
        logging.error(f"Timeout après {timeout} secondes")
        result["message"] = f"Connection timed out after {int(timeout)} seconds"
    except ConnectionError:
        logging.error("Connexion échouée : hôte injoignable")
        result["message"] = "Connection failed: host unreachable"
    except RequestException as e:
        logging.error(f"Erreur lors de la requête : {e}")
        result["message"] = "Unexpected error during request"

    return result

