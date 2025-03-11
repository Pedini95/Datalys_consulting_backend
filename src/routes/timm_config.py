from flask import request, jsonify
from app import app, db
from models.timm_config import TimmConfig
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from flasgger import swag_from
from utils.session_utils import get_user_session
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/timm_config/getByCriteria', methods=['POST'])
@cross_origin()
def get_timm_config():
    logging.info("**** Begin get_timm_config ****")
    logging.info("/timm_config/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    timm_configs, total_items = TimmConfig.get_by_criteria(r.get('data'), index, size)
    if timm_configs:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [timm_config.as_dict() for timm_config in timm_configs], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_timm_config ****")
    return response


@app.route('/timm_config/create', methods=['POST'])
@cross_origin()
def create_timm_config():
    logging.info("**** Begin create_timm_config ****")
    logging.info("/timm_config/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    items = []
    datas = r['datas']
    for data in datas:
        # Champs obligatoires
        required_fields = ['projet_name', 'timm_user', 'timm_password', 'timm_url']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400

        if TimmConfig.find_by_projet_name(data['projet_name'], False):
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400

        try:
            new_timm_config = TimmConfig(
                projet_name=data['projet_name'],
                timm_user=data['timm_user'],
                timm_password=utilities.encrypt_password_lite(data['timm_password']),
                timm_url=data['timm_url'],
                is_deleted=False,
                created_at=datetime.now(),
                created_by=1,
                search_string=utilities.build_search_string(data)
            )
            items.append(new_timm_config)
            db.session.add(new_timm_config)
        except Exception as e:
            db.session.rollback()
            logging.info(str(e))
    db.session.commit()
    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [timmConfig.as_dict() for timmConfig in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_timm_config ****")
    return response

@app.route('/timm_config/update', methods=['POST'])
@cross_origin()
def update_timm_config():
    logging.info("**** Begin update_timm_config ****")
    logging.info("/timm_config/update")
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
        
        timm_config = TimmConfig.query.get(data['id'])
        if timm_config:
            try:
                timm_config.projet_name = data['projet_name']
                timm_config.timm_user = data['timm_user']
                timm_config.timm_url = data['timm_url']
                timm_config.timm_password = timm_config.timm_password
                if data['timm_password'] and utilities.encrypt_password(data['timm_password']) != timm_config.timm_password:
                    logging.info("**** encrypting timm_password updated ****")
                    timm_config.timm_password = utilities.encrypt_password(data['timm_password'])
                timm_config.search_string = utilities.generate_search_string(data)
                db.session.commit()
                message = functional_error.MESSAGE_SUCCESS()
            except Exception as e:
                message = functional_error.MESSAGE_ERROR()
        items.append(timm_config)
    response = {"items": [timmConfig.as_dict() for timmConfig in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_timm_config ****")
    return response


@app.route('/timm_config/delete', methods=['POST'])
@cross_origin()
def delete_timm_config():
    logging.info("**** Begin delete_timm_config ****")
    logging.info("/timm_config/delete")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    datas = r['datas']
    for data in datas:
        timm_config = TimmConfig.query.get(data['id'])
        if timm_config:
            app.logger.debug(f"Deleting timm_config with id: {timm_config.id}, current is_deleted: {timm_config.is_deleted}")
            timm_config.is_deleted = True
            db.session.add(timm_config)
        else:
            app.logger.error(f"Timm_config with id: {data['id']} not found")
    
    db.session.flush()
    db.session.commit()
    
    message = functional_error.MESSAGE_SUCCESS()
    response = {"message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_timm_config ****")
    return response
