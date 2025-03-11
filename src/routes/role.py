from flask import request, jsonify
from app import app, db
from models.role import Role
from models.role_fonctionalite import RoleFonctionalite
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from flasgger import swag_from
from utils.session_utils import get_user_session
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/role/getByCriteria', methods=['POST'])
@cross_origin()
def get_role():
    logging.info("**** Begin get_role ****")
    logging.info("/role/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    roles, total_items = Role.get_by_criteria(r['data'], index, size)
    if roles:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [role.as_dict() for role in roles], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_role ****")
    return response, 200


@app.route('/role/create', methods=['POST'])
@cross_origin()
def create_role():
    logging.info("**** Begin create_role ****")
    logging.info("/role/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    message = None
    items = []
    datas = r['datas']
    for data in datas:
        # Champs obligatoires
        required_fields = ['libelle']
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Field {field} is missing or empty"}, 400

        libelle = data.get('libelle')
        if not libelle:
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_FIELD_EMPTY('libelle')}), 400
        
        if Role.find_by_libelle(libelle, False):
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_DUPLICATE()}), 400

        new_role = Role(
            libelle=data.get('libelle'),
            created_by=1,
            is_deleted=False,
            created_at=datetime.now(),
            search_string=utilities.build_search_string(data)
        )
        items.append(new_role)
        db.session.add(new_role)
        db.session.commit()
        if  utilities.is_not_empty(data.get('fonctionalites')):
            datas_fonctionalites = data.get('fonctionalites')
            for fonctionalite in datas_fonctionalites:
                new_role_fonctionalite = RoleFonctionalite(
                    role_id=new_role.id,
                    fonctionnalite_id=fonctionalite.get('fonctionalite_id'),
                    created_by=1,
                    is_deleted=False,
                    created_at=datetime.now(),
                    search_string=utilities.build_search_string(fonctionalite)
                )
                db.session.add(new_role_fonctionalite)
                db.session.commit()
    message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [role.as_dict() for role in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End create_role ****')
    return response
   

@app.route('/role/update', methods=['POST'])
@cross_origin()
def update_role():
    logging.info("**** Begin update_role ****")
    logging.info("/role/update")
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
        libelle = data.get('libelle')
        
        role = Role.find_one(id, False)
        if not role:
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_EMPTY()}), 400
        
        if utilities.not_blank(libelle):
            role.libelle = libelle
        
        if  utilities.is_not_empty(data.get('fonctionalites')):
            role_fonctionalite = RoleFonctionalite.find_by_role_id(role.id, False)
            logging.info('***** role_fonctionalite %s ****', role_fonctionalite)
            if role_fonctionalite:
                for fon in role_fonctionalite:
                    db.session.delete(fon)
                    db.session.commit()

            datas_fonctionalites = data.get('fonctionalites')
            for fonctionalite in datas_fonctionalites:
                new_role_fonctionalite = RoleFonctionalite(
                    role_id=role.id,
                    fonctionnalite_id=fonctionalite.get('fonctionalite_id'),
                    created_by=1,
                    is_deleted=False,
                    created_at=datetime.now(),
                    search_string=utilities.build_search_string(fonctionalite)
                )
                db.session.add(new_role_fonctionalite)
                db.session.commit()
        role.updated_by = 1
        role.updated_at = datetime.now()
        role.search_string = utilities.build_search_string(data)
        items.append(role)
        db.session.commit()
    if items:
        message = functional_error.MESSAGE_SUCCESS()
    response = {"items": [role.as_dict() for role in items], "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End create_role ****')
    return response, 200
   

@app.route('/role/delete', methods=['POST'])
@cross_origin()
def delete_role():
    logging.info("**** Begin delete_role ****")
    logging.info("/role/delete")
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
    
        role = Role.find_one(id, False)
        if not role:
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_EMPTY()}), 400
        role.is_deleted = True
        role.updated_by = 1
        role.updated_at = datetime.now()
        db.session.commit()
    message = functional_error.MESSAGE_SUCCESS()
    response = {"message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End update_module ****')
    return response