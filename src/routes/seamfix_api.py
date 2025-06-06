from re import search
from flask import request, json, jsonify
import requests
from app import app, db
import logging
from datetime import datetime
from flask_cors import CORS, cross_origin
from models.faces_matching import FacesMatching
from models.actions_logs import ActionsLogs
from models.ocr_seamfix import OCRSeamfix
from models.liveness import Liveness
import uuid
import utils.utilities as utilities
import re

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
    print("**** Begin face matching ****")
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
    logging.info("**** response : {}".format(response))
    logging.info("**** msisdn face matching : {}".format(msisdn))
    save_face_matching(json.dumps(data_api), response, msisdn)
    logging.info("**** response : {}".format(response))
    logging.info("**** End face matching ****")
    print("**** End face matching ****")
    # on save fin de logs dans action logs
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response), response.get("description"))
    return response


@app.route("/kyc/portrait/seamfix/validate", methods=['POST'])
@cross_origin()
def portrait_seamfix_validate():
    logging.info("**** Begin portrait_seamfix_validate ****")
    print("**** Begin portrait_seamfix_validate ****")
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
    # on save la reponse
    save_liveness(json.dumps(data_api), response.json())
    logging.info("**** End portrait_seamfix_validate ****")
    print("**** End portrait_seamfix_validate ****")
    # on save fin de logs dans action logs
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response.json()), response.json().get("transactionStatus"))
    return jsonify(response.json()), response.status_code



def portrait_seamfix_validate_lite(image):
    logging.info("**** Begin portrait_seamfix_validate ****")
    print("**** Begin portrait_seamfix_validate ****")
    transactionId = "txr-ABCD-EEFFDDE"
    libelle = "portrait_seamfix_validate_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/portrait/seamfix/validate", json.dumps({"image": image, "transactionId": transactionId, "actions": ["PLC"]}))
    # Appel de l'authentification
    auth_response = portrait_seamfix_authenticate()
    logging.info("**** auth_response : {}".format(auth_response))
    logging.info("**** auth_response.accessToken : {}".format(auth_response.get("accessToken")))
    if auth_response.get("code") != 0:
        return {"status": "error", "message": "Failed to authenticate with Seamfix", "code": 400, "has_error": True}, 400

    headers = {"Authorization": f"Bearer {auth_response.get('accessToken')}", "Content-Type": "application/json"}
    logging.info("**** headers : {}".format(headers))
    data_api = {"image": image, "transactionId": transactionId, "actions": ["PLC"]}
    # Appel de la validation
    response = requests.post(app.config['SEAMFIX_URL_VALIDATE'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    # on save la reponse
    save_liveness(json.dumps(data_api), response.json())
    logging.info("**** End portrait_seamfix_validate ****")
    print("**** End portrait_seamfix_validate ****")
    # on save fin de logs dans action logs
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response.json()), response.json().get("transactionStatus"))
    return jsonify(response.json()), response.status_code


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

def save_liveness(request, response):
    print("**** Begin save_liveness ****")
    action_type = None
    clipped_image = None
    code = None
    description = None
    icao_token_image = None
    metrics = None
    score = None
    transaction_id = None
    transaction_status = None
    transaction_status_code = None
    search_string = None
    logging.info("**** response responses : {} *****".format(response.get("responses")))
    if response.get("responses"):
        rep = response.get("responses")[0]
        action_type = rep.get("actionType")
        clipped_image = rep.get("clippedImage")
        code = rep.get("code")
        description = rep.get("description")
        icao_token_image = rep.get("icaoTokenImage")
        metrics = rep.get("metrics")
        score = rep.get("score")
        transaction_id = response.get("transactionId")
        transaction_status = response.get("transactionStatus")
        transaction_status_code = response.get("transactionStatusCode")
        # search_string = utilities.build_search_string(rep)
        new_liveness = Liveness(
            action_type=action_type,
            clipped_image=clipped_image,
            code=code,
            description=description,
            icao_token_image=icao_token_image,
            metrics=metrics,
            score=score,
            transaction_id=transaction_id,
            transaction_status=transaction_status,
            transaction_status_code=transaction_status_code,
            search_string=search_string,
            created_at=datetime.utcnow(),
            is_deleted=False,
            request=request
        )
        db.session.add(new_liveness)
        db.session.commit() 
    print("**** End save_liveness ****")
    return new_liveness
    


def save_face_matching(request, response, msisdn):
    code = None
    description = None
    match_id = None
    score = 0.0
    status = None
    transaction_ref = None
    errors = None
    search_string = None
    logging.info("**** response code : {} *****".format(response.get("code")))
    if response.get("code") == 0 or response.get("code") == -1:
        logging.info("**** response code 0 or -1 *****")
        code = response.get("code")
        description = response.get("description")
        match_id = response.get("matchId")
        logging.info("**** response score : {} *****".format(response.get("score")))
        score = response.get("score")
        status = response.get("status")
        transaction_ref = response.get("transactionRef")
    elif response.get("code") == 400:
        logging.info("**** response code 400 *****")
        code = response.get("code")
        description = response.get("description")
        errors_joined = None
        if len(response.get("errors")) == 1:
            errors_joined = response.get("errors")[0]
        else:
            errors_joined = ", ".join(response.get("errors"))
        errors = errors_joined
    
    new_face_matching = FacesMatching(
        description=description,
        msisdn=msisdn,
        code=code,
        match_id=match_id,
        score=score,
        status=status,
        transaction_ref=transaction_ref,
        errors=errors,
        created_at=datetime.utcnow(),
        is_deleted=False,
        search_string=search_string,
        request=request
    )
    db.session.add(new_face_matching)
    db.session.commit()
    return new_face_matching


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
    if response.get("code") == 0:
        retour_normalize = simplify_scanner_data(response)
        logging.info("**** retour_normalize : {}".format(retour_normalize))
        ocr_seamfix = save_ocr_seamfix(retour_normalize)
        logging.info("**** ocr_seamfix : {}".format(ocr_seamfix.as_dict()))
    logging.info("**** End ocr_seamfix ****")
    # on save fin de logs dans action logs
    status = "ERROR"
    if response.get("code") == 0:
        status = "SUCCESS"
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response), status)
    return response


def ocr_seamfix_lite(document, documentType, documentFormat):
    logging.info("**** Begin ocr_seamfix_lite ****")
    print("**** Begin ocr_seamfix_lite ****")
    # on save debut des logs dans action logs
    libelle = "ocr_seamfix_lite_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/ocr/seamfix_lite", json.dumps({"document": document,"documentType": documentType, "documentFormat": documentFormat}))

    headers = {"Authorization": f"Bearer {app.config['SEAMFIX_TOKEN']}", "Content-Type": "application/json"}
    data_api = {"document": document,"documentType": documentType, "documentFormat": documentFormat}
    # Appel de l'OCR
    response = requests.post(app.config['SEAMFIX_DOC_PROCESSING_URL'], data=json.dumps(data_api), headers=headers)
    logging.info("**** response : {}".format(response))
    response = response.json()
    if response.get("code") == 0:
        retour_normalize = simplify_scanner_data(response)
        print("**** retour_normalize : {}".format(retour_normalize))
        logging.info("**** retour_normalize : {}".format(retour_normalize))
        ocr_seamfix = save_ocr_seamfix(retour_normalize)
        print("**** ocr_seamfix : {}".format(ocr_seamfix.as_dict()))
        logging.info("**** ocr_seamfix : {}".format(ocr_seamfix.as_dict()))
    # on save fin de logs dans action logs
    status = "ERROR"
    if response.get("code") == 0:
        status = "SUCCESS"
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response), status)
    logging.info("**** response : {}".format(response))
    logging.info("**** End ocr_seamfix_lite ****")
    print("**** End ocr_seamfix_lite ****")
    return response


def clean_string(s: str, replace_with: str = '') -> str:
    return re.sub(r"[\s_\-']+", replace_with, s)

def simplify_scanner_data(data: dict) -> dict:
    logging.info("**** data Info: {} *****".format(data))
    fields = {}
    for item in data.get("data", {}).get("extractedDataList", []):
        field_name_clean = clean_string(item["fieldName"]).lower()
        fields[field_name_clean] = item.get("value", "")
    logging.info("**** fields Info: {} *****".format(fields))
        

    def get_field(*keys):
        for key in keys:
            value = fields.get(key, "")
            if value and value.strip():
                return value.strip()
        return ""

    return {
        "scannerType": "OCR",
        "typeScanner": {"id": 0, "label": "INCONNU"},
        "cardId": get_field("idnumber", "cardid", "nin"),
        "nin": get_field("nin"),
        "firstName": get_field("firstname") or get_field("name"),
        "middleName": get_field("middlename"),
        "lastName": get_field("surname"),
        "gender": get_field("sex", "gender"),
        "birdDate": get_field("dateofbirth"),
        "status": get_field("status"),
        "expiry": get_field("expiry"),
        "xxxxx": "",
        "adress": "",
        "photo": get_field("photo") if "Error" not in get_field("photo") else "",
        "placeOfBirth": get_field("placeofbirth", "birthplace"),
        "description": data.get("description", ""),
        "documentCountryName": data.get("documentCountryName", ""),
        "documentDescription": data.get("documentDescription", ""),
        "documentName": data.get("documentName", ""),
        "documentType": data.get("documentType", ""),
        "documentYear": data.get("documentYear", ""),
    }


def save_ocr_seamfix(response, msisdn=None):
    data_ocr = {
        "card_id": response.get("cardId"),
        # "msisdn": msisdn,
        "nin": response.get("nin"),
        "first_name": response.get("firstName"),
        "middle_name": response.get("middleName"),
        "last_name": response.get("lastName"),
        "document_type": response.get("documentType"),
        "document_year": response.get("documentYear"),
        "bird_date": response.get("birdDate"),
        "gender": response.get("gender"),
        "expiry": response.get("expiry"),
        "status": response.get("status"),
        "place_of_birth": response.get("placeOfBirth"),
        "description": response.get("description"),
        "document_country_name": response.get("documentCountryName"),
        "document_description": response.get("documentDescription"),
        "document_name": response.get("documentName"),
        "photo": response.get("photo"),
        "created_at":datetime.utcnow(),
        "updated_at":datetime.utcnow(),
        "is_deleted":False
    }
    new_ocr_seamfix = OCRSeamfix(**data_ocr)
    db.session.add(new_ocr_seamfix)
    db.session.commit()
    new_ocr_seamfix = OCRSeamfix.find_one(new_ocr_seamfix.id, False)
    new_ocr_seamfix.search_string = utilities.build_search_string(data_ocr)
    new_ocr_seamfix.update()
    return new_ocr_seamfix
    
    

    


