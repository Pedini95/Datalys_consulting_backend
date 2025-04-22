from flask import request, jsonify
from app import app, db
from models.actions_logs import ActionsLogs
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from flasgger import swag_from
from utils.session_utils import get_user_session
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/actions_logs/getByCriteria', methods=['POST'])
@cross_origin()
def get_actions_logs():
    logging.info("**** Begin get_actions_logs ****")
    logging.info("/actions_logs/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    actions_logs, total_items = ActionsLogs.get_by_criteria(r.get('data'), index, size)
    if actions_logs:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [actions_log.as_dict() for actions_log in actions_logs], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_actions_logs ****")
    return response


@app.route('/actions_logs/create', methods=['POST'])
@cross_origin()
def create_actions_logs():
    logging.info("**** Begin create_actions_logs ****")
    logging.info("/actions_logs/create")
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
        
        if ActionsLogs.find_by_projet_name(data['projet_name'], False):
            return {"status": "error", "message": f"Projet {data['projet_name']} already exists"}, 400
        
        try:
            new_actions_log = ActionsLogs(
                projet_name=data['projet_name'],
                timm_user=data['timm_user'],
                timm_password=utilities.encrypt_password_lite(data['timm_password']),
                timm_url=data['timm_url'],
                is_deleted=False,
                created_at=datetime.now(),
                created_by=1,
                search_string=utilities.build_search_string(data)
            )
            items.append(new_actions_log)
            db.session.add(new_actions_log)
        except Exception as e:
            db.session.rollback()
            logging.info(str(e))
    db.session.commit()
    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [actions_log.as_dict() for actions_log in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_actions_logs ****")
    return response
