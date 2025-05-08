from urllib import response
from flask import request, json, jsonify
import requests
from app import app, db
import logging
from datetime import datetime
import utils.utilities as utilities
from flask_cors import CORS, cross_origin
from models.faces_matching import FacesMatching
from models.actions_logs import ActionsLogs
from models.registration import Registration

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@app.route('/kyc/header/enrichement', methods=['GET'])
@cross_origin()
def get_header_enrichement():
    logging.info("**** Begin get_header_enrichement ****")
    logging.info("/kyc/header/enrichement")
    response = {"status": "success", "message": "Header enrichement retrieved successfully !", "code": 200, "has_error": False}
    logging.info("**** End get_header_enrichement ****")
    return response


def kyc_checkParty(msisdn):
    logging.info('***** Begin checkParty ****')
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data_api = {"auth":{"user":username, "pwd":password }, "param":{"MSISDN":msisdn}}
    res = requests.get('{}TIMM/v1/CRM/Subscriber'.format(url), data=json.dumps(data_api), verify=False)
    logging.info('***** End checkParty ****')
    return res


def kyc_kya_auth(msisdn, pin):
    logging.info('***** Begin kyc_kya_auth ****')
    libelle = "kyc_kya_auth_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc_kya/agent/login", json.dumps({"msisdn":msisdn, "pin":utilities.encrypt_password_lite(pin)}))
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data_api = {"auth":{ "user":username, "pwd": password}, "param":{ "MSISDN":msisdn, "PIN":pin, "CURRENCY":"usd"}}
    resp = requests.post('{}TIMM/v1/OM/Agent/Pin/Check'.format(app.config['TIMM_URL_AUTH']), data=json.dumps(data_api), verify=False)
    resp = resp.json()
    status = None
    if resp['exec_code'] == 200:
        status = "OK"
    else:
        status = "ERROR"
    logging.info('***** response : {} - date_action {} ****'.format(resp, datetime.now()))
    logging.info('***** End kyc_kya_auth ****')
    ActionsLogs.action_logs_final_save(libelle, json.dumps(resp), status)
    return resp


def kyc_agent_auth(msisdn, pin):
    logging.info('***** Begin kyc_agent_auth ****')
    libelle = "kyc_kya_login_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc_kya/agent/login", json.dumps({"msisdn":msisdn, "pin":utilities.encrypt_password_lite(pin)}))
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    data_api = {"auth":{ "user":username, "pwd": password}, "param":{ "MSISDN":msisdn, "AppVersion":"FUSION-KYA-KYC"}}
    logging.info('***** request : {} - date_action {} ****'.format(data_api, datetime.now()))
    resp = requests.post('{}TIMM/v1/SIMREG/Agent/Authenticate'.format(url), data=json.dumps(data_api), verify=False)
    resp = resp.json()
    status = None
    if resp['exec_code'] == 200:
        status = "OK"
    else:
        status = "ERROR"
    logging.info('***** response : {} - date_action {} ****'.format(resp, datetime.now()))
    ActionsLogs.action_logs_final_save(libelle, json.dumps(resp), status)
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
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400
    resp = kyc_kya_auth(data['msisdn'], data['pin'])
    resp = resp.json()
    response = {"status": "error", "message": "Agent authentication failed", "code": 400, "has_error": True}, 400
    if resp['exec_code'] == 200:
        response = {"status": resp['exec_code'], "message": resp['exec_msg'], "items": resp.get("resultset", None), "code": 200, "has_error": False}, 200
    logging.info("**** End kyc_kya_login ****")
    return response


@app.route("/kyc/agent/statistics", methods=['POST'])
@cross_origin()
def agent_statistics():
    logging.info("**** Begin agent_statistics ****")
    r = request.get_json() or {}
    # on save debut des logs dans action logs
    libelle = "agent_statistics_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/agent/statistics", json.dumps(r))
    data = r['data']
    # Champs obligatoires
    required_fields = ['msisdn', 'pin']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400

    resp = kyc_agent_auth(data['msisdn'], data['pin'])
    resp = resp.json()
    status = "ERROR"
    if resp['exec_code'] == 200:
        agentID = resp['resultset']['AgentID']
        username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
        password = utilities.decrypt_password_lite(password)
        data_api = {"auth":{ "user":username, "pwd": password}, "param":{"AGENTID":agentID}}
        logging.info('***** Request : {} - date_action {} ****'.format(data_api, datetime.now()))
        res = requests.get('{}TIMM/v1/SIMREG/Agent/Statistics'.format(url), data=json.dumps(data_api), verify=False)
        logging.info('***** Response : {} - date_action {} ****'.format(res, datetime.now()))
        res = res.json()
        week = getWeekDate()
        if res["exec_code"]>=0:
            status = "OK"
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
        response = {"status":status, "message":"Agent statistics retrieved successfully !", "items": res["resultset"], "code": 200, "has_error": False}, 200
    else:
        response = {"status": status, "message":"Agent authentication failed !", "code": 400, "has_error": True}, 400
    logging.info("**** End agent_statistics ****")
    # on save fin de logs dans action logs
    response_body, status_code = response
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response_body), status)
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
                    "BDay": datetime.strptime(data['birth_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d"),
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
                    "RegDate":datetime.strptime(data['reg_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d"),
                    "KName":data['k_name'],
                    "AgentMSISDN": data['agentmsisdn'],
                    "AgentIMEI": data['agentimei'] if data['agentimei'] else data['agentdeviceId'],
                    "AgentICCID": data['agenticcid'] if data['agenticcid'] else data['agentmsisdn'],
                    "AppVersion":"FUSION-KYA-KYC",
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
                "BDay": datetime.strptime(data['birth_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d"),
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
                "RegDate":datetime.strptime(data['reg_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d"),
                "KName":data['k_name'],
                "AgentMSISDN": data['agentmsisdn'],
                "AgentIMEI": data['agentimei'] if data['agentimei'] else data['agentdeviceId'],
                "AgentICCID": data['agenticcid'] if data['agenticcid'] else data['agentmsisdn'],
                "AppVersion":"FUSION-KYA-KYC",
                "LAT": data['latitude'],
                "LNG": data['longitude'],
                "CellID":data['cell_id'],
                "KINName": data['kin_name'],
                "KINPhone": data['kin_phone'],
                "KINEmail": data['kin_email'],
                "AgentPIN": data['agent_pin'].replace("\n", "")
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
    # on save debut des logs dans action logs
    libelle = "custorms_add_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    # On copie les données pour les logs sans agent_pin
    log_data = r.copy()
    log_data['data'] = data.copy()
    log_data['data']['agent_pin'] = "****"  # masquer la donnée sensible
    msisdn = data['msisdn']
    logging.info("MSISDN : {} ".format(msisdn))
    ActionsLogs.action_logs_init_save(libelle, "/kyc/custorms/add", json.dumps(log_data), msisdn)
    # Champs obligatoires
    required_fields = ['county_id', 'address','address_types_id','agentmsisdn','birth_date', 'birth_place', 'country_id', 'first_name', 
                    'gender_id', 'id_card_Number', 'id_card_type_id', 'last_name', 'msisdn', 'occupation_id', 'reg_date', 'workaddress']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400
        
    username, password, url = utilities.get_timm_user_password("Fision KYC KYA")
    password = utilities.decrypt_password_lite(password)
    # on fait appel a la fonction de save face_matching
    portrait_seamfix_verify_lite(data['customer_image'], data['customer_image_ocr'])
    save_registration(data)
    reg_type = data.get('reg_type')
    logging.info("Registration type : {} ".format(reg_type))
    if (reg_type == 'GSM'):
        data_api = registerGSM(data, username, password)
    elif (reg_type == 'OM'):
        data_api = registerOM(data, username, password)
    else:
        response = {"status":"error", "message":"Invalid registration type !", "code": 400, "has_error": True}, 400
        return response
    res = requests.post('{}TIMM/v1/SIMREG/Subscriber/Register'.format(url), data=json.dumps(data_api), verify=False)
    res_json = res.json()
    exec_code = res_json.get('exec_code')
    status = None
    if exec_code > 0:
        status = "OK"
        response = {"status": status, "message":"Customer added successfully !", "items": res.json(), "code": exec_code, "has_error": False}, 200
    else:
        status = "ERROR"
        response = {"status": status, "message":"Customer added failed !", "items": res.json(), "code": exec_code, "has_error": True}, 400
    logging.info("**** End custorms_add ****")
    # on save fin de logs dans action logs
    response_body, status_code = response
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response_body), status, msisdn)
    return response



@app.route("/kyc/custorms/check", methods=['POST'])
@cross_origin()
def custorms_check():
    logging.info("**** Begin custorms_check ****")
    r = request.get_json() or {}
    # on save debut des logs dans action logs
    libelle = "custorms_check_"+datetime.now().strftime("%Y%m%d_%H%M%S")
    ActionsLogs.action_logs_init_save(libelle, "/kyc/custorms/check", json.dumps(r))
    data = r['data']
    # Champs obligatoires
    required_fields = ['msisdn', 'pin']
    for field in required_fields:
        if field not in data or not data[field]:
            return {"status": "error", "message": f"Field {field} is missing or empty", "code": 400, "has_error": True}, 400
    resp = kyc_kya_auth(data['msisdn'], data['pin'])
    if resp['exec_code']==200:
        res = kyc_checkParty(data['msisdn'])
        response = {"status":"success", "message":"Customer checked successfully !", "items": res.json(), "code": 200, "has_error": False}, 200
    else:
        response = {"status":"error", "message":"Customer authentication failed !", "code": 400, "has_error": True}, 400
    logging.info("**** End custorms_check ****")
    # on save fin de logs dans action logs
    response_body, status_code = response
    ActionsLogs.action_logs_final_save(libelle, json.dumps(response_body), response_body.get("status"))
    return response


@app.route("/kyc/type/county", methods=['POST'])
@cross_origin()
def county_type():
    logging.info("**** Begin county_type ****")
    r = request.get_json() or {}
    response = {
            "code": 200,
            "has_error": False,
            "items": [
                {
                    "CountyID": "13",
                    "Description": "Montserrado"
                },{
                    "CountyID": "1",
                    "Description": "Bomi"
                },{
                    "CountyID": "2",
                    "Description": "Bong"
                },{
                    "CountyID": "4",
                    "Description": "Gbarpolu"
                },{
                    "CountyID": "6",
                    "Description": "Grand Bassa"
                },{
                    "CountyID": "7",
                    "Description": "Grand Cape Mount"
                },{
                    "CountyID": "8",
                    "Description": "Grand Gedeh"
                },{
                    "CountyID": "9",
                    "Description": "Grand Kru"
                },{
                    "CountyID": "10",
                    "Description": "Lofa"
                },{
                    "CountyID": "11",
                    "Description": "Margibi"
                },{
                    "CountyID": "12",
                    "Description": "Maryland"
                },{
                    "CountyID": "14",
                    "Description": "Nimba"
                },{
                    "CountyID": "15",
                    "Description": "Rivercess"
                },{
                    "CountyID": "16",
                    "Description": "River Gee"
                },{
                    "CountyID": "18",
                    "Description": "Sinoe"
                }
            ],
            "message": "Success",
            "status": 0
        }
    logging.info("**** End county_type ****")
    return response


@app.route("/kyc/types/country", methods=['POST'])
@cross_origin()
def county_types():
    logging.info("**** Begin county_types ****")
    r = request.get_json() or {}
    response = {
            "code": 200,
            "has_error": False,
            "items": [
                {
                    "CCode": "231",
                    "CountryID": "44",
                    "Description": "Liberia",
                    "ISO3166": "LBR"
                },{
                    "CCode": "234",
                    "CountryID": "47",
                    "Description": "Nigeria",
                    "ISO3166": "NGA"
                },{
                    "CCode": "224",
                    "CountryID": "37",
                    "Description": "Guinea",
                    "ISO3166": "GIN"
                },{
                    "CCode": "232",
                    "CountryID": "45",
                    "Description": "Sierra Leone",
                    "ISO3166": "SLE"
                },{
                    "CCode": "233",
                    "CountryID": "46",
                    "Description": "Ghana",
                    "ISO3166": "GHA"
                },{
                    "CCode": "1",
                    "CountryID": "22",
                    "Description": "United States",
                    "ISO3166": "USA"
                },{
                    "CCode": "225",
                    "CountryID": "38",
                    "Description": "Cote D'Ivoire",
                    "ISO3166": "CIV"
                },{
                    "CCode": "91",
                    "CountryID": "248",
                    "Description": "India",
                    "ISO3166": "IND"
                },{
                    "CCode": "961",
                    "CountryID": "254",
                    "Description": "Lebanon",
                    "ISO3166": "LBN"
                },{
                    "CCode": "223",
                    "CountryID": "36",
                    "Description": "Mali",
                    "ISO3166": "MLI"
                },{
                    "CCode": "93",
                    "CountryID": "250",
                    "Description": "Afghanistan",
                    "ISO3166": "AFG"
                },{
                    "CCode": "358",
                    "CountryID": "112",
                    "Description": "Aland Islands",
                    "ISO3166": "ALA"
                },{
                    "CCode": "355",
                    "CountryID": "109",
                    "Description": "Albania",
                    "ISO3166": "ALB"
                },{
                    "CCode": "213",
                    "CountryID": "30",
                    "Description": "Algeria",
                    "ISO3166": "DZA"
                },{
                    "CCode": "1",
                    "CountryID": "3",
                    "Description": "American Samoa",
                    "ISO3166": "ASM"
                },{
                    "CCode": "376",
                    "CountryID": "123",
                    "Description": "Andorra",
                    "ISO3166": "AND"
                },{
                    "CCode": "244",
                    "CountryID": "57",
                    "Description": "Angola",
                    "ISO3166": "AGO"
                },{
                    "CCode": "1",
                    "CountryID": "2",
                    "Description": "Anguilla",
                    "ISO3166": "AIA"
                },{
                    "CCode": "672",
                    "CountryID": "197",
                    "Description": "Antarctica",
                    "ISO3166": "ATA"
                },{
                    "CCode": "672",
                    "CountryID": "196",
                    "Description": "Antarctica & Norfolk Island",
                    "ISO3166": "AQ2"
                },{
                    "CCode": "1",
                    "CountryID": "1",
                    "Description": "Antigua and Barbuda",
                    "ISO3166": "ATG"
                },{
                    "CCode": "54",
                    "CountryID": "170",
                    "Description": "Argentina",
                    "ISO3166": "ARG"
                },{
                    "CCode": "374",
                    "CountryID": "121",
                    "Description": "Armenia",
                    "ISO3166": "ARM"
                },{
                    "CCode": "297",
                    "CountryID": "93",
                    "Description": "Aruba",
                    "ISO3166": "ABW"
                },{
                    "CCode": "247",
                    "CountryID": "60",
                    "Description": "Ascension Island",
                    "ISO3166": "ASC"
                },{
                    "CCode": "61",
                    "CountryID": "187",
                    "Description": "Australia",
                    "ISO3166": "AUS"
                },{
                    "CCode": "61",
                    "CountryID": "186",
                    "Description": "Australia & Christmas Island & Cocos Island",
                    "ISO3166": "AU2"
                },{
                    "CCode": "43",
                    "CountryID": "144",
                    "Description": "Austria",
                    "ISO3166": "AUT"
                },{
                    "CCode": "994",
                    "CountryID": "275",
                    "Description": "Azerbaijan",
                    "ISO3166": "AZE"
                },{
                    "CCode": "1",
                    "CountryID": "6",
                    "Description": "Bahamas",
                    "ISO3166": "BHS"
                },{
                    "CCode": "973",
                    "CountryID": "265",
                    "Description": "Bahrain",
                    "ISO3166": "BHR"
                },{
                    "CCode": "880",
                    "CountryID": "241",
                    "Description": "Bangladesh",
                    "ISO3166": "BGD"
                },{
                    "CCode": "1",
                    "CountryID": "4",
                    "Description": "Barbados",
                    "ISO3166": "BRB"
                },{
                    "CCode": "375",
                    "CountryID": "122",
                    "Description": "Belarus",
                    "ISO3166": "BLR"
                },{
                    "CCode": "32",
                    "CountryID": "98",
                    "Description": "Belgium",
                    "ISO3166": "BEL"
                },{
                    "CCode": "501",
                    "CountryID": "158",
                    "Description": "Belize",
                    "ISO3166": "BLZ"
                },{
                    "CCode": "229",
                    "CountryID": "42",
                    "Description": "Benin",
                    "ISO3166": "BEN"
                },{
                    "CCode": "1",
                    "CountryID": "5",
                    "Description": "Bermuda",
                    "ISO3166": "BMU"
                },{
                    "CCode": "975",
                    "CountryID": "267",
                    "Description": "Bhutan",
                    "ISO3166": "BTN"
                },{
                    "CCode": "591",
                    "CountryID": "176",
                    "Description": "Bolivia",
                    "ISO3166": "BOL"
                },{
                    "CCode": "387",
                    "CountryID": "133",
                    "Description": "Bosnia and Herzegovina",
                    "ISO3166": "BIH"
                },{
                    "CCode": "267",
                    "CountryID": "84",
                    "Description": "Botswana",
                    "ISO3166": "BWA"
                },{
                    "CCode": "55",
                    "CountryID": "171",
                    "Description": "Brazil",
                    "ISO3166": "BRA"
                },{
                    "CCode": "246",
                    "CountryID": "59",
                    "Description": "British Indian Ocean Territory",
                    "ISO3166": "IOT"
                },{
                    "CCode": "673",
                    "CountryID": "199",
                    "Description": "Brunei Darussalam",
                    "ISO3166": "BRN"
                },{
                    "CCode": "359",
                    "CountryID": "115",
                    "Description": "Bulgaria",
                    "ISO3166": "BGR"
                },{
                    "CCode": "226",
                    "CountryID": "39",
                    "Description": "Burkina Faso",
                    "ISO3166": "BFA"
                },{
                    "CCode": "257",
                    "CountryID": "72",
                    "Description": "Burundi",
                    "ISO3166": "BDI"
                },{
                    "CCode": "855",
                    "CountryID": "230",
                    "Description": "Cambodia",
                    "ISO3166": "KHM"
                },{
                    "CCode": "237",
                    "CountryID": "50",
                    "Description": "Cameroon",
                    "ISO3166": "CMR"
                },{
                    "CCode": "1",
                    "CountryID": "7",
                    "Description": "Canada",
                    "ISO3166": "CAN"
                },{
                    "CCode": "34",
                    "CountryID": "103",
                    "Description": "Canary Islands",
                    "ISO3166": ""
                },{
                    "CCode": "238",
                    "CountryID": "51",
                    "Description": "Cape Verde",
                    "ISO3166": "CPV"
                },{
                    "CCode": "1",
                    "CountryID": "14",
                    "Description": "Cayman Islands",
                    "ISO3166": "CYM"
                },{
                    "CCode": "236",
                    "CountryID": "49",
                    "Description": "Central African Republic",
                    "ISO3166": "CAF"
                },{
                    "CCode": "34",
                    "CountryID": "100",
                    "Description": "Ceuta and Melilla",
                    "ISO3166": ""
                },{
                    "CCode": "235",
                    "CountryID": "48",
                    "Description": "Chad",
                    "ISO3166": "TCD"
                },{
                    "CCode": "56",
                    "CountryID": "172",
                    "Description": "Chile",
                    "ISO3166": "CHL"
                },{
                    "CCode": "86",
                    "CountryID": "232",
                    "Description": "China",
                    "ISO3166": "CHN"
                },{
                    "CCode": "61",
                    "CountryID": "189",
                    "Description": "Christmas Island",
                    "ISO3166": "CXR"
                },{
                    "CCode": "61",
                    "CountryID": "188",
                    "Description": "Cocos (Keeling) Island",
                    "ISO3166": "CCK"
                },{
                    "CCode": "57",
                    "CountryID": "173",
                    "Description": "Colombia",
                    "ISO3166": "COL"
                },{
                    "CCode": "269",
                    "CountryID": "86",
                    "Description": "Comoros",
                    "ISO3166": "COM"
                },{
                    "CCode": "269",
                    "CountryID": "87",
                    "Description": "Comoros & Mayotte",
                    "ISO3166": "KM2"
                },{
                    "CCode": "242",
                    "CountryID": "55",
                    "Description": "Congo",
                    "ISO3166": "COG"
                },{
                    "CCode": "243",
                    "CountryID": "56",
                    "Description": "Congo, Democratic Republic of the",
                    "ISO3166": "COD"
                },{
                    "CCode": "682",
                    "CountryID": "208",
                    "Description": "Cook Islands",
                    "ISO3166": "COK"
                },{
                    "CCode": "506",
                    "CountryID": "163",
                    "Description": "Costa Rica",
                    "ISO3166": "CRI"
                },{
                    "CCode": "385",
                    "CountryID": "131",
                    "Description": "Croatia",
                    "ISO3166": "HRV"
                },{
                    "CCode": "53",
                    "CountryID": "169",
                    "Description": "Cuba",
                    "ISO3166": "CUB"
                },{
                    "CCode": "357",
                    "CountryID": "111",
                    "Description": "Cyprus, Republic of",
                    "ISO3166": "CYP"
                },{
                    "CCode": "90",
                    "CountryID": "247",
                    "Description": "Cyprus, Turkish Republic of Northern",
                    "ISO3166": ""
                },{
                    "CCode": "420",
                    "CountryID": "141",
                    "Description": "Czech Republic",
                    "ISO3166": "CZE"
                },{
                    "CCode": "45",
                    "CountryID": "150",
                    "Description": "Denmark",
                    "ISO3166": "DNK"
                },{
                    "CCode": "253",
                    "CountryID": "68",
                    "Description": "Djibouti",
                    "ISO3166": "DJI"
                },{
                    "CCode": "1",
                    "CountryID": "8",
                    "Description": "Dominica",
                    "ISO3166": "DMA"
                },{
                    "CCode": "1",
                    "CountryID": "9",
                    "Description": "Dominican Republic",
                    "ISO3166": "DOM"
                },{
                    "CCode": "593",
                    "CountryID": "178",
                    "Description": "Ecuador",
                    "ISO3166": "ECU"
                },{
                    "CCode": "20",
                    "CountryID": "26",
                    "Description": "Egypt",
                    "ISO3166": "EGY"
                },{
                    "CCode": "503",
                    "CountryID": "160",
                    "Description": "El Salvador",
                    "ISO3166": "SLV"
                },{
                    "CCode": "240",
                    "CountryID": "53",
                    "Description": "Equatorial Guinea",
                    "ISO3166": "GNQ"
                },{
                    "CCode": "291",
                    "CountryID": "92",
                    "Description": "Eritrea",
                    "ISO3166": "ERI"
                },{
                    "CCode": "372",
                    "CountryID": "119",
                    "Description": "Estonia",
                    "ISO3166": "EST"
                },{
                    "CCode": "251",
                    "CountryID": "64",
                    "Description": "Ethiopia",
                    "ISO3166": "ETH"
                },{
                    "CCode": "388",
                    "CountryID": "134",
                    "Description": "European Union",
                    "ISO3166": ""
                },{
                    "CCode": "500",
                    "CountryID": "157",
                    "Description": "Falkland Islands (Malvinas)",
                    "ISO3166": "FLK"
                },{
                    "CCode": "298",
                    "CountryID": "94",
                    "Description": "Faroe Islands",
                    "ISO3166": "FRO"
                },{
                    "CCode": "679",
                    "CountryID": "205",
                    "Description": "Fiji",
                    "ISO3166": "FJI"
                },{
                    "CCode": "358",
                    "CountryID": "114",
                    "Description": "Finland",
                    "ISO3166": "FIN"
                },{
                    "CCode": "358",
                    "CountryID": "113",
                    "Description": "Finland & Aland Islands",
                    "ISO3166": "FI2"
                },{
                    "CCode": "33",
                    "CountryID": "99",
                    "Description": "France",
                    "ISO3166": "FRA"
                },{
                    "CCode": "594",
                    "CountryID": "179",
                    "Description": "French Guiana",
                    "ISO3166": "GUF"
                },{
                    "CCode": "689",
                    "CountryID": "214",
                    "Description": "French Polynesia",
                    "ISO3166": "PYF"
                },{
                    "CCode": "262",
                    "CountryID": "77",
                    "Description": "French Southern and Antarctic Lands",
                    "ISO3166": "ATF"
                },{
                    "CCode": "262",
                    "CountryID": "78",
                    "Description": "French Sthrn and Antct Lands & R�union & Mayotte",
                    "ISO3166": "TF2"
                },{
                    "CCode": "241",
                    "CountryID": "54",
                    "Description": "Gabon",
                    "ISO3166": "GAB"
                },{
                    "CCode": "220",
                    "CountryID": "33",
                    "Description": "Gambia",
                    "ISO3166": "GMB"
                },{
                    "CCode": "995",
                    "CountryID": "276",
                    "Description": "Georgia",
                    "ISO3166": "GEO"
                },{
                    "CCode": "49",
                    "CountryID": "156",
                    "Description": "Germany",
                    "ISO3166": "DEU"
                },{
                    "CCode": "350",
                    "CountryID": "104",
                    "Description": "Gibraltar",
                    "ISO3166": "GIB"
                },{
                    "CCode": "881",
                    "CountryID": "242",
                    "Description": "Global Mobile Satellite System",
                    "ISO3166": ""
                },{
                    "CCode": "30",
                    "CountryID": "96",
                    "Description": "Greece",
                    "ISO3166": "GRC"
                },{
                    "CCode": "299",
                    "CountryID": "95",
                    "Description": "Greenland",
                    "ISO3166": "GRL"
                },{
                    "CCode": "1",
                    "CountryID": "10",
                    "Description": "Grenada",
                    "ISO3166": "GRD"
                },{
                    "CCode": "590",
                    "CountryID": "175",
                    "Description": "Guadeloupe",
                    "ISO3166": "GLP"
                },{
                    "CCode": "1",
                    "CountryID": "11",
                    "Description": "Guam",
                    "ISO3166": "GUM"
                },{
                    "CCode": "502",
                    "CountryID": "159",
                    "Description": "Guatemala",
                    "ISO3166": "GTM"
                },{
                    "CCode": "44",
                    "CountryID": "146",
                    "Description": "Guernsey",
                    "ISO3166": "GGY"
                },{
                    "CCode": "245",
                    "CountryID": "58",
                    "Description": "Guinea-Bissau",
                    "ISO3166": "GNB"
                },{
                    "CCode": "592",
                    "CountryID": "177",
                    "Description": "Guyana",
                    "ISO3166": "GUY"
                },{
                    "CCode": "509",
                    "CountryID": "166",
                    "Description": "Haiti",
                    "ISO3166": "HTI"
                },{
                    "CCode": "39",
                    "CountryID": "138",
                    "Description": "Holy See (Vatican City State)",
                    "ISO3166": "VAT"
                },{
                    "CCode": "504",
                    "CountryID": "161",
                    "Description": "Honduras",
                    "ISO3166": "HND"
                },{
                    "CCode": "852",
                    "CountryID": "228",
                    "Description": "Hong Kong",
                    "ISO3166": "HKG"
                },{
                    "CCode": "36",
                    "CountryID": "116",
                    "Description": "Hungary",
                    "ISO3166": "HUN"
                },{
                    "CCode": "354",
                    "CountryID": "108",
                    "Description": "Iceland",
                    "ISO3166": "ISL"
                },{
                    "CCode": "62",
                    "CountryID": "190",
                    "Description": "Indonesia",
                    "ISO3166": "IDN"
                },{
                    "CCode": "871",
                    "CountryID": "234",
                    "Description": "Inmarsat Atlantic Ocean-East",
                    "ISO3166": ""
                },{
                    "CCode": "874",
                    "CountryID": "239",
                    "Description": "Inmarsat Atlantic Ocean-West",
                    "ISO3166": ""
                },{
                    "CCode": "873",
                    "CountryID": "238",
                    "Description": "Inmarsat Indian Ocean",
                    "ISO3166": ""
                },{
                    "CCode": "872",
                    "CountryID": "237",
                    "Description": "Inmarsat Pacific Ocean",
                    "ISO3166": ""
                },{
                    "CCode": "870",
                    "CountryID": "233",
                    "Description": "Inmarsat Single Network Access Code",
                    "ISO3166": ""
                },{
                    "CCode": "800",
                    "CountryID": "222",
                    "Description": "International Freephone Service",
                    "ISO3166": "XTN"
                },{
                    "CCode": "882",
                    "CountryID": "243",
                    "Description": "International Networks",
                    "ISO3166": "XVS"
                },{
                    "CCode": "979",
                    "CountryID": "270",
                    "Description": "International Premium Rate Service",
                    "ISO3166": "XRM"
                },{
                    "CCode": "991",
                    "CountryID": "272",
                    "Description": "International Public Correspondence Service",
                    "ISO3166": "XCN"
                },{
                    "CCode": "808",
                    "CountryID": "223",
                    "Description": "International Shared Cost Service",
                    "ISO3166": "XSA"
                },{
                    "CCode": "98",
                    "CountryID": "271",
                    "Description": "Iran",
                    "ISO3166": "IRN"
                },{
                    "CCode": "964",
                    "CountryID": "257",
                    "Description": "Iraq",
                    "ISO3166": "IRQ"
                },{
                    "CCode": "353",
                    "CountryID": "107",
                    "Description": "Ireland",
                    "ISO3166": "IRL"
                },{
                    "CCode": "44",
                    "CountryID": "147",
                    "Description": "Isle of Man",
                    "ISO3166": "IMN"
                },{
                    "CCode": "972",
                    "CountryID": "264",
                    "Description": "Israel",
                    "ISO3166": "ISR"
                },{
                    "CCode": "39",
                    "CountryID": "137",
                    "Description": "Italy",
                    "ISO3166": "ITA"
                },{
                    "CCode": "39",
                    "CountryID": "136",
                    "Description": "Italy & Holy See (Vatican City State)",
                    "ISO3166": "IT2"
                },{
                    "CCode": "1",
                    "CountryID": "12",
                    "Description": "Jamaica",
                    "ISO3166": "JAM"
                },{
                    "CCode": "81",
                    "CountryID": "224",
                    "Description": "Japan",
                    "ISO3166": "JPN"
                },{
                    "CCode": "44",
                    "CountryID": "148",
                    "Description": "Jersey",
                    "ISO3166": "JEY"
                },{
                    "CCode": "962",
                    "CountryID": "255",
                    "Description": "Jordan",
                    "ISO3166": "JOR"
                },{
                    "CCode": "7",
                    "CountryID": "219",
                    "Description": "Kazakhstan",
                    "ISO3166": "KAZ"
                },{
                    "CCode": "254",
                    "CountryID": "69",
                    "Description": "Kenya",
                    "ISO3166": "KEN"
                },{
                    "CCode": "686",
                    "CountryID": "211",
                    "Description": "Kiribati",
                    "ISO3166": "KIR"
                },{
                    "CCode": "850",
                    "CountryID": "227",
                    "Description": "Korea, Democratic People's Republic of",
                    "ISO3166": "PRK"
                },{
                    "CCode": "82",
                    "CountryID": "225",
                    "Description": "Korea, Republic of",
                    "ISO3166": "KOR"
                },{
                    "CCode": "383",
                    "CountryID": "281",
                    "Description": "Kosovo",
                    "ISO3166": "KSV"
                },{
                    "CCode": "965",
                    "CountryID": "258",
                    "Description": "Kuwait",
                    "ISO3166": "KWT"
                },{
                    "CCode": "996",
                    "CountryID": "277",
                    "Description": "Kyrgyz Republic",
                    "ISO3166": "KGZ"
                },{
                    "CCode": "856",
                    "CountryID": "231",
                    "Description": "Laos",
                    "ISO3166": "LAO"
                },{
                    "CCode": "371",
                    "CountryID": "118",
                    "Description": "Latvia",
                    "ISO3166": "LVA"
                },{
                    "CCode": "266",
                    "CountryID": "83",
                    "Description": "Lesotho",
                    "ISO3166": "LSO"
                },{
                    "CCode": "218",
                    "CountryID": "32",
                    "Description": "Libya",
                    "ISO3166": "LBY"
                },{
                    "CCode": "423",
                    "CountryID": "143",
                    "Description": "Liechtenstein",
                    "ISO3166": "LIE"
                },{
                    "CCode": "370",
                    "CountryID": "117",
                    "Description": "Lithuania",
                    "ISO3166": "LTU"
                },{
                    "CCode": "352",
                    "CountryID": "106",
                    "Description": "Luxembourg",
                    "ISO3166": "LUX"
                },{
                    "CCode": "853",
                    "CountryID": "229",
                    "Description": "Macao",
                    "ISO3166": "MAC"
                },{
                    "CCode": "389",
                    "CountryID": "135",
                    "Description": "Macedonia",
                    "ISO3166": "MKD"
                },{
                    "CCode": "261",
                    "CountryID": "75",
                    "Description": "Madagascar",
                    "ISO3166": "MDG"
                },{
                    "CCode": "265",
                    "CountryID": "82",
                    "Description": "Malawi",
                    "ISO3166": "MWI"
                },{
                    "CCode": "60",
                    "CountryID": "185",
                    "Description": "Malaysia",
                    "ISO3166": "MYS"
                },{
                    "CCode": "960",
                    "CountryID": "253",
                    "Description": "Maldives",
                    "ISO3166": "MDV"
                },{
                    "CCode": "356",
                    "CountryID": "110",
                    "Description": "Malta",
                    "ISO3166": "MLT"
                },{
                    "CCode": "692",
                    "CountryID": "217",
                    "Description": "Marshall Islands",
                    "ISO3166": "MHL"
                },{
                    "CCode": "596",
                    "CountryID": "181",
                    "Description": "Martinique",
                    "ISO3166": "MTQ"
                },{
                    "CCode": "222",
                    "CountryID": "35",
                    "Description": "Mauritania",
                    "ISO3166": "MRT"
                },{
                    "CCode": "230",
                    "CountryID": "43",
                    "Description": "Mauritius",
                    "ISO3166": "MUS"
                },{
                    "CCode": "262",
                    "CountryID": "79",
                    "Description": "Mayotte",
                    "ISO3166": "MYT"
                },{
                    "CCode": "52",
                    "CountryID": "168",
                    "Description": "Mexico",
                    "ISO3166": "MEX"
                },{
                    "CCode": "691",
                    "CountryID": "216",
                    "Description": "Micronesia",
                    "ISO3166": "FSM"
                },{
                    "CCode": "373",
                    "CountryID": "120",
                    "Description": "Moldova",
                    "ISO3166": "MDA"
                },{
                    "CCode": "377",
                    "CountryID": "124",
                    "Description": "Monaco",
                    "ISO3166": "MCO"
                },{
                    "CCode": "976",
                    "CountryID": "268",
                    "Description": "Mongolia",
                    "ISO3166": "MNG"
                },{
                    "CCode": "382",
                    "CountryID": "130",
                    "Description": "Montenegro",
                    "ISO3166": "MNE"
                },{
                    "CCode": "381",
                    "CountryID": "129",
                    "Description": "Montenegro",
                    "ISO3166": "XMN"
                },{
                    "CCode": "1",
                    "CountryID": "17",
                    "Description": "Montserrat",
                    "ISO3166": "MSR"
                },{
                    "CCode": "212",
                    "CountryID": "29",
                    "Description": "Morocco",
                    "ISO3166": "MAR"
                },{
                    "CCode": "212",
                    "CountryID": "28",
                    "Description": "Morocco & Western Sahara",
                    "ISO3166": "MA2"
                },{
                    "CCode": "258",
                    "CountryID": "73",
                    "Description": "Mozambique",
                    "ISO3166": "MOZ"
                },{
                    "CCode": "95",
                    "CountryID": "252",
                    "Description": "Myanmar",
                    "ISO3166": "MMR"
                },{
                    "CCode": "264",
                    "CountryID": "81",
                    "Description": "Namibia",
                    "ISO3166": "NAM"
                },{
                    "CCode": "674",
                    "CountryID": "200",
                    "Description": "Nauru",
                    "ISO3166": "NRU"
                },{
                    "CCode": "977",
                    "CountryID": "269",
                    "Description": "Nepal",
                    "ISO3166": "NPL"
                },{
                    "CCode": "31",
                    "CountryID": "97",
                    "Description": "Netherlands",
                    "ISO3166": "NLD"
                },
                {
                    "CCode": "599",
                    "CountryID": "184",
                    "Description": "Netherlands Antilles",
                    "ISO3166": "ANT"
                },{
                    "CCode": "687",
                    "CountryID": "212",
                    "Description": "New Caledonia",
                    "ISO3166": "NCL"
                },{
                    "CCode": "64",
                    "CountryID": "192",
                    "Description": "New Zealand",
                    "ISO3166": "NZL"
                },{
                    "CCode": "505",
                    "CountryID": "162",
                    "Description": "Nicaragua",
                    "ISO3166": "NIC"
                },{
                    "CCode": "227",
                    "CountryID": "40",
                    "Description": "Niger",
                    "ISO3166": "NER"
                },{
                    "CCode": "683",
                    "CountryID": "209",
                    "Description": "Niue",
                    "ISO3166": "NIU"
                },{
                    "CCode": "672",
                    "CountryID": "198",
                    "Description": "Norfolk Island",
                    "ISO3166": "NFK"
                },{
                    "CCode": "1",
                    "CountryID": "16",
                    "Description": "Northern Mariana Islands",
                    "ISO3166": "MNP"
                },{
                    "CCode": "47",
                    "CountryID": "153",
                    "Description": "Norway",
                    "ISO3166": "NOR"
                },{
                    "CCode": "47",
                    "CountryID": "152",
                    "Description": "Norway & Svalbard and Jan Mayen",
                    "ISO3166": "NO2"
                },{
                    "CCode": "968",
                    "CountryID": "261",
                    "Description": "Oman",
                    "ISO3166": "OMN"
                },{
                    "CCode": "92",
                    "CountryID": "249",
                    "Description": "Pakistan",
                    "ISO3166": "PAK"
                },{
                    "CCode": "680",
                    "CountryID": "206",
                    "Description": "Palau",
                    "ISO3166": "PLW"
                },{
                    "CCode": "970",
                    "CountryID": "262",
                    "Description": "Palestine",
                    "ISO3166": "PSE"
                },{
                    "CCode": "507",
                    "CountryID": "164",
                    "Description": "Panama",
                    "ISO3166": "PAN"
                },{
                    "CCode": "675",
                    "CountryID": "201",
                    "Description": "Papua New Guinea",
                    "ISO3166": "PNG"
                },{
                    "CCode": "595",
                    "CountryID": "180",
                    "Description": "Paraguay",
                    "ISO3166": "PRY"
                },{
                    "CCode": "51",
                    "CountryID": "167",
                    "Description": "Peru",
                    "ISO3166": "PER"
                },{
                    "CCode": "63",
                    "CountryID": "191",
                    "Description": "Philippines",
                    "ISO3166": "PHL"
                },{
                    "CCode": "872",
                    "CountryID": "235",
                    "Description": "Pitcairn",
                    "ISO3166": "PCN"
                },{
                    "CCode": "872",
                    "CountryID": "236",
                    "Description": "Pitcairn & Inmarsat Pacific Ocean",
                    "ISO3166": "PN2"
                },{
                    "CCode": "48",
                    "CountryID": "155",
                    "Description": "Poland",
                    "ISO3166": "POL"
                },{
                    "CCode": "351",
                    "CountryID": "105",
                    "Description": "Portugal",
                    "ISO3166": "PRT"
                },{
                    "CCode": "1",
                    "CountryID": "18",
                    "Description": "Puerto Rico",
                    "ISO3166": "PRI"
                },{
                    "CCode": "974",
                    "CountryID": "266",
                    "Description": "Qatar",
                    "ISO3166": "QAT"
                },{
                    "CCode": "262",
                    "CountryID": "76",
                    "Description": "R�union",
                    "ISO3166": "REU"
                },{
                    "CCode": "40",
                    "CountryID": "139",
                    "Description": "Romania",
                    "ISO3166": "ROU"
                },{
                    "CCode": "7",
                    "CountryID": "221",
                    "Description": "Russian Federation",
                    "ISO3166": "RUS"
                },{
                    "CCode": "7",
                    "CountryID": "220",
                    "Description": "Russian Federation & Kazakhstan",
                    "ISO3166": "RU2"
                },{
                    "CCode": "250",
                    "CountryID": "63",
                    "Description": "Rwanda",
                    "ISO3166": "RWA"
                },{
                    "CCode": "290",
                    "CountryID": "90",
                    "Description": "Saint Helena",
                    "ISO3166": "SHN"
                },{
                    "CCode": "290",
                    "CountryID": "89",
                    "Description": "Saint Helena & Tristan da Cunha",
                    "ISO3166": "SH2"
                },{
                    "CCode": "1",
                    "CountryID": "13",
                    "Description": "Saint Kitts and Nevis",
                    "ISO3166": "KNA"
                },{
                    "CCode": "1",
                    "CountryID": "15",
                    "Description": "Saint Lucia",
                    "ISO3166": "LCA"
                },{
                    "CCode": "508",
                    "CountryID": "165",
                    "Description": "Saint Pierre and Miquelon",
                    "ISO3166": "SPM"
                },{
                    "CCode": "1",
                    "CountryID": "23",
                    "Description": "Saint Vincent and the Grenadines",
                    "ISO3166": "VCT"
                },{
                    "CCode": "685",
                    "CountryID": "210",
                    "Description": "Samoa",
                    "ISO3166": "WSM"
                },{
                    "CCode": "378",
                    "CountryID": "125",
                    "Description": "San Marino",
                    "ISO3166": "SMR"
                },{
                    "CCode": "239",
                    "CountryID": "52",
                    "Description": "S�o Tome and Principe",
                    "ISO3166": "STP"
                },{
                    "CCode": "966",
                    "CountryID": "259",
                    "Description": "Saudi Arabia",
                    "ISO3166": "SAU"
                },{
                    "CCode": "221",
                    "CountryID": "34",
                    "Description": "Senegal",
                    "ISO3166": "SEN"
                },{
                    "CCode": "381",
                    "CountryID": "128",
                    "Description": "Serbia",
                    "ISO3166": "SRB"
                },{
                    "CCode": "381",
                    "CountryID": "127",
                    "Description": "Serbia & Montenegro",
                    "ISO3166": "RS2"
                },{
                    "CCode": "248",
                    "CountryID": "61",
                    "Description": "Seychelles",
                    "ISO3166": "SYC"
                },{
                    "CCode": "65",
                    "CountryID": "193",
                    "Description": "Singapore",
                    "ISO3166": "SGP"
                },{
                    "CCode": "421",
                    "CountryID": "142",
                    "Description": "Slovakia",
                    "ISO3166": "SVK"
                },{
                    "CCode": "386",
                    "CountryID": "132",
                    "Description": "Slovenia",
                    "ISO3166": "SVN"
                },{
                    "CCode": "677",
                    "CountryID": "203",
                    "Description": "Solomon Islands",
                    "ISO3166": "SLB"
                },{
                    "CCode": "252",
                    "CountryID": "66",
                    "Description": "Somalia",
                    "ISO3166": "SOM"
                },{
                    "CCode": "252",
                    "CountryID": "65",
                    "Description": "Somalia & Somaliland",
                    "ISO3166": "SO2"
                },{
                    "CCode": "252",
                    "CountryID": "67",
                    "Description": "Somaliland",
                    "ISO3166": ""
                },{
                    "CCode": "27",
                    "CountryID": "88",
                    "Description": "South Africa",
                    "ISO3166": "ZAF"
                },{
                    "CCode": "211",
                    "CountryID": "280",
                    "Description": "South Sudan",
                    "ISO3166": "SSD"
                },{
                    "CCode": "34",
                    "CountryID": "101",
                    "Description": "Spain",
                    "ISO3166": "ES2"
                },{
                    "CCode": "34",
                    "CountryID": "102",
                    "Description": "Spain",
                    "ISO3166": "ESP"
                },{
                    "CCode": "94",
                    "CountryID": "251",
                    "Description": "Sri Lanka",
                    "ISO3166": "LKA"
                },{
                    "CCode": "249",
                    "CountryID": "62",
                    "Description": "Sudan",
                    "ISO3166": "SDN"
                },{
                    "CCode": "597",
                    "CountryID": "182",
                    "Description": "Suriname",
                    "ISO3166": "SUR"
                },{
                    "CCode": "47",
                    "CountryID": "154",
                    "Description": "Svalbard and Jan Mayen",
                    "ISO3166": "SJM"
                },{
                    "CCode": "268",
                    "CountryID": "85",
                    "Description": "Swaziland",
                    "ISO3166": "SWZ"
                },{
                    "CCode": "46",
                    "CountryID": "151",
                    "Description": "Sweden",
                    "ISO3166": "SWE"
                },{
                    "CCode": "41",
                    "CountryID": "140",
                    "Description": "Switzerland",
                    "ISO3166": "CHE"
                },{
                    "CCode": "963",
                    "CountryID": "256",
                    "Description": "Syria",
                    "ISO3166": "SYR"
                },{
                    "CCode": "886",
                    "CountryID": "244",
                    "Description": "Taiwan",
                    "ISO3166": "TWN"
                },{
                    "CCode": "992",
                    "CountryID": "273",
                    "Description": "Tajikistan",
                    "ISO3166": "TJK"
                },{
                    "CCode": "255",
                    "CountryID": "70",
                    "Description": "Tanzania",
                    "ISO3166": "TZA"
                },{
                    "CCode": "999",
                    "CountryID": "279",
                    "Description": "Telecommunications for Disaster Relief",
                    "ISO3166": ""
                },{
                    "CCode": "66",
                    "CountryID": "194",
                    "Description": "Thailand",
                    "ISO3166": "THA"
                },{
                    "CCode": "670",
                    "CountryID": "195",
                    "Description": "Timor-Leste",
                    "ISO3166": "TLS"
                },{
                    "CCode": "228",
                    "CountryID": "41",
                    "Description": "Togo",
                    "ISO3166": "TGO"
                },{
                    "CCode": "690",
                    "CountryID": "215",
                    "Description": "Tokelau",
                    "ISO3166": "TKL"
                },{
                    "CCode": "676",
                    "CountryID": "202",
                    "Description": "Tonga",
                    "ISO3166": "TON"
                },{
                    "CCode": "1",
                    "CountryID": "20",
                    "Description": "Trinidad and Tobago",
                    "ISO3166": "TTO"
                },{
                    "CCode": "290",
                    "CountryID": "91",
                    "Description": "Tristan da Cunha",
                    "ISO3166": "TAA"
                },{
                    "CCode": "216",
                    "CountryID": "31",
                    "Description": "Tunisia",
                    "ISO3166": "TUN"
                },{
                    "CCode": "90",
                    "CountryID": "246",
                    "Description": "Turkey",
                    "ISO3166": "TUR"
                },{
                    "CCode": "90",
                    "CountryID": "245",
                    "Description": "Turkey & Cyprus, Turkish Republic of Northern",
                    "ISO3166": "TR2"
                },{
                    "CCode": "993",
                    "CountryID": "274",
                    "Description": "Turkmenistan",
                    "ISO3166": "TKM"
                },{
                    "CCode": "1",
                    "CountryID": "19",
                    "Description": "Turks and Caicos Islands",
                    "ISO3166": "TCA"
                },{
                    "CCode": "688",
                    "CountryID": "213",
                    "Description": "Tuvalu",
                    "ISO3166": "TUV"
                },{
                    "CCode": "256",
                    "CountryID": "71",
                    "Description": "Uganda",
                    "ISO3166": "UGA"
                },{
                    "CCode": "380",
                    "CountryID": "126",
                    "Description": "Ukraine",
                    "ISO3166": "UKR"
                },{
                    "CCode": "971",
                    "CountryID": "263",
                    "Description": "United Arab Emirates",
                    "ISO3166": "ARE"
                },{
                    "CCode": "44",
                    "CountryID": "145",
                    "Description": "United Kingdom",
                    "ISO3166": "GBR"
                },{
                    "CCode": "699",
                    "CountryID": "218",
                    "Description": "United States Minor Outlying Islands",
                    "ISO3166": "UMI"
                },{
                    "CCode": "878",
                    "CountryID": "240",
                    "Description": "Universal Personal Telecommunication Service",
                    "ISO3166": ""
                },{
                    "CCode": "598",
                    "CountryID": "183",
                    "Description": "Uruguay",
                    "ISO3166": "URY"
                },{
                    "CCode": "1",
                    "CountryID": "21",
                    "Description": "USA & Canada",
                    "ISO3166": "US2"
                },{
                    "CCode": "998",
                    "CountryID": "278",
                    "Description": "Uzbekistan",
                    "ISO3166": "UZB"
                },{
                    "CCode": "678",
                    "CountryID": "204",
                    "Description": "Vanuatu",
                    "ISO3166": "VUT"
                },{
                    "CCode": "58",
                    "CountryID": "174",
                    "Description": "Venezuela",
                    "ISO3166": "VEN"
                },{
                    "CCode": "84",
                    "CountryID": "226",
                    "Description": "Viet Nam",
                    "ISO3166": "VNM"
                },{
                    "CCode": "1",
                    "CountryID": "24",
                    "Description": "Virgin Islands, British",
                    "ISO3166": "VGB"
                },{
                    "CCode": "1",
                    "CountryID": "25",
                    "Description": "Virgin Islands, U.S.",
                    "ISO3166": "VIR"
                },{
                    "CCode": "681",
                    "CountryID": "207",
                    "Description": "Wallis and Futuna Islands",
                    "ISO3166": "WLF"
                },{
                    "CCode": "212",
                    "CountryID": "27",
                    "Description": "Western Sahara",
                    "ISO3166": "ESH"
                },{
                    "CCode": "967",
                    "CountryID": "260",
                    "Description": "Yemen",
                    "ISO3166": "YEM"
                },{
                    "CCode": "260",
                    "CountryID": "74",
                    "Description": "Zambia",
                    "ISO3166": "ZMB"
                },{
                    "CCode": "263",
                    "CountryID": "80",
                    "Description": "Zimbabwe",
                    "ISO3166": "ZWE"
                }
            ],
            "message": "Success",
            "status": 0
        }
    logging.info("**** End county_types ****")
    return response


@app.route("/kyc/types/gender", methods=['POST'])
@cross_origin()
def gender_type():
    logging.info("**** Begin gender_type ****")
    r = request.get_json() or {}
    response = {
            "code": 200,
            "has_error": False,
            "items": [
                {
                    "Description": "Not Aplicable",
                    "GenderID": "1"
                },
                {
                    "Description": "Male",
                    "GenderID": "2"
                },
                {
                    "Description": "Female",
                    "GenderID": "3"
                }
            ],
            "message": "Success",
            "status": 0
        }
    logging.info("**** End gender_type ****")
    return response


@app.route("/kyc/types/occupation", methods=['POST'])
@cross_origin()
def get_occupation():
    logging.info("**** Begin occupation ****")
    r = request.get_json() or {}
    response = {
            "code": 200,
            "has_error": False,
            "items": [
                {
                    "Description": "Independent Worker",
                    "OccupationID": "1"
                },
                {
                    "Description": "Other",
                    "OccupationID": "2"
                },
                {
                    "Description": "Private Company Employee",
                    "OccupationID": "3"
                },
                {
                    "Description": "State Employee",
                    "OccupationID": "4"
                },
                {
                    "Description": "Unemployed",
                    "OccupationID": "5"
                }
            ],
            "message": "Success",
            "status": 0
        }
    logging.info("**** End occupation ****")
    return response


@app.route("/kyc/types/document_id", methods=['POST'])
@cross_origin()
def get_document_id():  
    logging.info("**** Begin document_id ****")
    r = request.get_json() or {}
    response = {
            "code": 200,
            "has_error": False,
            "items": [
                {
                    "Description": "National ID Card",
                    "TypeDocID": "1"
                },{
                    "Description": "Passport",
                    "TypeDocID": "2"
                },{
                    "Description": "Other",
                    "TypeDocID": "3"
                },{
                    "Description": "Voter's ID",
                    "TypeDocID": "4"
                },{
                    "Description": "Driver's Licence",
                    "TypeDocID": "5"
                },{
                    "Description": "Birth Certificate",
                    "TypeDocID": "6"
                },{
                    "Description": "Employee Card",
                    "TypeDocID": "7"
                },{
                    "Description": "Student Card",
                    "TypeDocID": "8"
                },{
                    "Description": "Invalid National ID",
                    "TypeDocID": "9"
                },{
                    "Description": "Business TIN",
                    "TypeDocID": "10"
                }
            ],
            "message": "Success",
            "status": 0
        }
    logging.info("**** End document_id ****")
    return response


@app.route("/kyc/types/address", methods=['POST'])
@cross_origin()
def get_address():  
    logging.info("**** Begin address ****")
    r = request.get_json() or {}
    response = {
            "code": 200,
            "has_error": False,
            "items": [
                {
                    "AddressTypeID": "1",
                    "Description": "Other"
                },{
                    "AddressTypeID": "2",
                    "Description": "Residence"
                },{
                    "AddressTypeID": "3",
                    "Description": "Business"
                },{
                    "AddressTypeID": "4",
                    "Description": "School"
                }
            ],
            "message": "Success",
            "status": 0
        }
    logging.info("**** End address ****")
    return response


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


def portrait_seamfix_verify_lite(probe=None, candidate=None):
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
    # r = request.get_json() or {}
    # # on save debut des logs dans action logs
    # libelle = "ocr_seamfix_get_"+datetime.now()
    # ActionsLogs.action_logs_init_save(libelle, "/kyc/ocr/seamfix/get", json.dumps(r))
    headers = {"Content-Type": "application/json"}
    # Appel de l'OCR
    response = requests.get(app.config['SEAMFIX_HEALTH_CHECK_URL'], headers=headers)
    logging.info("**** response : {}".format(response))
    logging.info("**** response : {}".format(response.json()))
    response = response.json()
    logging.info("**** End ocr_seamfix_get ****")
    # on save fin de logs dans action logs
    # ActionsLogs.action_logs_final_save(libelle, response, response.get("status"))
    return response


def save_registration(data: dict):
    """
    Enregistre une nouvelle ligne dans la table registration avec traitement d’images.
    """
    try:
        # Nettoyage des données
        cleaned_data = {k: (v if v not in ("", None) else None) for k, v in data.items()}

        # Liste des champs images à traiter
        image_fields = [
            "contract_image",
            "agent_signature",
            "id_document_image",
            "id_document_image_back",
            "customer_image",
            "customer_image_ocr"
        ]

        for field in image_fields:
            if cleaned_data.get(field):
                # Appel d'une fonction qui sauvegarde l'image et retourne le chemin du fichier
                cleaned_data[field] = utilities.save_base64_image_lite(
                    cleaned_data[field],
                    prefix=field  # permet d’avoir un nom clair pour chaque fichier
                )

        # Valeurs par défaut
        cleaned_data.setdefault("created_at", datetime.utcnow())
        cleaned_data.setdefault("updated_at", datetime.utcnow())
        cleaned_data.setdefault("is_deleted", False)
        cleaned_data["agent_pin"] = "****"
        cleaned_data["birth_date"] = datetime.strptime(cleaned_data['birth_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d"),
        cleaned_data["reg_date"] = datetime.strptime(cleaned_data['reg_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d %H:%M:%S"),
        cleaned_data["search_string"] = utilities.build_search_string(cleaned_data)

        # Création de l'entité SQLAlchemy
        registration = Registration(**cleaned_data)
        db.session.add(registration)
        db.session.commit()

        return registration
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Erreur lors de l’enregistrement : {str(e)}")


# @app.route("/kya/partner/create", methods=['POST'])
# @cross_origin()
# def create_partner():
#     logging.info("**** Begin create_partner ****")
#     r = request.get_json() or {}
#     data = r['data']
    
#     logging.info("**** End create_partner ****")
#     return response
