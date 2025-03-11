from flask import request, jsonify
from app import app, db
from models.fonctionalite import Fonctionalite
import logging
import utils.functional_error as functional_error
from datetime import datetime, date
import utils.utilities as utilities
from models.timm_config import TimmConfig
from flasgger import swag_from
from utils.session_utils import get_user_session
from flask_cors import CORS, cross_origin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/kyc/header/enrichement', methods=['GET'])
@cross_origin()
def get_header_enrichement():
    logging.info("**** Begin get_header_enrichement ****")
    logging.info("/kyc/header/enrichement")
    logging.info("**** End get_header_enrichement ****")
    return "OK"


def kyc_checkParty(msisdn):
    logging.info('***** Begin checkParty ****')
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{"user":username, "pwd":password },
            "param":{"MSISDN":msisdn}
        }
    res = requests.get('{}TIMM/v1/CRM/Subscriber'.format(url), data=json.dumps(data))
    logging.info('***** End checkParty ****')
    return res

def kyc_kya_auth(msisdn, pin):
    logging.info('***** Begin kyc_kya_auth ****')
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
        "auth":{ "user":username, "pwd": password},
        "param":{ "msisdn":msisdn, "pin":pin,"AppVersion":"KYC:1.0" }
    }
    resp = requests.post('{}TIMM/v1/SIMREG/Agent/Authenticate'.format(url), data=json.dumps(data))
    logging.info('***** End kyc_kya_auth ****')
    return resp


@app.route("/kyc_kya/agent/login", methods=['POST'])
@cross_origin()
def kyc_kya_login():
    logging.info("**** Begin kyc_kya_login ****")
    r = request.get_json() or {}
    data = r['data']
    # Champs obligatoires
    required_fields = ['msisdn', 'pin']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty"}, 400
    resp = kyc_kya_auth(data['msisdn'], data['pin'])
    custo_inf = kyc_checkParty(data['msisdn'])
    reponse = {"status": "error", "message": "Agent authenticated failed", "code": 400}
    if 'resultset' in resp and 'resultset' in custo_inf.text:
        resp['resultset']["details"] = custo_inf.json().get("resultset", None)
        reponse = {"status": "success", "message": "Agent authenticated successfully", "items": resp.json().get("resultset", None), "code": 200}
    logging.info("**** End kyc_kya_login ****")
    return reponse


@app.route("/kyc/agent/statistics", methods=['POST'])
@cross_origin()
def agent_statistics():
    logging.info("**** Begin agent_statistics ****")
    r = request.get_json() or {}
    data = r['data']
    # Champs obligatoires
    required_fields = ['msisdn', 'pin']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty"}, 400

    resp = kyc_kya_auth(data['msisdn'], data['pin'])
    if resp['exec_code']==200:
        agentID = resp['resultset']['AgentID']
        username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
        password = utilities.decrypt_password_lite(password)
        data = {
            "auth":{ "user":username, "pwd": password},
            "param":{"AGENTID":agentID}
        }
        logging.info('***** Request : {} - date_action {} ****'.format(data, datetime.now()))
        res = requests.get('{}TIMM/v1/SIMREG/Agent/Statistics'.format(url), data=json.dumps(data))
        logging.info('***** Response : {} - date_action {} ****'.format(res, datetime.now()))
        res = res.json()
        week = getWeekDate()
        if res["exec_code"]>=0:
            i=0
            if 'resultset' in res:
                for item in res["resultset"]:
                    if item["Date"]>=str(week["week_start"]) and item["Date"]<=str(week["week_end"]):
                        now =datetime.strptime(item["Date"], '%Y-%m-%d')
                        i = now.weekday()
                        week["data_type"]["statAll"]["registriesValues"][i]["value"] = int(item["GSMOMRegistrations"])+int(item["GSMRegistrations"])
                        week["data_type"]["statSim"]["registriesValues"][i]["value"] = int(item["GSMRegistrations"])
                        week["data_type"]["statOm"]["registriesValues"][i]["value"] = int(item["GSMOMRegistrations"])
                    i+=1
            res["resultset"] = week["data_type"]
        response = {"status":"success","message":"Agent statistics retrieved successfully !", "items": res["resultset"], "code": 200}
    else:
        response = {"status":"error","message":"Agent authentication failed !", "code": 400}
    logging.info("**** End agent_statistics ****")
    return response


def registerGSM(data, username, password):
    data_gsm = {
            "auth":{ "user":username, "pwd": password},
            "param":{
                "Documents":[
                {
                    "Type":"FACE",
                    "FORMAT":"JPEG",
                    "IMG":data['customer_image'].replace("\n", "")
                },
                {
                    "Type":"IDCARD",
                    "FORMAT":"JPEG",
                    "IMG":data['id_document_image'].replace("\n", "")
                },
                {
                    "Type":"IDCARDBACK",
                    "FORMAT":"JPEG",
                    "IMG": data['id_document_image_back'].replace("\n", "") if data['id_document_image_back'] else data['id_document_image'].replace("\n", "")
                },
            ],
                "Reg": {
                    "RegType":"GSM",
                    "MSISDN": data['msisdn'],
                    "ICCID": data['iccid'],
                    "FName": data['first_name'],
                    "LName": data['last_name'],
                    "BDay": data['birth_date'],
                    "BPlace": data['birth_place'],
                    "GenderID": data['gender_id'],
                    "IDCard": data['id_card_Number'],
                    "IDCardType": data['id_card_type_id'],
                    "OccupationID": data['occupation_id'],
                    "ADDTypeID": data['address_types_id'],
                    "ADDCounty": data['county_id'],
                    "Address": data['address'],
                    "eMail": data['email'],
                    "CountryID": data['country_id'],
                    "WorkAddress": data['workaddress'],
                    "RegDate":data['reg_date'],
                    "KName":data['k_name'],
                    "AgentMSISDN": data['agentmsisdn'],
                    "AgentIMEI": data['agentimei'] if data['agentimei'] else data['agentdeviceId'],
                    "AgentICCID": data['agenticcid'] if data['agenticcid'] else data['agentmsisdn'],
                    "AppVersion":data['app_version'] if data['app_version'] else "KYC:1.0",
                    "LAT": data['latitude'],
                    "LNG": data['longitude'],
                    "CellID":data['cell_id'],
                    "KINName": data['kin_name'],
                    "KINPhone": data['kin_phone'],
                    "KINEmail": data['kin_email']
                }
            }
        }
    return data_gsm


def registerOM(data, username, password):
    data_om = {
            "auth":{"user":username, "pwd":password },
            "param":{
                "Documents":[
                {
                    "Type":"Face",
                    "Format":"JPEG",
                    "Img":data['customer_image'].replace("\n", "")
                },
                {
                    "Type":"IDCard",
                    "Format":"JPEG",
                    "Img":data['id_document_image'].replace("\n", "")
                },
                {
                    "Type":"IDCARDBACK",
                    "FORMAT":"JPEG",
                    "IMG": data['id_document_image_back'].replace("\n", "") if data['id_document_image_back'] else data['id_document_image'].replace("\n", "")
                },
                {
                    "Type":"Contract",
                    "Format":"JPEG",
                    "Img":data['contract_image'].replace("\n", "")
                }
            ],
            "Reg": {
                "RegType":"OM",
                "MSISDN": data['msisdn'],
                "ICCID": data['iccid'],
                "FName": data['first_name'],
                "LName": data['last_name'],
                "BDay": data['birth_date'],
                "BPlace": data['birth_place'],
                "GenderID": data['gender_id'],
                "IDCard": data['id_card_Number'],
                "IDCardType": data['id_card_type_id'],
                "OccupationID": data['occupation_id'],
                "ADDTypeID": data['address_types_id'],
                "ADDCounty": data['county_id'],
                "Address": data['address'],
                "eMail": data['email'],
                "CountryID": data['country_id'],
                "WorkAddress": data['workaddress'],
                "RegDate":data['reg_date'],
                "KName":data['k_name'],
                "AgentMSISDN": data['agentmsisdn'],
                "AgentIMEI": data['agentimei'] if data['agentimei'] else data['agentdeviceId'],
                "AgentICCID": data['agenticcid'] if data['agenticcid'] else data['agentmsisdn'],
                "AppVersion":data['app_version'] if data['app_version'] else "KYC:1.0",
                "LAT": data['latitude'],
                "LNG": data['longitude'],
                "CellID":data['cell_id'],
                "KINName": data['kin_name'],
                "KINPhone": data['kin_phone'],
                "KINEmail": data['kin_email'],
                "AGENTPINENC": data['agent_pin'].replace("\n", "")
            }
        }
    }

    return data_om



@app.route("/kyc/custorms/add", methods=['POST'])
@cross_origin()
def custorms_add():
    logging.info("**** Begin custorms_add ****")
    r = request.get_json() or {}
    data = r['data']
    resp = kyc_kya_auth(data['msisdn'], data['pin'])
    if resp['exec_code']==200:
        username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
        password = utilities.decrypt_password_lite(password)
        if (data['RegType'] == 'GSM'):
            data = registerGSM(data, username, password)
        elif (data['RegType'] == 'OM'):
            data = registerOM(data, username, password)
        else:
            response = {"status":"error", "message":"Invalid registration type !", "code": 400}
            return response
        res = requests.post('{}TIMM/v1/SIMREG/Subscriber/Register'.format(url), data=json.dumps(data))
        response = {"status":"success", "message":"Customer added successfully !", "items": res.json(), "code": 200}
    else:
        response = {"status":"error", "message":"Customer authentication failed !", "code": 400}
        
    logging.info("**** End custorms_add ****")
    return response




@app.route("/kyc/custorms/check", methods=['POST'])
@cross_origin()
def custorms_check():
    logging.info("**** Begin custorms_check ****")
    r = request.get_json() or {}
    data = r['data']
    resp = kyc_kya_auth(data['msisdn'], data['pin'])
    if resp['exec_code']==200:
        res = kyc_checkParty(data['msisdn'])
        response = {"status":"success", "message":"Customer checked successfully !", "items": res.json(), "code": 200}
    else:
        response = {"status":"error", "message":"Customer authentication failed !", "code": 400}
    logging.info("**** End custorms_check ****")
    return response


@app.route("/kyc/type/county", methods=['POST'])
@cross_origin()
def county_type():
    logging.info("**** Begin county_type ****")
    r = request.get_json() or {}
    data = r['data']
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{ "user":username, "pwd": password}
        }
    res = requests.get('{}TIMM/v1/CRM/Types/County'.format(url), data=json.dumps(data))
    res = res.json()
    response = {"status": res.get("exec_code", None), "message": res.get("message", None), "items": res.get("resultset", None), "code": 200}
    logging.info("**** End county_type ****")
    return response


@app.route("/kyc/types/county", methods=['POST'])
@cross_origin()
def county_types():
    logging.info("**** Begin county_types ****")
    r = request.get_json() or {}
    data = r['data']
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{ "user":username, "pwd": password}
        }
    res = requests.get('{}TIMM/v1/CRM/Types/Country'.format(url), data=json.dumps(data))
    res = res.json()
    response = {"status": res.get("exec_code", None), "message": res.get("message", None), "items": res.get("resultset", None), "code": 200}
    logging.info("**** End county_types ****")
    return response


@app.route("/kyc/types/gender", methods=['POST'])
@cross_origin()
def gender_type():
    logging.info("**** Begin gender_type ****")
    r = request.get_json() or {}
    data = r['data']
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{ "user":username, "pwd": password}
        }
    res = requests.get('{}TIMM/v1/CRM/Types/Gender'.format(url), data=json.dumps(data))
    res = res.json()
    response = {"status": res.get("exec_code", None), "message": res.get("message", None), "items": res.get("resultset", None), "code": 200}
    logging.info("**** End gender_type ****")
    return response


@app.route("/kyc/types/occupation", methods=['POST'])
@cross_origin()
def get_occupation():
    logging.info("**** Begin occupation ****")
    r = request.get_json() or {}
    data = r['data']
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{ "user":username, "pwd": password}
        }
    res = requests.get('{}TIMM/v1/CRM/Types/Occupation'.format(url), data=json.dumps(data))
    res = res.json()
    response = {"status": res.get("exec_code", None), "message": res.get("message", None), "items": res.get("resultset", None), "code": 200}
    logging.info("**** End occupation ****")
    return response


@app.route("/kyc/types/document_id", methods=['POST'])
@cross_origin()
def get_document_id():  
    logging.info("**** Begin document_id ****")
    r = request.get_json() or {}
    data = r['data']
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{ "user":username, "pwd": password}
        }
    res = requests.get('{}TIMM/v1/CRM/Types/Document/ID'.format(url), data=json.dumps(data))
    res = res.json()
    response = {"status": res.get("exec_code", None), "message": res.get("message", None), "items": res.get("resultset", None), "code": 200}
    logging.info("**** End document_id ****")
    return response


@app.route("/kyc/types/address", methods=['POST'])
@cross_origin()
def get_address():  
    logging.info("**** Begin address ****")
    r = request.get_json() or {}
    data = r['data']
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data = {
            "auth":{ "user":username, "pwd": password}
        }
    res = requests.get('{}TIMM/v1/CRM/Types/Address'.format(url), data=json.dumps(data))
    res = res.json()
    response = {"status": res.get("exec_code", None), "message": res.get("message", None), "items": res.get("resultset", None), "code": 200}
    logging.info("**** End address ****")
    return response

