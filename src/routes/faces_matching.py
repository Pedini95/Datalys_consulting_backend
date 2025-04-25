from flask import request, jsonify
from app import app, db
from models.faces_matching import FacesMatching
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/faces_matching/getByCriteria', methods=['POST'])
@cross_origin()
def get_faces_matching():
    logging.info("**** Begin get_faces_matching ****")
    logging.info("/faces_matching/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    faces_matchings, total_items = FacesMatching.get_by_criteria(r['data'], index, size)
    if faces_matchings:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [faces_matching.as_dict() for faces_matching in faces_matchings], "count": total_items, "message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_faces_matching ****")
    return response, 200


@app.route('/faces_matching/delete', methods=['POST'])
@cross_origin()
def delete_faces_matching():
    logging.info("**** Begin delete_faces_matching ****")
    logging.info("/faces_matching/delete")
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
    
        faces_matching = FacesMatching.find_one(id, False)
        if not faces_matching:
            return jsonify({'message': 'ERROR', 'details': functional_error.MESSAGE_DATA_EMPTY()}), 400
        faces_matching.is_deleted = True
        faces_matching.updated_by = 1
        faces_matching.updated_at = datetime.now()
        db.session.commit()
    message = functional_error.MESSAGE_SUCCESS()
    response = {"message": message, "code": 200}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info('***** End delete_faces_matching ****')
    return response