# from datetime import datetime
# from pipes import Template
# from urllib import response
# from flask import jsonify, request, url_for, redirect, send_file,session, render_template, send_file
# from sqlalchemy import desc, or_,and_,func, true
# from functools import wraps
# import ast

# # from PIL import Image
# # from io import BytesIO

# from src import db, app
# from src.models import *
# from src.auth import token_auth
# import random
# import string
# import re
# from sqlalchemy.sql import text
# from sqlalchemy.sql.sqltypes import *
# from psycopg2 import errors 
# import uuid
# import hashlib
# import base64
# import csv
# import json
# import xlsxwriter
# import glob, os
# import logging
# from flask_request_id_header.middleware import RequestID
# import asyncio
# import time
# import threading
# # from flask_security import Security, SQLAlchemySessionUserDatastore,roles_accepted
# from src.utils import check_password_requirements

# from models import *


# # import qrcode
# # from PIL import Image, ImageDraw, ImageFont
# # import io


# # user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Rules)
# # security = Security(app, user_datastore)


# logging.warning('This will get logged to a file')

# # @app.errorhandler(Exception)          
# # def  basic_error (e) :
# #     print(e)
# #     return  bad_request_func("An error occurred : " + str(e))          
# app.config['REQUEST_ID_UNIQUE_VALUE_PREFIX'] = 'OLIB-'
# RequestID(app)

# def set_password(password):
#     return generate_password_hash(password)


# # def save_base64_image(base64_str, file_name, extension):
# #     app.logger.info("***** Begin save_base64_image ****")
# #     try:
# #         # upload_folder = "/src/static"
# #         upload_folder = "/srv/www/kya-backend.orange.com.lr/htdocs/src/static"
# #         # Decode the base64 string
# #         image_data = base64.b64decode(base64_str)
# #         # Convert binary data to an image
# #         image = Image.open(BytesIO(image_data))
# #         # Create a secure filename
# #         filename = secure_filename(f"{file_name}_{datetime.now()}.{extension}")
# #         file_path = os.path.join(upload_folder, filename)
# #         app.logger.info("***** file_path 1 %s****", file_path)
# #         file_path = file_path.split('/')[-1]
# #         app.logger.info("***** file_path 2 %s****", file_path)
# #         # Save the image
# #         image.save(file_path)
# #         app.logger.info("***** End save_base64_image ****")
# #         # Return the file path
# #         return file_path
# #     except Exception as e:
# #         print(f"Error saving image: {e}")
# #         return None


# def requires_access(access_level):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             user = User.query.filter_by(email=session['email']).first()
#             if not session.get('email'):
#                 return redirect(url_for('acces_denied'))
#             elif not user.allowed(access_level):
#                 return redirect(url_for('acces_denied'))
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# def get_json_data(db_nber,data,obj):
#     data[obj] = data[obj][-(len(data[obj])-db_nber):]
#     return data[obj] 

# def openDataFile():
#     # Opening JSON file
#     files = glob.glob(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")),'src/static/{}'.format("data.json")))
#     print(files)
#     f = open(files[0], newline='',encoding='utf8')
#     # returns JSON object as 
#     # a dictionary
#     data = json.load(f)
#     return data

# def init_function():
#     data = openDataFile()
#     #insert Roles
#     rules = Rules.query.all()
#     if len(rules)<len(data['Rules']):
        
#         print("Add Rules items [Start]")
#         for item in get_json_data(len(rules),data,'Rules'):
#             rule = Rules()
#             rule.from_dict(item)
#             db.session.add(rule)
#             db.session.commit()
#             print("Rule -- {} [Created]".format(item["title"]))
#         print("Add Rules items [Ended]")

#     #insert User_type
#     usertype = UserType.query.all()
#     if len(usertype)<len(data['UserType']):
#         print("Add UserTypes items [Start]")
#         for item in get_json_data(len(usertype),data,'UserType'):
#             usertype = UserType()
#             usertype.from_dict(item)
#             db.session.add(usertype)
#             db.session.commit()
#             print("UserType -- {} [Created]".format(item["title"]))
#         print("Add UserTypes items [Ended]")

#         #insert user_type
#     #insert User
#     user = User.query.all()
#     if len(user)<len(data['User']):
#         print("Add User items [Start]")
#         for item in get_json_data(len(user),data,'User'):
#             user = User()
#             usertype = UserType.query.filter_by(code="AAll").first()
#             item["user_type_id"] = usertype.id
#             user.from_dict(item)
#             db.session.add(user)
#             db.session.commit()
#             print("User -- {} {} [Created] ".format(item["first_name"],item["last_name"]))
#             # print("\n\nUser Admin Credentials: \n Login:  {} \n Password: {}".format(item["email"],item["password"]))
#         print("Add User items [Ended]")

#     #insert WorkflowSteps
#     workflowStep = WorkflowSteps.query.all()
#     if len(workflowStep)<len(data['WorkflowSteps']):
#         print("Add WorkflowSteps items [Start]")
#         for item in get_json_data(len(workflowStep),data,'WorkflowSteps'):
#             workflowStep = WorkflowSteps()
            
#             workflowStep.from_dict(item)
#             db.session.add(workflowStep)
#             db.session.commit()
#             print("WorkflowStep -- {} [Created] ".format(item["title"]))
#         print("Add workflowSteps items [Ended]")

#     #insert PartnerType
#     partner_type = PartnerType.query.all()
#     if len(partner_type)<len(data['PartnerType']):
#         print("Add PartnerType items [Start]")
#         for item in get_json_data(len(partner_type),data,'PartnerType'):
#             partner_type = PartnerType()
            
#             partner_type.from_dict(item)
#             db.session.add(partner_type)
#             db.session.commit()
#             print("PartnerType -- {} [Created] ".format(item["title"]))
#         print("Add partner_type items [Ended]")

    
# @app.route("/kya_api/v1/init_data", methods=['POST'])
# def init_app():
#     init_function()
#     return jsonify({"message":"App data initialization successed !"})

# def chverif_pwd(passwd):
#     #passwd = 'Geek12@'
#     reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
      
#     # compiling regex
#     pat = re.compile(reg)
      
#     # searching regex                 
#     mat = re.search(pat, passwd)
      
#     # validating conditions
#     if mat:
#         print("Password is valid.")
#     else:
#         print("Password invalid !!")
    
# def delete_file():
#     # p = multiprocessing.Pool(4)
#     files = glob.glob(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")),'src/static/{}'.format("*.xlsx")))
#     for file in files:
#         os.remove(file)

#     files = glob.glob(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")),'src/static/{}'.format("*.csv")))
#     for file in files:
#         os.remove(file)

# format = "%(asctime)s: %(message)s"

# logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")

# def update_partner_status(partner):
#     with app.app_context():
#         time.sleep(180)
#         logging.info("Status checking: Starting")
        
#         transactions = Transactions.query.filter_by(status="In queue")
        
#         for transaction in transactions:
#             if transaction.status=='In queue':
#                 print(transaction)
#                 value = Transactions.transStatus(partner_api_user=partner.api_user, partner_api_password=partner.get_api_password(), ExternalID=transaction.externalID, OPID=transaction.opid)
#                 print(value.json())
#                 if "resultset" in value.json():
#                     transaction.status = value.json()["resultset"]['ExecMessage']
#                     transaction.Message = value.json()["resultset"]['Message']
#                     transaction.transactionID = value.json()["resultset"]['TXNID']
#                 else:
#                     transaction.status = "API Error"
#                     transaction.Message = value.json()["exec_msg"]
                        
#                 db.session.commit()

#         logging.info("Status checking: Ending")

#         return jsonify([{"Message":"Actions done !"}])


# def run_templates_scheduled():
#     """
#     Function to perform payment that scheduled
#     """
#     now = datetime.utcnow
#     templates  = Templates.query.filter_by(run_date=datetime.strptime(now,'%Y-%m-%d'),workflow_state="SCHEDULE").all()
#     for template in templates:
#         template = template.to_dict(partner=True,template_items=True)
#         transactions = template["items"]
#         dict_val = {"otp":"","api_uuid":"","partner_id":template["partner_id"],"service_type":template['service_type'],"remarks":template["remarks"]}
#         transactions.update(dict_val)
#         add_transaction(transactions)

# def export_json(json_data,header=[],export=None):
#     # print(json_data)
#     # header = eval(header)
#     if isinstance(header, str):
#             header = ast.literal_eval(header)  # Analyse sécurisée des littéraux
#     elif not isinstance(header, list):
#         raise ValueError("Le header doit être une liste ou une chaîne représentant une liste.")
#     print(json_data)
#     delete_file()
#     if export=="CSV":
#         #csv
#         filename = "{}.{}".format(get_random_string(18).replace("#", "").replace("#", "").replace("?", ""),"csv")

#         path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")),'src/static/{}'.format(filename)) # à générer
#         data_file = open(path, 'w', newline='',encoding='utf8')
#         csv_writer = csv.writer(data_file)

#         count = 0
#         for data in json_data['items']:
#             if count == 0:
#                 # print(header)

#                 csv_writer.writerow(header)
#                 count += 1
#             # print(type(data.values()))
#             value = {}
#             for y in header:
#                 #print(y)
#                 y = y.split(":")
#                 if y[0] in data:
                    
#                     if len(y)>1:
#                         #print(data[y[0]])
#                         if y[1] in data[y[0]]:
#                             if y[1] in data[y[0]]:
#                                 value[y[0]+":"+y[1]] = data[y[0]][y[1]]
#                     else:
#                         value[y[0]] = data[y[0]]

#             csv_writer.writerow(value.values())
        
#         data_file.close()
#     elif export=="XLSX":
#         #excel
#         # Create a workbook and add a worksheet.
#         filename = "{}.{}".format(get_random_string(18).replace("#", "").replace("#", "").replace("?", ""),"xlsx")
        
#         path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")),'src/static/{}'.format(filename))
#         workbook = xlsxwriter.Workbook(path)
#         worksheet = workbook.add_worksheet()

#         row = 0
#         # Iterate over the data and write it out row by row.
#         for data in json_data['items']:
#             col = 0
#             value = {}
#             if row == 0:
#                 for x in header:
#                     if type(header)==list:
#                         worksheet.write(row, col, x)
#                     else:
#                         worksheet.write(row, col, value[x])
#                     col+=1
#                 row +=1
#                 col = 0

#             for y in header:
#                 y = y.split(":")
#                 if y[0] in data:
#                     if len(y)>1:
#                         print(data[y[0]])
#                         if y[1] in data[y[0]]:
#                             if y[1] in data[y[0]]:
#                                 value[y[0]+":"+y[1]] = data[y[0]][y[1]]
#                     else:
#                         value[y[0]] = data[y[0]]
#             for x in value:
#                 if type(value)==list:
#                     worksheet.write(row, col,  x)
#                 else:
#                     worksheet.write(row, col,  value[x])

#                 col+=1
#             row += 1

#         workbook.close()

#     return {'path':path}

# def bad_request_func(msg):
#     print("reques ended")
#     request_id = request.environ.get("HTTP_X_REQUEST_ID")
#     print(response.__dir__())

#     # history = Histories.query.filter_by(uuid=request_id).first()
#     # history.response = jsonify({"type":"error","message":msg})
#     # history.response_code = 200

#     # db.session.add(history)
#     # db.session.commit()

#     return jsonify({"type":"error","message":msg}),200


# def get_paginated_list(results, index, limit):
#     index = int(index)
#     limit = int(limit)
#     count = int(len(results))
#     start = (limit)*(index-1)
#     if start<0:
#         start = (limit)*index

#     print(count,index,limit)
#     # if count < start or limit < 0:
#     #     return bad_request_func('Page doesn\'t exist')

#     # make response
#     obj = {}

#     if  limit:
#         obj['items'] = results[start:(start + limit)]
#     else:
#         obj['items'] = results

#     obj['count'] = len(results)
#     return obj


# def timm_partner_response(data, partner):
#     with app.app_context():
#         """
#         { "exec_code":0, "exec_msg":"Success", "resultset":{"EXTERNALID":"0002177","ExecMessage":"Fail", \
#         "ExecStatus":"-1","Message":"The transaction amount is more than the maximum value defined for this service", \
#         "TXNID":"CI220621.1250.B07354"} }
#         """
#         #time.sleep(2)
#         if data["service_type"]=="SALARY":
#             transaction = Transactions.query.get(data['id'])
#             if transaction.status=='In queue':
#                 value = Transactions.transStatus(partner_api_user=partner.api_user, partner_api_password=partner.get_api_password(), ExternalID=data['externalID'], OPID=data['opid'])
#                 print(value.json())
#                 if "resultset" in value.json():
#                     transaction.status = value.json()["resultset"]['ExecMessage']
#                     transaction.Message = value.json()["resultset"]['Message']
#                     transaction.transactionID = value.json()["resultset"]['TXNID']
#                 else:
#                     transaction.status = "API Error"
#                     transaction.Message = value.json()["exec_msg"]
                    
#                 db.session.commit()
        
# def timm_response(bundle,data):
#     print(bundle.json())
#     """
#     { "exec_code":0, "exec_msg":"Success", "resultset":{"EXTERNALID":"0002177","ExecMessage":"Fail", \
#     "ExecStatus":"-1","Message":"The transaction amount is more than the maximum value defined for this service", \
#      "TXNID":"CI220621.1250.B07354"} }
#     """
#     # if data["service_type"]=="SALARY":
#     #     if "resultset" in bundle.json():
#     #         if "opid" in bundle.json()["resultset"]:
#     #             data["opid"]=bundle.json()["resultset"]["opid"]
#     # else:
#     data["Message"] = ""
#     if "exec_msg" in bundle.json():
#         if bundle.json()["exec_msg"]=="Success":
#             if data["service_type"] =="SALARY":
#                 data["status"] = "In queue"
#             else:
#                 data["status"] = bundle.json()["exec_msg"]

#         else:
#             data["status"] = "Failed"

#     if bundle.json()['exec_code'] >=0:
#         if "resultset" in bundle.json():

#             if "TXNID" in bundle.json()["resultset"]:
#                 data["Message"]=bundle.json()["resultset"]["TXNID"]
                
#             if "Message" in bundle.json()["resultset"]:
#                 if data["service_type"] =="SALARY":
#                     data["Message"] = "Pending"
#                 else:
#                     data["Message"]=bundle.json()["resultset"]["Message"]
                
#             if "opid" in bundle.json()["resultset"]:
#                 data["opid"]=bundle.json()["resultset"]["opid"]

#     else:
#         data["status"] = "Failed"

#         data["Message"] = bundle.json()["exec_msg"]
#         if "resultset" in bundle.json():
#             for x in bundle.json()["resultset"]:
#                 data["Message"] += bundle.json()["resultset"][x]
                
#     return data

# def no_dele(objet):
#     objets = db.session.query(objet).filter_by(dele=None)
#     print(objets)

#     for obj in objets:
#         print(obj)

#         obj.dele = "FALSE"
#         db.session.add(obj)
#         db.session.commit() 

# def query(data, objet, mapping={}, foreign=True):
#     # Marquer les objets comme non supprimés
#     no_dele(objet)
#     spec = False

#     # Valeurs par défaut pour les champs obligatoires
#     data.setdefault("dele", "FALSE")

#     # Gestion de la pagination
#     if "index" in data and "size" in data:
#         page = int(data["index"])
#         del data["index"]
#         page_size = int(data["size"])
#         del data["size"]
#         spec = True

#     # Initialisation de la requête
#     q = db.session.query(objet).order_by(desc(objet.id))

#     # Recherche dynamique
#     if "search" not in data:
#         for attr in data:
#             try:
#                 if data[attr]:
#                     # Valider et convertir les entrées utilisateur
#                     attr_values = (
#                         ast.literal_eval(data[attr])
#                         if isinstance(data[attr], str) else data[attr]
#                     )

#                     # Traitement pour les champs numériques ou booléens
#                     if isinstance(attr_values, (int, bool)):
#                         q = q.filter(getattr(objet, attr) == attr_values)

#                     # Traitement pour les champs de type date
#                     elif attr in ["date", "date_created"]:
#                         q = q.filter(
#                             getattr(objet, attr) >= f"{attr_values} 00:00:00",
#                             getattr(objet, attr) <= f"{attr_values} 23:59:59"
#                         )

#                     # Traitement pour les listes
#                     elif isinstance(attr_values, list):
#                         filters = [
#                             getattr(objet, attr) == x if isinstance(x, int) else getattr(objet, attr).like(f"%{x}%")
#                             for x in attr_values
#                         ]
#                         q = q.filter(or_(*filters))

#                     # Traitement pour les chaînes de caractères
#                     else:
#                         q = q.filter(getattr(objet, attr).like(f"%{data[attr]}%"))

#             except (ValueError, SyntaxError, AttributeError) as e:
#                 print(f"Erreur lors du traitement de {attr}: {e}")
#     else:
#         # Recherche globale (text search)
#         filters = []

#         # Gestion des clés étrangères
#         if foreign:
#             foreign_keys = [fk._column_tokens[1] for fk in objet.__table__.foreign_keys]

#             for fk_name in foreign_keys:
#                 try:
#                     if "_" in fk_name:
#                         parts = fk_name.split("_")
#                         foreign_objet = globals().get(parts[0].capitalize() + parts[1].capitalize())
#                     else:
#                         foreign_objet = globals().get(fk_name.capitalize())

#                     if foreign_objet:
#                         foreign_data = query({"search": data["search"]}, foreign_objet, mapping={}, foreign=False)
#                         if foreign_data.get("items"):
#                             filters.append(getattr(objet, fk_name) == foreign_data["items"][0]["id"])
#                 except Exception as e:
#                     print(f"Erreur lors de la recherche dans les clés étrangères : {e}")

#         # Recherche dans les colonnes locales
#         for column in objet.__table__.columns:
#             if isinstance(column.type, Integer):
#                 try:
#                     filters.append(column == int(data["search"]))
#                 except ValueError:
#                     pass
#             elif isinstance(column.type, String):
#                 filters.append(column.ilike(f"%{data['search']}%"))

#         # Appliquer les filtres
#         if filters:
#             q = q.filter(or_(*filters))

#         # Supprimer "search" pour éviter les conflits
#         del data["search"]

#         # Appliquer les autres filtres
#         for attr in data:
#             try:
#                 if data[attr]:
#                     if isinstance(data[attr], (int, bool)):
#                         q = q.filter(getattr(objet, attr) == data[attr])
#                     elif attr in ["date", "date_created"]:
#                         q = q.filter(getattr(objet, attr) == f"{data[attr]}")
#                     else:
#                         q = q.filter(getattr(objet, attr).like(f"%{data[attr]}%"))
#             except Exception as e:
#                 print(f"Erreur lors de l'application des filtres : {e}")

#     # Retourner les résultats paginés ou exportés
#     if "export" not in data:
#         if spec:
#             return get_paginated_list([val.to_dict(**mapping) for val in q], page, page_size)
#         else:
#             return get_paginated_list([val.to_dict(**mapping) for val in q], 0, 0)
#     else:
#         return export_json(
#             get_paginated_list([val.to_dict(**mapping) for val in q], 0, 0),
#             data["header"],
#             data["export"]
#         )

# #genrate ramdom password
# def get_random_string(length=8):
#     # With combination of lower and upper case
#     result_str = ''.join(random.choice("{}{}".format("0123456789#@",string.ascii_letters)) for i in range(length))

#     # print random string
#     print(result_str)
#     return result_str

# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


# """
# @app.after_request  
# def after_request_callback(response): 
#     print("reques ended")
#     request_id = request.environ.get("HTTP_X_REQUEST_ID")
#     print(response.__dir__())

#     history = Histories.query.filter_by(uuid=request_id).first()
#     if history:
#         if response.get_json():
#             history.response = str(response.get_json())
#         else:
#             try:
#                 history.response = response.get_data(as_text=True)
#             except:
#                 history.response = "Download file or Error"
#         history.response_code = response.status_code

#         db.session.add(history)
#         db.session.commit()

    
#     return  response
# """    
# """
# @app.before_request   
# def before_request_callback(): 
#     print(request.headers)
#     data = request.get_json() or dict(request.args) or request.form.to_dict() or {}
#     api_uuid = uuid.uuid4()
#     request_id = request.environ.get("HTTP_X_REQUEST_ID")
#     d = {}
#     if 'password' in data:
#         d['email'] = data['email']
#         d['password'] = '*'*len(data['password'])
#     else:
#         d = data

#     data = {
#         'urls': "{}{}".format(request.host,request.path),
#         'body': str(d),
#         'uuid': request_id
#     }
    
#     if 'password' in d:
#         data["user_id"] = User.query.filter_by(email=d['email']).first().id
#     else:
#         if "Authorization" in request.headers:
#             user  = User.query.filter_by(login_token=request.headers['Authorization'].replace("Bearer ","")).first()
#             if user:
#                 data["user_id"] = User.query.filter_by(login_token=request.headers['Authorization'].replace("Bearer ","")).first().id
            

#     history = Histories()
#     history.from_dict(data)
#     db.session.add(history)
#     db.session.commit()

# #    print(request.args.__setitem__("uuid",api_uuid))
#     # request.args.add("uuid",api_uuid)
#     # request.form["uuid"] = api_uuid

#     path = request.path   
#     method = request.method 
    
#     logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
# """
# ##### Authentification endpoints


# @app.route('/kya_api/v1/otpSend', methods=['POST'])
# def otpSend():
#     data = request.get_json() or {}
#     user = User.query.filter_by(email=data['email']).first()
#     result_str = ''.join(random.choice("{}".format("0123456789")) for i in range(6))
#     res = user.sendSMSasOTP(result_str)
#     user.otp_code=result_str
#     db.session.commit()
#     print(res,result_str)
#     return "OTP code sended", 200

# @app.route('/kya_api/v1/otpVerify', methods=['POST'])
# def otpVerify():
#     data = request.get_json() or {}
#     user = User.query.filter_by(email=data['email'],otp_code=data['otp_code']).first()
#     if user:
#         return jsonify(user.to_dict())

#     return "OTP not valid", 401
# #Login
# @app.route('/kya_api/v1/login', methods=['POST'])
# def login():
#     data = request.get_json() or {}

#     if 'email' in data and 'password' in data:
#         no_dele(User)
#         user = User.query.filter_by(email=data['email']).first()
#         if user is not None and user.check_password(data['password']): # on verifie si le mot de passe est juste
#             if user.status=='new' or not user.status:
#                 user.status = "change_password"

#             user.login_token = user.generate_auth_token(expiration=604800000).decode("utf-8")
#             db.session.commit() 
#             session['email'] = user.email
#             return jsonify({'token':  user.login_token , 'expiration': 604800000,"user":user.to_dict(rules=True,user_type=True,password=False,partners=True,workflow=True)}) # on redirige vers l'interface

#         else:
#             return "Access Denied", 401
#     else:
#             return "Access Denied", 401

# #Login
# @app.route('/kya_api/v1/logout', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def logout():
#     user = User.query.get(token_auth.current_user().id)
#     user.login_token = ""
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({'message':"User logout"})

# # check OTP 
# @app.route('/kya_api/v1/checkotp', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def check_otp_user():
#     data = request.get_json() or {}

#     print(data['otp'])

#     user = User.query.get(token_auth.current_user().id)
#     if not user:
#         return bad_request_func('Entity not found')
#     if user and user.status=='otp':
#         opt_result = user.validateOtpSms(data['otp'])
#         resp_data = opt_result.json()
#         print(resp_data)

#         # user.status = "validated"
#         # db.session.commit()

#         if resp_data['exec_code']>=0:
#             # user.status = resp_data['resultset']['Message'].lower()
#             user.status = "validated"
#             db.session.commit()

#         # return jsonify(user.to_dict(rules=True,user_type=True,password=False,partners=True))
#         return jsonify({'token':  user.login_token , 'expiration': 604800000,"user":user.to_dict(rules=True,user_type=True,password=False,partners=True,workflow=True)}) # on redirige vers l'interface

#     else:
#         return bad_request_func("Your account already validated!")

# #Logout

# # change password 
# @app.route('/kya_api/v1/otp_resend', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def otp_resend():
#     user = User.query.get(token_auth.current_user().id)
#     if user.status=="otp" or user.status=="change_password":
#         d = user.sendOtpSms()
#         #resp_data = d
#         resp_data = d.json()
#         print(resp_data)
#         user.otp_id = resp_data['resultset']['OTPID']
#         db.session.commit()
#         return jsonify(user.to_dict(workflow=True))
#     else:
#         return bad_request_func("Your account doesn't allowed to resend OTP !")

# # check OTP 
# @app.route('/kya_api/v1/check_payment_otp', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def check_payment_otp():
#     data = request.get_json() or {}

#     print(data['otp'])

#     user = User.query.get(token_auth.current_user().id)
#     if not user:
#         return bad_request_func('Entity not found')
#     opt_result = user.validateOtpSms(data['otp'])
#     resp_data = opt_result.json()
#     print(resp_data)

#     if resp_data['exec_code']>=0:
#         user.status = "validated"
#         db.session.commit()

#         return jsonify({"MESSAGE": "OTP Validated !"}) # on redirige vers l'interface

#     else:
#         return bad_request_func("OTP didn't validate, please resend new OTP !")

# # change password 
# @app.route('/kya_api/v1/otp_payment_send', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def otp_payment_send():
#     data = request.get_json() or {}

#     partner = Partners.query.get(token_auth.current_user().partner_id)
#     api_uuid = uuid.uuid4()
#     print(api_uuid)
#     if 'transactionCount' not in data:
#         data['transactionCount'] = 1 
#     d = Transactions.paymentAuthCodeSms(phone=token_auth.current_user().phone, api_uuid=str(api_uuid),TransactionCount=data['transactionCount'],partner_api_user=partner.api_user, partner_api_password=partner.get_api_password())
#     resp_data = d.json()
#     #resp_data ={"exec_code":0 , "exec_msg":"Success", "resultset": {"OTPID":1010}}
#     print(resp_data)
#     return jsonify({"MESSAGE":"OTP Sended !","api_uuid":api_uuid})

# # change password 
# @app.route('/kya_api/v1/otp_bundle_send', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def otp_bundle_send():
#     data = request.get_json() or {}

#     partner = Partners.query.get(token_auth.current_user().partner_id)
#     api_uuid = uuid.uuid4()
#     print(api_uuid)
#     if 'transactionCount' not in data:
#         data['transactionCount'] = 1 
#     d = Transactions.paymentAuthCodeSms(phone=token_auth.current_user().phone, api_uuid=str(api_uuid),TransactionCount=data['transactionCount'],partner_api_user=partner.api_user, partner_api_password=partner.get_api_password())
#     resp_data = d.json()
#     #resp_data ={"exec_code":0 , "exec_msg":"Success", "resultset": {"OTPID":1010}}
#     # {'exec_code': 0, 'exec_msg': 'Success', 'resultset': {'Exec_MSG': 'OK'}}
#     # {'exec_code': -100, 'exec_msg': 'Error on Execution', 'resultset': {'Exec_MSG': 'Invalid MSISDN'}}
#     print(resp_data)
#     if d.json()["exec_code"]!=0:
#         return jsonify(d)
#     else:
#         return jsonify({"MESSAGE":"OTP Sended !","api_uuid":api_uuid})

# # change password 
# @app.route('/kya_api/v1/change_pwd', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def change_pwd():
#     data = request.get_json() or {}

#     user = User.query.get(token_auth.current_user().id)
#     if not user:
#         return bad_request_func('Entity not found')

#     if user.status=="change_password":
#         user.set_password(data['password'])
#         d = user.sendOtpSms()
#         #resp_data = d
#         resp_data = d.json()
#         print(resp_data)
#         # user.otp_id = 4455

#         if 'resultset' in resp_data and 'OTPID' in resp_data['resultset']:
#             user.otp_id = resp_data['resultset']['OTPID']
        
#         user.status = 'otp'
#         db.session.commit()
#         return jsonify(user.to_dict())
#     else:
#         return bad_request_func("Your Password already changed !")

# ##### Authentification endpoints


# ##### User CRUD
# def get_last_seen(item):
#     return item.get('last_seen')
# # return all users
# @app.route('/kya_api/v1/get_all_users', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def get_all_users():
#     mapping = {"rules":True,"user_type":True,"password":False,"partners":True,"workflow":True} 
#     data = request.get_json() or {}
#     if "user_type_code" in data:
#         user_type = UserType.query.filter_by(code=data["user_type_code"]).first()
#         if not user_type:
#             return bad_request_func('Entity not found !')
            
#         data["user_type_id"] = user_type.id
#         del(data["user_type_code"])

#     q = query(data,User,mapping)
#     try:
#         q["items"].sort(key=get_last_seen,reverse=True)
#         return jsonify(q)
#     except:
#         q["items"].sort(key=get_last_seen,reverse=True)
#         return q

#     # return jsonify([user.to_dict() for user in User.query.order_by(desc(User.id)).all()])


# # create a new user
# @app.route('/kya_api/v1/create_user', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def create_user():
#     data = request.get_json() or {}
#     if "password" not in data:
#         data["password"] = app.config['PWD_DEFAULT']
#     if 'email' not in data or 'phone' not in data:
#         return bad_request_func('must include email, phone and password fields')
        
#     if User.query.filter_by(email=data['email']).first():
#         return bad_request_func('please use a different email address')

#     if User.query.filter_by(phone=data['phone']).first():
#         return bad_request_func('please use a different phone number')

#     if not check_password_requirements(data['password'], data):
#         return bad_request_func("weak password")
    
#     #data["password"]=get_random_string()
#     #data["password"]="passw"
#     data["status"] = 'new'
#     # if "partner_id" not in data:
#     #     data["partner_id"] = token_auth.current_user.partner_id

#     user = User()
#     user.from_dict(data, new_user=True)
#     # if "user_type_id" not in data:
#     #     user_type = UserType.query.get(user.user_type_id)
#     #     user.user_type_id = user_type.id

    

#     # user.set_password(data["password"])

#     db.session.add(user)
#     db.session.commit()


#     user_type = UserType.query.get(user.user_type_id)
#     response = jsonify(user.to_dict(user_type=True,workflow=True,password=data["password"]))

#     response.status_code = 201

#     response.headers['Location'] = url_for('get_all_users', id=user.id)

#     #Send generate password by mail
#     # user.sendMailMessage(data["password"])
#     # res = user.sendSMSNotification(data["password"])
#     # print(dir(res))

#     return response



# """
# Only uncomment this when you want to update the database
# with common names in Liberia

# Only run once running it twice will insert duplicate data
# @app.get("/names")
# def create_name():
#     import csv


#     csv_file_path = '/srv/www/kya_backend/htdocs/backend/src/namesinliberia.csv'

#     with open(csv_file_path, 'r', encoding="utf-8") as file:
#         from src.models import Names
#         csv_reader = csv.reader(file)

#         for row in csv_reader:
#             names = row[0].split(" ")
#             fname, lname = names[0], names[len(names) - 1]
#             n = Names()
#             n.first_name = fname;
#             n.last_name = lname
#             db.session.add(n)
#     db.session.commit()

#     return {"Status": "OK"}
# """

# # create a new backend user
# @app.route('/kya_api/v1/create_backend_users', methods=['POST'])
# def create_backend_users():
#     data = request.get_json() or {}
#     if 'email' not in data or 'password' not in data or 'phone' not in data:
#         return bad_request_func('must include email, phone and password field')
#     if User.query.filter_by(email=data['email']).first():
#         return bad_request_func('please use a different email address')

#     if User.query.filter_by(phone=data['phone']).first():
#         return bad_request_func('please use a different phone number')
#     if not check_password_requirements(data['password'], data):
#         return bad_request_func("weak password")
    
#     data["status"] = 'validated'
    
#     user = User()
#     user.from_dict(data, new_user=True)
#     if "user_type_id" not in data:
#         user_type = UserType.query.filter_by(code="BACKU").first()
#         user.user_type_id=user_type.id
#         user.rule_id=1

#     db.session.add(user)
#     db.session.commit()
#     response = jsonify(user.to_dict(user_type=True))
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_users', id=user.id)
#     # Send.generate password by mail
#     # user.sendMailMessage(data["password"])

#     return response

# # update user role data
# @app.route('/kya_api/v1/update_user_role', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_user_role():
#     data = request.get_json() or {}
#     mapping = {"rules":True,"user_type":True,"password":False,"partners":True,"workflow":True} 
#     q = query(data,User,mapping)
#     print(q)

#     for val in q["items"]:
#         user = User.query.get(val['id'])
#         role = Role.query.filter_by(id=1).first()
#         user.roles.append(role)
         
#         # commit the changes to database
#         db.session.add(user)
#         db.session.commit()

#     return jsonify(q)
    

# # update user data
# @app.route('/kya_api/v1/update_user', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_user():
#     data = request.get_json() or {}
#     # if token_auth.current_user().id != data['id']:
#     #     abort(403)
#     user = User.query.get(data['id'])
#     if not user:
#         return bad_request_func('Entity not found')
#     if 'email' in data and data['email'] != user.email and \
#             User.query.filter_by(email=data['email']).first():
#         return bad_request_func('please use a different email address')

#     if 'phone' in data and data['phone'] != user.phone and \
#             User.query.filter_by(phone=data['phone']).first():
#         return bad_request_func('please use a different phone number')

#     if 'password' in data or 'old_password' in data:
#         user = User.query.filter_by(id=token_auth.current_user().id).first()
#         if user is None:
#             return bad_request_func('You have not allow to update other user informations')
#         if 'old_password' in data:
#             if not user.check_password(data['old_password']):
#                 return bad_request_func('Your old password doesn\'t correct !')
            

#     del(data['id'])
#     user.from_dict(data, new_user=False)
#     db.session.commit()

#     usertype = UserType.query.filter_by(id=user.user_type_id).first()
#     if usertype:
#         if usertype.code=="ORGU":
#             partner = Partners.query.filter_by(id=user.partner_id).first()
#             if partner:
#                 partner.contact_firstName = user.first_name
#                 partner.contact_lastName = user.last_name
#                 partner.contact_phone = user.phone
#                 partner.contact_email = user.email

#                 db.session.add(partner)
#                 db.session.commit()

#         if usertype.code=="ORGU" or usertype.code=="ORGSU":
#             #Workflow
#             if 'workflow_items' in data:
#                 user_aps = UserWorkflows.query.filter_by(user_id=user.id).all() 
#                 for app in user_aps:
#                     db.session.delete(app)
#                     db.session.commit()
                    
#                 try:
#                     workflow_items = ast.literal_eval(data['workflow_items'])
#                 except:
#                     workflow_items = data['workflow_items']

#                 # for workflow in workflow_items:

#                 #     userWorkflow = UserWorkflows(user_id=user.id,workflowstep_id=workflow)
#                 #     db.session.add(userWorkflow)
#                 #     db.session.commit() 

#     if token_auth.current_user().id == user.id:
#         return jsonify({'token':  user.login_token , 'expiration': 604800000,"user":user.to_dict(rules=True,user_type=True,password=False,partners=True,workflow=True)}) # on redirige vers l'interface
#     else:
#         return jsonify(user.to_dict(rules=True,user_type=True,password=False,partners=True,workflow=True))



# # update user data
# @app.route('/kya_api/v1/get_update_user', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def get_update_user():
#     user = User.query.get(token_auth.current_user().id)
#     return jsonify({'token':  user.login_token , 'expiration': 604800000,"user":user.to_dict(rules=True,user_type=True,password=False,partners=True,workflow=True)}) # on redirige vers l'interface


# # update user data
# @app.route('/kya_api/v1/add_user_api_info', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def add_use_api_infor():
#     data = request.get_json() or {}
#     if "user_id" in data:
#         user = User.query.filter_by(id=data['user_id']).first()
#         if not user:
#             return bad_request_func('Email doesn\'t find.')
        
#         user.api_user = data['api_user']
#         user.set_api_password(data['api_user'])
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(user.to_dict())
#     else : 
#         return bad_request_func('user_id needed in body. Please use this {}'.format({"user_id":"","api_user":"","api_password":""}))


# # update user password data
# @app.route('/kya_api/v1/update_password_user', methods=['POST'])
# def update_password_user():
#     data = request.get_json() or {}
#     if "email" in data:
#         user = User.query.filter_by(email=data['email']).first()
#         if not user:
#             return bad_request_func('Email doesn\'t find.')
#     else:
#         return bad_request_func('Email needed in body. Please use this {}'.format({"email":"","password":""}))

#     if "password" in data:
#         data = {"password":data['password']} or {}
#     else:
#         return bad_request_func('Email needed in body. Please use this {}'.format({"email":"","password":""}))

#     data["status"] = "change_password"
#     user.from_dict(data, new_user=False)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify(user.to_dict())


# # remove user from partner organization
# @app.route('/kya_api/v1/delete_user', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_user():
#     data = request.get_json() or {}
#     user = User.query.get(data['id'])
#     if user:
#         user.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"User ID::{} deleted".format(user.id)})
#     else:
#         return bad_request_func('Entity not found')


# #associated user with partner organization
# @app.route('/kya_api/v1/associatePartner', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def add_partner():
#     data = request.get_json() or {}
#     if data['user_id'] is None:
#         return bad_request_func('please define user_id address')
#     if data['partner_id'] is None:
#         return bad_request_func('please define partner_id address')

#     user = User.query.filter_by(id=data['user_id']).first()
#     if not user:
#         return bad_request_func("User not found")
#     partner = Partners.query.filter_by(id=data['partner_id']).first()
#     if not partner:
#         return bad_request_func("Partner not found")

#     if token_auth.current_user().id == data['user_id']:
#         return bad_request_func('You cannot associated your partner youself')

#     user.add_partner(partner)
#     db.session.commit()
#     return jsonify(user.to_dict(partners=True))

# # remove user from partner organization
# @app.route('/kya_api/v1/removePartnerUser', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def remove_partner():
#     data = request.form.to_dict() or {}
#     user = User.query.filter_by(id=data['user_id']).first()
#     partner = Partners.query.filter_by(id=data['partner_id']).first()
#     if user is None:
#         return bad_request_func('please define user_id address')
#     if partner is None:
#         return bad_request_func('please define partner_id address')

#     if token_auth.current_user().id == data['user_id']:
#         return bad_request_func('You cannot remove your partner youself')

#     user.remove_partner(partner)
#     db.session.commit()
#     return jsonify(partner.to_dict())

# ##### User CRUD

# ##### Partner CRUD
# def build_search_string(data):
#     # Liste des champs d'images à ignorer
#     image_fields = {'id_card_image', 'business_reg_image', 'partner_image', 'signature_image', 'portrait_image'}
#     # Concaténer les valeurs des champs, en ignorant les champs d'images et en filtrant les champs non vides
#     search_string = ', '.join(str(data.get(field, '')).strip() 
#                               for field in data 
#                               if field not in image_fields and data.get(field))

#     return search_string

# # create new partner organization
# @app.route('/kya_api/v1/self_create_partner', methods=['POST'])
# def self_create_partner():
#     data = request.form.to_dict() or request.get_json() or {}
#     print(data)
      
#     current_workflow = WorkflowSteps.query.filter_by(code="ENR").first()
#     data["workflow_state"]=current_workflow.code
#     data["registration_type"]="SELF"
#     partner = Partners()
#     partner.from_dict(data, request.files, new_partner=True)
#     partner.search_string = build_search_string(data)
#     db.session.add(partner)
#     db.session.commit()

#     cur_partnerworkflows = PartnerWorkflows(state="PENDING",partner_id=partner.id,workflowstep_id=current_workflow.id)
#     db.session.add(cur_partnerworkflows)
#     db.session.commit()


#     response = jsonify(partner.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_partners', id=partner.id)
#     return response



# # create new partner organization
# @app.route('/kya/partner/create', methods=['POST'])
# def create_partner_kyc():
#     data = request.form.to_dict() or request.get_json() or {}
#     print(data)
#     current_workflow = WorkflowSteps.query.filter_by(code="ENR").first()
#     data["workflow_state"]=current_workflow.code
#     data["registration_type"]="NON-SELF"
#     partner = Partners()
#     partner.from_dict(data, request.files, new_partner=True)
#     user_number = request.headers.get('number')
#     user_name = request.headers.get('name')
#     user = User.query.filter_by(phone=user_number).first()
#     if not user:
#         if User.query.filter_by(phone=user_number).first():
#             return bad_request_func('please use a different phone number')
#         password = app.config['PWD_DEFAULT']
#         user = User(
#             first_name=user_name,
#             last_name=user_name,
#             phone=user_number,
#             user_type_id=3,
#             password_hash=set_password(password),
#             status="new"
#         )
#         db.session.add(user)
#         db.session.commit()
#     partner.userid = user.id
#     partner.search_string = build_search_string(data)
#     db.session.add(partner)
#     db.session.commit()
#     cur_partnerworkflows = PartnerWorkflows(user_id=user.id, state="PENDING", partner_id=partner.id,workflowstep_id=current_workflow.id)
#     db.session.add(cur_partnerworkflows)
#     db.session.commit()
#     response = jsonify(partner.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_partners', id=partner.id)
#     return response


# @app.route('/kya_api/v1/create_partner', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def create_partner():
#     data = request.form.to_dict() or request.get_json() or {}
#     print(data)
      
#     current_workflow = WorkflowSteps.query.filter_by(code="ENR").first()
#     data["workflow_state"]=current_workflow.code
#     data["registration_type"]="NON-SELF"
#     partner = Partners()
#     partner.from_dict(data, request.files, new_partner=True)
#     token = request.headers.get('Authorization')
#     print("---- token ---")
#     print(token)
#     user = None
#     if token:
#         user = User.query.filter_by(login_token=token.split(" ")[1]).first()
#         print(user)
#     partner.userid = user.id
#     partner.search_string = build_search_string(data)
#     db.session.add(partner)
#     db.session.commit()

#     cur_partnerworkflows = PartnerWorkflows(user_id=token_auth.current_user().id,state="PENDING",partner_id=partner.id,workflowstep_id=current_workflow.id)
#     db.session.add(cur_partnerworkflows)
#     db.session.commit()

#     response = jsonify(partner.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_partners', id=partner.id)
#     return response

# # return all partners 
# @app.route('/kya_api/v1/get_all_partners', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_partners():
#     status = request.args.get("validated")
#     mapping = {"partner_type":True,"workflows_history":True} 
#     data = request.get_json() or {}
#     index = data['index']
#     size = data['size']
#     conditions = []
#     if data.get('search_string'):
#         conditions.append(Partners.search_string.like(f"%{data['search_string']}%"))

#     if data.get('workflow_state'):
#         conditions.append(Partners.workflow_state == data['workflow_state'])
        
#     if status and status.upper() == "TRUE":
#         print("----------- True -------------")
#         conditions.append(Partners.status == "validated")
#         count = Partners.query.filter(and_(*conditions)).count()
#         partners = Partners.query.filter(and_(*conditions)).paginate(page=index, per_page=size, error_out=False)
#         mapping["status"] = "validated"
#         response = {"items": [partner.to_dict(partner_type=True) for partner in partners.items], "count": count}
#         return response
#     if status and status.upper() == "FALSE":
#         print("----------- False -------------")
#         conditions.append(Partners.status == None)
#         count = Partners.query.filter(and_(*conditions)).count()
#         partners = Partners.query.filter(and_(*conditions)).paginate(page=index, per_page=size, error_out=False)
#         response = {"items": [partner.to_dict(partner_type=True) for partner in partners.items], "count": count}
#         return response

#     q = query(data,Partners,mapping)

#     return jsonify(q)


# @app.get('/kya_api/v1/names')
# # @token_auth.login_required
# def tsvector():

#     term = str(request.args.get("query"))
    
#     stmt = text("select first_name, last_name from names where ts_vector @@ to_tsquery(:t1':*') order by ts_rank('ts_vector_weight_index', plainto_tsquery(:t2':*')) desc limit 50")
    

#     names_db = db.session.execute(stmt, {'t1': term, 't2': term }).all()
#     res = {
#         "names": []
#     }
#     names = set()
#     for name in names_db:
#         if len(name[0]) > 1 and (term.lower() in name[0].lower() or name[0].lower() in term.lower()):
#             names.add(name[0])
#         elif len(name[1]) > 1 and (term.lower() in name[1].lower() or name[1].lower() in term.lower()):
#             names.add(name[1])
#     res["names"] = list(names)

#     return jsonify(res)


# # return all partners 
# @app.route('/kya_api/v1/partner_images', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_partner_images():
#     data = request.get_json() or {}
#     partner = Partners.query.get(data['id'])
#     return jsonify({"id_card_image":partner.id_card_image,"business_reg_image":partner.business_reg_image,"portrait_image":partner.portrait_image,"partner_image":partner.partner_image,"signature_image":partner.signature_image})


# # update new partner organization
# @app.route('/kya_api/v1/update_partner', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def update_partner():
#     data = request.form.to_dict() or request.get_json() or {}

#     partner = Partners.query.get(data['id'])
#     if not partner:
#         return bad_request_func('Entity not found')
#     del(data['id'])

#     if 'workflow_next' in data:
#         next_workflow = WorkflowSteps.query.filter_by(code=data['workflow_next']).first()
#         state_workflow = WorkflowSteps.query.filter_by(code=data['workflow_state']).first()
#         complaint_stage = PartnerWorkflows.query.filter_by(partner_id=partner.id, workflowstep_id=4).first()
#         if data["workflow_state"] == "EXT" and data["workflow_next"] == "VALIDATE" and complaint_stage and complaint_stage.state == "VALIDATE":
#             partner.status = "validated"

#         if data["workflow_state"] =="REJECTED" and (next_workflow and data["workflow_next"] != "VALIDATE"):
#             next_partnerworkflow = PartnerWorkflows.query.filter_by(workflowstep_id=next_workflow.id,partner_id=partner.id).first()
#             next_partnerworkflow.state = "PENDING"
#             data['workflow_state'] = data['workflow_next']
#         elif next_workflow and (data["workflow_next"] != "VALIDATE" and data["workflow_next"] != "REJECTED"):
            
#             next_partnerworkflow = PartnerWorkflows.query.filter_by(workflowstep_id=next_workflow.id,partner_id=partner.id).first()
#             state_partnerworkflow = PartnerWorkflows.query.filter_by(partner_id=partner.id,workflowstep_id=state_workflow.id).first()
            
#             if not next_partnerworkflow:
#                 next_partnerworkflow = PartnerWorkflows(partner_id=partner.id,workflowstep_id=next_workflow.id)
#                 db.session.add(next_partnerworkflow)
                    
#             next_partnerworkflow.state = "PENDING"

#             if state_partnerworkflow:
#                 state_partnerworkflow.state = "VALIDATE"
#                 if state_partnerworkflow.id >= 4 and data["workflow_next"] == "VALIDATE":
#                     partner.status = "validated"
#                 state_partnerworkflow.user_id = token_auth.current_user().id
#             if "comment_state" in data:
#                 state_partnerworkflow.comment = data["comment"]

#             data['workflow_state'] = data['workflow_next']
#         elif data["workflow_next"] == "VALIDATE" or data["workflow_next"] =="REJECTED":
#             state_partnerworkflow = PartnerWorkflows.query.filter_by(partner_id=partner.id,workflowstep_id=state_workflow.id).first()
            
#             state_partnerworkflow.user_id = token_auth.current_user().id
#             state_partnerworkflow.state = data["workflow_next"]
#             data['workflow_state'] = data['workflow_next']
#             if "comment_state" in data:
#                 state_partnerworkflow.comment = data["comment_state"]


#     partner.from_dict(data, request.files)
#     db.session.add(partner)
#     db.session.commit()
#     response = jsonify(partner.to_dict(workflows_history=True))
#     return response


# # remove user from partner organization
# @app.route('/kya_api/v1/delete_partner', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_partner():
#     data = request.get_json() or {}
#     partner = Partners.query.get(data['id'])
#     if partner:
#         partner.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"Partner ID::{} deleted".format(partner.id)})
#     else:
#         return bad_request_func('Entity not found')


# ##### Partner CRUD


# ##### Partner Type CRUD

# # create new partner organization
# @app.route('/kya_api/v1/create_partner_type', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def create_partner_type():
#     data = request.form.to_dict() or request.get_json() or {}
#     print(data)
    
#     partner_type = PartnerType()
#     partner_type.from_dict(data, new_partner_type=True)
#     db.session.add(partner_type)
#     db.session.commit()

#     response = jsonify(partner_type.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_partner_types', id=partner_type.id)
#     return response


# # return self all partner_types 
# @app.route('/kya_api/v1/self_get_all_partner_types', methods=['POST'])
# def self_get_all_partner_types():

#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,PartnerType,mapping)

#     return jsonify(q)



# # return all partner_types 
# @app.route('/kya_api/v1/get_all_partner_types', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_partner_types():

    
#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,PartnerType,mapping)

#     return jsonify(q)


# # update new partner_type organization
# @app.route('/kya_api/v1/update_partner_type', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_partner_type():
#     data = request.form.to_dict() or request.get_json() or {}

#     print(data)

#     partner_type = PartnerType.query.get(data['id'])
#     if not partner_type:
#         return bad_request_func('Entity not found')
#     del(data['id'])

#     partner_type.from_dict(data, request.files)
#     db.session.commit()
#     response = jsonify(partner_type.to_dict())
#     return response


# # remove user from partner_type 
# @app.route('/kya_api/v1/delete_partner_type', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_partner_type():
#     data = request.get_json() or {}
#     partner_type = PartnerType.query.get(data['id'])
#     if partner_type:
#         partner_type.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"Partner_type ID::{} deleted".format(partner_type.id)})
#     else:
#         return bad_request_func('Entity not found')

# ##### Partner_type CRUD

# ##### Notification routes ########

# # return all notifications
# @app.route('/kya_api/v1/get_all_notifications', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_notifications():
#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,Notification,mapping)
#     return jsonify(q)


# # create a new notification
# @app.route('/kya_api/v1/create_notification', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def create_notification():
#     print(request.form.to_dict(flat=False))
#     data = request.form.to_dict(flat=False) or {}
    

#     if 'title' not in data or 'text' not in data:
#         return bad_request_func('must include title, text in fields')
    
#     notification = Notification()
#     notification.from_dict(data,files=request.files, new_notification=True)
#     db.session.add(notification)
#     db.session.commit()
#     response = jsonify(notification.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_notifications', id=notification.id)
#     return response


# # update notification data
# @app.route('/kya_api/v1/update_notification', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def update_notification():
#     data  = request.form.to_dict(flat=False) or {}
#     notification = Notification.query.get(data["id"])
#     if not notification:
#         return bad_request_func('Entity not found')
#     del(data['id'])
    
#     notification.from_dict(data,files=request.files, new_notification=False)
#     db.session.commit()
#     return jsonify(notification.to_dict())

# # Delete notifications
# @app.route('/kya_api/v1/delete_notification', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def delete_notification():
#     data  = request.get_json() or {}
#     notification = Notification.query.get(data["id"])
#     if notification:
#         notification.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"Notification ID::{} deleted".format(notification.id)})
#     else:
#         return bad_request_func('Entity not found')

# ##### Notification routes ########


# ##### WorkflowSteps routes ########
# @app.route('/kya_api/v1/get_all_workflowsteps', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_workflowsteps():
#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,WorkflowSteps,mapping)
#     return jsonify(q)

# # create a new transaction
# @app.route('/kya_api/v1/create_workflowstep', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def create_workflowsteps():
#     data = request.get_json() or {}

#     workflowsteps = WorkflowSteps()
#     workflowsteps.from_dict(data, new_workflowstep=True)
#     db.session.add(workflowsteps)
#     db.session.commit()

#     return jsonify(workflowsteps.to_dict())

# # update workflowsteps data
# @app.route('/kya_api/v1/update_workflowstep', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def update_workflowsteps():
#     data  = request.get_json() or {}
#     print(data)
#     workflowsteps = WorkflowSteps.query.get(data["id"])
#     if not workflowsteps:
#         return bad_request_func('Entity not found')
#     del(data['id'])
    
#     workflowsteps.from_dict(data, new_workflowstep=True)
#     db.session.commit()
#     return jsonify(workflowsteps.to_dict())

# # Delete workflowsteps
# @app.route('/kya_api/v1/delete_workflowstep', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def delete_workflowsteps():
#     data  = request.get_json() or {}
#     workflowsteps = WorkflowSteps.query.get(data["id"])
#     if workflowsteps:
#         workflowsteps.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"WorkflowSteps ID::{} deleted".format(workflowsteps.id)})
#     else:
#         return bad_request_func('Entity not found')
# ##### WorkflowSteps routes ########


# ##### PartnerWorkflows routes ########
# @app.route('/kya_api/v1/get_all_partnerworkflows', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_partnerworkflows():
#     mapping = {"workflows":True,"user":True} 
#     data = request.get_json() or {}

#     q = query(data,PartnerWorkflows,mapping)
#     return jsonify(q)

# # create a new partnerworkflow
# @app.route('/kya_api/v1/create_partnerworkflow', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def create_partnerworkflow():
#     data = request.get_json() or {}

#     partnerworkflows = PartnerWorkflows()
#     partnerworkflows.from_dict(data, new_partnerworkflows=True)
#     db.session.add(partnerworkflows)
#     db.session.commit()

#     return jsonify(partnerworkflows.to_dict())
    

# # update partnerworkflows data
# @app.route('/kya_api/v1/update_partnerworkflow', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def update_partnerworkflow():
#     """If you want to reject transactions, you must to send state(REJECTED) and comment (why they are rejected)"""
#     data  = request.get_json() or {}
#     print(data)
#     partnerworkflow = PartnerWorkflows.query.get(data["id"])
#     if not partnerworkflow:
#         return bad_request_func('Entity not found')
#     del(data['id'])
    
#     partnerworkflow.from_dict(data, new_partnerworkflows=True)
#     db.session.commit()
#     return jsonify(partnerworkflow.to_dict())

# # Delete partnerworkflows
# @app.route('/kya_api/v1/delete_partnerworkflow', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def delete_partnerworkflow():
#     data  = request.get_json() or {}
#     partnerworkflow = PartnerWorkflows.query.get(data["id"])
#     if partnerworkflow:
#         partnerworkflow.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"PartnerWorkflows ID::{} deleted".format(partnerworkflow.id)})
#     else:
#         return bad_request_func('Entity not found')

# ##### PartnerWorkflows routes ########


# ##### UserWorkflows routes ########
# @app.route('/kya_api/v1/get_all_userworkflows', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_userworkflows():
#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,UserWorkflows,mapping)
#     return jsonify(q)

# # create a new userworkflow
# @app.route('/kya_api/v1/create_userworkflow', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def create_userworkflow():
#     data = request.get_json() or {}

#     userworkflows = UserWorkflows()
#     userworkflows.from_dict(data, new_userworkflows=True)
#     db.session.add(userworkflows)
#     db.session.commit()

#     return jsonify(userworkflows.to_dict())


# # update userworkflows data
# @app.route('/kya_api/v1/update_userworkflow', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def update_userworkflow():
#     data  = request.get_json() or {}
#     print(data)
#     userworkflow = UserWorkflows.query.get(data["id"])
#     if not userworkflow:
#         return bad_request_func('Entity not found')
#     del(data['id'])
    
#     userworkflow.from_dict(data, new_userworkflows=True)
#     db.session.commit()
#     return jsonify(userworkflow.to_dict())

# # Delete userworkflows
# @app.route('/kya_api/v1/delete_userworkflow', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def delete_userworkflow():
#     data  = request.get_json() or {}
#     userworkflow = UserWorkflows.query.get(data["id"])
#     if userworkflow:
#         userworkflow.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"UserWorkflows ID::{} deleted".format(userworkflow.id)})
#     else:
#         return bad_request_func('Entity not found')

# ##### UserWorkflows routes ########



# ##### Permissions routes ########

# # return all permissions
# @app.route('/kya_api/v1/get_all_permissions', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_permissions():
#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,Permissions,mapping)
#     return jsonify(q)


# # create a new permission
# @app.route('/kya_api/v1/create_permission', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def create_permission():
#     data = request.get_json() or {}
    
#     if 'definition' not in data or 'permission' not in data:
#         return bad_request_func('must include definition, permission in fields')
    
#     permission = Permissions()
#     permission.from_dict(data, new_permission=True)
#     db.session.add(permission)
#     db.session.commit()
#     response = jsonify(permission.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_permissions', id=permission.id)
#     return response


# # update permission data
# @app.route('/kya_api/v1/update_permission', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_permission():
#     data = request.get_json() or {}
#     permission = Permissions.query.get(data["id"])
#     if not permission:
#         return bad_request_func('Entity not found')

#     if 'definition' not in data or 'permission' not in data:
#         return bad_request_func('must include definition, permission in fields')
#     del(data['id'])
#     permission.from_dict(data, new_permission=False)
#     db.session.commit()
#     return jsonify(permission.to_dict(feature=True,user_type=True))


# # delete permission data
# @app.route('/kya_api/v1/delete_permission/<int:id>', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_permission(id):
#     data = request.get_json() or {}
#     permission = Permissions.query.get(data["id"])
#     if permission:
#         permission.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"Notification ID::{} deleted".format(permission.id)}),200
#     else:
#         return bad_request_func('Entity not found')

# ##### Permissions routes ########


# ##### User Type routes ########

# # return all User Type
# @app.route('/kya_api/v1/get_all_user_types', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def get_all_user_types():
#     mapping = {} 
#     data = request.get_json() or {}

#     q = query(data,UserType,mapping)
#     return jsonify(q)


# # create a new User Type
# @app.route('/kya_api/v1/create_user_type', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def create_user_type():
#     data = request.get_json() or {}
    
#     if 'title' not in data or 'description' not in data:
#         return bad_request_func('must include title, description in fields')
    
#     user_type = UserType()
#     user_type.from_dict(data, new_user_type=True)
#     db.session.add(user_type)
#     db.session.commit()
#     response = jsonify(user_type.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_user_types', id=user_type.id)
#     return response


# # update User Type data
# @app.route('/kya_api/v1/update_user_type', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_user_type():
#     data = request.get_json() or {}
#     user_types = UserType.query.get(data["id"])
#     if not user_types:
#         return bad_request_func('Entity not found')
#     del(data["id"])
#     user_types.from_dict(data, new_user_type=False)
#     db.session.add(user_types)
#     db.session.commit()
#     return jsonify(user_types.to_dict())


# # delete User Type data
# @app.route('/kya_api/v1/delete_user_type', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_user_type():
#     data = request.get_json() or {}
#     user_type = UserType.query.get(data["id"])
#     if user_type:
#         user_type.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"User Type ID::{} deleted".format(user_type.id)}),200
#     else:
#         return bad_request_func('Entity not found')

# ##### User Type routes ########


# ##### Features routes ########

# # retrun a single features

# # return all features
# @app.route('/kya_api/v1/get_all_features', methods=['POST'])
# @token_auth.login_required
# @requires_access(["Viewer","Coo","CU","BOA","BOU","TSAA","RoT","RoTSA","RT","RTSA","ABO","AREG","AAll"])
# def get_all_features():
#     data = request.get_json() or {}
#     if data['hierarchy'] ==1:
#         features = Features.query.filter_by(parent_id=None).all() 
#         del(data['hierarchy'])
#         return jsonify( {"count": len(features),"items":[feature.to_dict(childs=True) for feature in features]})
#     else:
#         del(data['hierarchy'])
#         mapping = {"childs":True,"parent":True} 
#         q = query(data,Features,mapping)
#         return jsonify(q)


# # create a new features
# @app.route('/kya_api/v1/create_feature', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def create_feature():
#     data = request.get_json() or {}
    
#     if 'title' not in data or 'description' not in data:
#         return bad_request_func('must include title, description in fields')
    
#     feature = Features()
#     feature.from_dict(data, new_feature=True)
#     db.session.add(feature)
#     db.session.commit()
#     response = jsonify(feature.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_features', id=feature.id)
#     return response


# # update User Type data
# @app.route('/kya_api/v1/update_feature', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_feature():
#     data = request.get_json() or {}
#     feature = Features.query.get(data["id"])
#     if not feature:
#         return bad_request_func('Entity not found')
#     del(data['id'])
#     feature.from_dict(data, new_feature=False)
#     db.session.commit()
#     return jsonify(feature.to_dict())


# # delete Feature data
# @app.route('/kya_api/v1/delete_feature', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_feature():
#     data = request.get_json() or {}
#     feature = Features.query.get(data["id"])
#     if feature:
#         feature.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"Feature ID::{} deleted".format(feature.id)}),200
#     else:
#         if not feature:
#             return bad_request_func('Entity not found')

# ##### Feature routes ########

# ##### Type routes ########
# @app.route('/kya_api/v1/county', methods=['POST'])
# def county():
#     data = openDataFile()
#     val = get_json_data(0,data,'County')
#     return jsonify({"count":len(val),"items":val})

# @app.route('/kya_api/v1/country', methods=['POST'])
# def country():
#     data = openDataFile()
#     val = get_json_data(0,data,'Country')
#     return jsonify({"count":len(val),"items":val})

# @app.route('/kya_api/v1/gender', methods=['POST'])
# def gender():
#     data = openDataFile()
#     val = get_json_data(0,data,'Gender')
#     return jsonify({"count":len(val),"items":val})

# @app.route('/kya_api/v1/occupation', methods=['POST'])
# def occupation():
#     data = openDataFile()
#     val = get_json_data(0,data,'Occupation')
#     return jsonify({"count":len(val),"items":val})


# @app.route('/kya_api/v1/document_id', methods=['POST'])
# def document_id():
#     data = openDataFile()
#     val = get_json_data(0,data,'DocumentId')
#     return jsonify({"count":len(val),"items":val})


# @app.route('/kya_api/v1/address', methods=['POST'])
# def address():
#     data = openDataFile()
#     val = get_json_data(0,data,'Address')
#     return jsonify({"count":len(val),"items":val})
# ##### Type routes ########


# #

# ##### Rules routes ########

# # return all Rules
# @app.route('/kya_api/v1/get_all_rules', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def get_all_rules():

#     mapping = {'permissions':True,"user_type":True} 
#     data = request.get_json() or {}

#     if "user_type_code" in data:
#         user_type = UserType.query.filter_by(code=data["user_type_code"]).first()
#         if not user_type:
#             return bad_request_func('Entity not found !')
            
#         data["user_type_id"] = user_type.id
#         del(data["user_type_code"])

#     q = query(data,Rules,mapping)

#     return jsonify(q)


# # create a new Rule
# @app.route('/kya_api/v1/create_rule', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def create_rule():
#     data = request.get_json() or {}
    
#     if 'title' not in data :
#         return bad_request_func('must include title in fields')
    
#     rule = Rules()
#     print(data)
#     rule.from_dict(data, new_rule=True)
#     fonction = []

#     if 'fonctionalites' in data:
#         fonction = data['fonctionalites']
#         del(data["fonctionalites"])

    

#     for perm in fonction:
#         print(perm)
#         feature = Features.query.filter_by(id=perm).first()
#         permission =  Permissions(definition="{}_{}".format(data['title'][0:3],feature.title[0:3]),permission="",feature_id=perm)
#         db.session.add(permission)
#         rule.add_permissions(permission)
   
    
#     db.session.add(rule)
#     db.session.commit()
#     response = jsonify(rule.to_dict(permissions=True,users=True))
#     response.status_code = 201
#     response.headers['Location'] = url_for('get_all_rules', id=rule.id)
#     return response


# # update Rule data
# @app.route('/kya_api/v1/update_rule', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def update_rule():
#     data = request.get_json() or {}
#     print(data)
#     rule = Rules.query.get(int(data["id"]))
#     if not rule:
#         return bad_request_func('Entity not found')

    
#     permissions = Permissions.query.filter_by(rule_id=rule.id).all()
#     for permission in permissions:
#         db.session.delete(permission)
#         db.session.commit()

#     fonction = []

#     if 'fonctionalites' in data:
#         fonction = data['fonctionalites']
#     del(data["fonctionalites"])

#     for perm in fonction:
#         print(perm)
#         feature = Features.query.filter_by(id=perm).first()
#         permission =  Permissions(definition="{}_{}".format(data['title'][0:3],feature.title[0:3]),permission="",feature_id=perm)
#         db.session.add(permission)
#         rule.add_permissions(permission)

#     del(data['id'])
#     rule.from_dict(data, new_rule=False)
#     db.session.commit()
#     return jsonify(rule.to_dict(permissions=True,user_type=True))


# # delete Rule data
# @app.route('/kya_api/v1/delete_rule', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def delete_rule():
#     data = request.get_json() or {}
#     rule = Rules.query.get(data["id"])
#     if rule:
#         rule.dele = "TRUE"
#         db.session.commit()
#         return jsonify({'response':"Rule ID::{} deleted".format(rule.id)}),200
#     else:
#         return bad_request_func('Entity not found')
# ##### Rule routes ########


# @app.route('/kya_api/v1/export_file', methods=['POST','GET'])
# def export_file():
    
#     mapping = {"partner_type":True,"workflows_history":True,"partner_name":True}
#     data = dict(request.args) or {}
#     # for x in  data:
#     #     try:
#     #         if type(eval(data[x]))==int:
#     #             data[x]= eval(data[x])
#     #     except:
#     #         pass
#     for x in data:
#         try:
#             # Vérifiez si data[x] peut être converti en entier
#             if isinstance(data[x], str) and data[x].isdigit():
#                 data[x] = int(data[x])
#         except (ValueError, TypeError) as e:
#             # Gérez l'erreur (par exemple, journalisez l'erreur)
#             print(f"Erreur de conversion pour {x}: {e}")

#     print(data)
#     part = db.session.query(Partners).order_by(desc(Partners.bacthID)).first()
#     if type(data["id"]) != int :
#         if type(data["id"]) == list:
#             for x in data["id"]:
#                 partner = Partners.query.get(x)
#                 try:
#                     partner.bacthID=eval(part['items'][0].bacthID)+1
#                 except:
#                     partner.bacthID =1

#                 db.session.commit()

#     q = query(data,Partners,mapping)
    
#     if data["export"]=="CSV":
#         return  send_file(q['path'], as_attachment=True,mimetype="text/csv")
#     elif data["export"]=="XLSX":
#         return  send_file(q['path'], as_attachment=True,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



# # return all getLogDatabase
# @app.route('/kya_api/v1/getLogs', methods=['POST'])
# @token_auth.login_required
# @requires_access(["AAll"])
# def getLogs():

#     mapping = {"user":True} 
#     data = request.get_json() or {}

#     q = query(data,Histories,mapping)

#     return jsonify(q)


# @app.route('/index', methods=['GET'])
# def indexLite():
#     return render_template('index.html')


# # @app.route('/generate_qrcode', methods=['POST'])
# # def generate_qrcode():
# #     try:
# #         # Récupérer les données envoyées (URL et texte d'arrière-plan)
# #         data = request.json
# #         url = "http://127.0.0.1:5000/index \n"
# #         url += "Test \n"
# #         url += "Test \n"
# #         url += "Test"
# #         background_text = data.get('background_text', '')

# #         if not url:
# #             return jsonify({"error": "URL is required"}), 400

# #         # Générer le QR code
# #         qr = qrcode.QRCode(
# #             version=1,
# #             error_correction=qrcode.constants.ERROR_CORRECT_L,
# #             box_size=10,
# #             border=4,
# #         )
# #         qr.add_data(url)
# #         qr.make(fit=True)

# #         qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

# #         # Ajouter du texte en arrière-plan
# #         if background_text:
# #             draw = ImageDraw.Draw(qr_image)
# #             width, height = qr_image.size

# #             # Définir une taille de police appropriée
# #             font_size = int(min(width, height) * 0.05)
# #             try:
# #                 font = ImageFont.truetype("arial.ttf", font_size)
# #             except IOError:
# #                 font = ImageFont.load_default()

# #             # Calculer la position pour centrer le texte
# #             text_bbox = draw.textbbox((0, 0), background_text, font=font)
# #             text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
# #             position = ((width - text_width) // 2, (height - text_height) // 2)

# #             # Dessiner le texte en arrière-plan (avec une transparence partielle si souhaitée)
# #             draw.text(position, background_text, fill=(400, 400, 400), font=font)

# #         # Sauvegarder l'image dans un objet BytesIO
# #         img_bytes = io.BytesIO()
# #         qr_image.save(img_bytes, format="PNG")
# #         img_bytes.seek(0)

# #         # Retourner l'image en réponse
# #         return send_file(img_bytes, mimetype='image/png')

# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500