from flask import request, json, jsonify
import requests
from app import app, db
import logging
from datetime import datetime
from flask_cors import CORS, cross_origin
from models.faces_matching import FacesMatching
from models.actions_logs import ActionsLogs
import uuid

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route("/kyc/seamfix/authenticate", methods=['POST'])
@cross_origin()
def seamfix_authenticate():
    logging.info("**** Begin seamfix_authenticate ****")
    headers = {"Content-Type": "application/json"}
    data_api = {"publicKey": app.config['SEAMFIX_PUBLIC_KEY'],"privateKey": app.config['SEAMFIX_PRIVATE_KEY'],"userId": app.config['SEAMFIX_USER_ID']}
    logging.info("**** data_api : {}".format(data_api))
    response = requests.post(app.config['SEAMFIX_URL'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    response = response.json()
    logging.info("**** response : {}".format(response))
    logging.info("**** End seamfix_authenticate ****")
    return response


def portrait_seamfix_authenticate():
    logging.info("**** Begin portrait_seamfix_authenticate ****")
    headers = {"Content-Type": "application/json"}
    data_api = {"publicKey": app.config['SEAMFIX_PUBLIC_KEY'],"privateKey": app.config['SEAMFIX_PRIVATE_KEY'],"userId": app.config['SEAMFIX_USER_ID']}
    response = requests.post(app.config['SEAMFIX_URL'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    response = response.json()
    logging.info("**** response : {}".format(response))
    logging.info("**** End portrait_seamfix_authenticate ****")
    return response


@app.route("/kyc/portrait/seamfix/verify", methods=['POST'])
@cross_origin()
def portrait_seamfix_verify():
    logging.info("**** Begin portrait_seamfix_verify ****")
    r = request.get_json() or {}
    # on save debut des logs dans action logs
    libelle = "portrait_seamfix_verify_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/portrait/seamfix/verify", json.dumps(r))
    data = r['data']
    # Champs obligatoires
    required_fields = ['probe', 'candidate']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400

    # Appel de l'authentification
    auth_response = portrait_seamfix_authenticate()
    if auth_response.get("code") != 0:
        return {"status": "error", "message": "Failed to authenticate with Seamfix", "code": 400, "has_error": True}, 400

    headers = {"Authorization": f"Bearer {auth_response.get('accessToken')}", "Content-Type": "application/json"}
    data_api = {"probe": data['probe'],"candidate": data['candidate']}
    response = requests.post(app.config['SEAMFIX_URL_VERIFY'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    response = response.json()
    new_face_matching = FacesMatching(
        description="Face matching",
        request=json.dumps(data_api),
        response=json.dumps(response),
        created_at=datetime.utcnow(),
        is_deleted=False
    )
    db.session.add(new_face_matching)
    db.session.commit()
    logging.info("**** response : {}".format(response))
    logging.info("**** End portrait_seamfix_verify ****")
    # on save fin de logs dans action logs
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response), response.get("description"))
    return response


def portrait_seamfix_verify_lite(probe=None, candidate=None, msisdn=None):
    logging.info("**** Begin face matching ****")
    libelle = "face_matching_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/portrait/seamfix/verify", json.dumps({"probe": probe,"candidate": candidate}))
    if probe is None:
        response = {"status": "error", "message": "Missing required fields probe", "code": 400, "has_error": True}, 400
        ActionsLogs.action_logs_final_save(libelle, json.dumps(response), "Face matching")
        return response
    
    if candidate is None:
        response = {"status": "error", "message": "Missing required fields candidate", "code": 400, "has_error": True}, 400
        ActionsLogs.action_logs_final_save(libelle, json.dumps(response), "Face matching")
        return response

    # Appel de l'authentification
    auth_response = portrait_seamfix_authenticate()
    if auth_response.get("code") != 0:
        response = {"status": "error", "message": "Failed to authenticate with Seamfix", "code": 400, "has_error": True}, 400
        ActionsLogs.action_logs_final_save(libelle, json.dumps(response), "Face matching")
        return response

    headers = {"Authorization": f"Bearer {auth_response.get('accessToken')}", "Content-Type": "application/json"}
    data_api = {"probe": probe,"candidate": candidate}
    response = requests.post(app.config['SEAMFIX_URL_VERIFY'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    response = response.json()
    new_face_matching = FacesMatching(
        description="Face matching",
        msisdn=msisdn,
        request=json.dumps(data_api),
        response=json.dumps(response),
        created_at=datetime.utcnow(),
        is_deleted=False
    )
    db.session.add(new_face_matching)
    db.session.commit()
    logging.info("**** response : {}".format(response))
    logging.info("**** End face matching ****")
    # on save fin de logs dans action logs
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response), response.get("description"))
    return response


@app.route("/kyc/portrait/seamfix/validate", methods=['POST'])
@cross_origin()
def portrait_seamfix_validate():
    logging.info("**** Begin portrait_seamfix_validate ****")
    r = request.get_json() or {}
    # on save debut des logs dans action logs
    libelle = "portrait_seamfix_validate_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/portrait/seamfix/validate", json.dumps(r))
    data = r['data']
    # Champs obligatoires
    required_fields = ['image', 'transactionId']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400

    # Appel de l'authentification
    auth_response = portrait_seamfix_authenticate()
    logging.info("**** auth_response : {}".format(auth_response))
    logging.info("**** auth_response.accessToken : {}".format(auth_response.get("accessToken")))
    if auth_response.get("code") != 0:
        return {"status": "error", "message": "Failed to authenticate with Seamfix", "code": 400, "has_error": True}, 400

    headers = {"Authorization": f"Bearer {auth_response.get('accessToken')}", "Content-Type": "application/json"}
    logging.info("**** headers : {}".format(headers))
    data_api = {"image": data['image'], "transactionId": data['transactionId'], "actions": ["PLC"]}
    # Appel de la validation
    response = requests.post(app.config['SEAMFIX_URL_VALIDATE'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    logging.info("**** End portrait_seamfix_validate ****")
    # on save fin de logs dans action logs
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response.json()), response.json().get("transactionStatus"))
    return jsonify(response.json()), response.status_code


@app.route("/kyc/ocr/seamfix", methods=['POST'])
@cross_origin()
def ocr_seamfix():
    logging.info("**** Begin ocr_seamfix ****")
    r = request.get_json() or {}
    # on save debut des logs dans action logs
    libelle = "ocr_seamfix_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/ocr/seamfix", json.dumps(r))
    data = r['data']
    # Champs obligatoires
    required_fields = ['document', 'documentType', 'documentFormat']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400

    headers = {"Authorization": f"Bearer {app.config['SEAMFIX_TOKEN']}", "Content-Type": "application/json"}
    data_api = {"document": data['document'],"documentType": data['documentType'], "documentFormat": data['documentFormat']}
    # Appel de l'OCR
    response = requests.post(app.config['SEAMFIX_DOC_PROCESSING_URL'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    response = response.json()
    logging.info("**** response : {}".format(response))
    logging.info("**** End ocr_seamfix ****")
    # on save fin de logs dans action logs
    status = "ERROR"
    if response.get("code") == 0:
        status = "SUCCESS"
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response), status)
    return response


@app.route("/kyc/ocr/seamfix/get", methods=['GET'])
@cross_origin()
def ocr_seamfix_get():
    logging.info("**** Begin ocr_seamfix_get ****")
    headers = {"Content-Type": "application/json"}
    # Appel de l'OCR
    response = requests.get(app.config['SEAMFIX_HEALTH_CHECK_URL'], headers=headers)
    logging.info("**** response : {}".format(response))
    logging.info("**** response : {}".format(response.json()))
    response = response.json()
    logging.info("**** End ocr_seamfix_get ****")
    return response


