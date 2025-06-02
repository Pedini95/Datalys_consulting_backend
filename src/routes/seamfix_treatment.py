from flask import request, jsonify, render_template
from app import app, db
from models.seamfix_treatment import SeamfixTreatment
from redis_template import RedisTemplate
import logging
import utils.functional_error as functional_error
from datetime import datetime, date, timedelta
import utils.utilities as utilities
from flask_cors import CORS, cross_origin
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import base64


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PDF_DIRECTORY = '/Users/louisinnocentkouadio/Desktop/pdf_files'

# Configurez le chemin vers wkhtmltopdf
# pdfkit_config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

from flasgger import swag_from

import pyodbc

# on fait la connection a la base de données sql server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=192.168.19.50\ERIS;'
    'DATABASE=SIMRegistration;'
    'UID=MISreader;'
    'PWD=M!SReader'
)
cursor = conn.cursor()


# Initialiser RedisTemplate
redis_template = RedisTemplate(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT']
)
        
@app.route('/seamfix_treatment/getByCriteria', methods=['POST'])
@cross_origin()
def get_seamfix_treatment():
    logging.info("**** Begin get_seamfix_treatment ****")
    logging.info("/seamfix_treatment/getByCriteria")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    index = r.get('index')
    size = r.get('size')
    seamfix_treatments, total_items = SeamfixTreatment.get_by_criteria(r['data'], index, size)
    if seamfix_treatments:
        message = functional_error.MESSAGE_SUCCESS()
    else:
        message = functional_error.MESSAGE_DATA_EMPTY()
    response = {"items": [seamfix_treatment.as_dict() for seamfix_treatment in seamfix_treatments], "count": total_items, "message": message, "code": 200, "has_error": False}
    logging.info("**** response output ****")
    logging.info(response)
    logging.info("**** End get_user ****")
    return response


@app.route('/seamfix_treatment/create', methods=['POST'])
@cross_origin()
def create_seamfix_treatment():
    logging.info("**** Begin create_seamfix_treatment ****")
    logging.info("/seamfix_treatment/create")
    r = request.get_json() or {}
    logging.info("**** request input ****")
    logging.info(r)
    # on va aller dans la bd sql serveur pour recuperer les informations
    cursor.execute(""" 
        SELECT TOP (1) 
            b.[ID],
            b.[MSISDN],
            b.[APP],
            b.[ExecState],
            b.[ReturnID],
            p1.Picture AS IDCardFPicturePath,
            p2.Picture AS IDContractPicturePath,
            p3.Picture AS IDFrontPicturePath
        FROM [SIMRegistration].[dbo].[SIMRegistrationQueue] b WITH (NOLOCK)
        LEFT JOIN [SIMRegistration].[dbo].[SIMRegistrationPictures] p1 WITH (NOLOCK)
            ON p1.ID = b.IDCardFPicture
        LEFT JOIN [SIMRegistration].[dbo].[SIMRegistrationPictures] p2 WITH (NOLOCK)
            ON p2.ID = b.IDContractPicture
        LEFT JOIN [SIMRegistration].[dbo].[SIMRegistrationPictures] p3 WITH (NOLOCK)
            ON p3.ID = b.IDFrontPicture
        ORDER BY b.ID DESC;
     """)
    rows = cursor.fetchall()
    logging.info("rows :::>")
    logging.info(rows)
    for row in rows:
        logging.info("row :::>")
        logging.info(row)
        logging.info(f"msisdn: {row[1]}")
        logging.info(f"id_card_f_picture: {row[5]}")
        logging.info(f"id_contract_picture: {row[6]}")
        logging.info(f"id_front_picture: {row[7]}")
        msisdn=row[1]
        id_card_f_picture = base64.b64encode(row[5]).decode('utf-8')
        id_card_f_picture_path = utilities.save_base64_image_lite(id_card_f_picture, "id_card_f_picture_path_"+msisdn)
        id_contract_picture = base64.b64encode(row[6]).decode('utf-8')
        id_contract_picture_path = utilities.save_base64_image_lite(id_contract_picture, "id_contract_picture_path_"+msisdn)
        id_front_picture = base64.b64encode(row[7]).decode('utf-8')
        id_front_picture_path = utilities.save_base64_image_lite(id_front_picture, "id_front_picture_path_"+msisdn)
        # on va creer un nouveau seamfix treatment
        seamfix_treatment = SeamfixTreatment(
            msisdn=msisdn,
            id_card_f_picture_path=id_card_f_picture_path,
            id_contract_picture_path=id_contract_picture_path,
            id_front_picture_path=id_front_picture_path,
            created_by=1,
            created_at=datetime.now(),
            search_string=utilities.build_search_string(row),
            is_deleted=False,
        )
        db.session.add(seamfix_treatment)
        db.session.commit()
    logging.info("**** End create_seamfix_treatment ****")
    return functional_error.MESSAGE_SUCCESS()


def create_seamfix_treatment_job():
    logging.info("**** Begin create_seamfix_treatment_job ****")
    # on va aller dans la bd sql serveur pour recuperer les informations
    cursor.execute("""
        SELECT TOP (1) 
            b.[ID],
            b.[MSISDN],
            b.[APP],
            b.[ExecState],
            b.[ReturnID],
            p1.Picture AS IDCardFPicturePath,
            p2.Picture AS IDContractPicturePath,
            p3.Picture AS IDFrontPicturePath
        FROM [SIMRegistration].[dbo].[SIMRegistrationQueue] b WITH (NOLOCK)
        LEFT JOIN [SIMRegistration].[dbo].[SIMRegistrationPictures] p1 WITH (NOLOCK)
            ON p1.ID = b.IDCardFPicture
        LEFT JOIN [SIMRegistration].[dbo].[SIMRegistrationPictures] p2 WITH (NOLOCK)
            ON p2.ID = b.IDContractPicture
        LEFT JOIN [SIMRegistration].[dbo].[SIMRegistrationPictures] p3 WITH (NOLOCK)
            ON p3.ID = b.IDFrontPicture
        ORDER BY b.ID DESC;
     """)
    rows = cursor.fetchall()
    logging.info("rows :::> %s", rows)
    for row in rows:
        logging.info("row :::> %s", row)
        msisdn=row[1]
        id_card_f_picture = base64.b64encode(row[5]).decode('utf-8')
        id_card_f_picture_path = utilities.save_base64_image_lite(id_card_f_picture, "id_card_f_picture_path_"+msisdn)
        id_contract_picture = base64.b64encode(row[6]).decode('utf-8')
        id_contract_picture_path = utilities.save_base64_image_lite(id_contract_picture, "id_contract_picture_path_"+msisdn)
        id_front_picture = base64.b64encode(row[7]).decode('utf-8')
        id_front_picture_path = utilities.save_base64_image_lite(id_front_picture, "id_front_picture_path_"+msisdn)
        # on va creer un nouveau seamfix treatment
        seamfix_treatment = SeamfixTreatment(
            msisdn=msisdn,
            id_card_f_picture_path=id_card_f_picture_path,
            id_contract_picture_path=id_contract_picture_path,
            id_front_picture_path=id_front_picture_path,
            created_by=1,
            created_at=datetime.now(),
            search_string=utilities.build_search_string(row),
            is_deleted=False,
        )
        db.session.add(seamfix_treatment)
        db.session.commit()
    logging.info("**** End create_seamfix_treatment_job ****")
    return functional_error.MESSAGE_SUCCESS()

    
    
