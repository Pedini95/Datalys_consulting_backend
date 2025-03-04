from flask import request, jsonify, render_template
from app import app, db
from models.user import User
from models.role_fonctionalite import RoleFonctionalite
from models.role import Role
from models.fonctionalite import Fonctionalite
from redis_template import RedisTemplate
import logging
import utils.notification as notification
import utils.functional_error as functional_error
from datetime import datetime, date, timedelta
import utils.utilities as utilities
from auth import token_auth
import jwt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import hashlib
from utils.session_utils import get_user_session
from flask_cors import CORS, cross_origin

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import pdfkit
from utils.notification import send_mail_login


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PDF_DIRECTORY = '/Users/louisinnocentkouadio/Desktop/pdf_files'

# Configurez le chemin vers wkhtmltopdf
# pdfkit_config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

from flasgger import swag_from

# Initialiser RedisTemplate
redis_template = RedisTemplate(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT']
)
        
@app.route('/user/getByCriteria', methods=['POST'])
@cross_origin()
def get_user():
    logging.info("**** Begin get_user ****")
    logging.info("/user/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    users, total_items = User.get_by_criteria(r['data'], index, size)
    if users:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [user.as_dict() for user in users], "count": total_items, "message": message, "code": 200, "has_error": False}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_user ****")
    return response


@app.route('/user/create', methods=['POST'])
@cross_origin()
def create_user():
    logging.info("**** Begin create_user ****")
    logging.info("/user/create")
    r = request.get_json() or {}
    if 'datas' in r:
        for item in r['datas']:
            if 'file_base_64' in item:
                item['file_base_64'] = ''
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    items = []
    datas = r['datas']
    for data in datas:
        # Champs obligatoires
        required_fields = ['first_name', 'last_name', 'email', 'role_id', 'telephone', 'is_ldap_user']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
            
        is_ldap_user = data.get('is_ldap_user')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        role_id = data.get('role_id')
        telephone=data.get('telephone'),
        
        # Verifier l'unicité du email
        if User.find_by_email(email, False):
            return functional_error.MESSAGE_DATA_DUPLICATE(email)
        
        # Verifier l'unicité du telephone
        if User.find_by_telephone(telephone, False):
            return functional_error.MESSAGE_DATA_DUPLICATE(telephone)
        
        # Verifier l'existance du role
        role = Role.find_one(role_id, False)
        if not role:
            return functional_error.MESSAGE_DATA_NOT_EXIST()
        
        # Gestion des fichiers
        if data.get('file_base_64') and data.get('file_name') and data.get('extension'):
            file_base_64 = data.get('file_base_64')
            file_name = data.get('file_name')
            extension = data.get('extension')
            filename = None
            if file_base_64 and file_name and extension:
                filename = utilities.save_base64_image(file_base_64, file_name, extension)
    
        # Gestion du mot de passe
        password_encrypted = None
        password = None
        if utilities.is_false(is_ldap_user):
            # on genere un mot de passe aleatoire
            password = utilities.generate_alphanumeric_code(8)
            password_encrypted = utilities.encrypt_password(password)
        
        # Gestion de la recherche
        search_string = f"{email},{telephone},{first_name},{last_name}, {role.libelle}"

        # Creation de l'utilisateur
        new_user = User(
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            telephone=data.get('telephone'),
            role_id=role_id,
            created_by=1,
            password=password_encrypted,
            file_path=filename,
            created_at=datetime.now(),
            search_string = search_string,
            is_default_password = True,
            search_string=utilities.build_search_string(data)
        )
        items.append(new_user)
        db.session.add(new_user)
        db.session.commit()
        
        # Envoyer l'email et le mot de passe par mail
        emails = [data.get('email')]
        send_mail_login(emails, password)
        # notification.send_sms(data.get('telephone'), email_body)

    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [user.as_dict() for user in items], "message": message, "code": 200, "has_error": False}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End create_user ****')
    return response


@app.route('/user/update', methods=['POST'])
@cross_origin()
def update_user():
    logging.info("**** Begin update_user ****")
    logging.info("/user/update")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    items = []
    datas = r['datas']
    for data in datas:
        # Champs obligatoires
        required_fields = ['id']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
            
        user = User.query.get(data['id'])
        if utilities.not_blank(data.get('email')):
            if User.find_by_email(data.get('email'), False):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
        
        if utilities.not_blank(data.get('first_name')):
            if User.find_by_first_name(data.get('first_name'), False):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
        
        if utilities.not_blank(data.get('last_name')):
            if User.find_by_last_name(data.get('last_name'), False):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400

        if utilities.not_blank(data.get('telephone')):
            if User.find_by_telephone(data.get('telephone'), False):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
        
        if utilities.not_blank(data.get('role_id')):
            if not User.query.get(data.get('role_id')):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_EMPTY('role_id')}), 400

        user.email=data.get('email'),
        user.first_name=data.get('first_name'),
        user.last_name=data.get('last_name'),
        user.telephone=data.get('telephone'),
        user.role_id=data.get('role_id'),
        user.updated_by=1,
        user.updated_at=datetime.now(),
        user.search_string=utilities.build_search_string(data),
        items.append(user)
        db.session.commit()

    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [user.as_dict() for user in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End update_user ****')
    return response, 200

@app.route('/user/delete', methods=['POST'])
@cross_origin()
def delete_user():
    logging.info("**** Begin delete_user ****")
    logging.info("/user/delete")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    datas = r['datas']
    for data in datas:
        # Champs obligatoires
        required_fields = ['id']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
            
        user = User.query.get(data['id'])
        user.is_deleted = True
        user.deleted_by = 1
        user.deleted_at = datetime.now()
        db.session.commit()
    if user:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End update_module ****')
    return response, 200 


@app.route('/user/login', methods=['POST'])
@cross_origin()
def login_user():
    logging.info("**** Begin login_user ****")
    logging.info("/user/login")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    items = []
    data = r['data']
     # Champs obligatoires
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
    
    email = data.get('email')
    password = data.get('password')
    
    user = User.find_by_email(email, False)
    if user:
        if utilities.check_password_hash(user.password, password):
            roleFonctionalites = RoleFonctionalite.find_by_role_id(user.role_id, False)
            datas_fonctionalites = []
            if roleFonctionalites:
                for roleFonctionalite in roleFonctionalites:
                    fonctionalite = Fonctionalite.find_one(roleFonctionalite.fonctionnalite_id, False)
                    data_fonctionalite = {
                        'fonctionalite_id': fonctionalite.id,
                        'fonctionalite_libelle': fonctionalite.libelle,
                        'fonctionalite_code': fonctionalite.code
                    }
                    datas_fonctionalites.append(data_fonctionalite)
            data_user = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'token': user.token,
                'telephone': user.telephone,
                'is_default_password': user.is_default_password,
                'fonctionalites': datas_fonctionalites
            }
            response = {'status': functional_error.MESSAGE_SUCCESS(), "has_error": False, "items": [data_user]}
            logging.info("**** response output ****")
            logging.info(response)
            logging.info('***** End login_user ****')
            return response
        else:
            response = {'message': 'Invalid password', "code": 400, "has_error": True}
            logging.info("**** response output ****")
            logging.info(response)
            logging.info('***** End login_user ****')
            return response
    else:
        response = {'message': 'Invalid email', "code": 400, "has_error": True}
        logging.info("**** response output ****")
        logging.info(response)
        logging.info('***** End login_user ****')
        return response


@app.route('/user/validation_otp', methods=['POST'])
@cross_origin()
def validation_otp():
    logging.info("**** Begin validation_otp ****")
    logging.info("/user/validation_otp")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    items = []
    data = r['data']
     # Champs obligatoires
    required_fields = ['email', 'code_otp']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty"}, 400

    email = data.get('email')
    code_otp = data.get('code_otp')
    user = User.find_by_email(email, False)
    user_otp = None
    if user:
        user_otp = redis_template.get(code_otp)
        if user_otp:
            token = utilities.generate_alphanumeric_code_lite(100)
            user.token = token
            user.token_created_at = datetime.now()
            items.append(user)
            db.session.commit()
            redis_template.set(token, email, ex=1800)  # OTP expire après 30 minutes
            roleFonctionalites = RoleFonctionalite.find_by_role_id(user.role_id, False)
            datas_fonctionalites = []
            if roleFonctionalites:
                for roleFonctionalite in roleFonctionalites:
                    fonctionalite = Fonctionalite.find_one(roleFonctionalite.fonctionnalite_id, False)
                    data_fonctionalite = {
                        'fonctionalite_id': fonctionalite.id,
                        'fonctionalite_libelle': fonctionalite.libelle,
                        'fonctionalite_code': fonctionalite.code
                    }
                    datas_fonctionalites.append(data_fonctionalite)
            data_user = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'token': user.token,
                'telephone': user.telephone,
                'fonctionalites': datas_fonctionalites
            }
            response = {'message': functional_error.MESSAGE_SUCCESS(), "code": 200, "has_error": False, "items": [data_user]}
            logging.info("**** response output ****")
            logging.info(response)
            logging.info('***** End login_user ****')
            return response
        else:
            response = {'message': 'Code opt invalide', "code": 400, "has_error": True}
            logging.info("**** response output ****")
            logging.info(response)
            logging.info('***** End login_user ****')
            return response
    else:
        response = {'message': 'Login invalide', "code": 400, "has_error": True}
        logging.info("**** response output ****")
        logging.info(response)
        logging.info('***** End login_user ****')
        return response


@app.route('/user/rest_password', methods=['POST'])
def rest_password():
    logging.info("**** Begin rest_password ****")
    logging.info("/user/rest_password")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    data = r['data']
    # Champs obligatoires
    required_fields = ['email', 'password', 'new_password']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty"}, 400

    email = data.get('email')
    password = data.get('password')
    new_password = data.get('new_password')

    user = User.find_by_email(email, False)
    if user:
        if utilities.check_password_hash(user.password, password):
            user.password = utilities.encrypt_password(new_password)
            user.is_default_password = False
            db.session.commit()

            roleFonctionalites = RoleFonctionalite.find_by_role_id(user.role_id, False)
            datas_fonctionalites = []
            if roleFonctionalites:
                for roleFonctionalite in roleFonctionalites:
                    fonctionalite = Fonctionalite.find_one(roleFonctionalite.fonctionnalite_id, False)
                    data_fonctionalite = {
                        'fonctionalite_id': fonctionalite.id,
                        'fonctionalite_libelle': fonctionalite.libelle,
                        'fonctionalite_code': fonctionalite.code
                    }
                    datas_fonctionalites.append(data_fonctionalite)
            data_user = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'token': user.token,
                'telephone': user.telephone,
                'is_default_password': user.is_default_password,
                'fonctionalites': datas_fonctionalites
            }
            response = {"status": functional_error.MESSAGE_SUCCESS(), "has_error": False, "items": [data_user]}
            logging.info("**** response output ****")
            logging.info(response)
        else:
            response = {'message': 'Invalid password', "code": 400, "has_error": True}
            logging.info("**** response output ****")
            logging.info(response)
    else:
        response = {"status": 'Login invalide', "has_error": True}
        logging.info("**** response output ****")
        logging.info(response)
    
    logging.info('***** End rest_password ****')
    return response


@app.route('/user/get_user_session', methods=['GET'])
@cross_origin()
def get_user_session_api():
    logging.info("**** Begin get_user_session_api ****")
    logging.info("/user/get_user_session")
    logging.info(request.headers)
    token = request.headers.get('Authorization')
    logging.info("===== token =====")
    logging.info(token)
    token = token.split(" ")[1]
    logging.info(token)
    if token is None:
        return {'message': 'Missing token', 'code': 401}, 401
    user = User.find_by_token(token, False)
    logging.info("**** User ****")
    logging.info(user)
    if user:
        logging.info(user.login)
        if user.login != 'SUPERADMIN':
            date1 = user.token_created_at.strftime("%Y-%m-%d %H:%M:%S")
            date2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session = utilities.calculate_minutes_between_dates(date2, date1)
            if session > app.config['SESSION_EXPIRE_MINUTES']:
                response = {'message': 'Session expires', "code": 405, "has_error": True}
                logging.info("**** response output ****")
                logging.info(response)
                return response
            
            # on delete token_created_at
            user.token_created_at = None
            db.session.commit()
            logging.info("**** After commit delete {} ****".format(user.token_created_at))
            # on sette la new valeur de token_created_at
            user.token_created_at = datetime.now()
            db.session.commit()
            logging.info("**** datetime.now() {} ****".format(datetime.now()))
            logging.info("**** After commit sette {} ****".format(user.token_created_at))
            item = get_item_user(user)
            response = {'item': item, "code": 200, "has_error": False, 'message': functional_error.MESSAGE_SUCCESS()}
            logging.info("**** response output ****")
            logging.info(response)
        else:
            item = get_item_user(user)
            response = {'item': item, "code": 200, "has_error": False, 'message': functional_error.MESSAGE_SUCCESS()}
            logging.info("**** response output ****")
            logging.info(response)
    else:
        response = {'message': 'User not found in system', "code": 401, "has_error": True}
        logging.info("**** response output ****")
        logging.info(response)

    logging.info("**** End get_user_session_api ****")
    return response


def get_item_user(user):
    logging.info("**** Begin get_item_user ****")
    item = {
        "id": user.id,
        "login": user.login,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
    logging.info("**** End get_item_user ****")
    return item