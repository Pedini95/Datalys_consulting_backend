from flask import request, jsonify
from datetime import datetime, timedelta
from models.user import User
# from app import app
from app import app, db
from redis_template import RedisTemplate
# from utils.session_utils import utilities
import utils.functional_error as functional_error

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Initialiser RedisTemplate
redis_template = RedisTemplate(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT']
)

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

def get_item_user(user):
    item = {
        "id": user.id,
        "login": user.login,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
    return item

def get_user_session():
    print("**** Begin get_user_session ****")
    print("/user/get_user_session")
    token = request.headers.get('Authorization')
    print("**** token ****")
    print(token)
    token = token.split(" ")[1]
    print(token)
    if token is None:
        return {'message': 'Missing token', 'code': 400}
    user = User.find_by_token(token, False)
    print("**** User ****")
    if user:
        print(user.login)
        if user.login != 'SUPERADMIN':
            user_token = redis_template.get(token)
            if user_token:
                # on delete token
                redis_template.delete(token)
                # on sette la new valeur de token
                redis_template.set(token, user.email, ex=1800) # OTP expire après 30 minutes
                user.token = token
                db.session.commit()  
            else:
                return {'message': 'Token not found', 'code': 400}
    else:
        response = {'message': 'User not found in system', "code": 400, "has_error": True}
        print("**** End get_user_session ****")
        print("**** response received ****")
        print(response)
        return response
