from flask import request, jsonify
from app import app, db
from models.fonctionalite import Fonctionalite
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from flasgger import swag_from
from utils.session_utils import get_user_session
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/fonctionalite/getByCriteria', methods=['POST'])
@cross_origin()
def get_fonctionalite():
    logging.info("**** Begin get_fonctionalite ****")
    logging.info("/fonctionalite/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    fonctionalites, total_items = Fonctionalite.get_by_criteria(r.get('data'), index, size)
    if fonctionalites:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [fonctionalite.as_dict() for fonctionalite in fonctionalites], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_fonctionalite ****")
    return response


@app.route('/fonctionalite/create', methods=['POST'])
@cross_origin()
def create_fonctionalite():
    logging.info("**** Begin create_fonctionalite ****")
    logging.info("/fonctionalite/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    items = []
    datas = r['datas']
    for data in datas:
        # Champs obligatoires
        required_fields = ['code', 'libelle']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400

        code = data.get('code')
        libelle = data.get('libelle')
        if Fonctionalite.find_by_code(code, False):
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
        
        if Fonctionalite.find_by_libelle(libelle, False):
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
        try:
            new_fonctionalite = Fonctionalite(
                code=data.get('code'),
                libelle=data.get('libelle'),
                is_available_for_user=False,
                created_by=1,
                is_deleted=False,
                created_at=datetime.now(),
                search_string=utilities.build_search_string(data)
            )
        except Exception as e:
            db.session.rollback()
            logging.info(str(e))
        items.append(new_fonctionalite)
        db.session.add(new_fonctionalite)
    db.session.commit()
    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [fonctionalite.as_dict() for fonctionalite in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End create_fonctionalite ****")
    return response


@app.route('/fonctionalite/update', methods=['POST'])
@cross_origin()
def update_fonctionalite():
    logging.info("**** Begin update_fonctionalite ****")
    logging.info("/fonctionalite/update")
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
            
        id = data.get('id')
        fonctionalite = Fonctionalite.query.get(data['id'])
        if utilities.not_blank(data.get('code')):
            if Fonctionalite.find_by_code(data.get('code'), False):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
            fonctionalite.code = data.get('code', fonctionalite.code)

        if utilities.not_blank(data.get('libelle')):
            if Fonctionalite.find_by_libelle(data.get('libelle'), False):
                return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400
            fonctionalite.libelle = data.get('libelle', fonctionalite.libelle)

        fonctionalite.updated_at = datetime.utcnow()
        fonctionalite.updated_by = 1
        fonctionalite.search_string = utilities.build_search_string(data)
        items.append(fonctionalite)
        db.session.commit()
    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [fonctionalite.as_dict() for fonctionalite in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End update_fonctionalite ****")
    return response

    
@app.route('/fonctionalite/delete', methods=['POST'])
@cross_origin()
def delete_fonctionalite():
    logging.info("**** Begin delete_fonctionalite ****")
    logging.info("/fonctionalite/delete")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    datas = r['datas']
    for data in datas:
        fonctionalite = Fonctionalite.query.get(data['id'])
        if fonctionalite:
            app.logger.debug(f"Deleting fonctionalite with id: {fonctionalite.id}, current is_deleted: {fonctionalite.is_deleted}")
            fonctionalite.is_deleted = True
            db.session.add(fonctionalite)
        else:
            app.logger.error(f"Fonctionalite with id: {data['id']} not found")
    
    db.session.flush()
    db.session.commit()
    
    message = functional_error.MESSAGE_SUCCESS()
    response = {"message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End delete_fonctionalite ****")
    return response