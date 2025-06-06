from flask import request, jsonify, render_template
from app import app, db
from models.seamfix_treatment import SeamfixTreatment
from routes.seamfix_api import ocr_seamfix_lite, portrait_seamfix_verify_lite, portrait_seamfix_validate_lite

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
    print("**** Begin create_seamfix_treatment ****")
    logging.info("/seamfix_treatment/create")
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
    for row in rows:
        msisdn = str(row[1])  # Assurez-vous que ce soit une string
        def safe_image_save(binary_data, prefix):
            if binary_data:
                try:
                    base64_str = base64.b64encode(binary_data).decode("utf-8")
                    return utilities.save_base64_image_lite(base64_str, f"{prefix}_{msisdn}")
                except Exception as e:
                    logging.error(f"Erreur lors de la sauvegarde de l'image {prefix}: {e}")
            return None
            
        id_card_picture_path = safe_image_save(row[5], "id_card_picture_path")
        id_contrat_picture_path = safe_image_save(row[6], "id_contrat_picture_path")
        id_front_picture_path = safe_image_save(row[7], "id_front_picture_path")
        seamfix_treatment = SeamfixTreatment(
            msisdn=msisdn,
            id_card_picture_path=id_card_picture_path,
            id_contrat_picture_path=id_contrat_picture_path,
            id_front_picture_path=id_front_picture_path,
            created_at=datetime.now(),
            # search_string=utilities.build_search_string(row),
            is_deleted=False,
        )
        db.session.add(seamfix_treatment)
        db.session.commit()

        card_picture = binary_to_base64(row[5])
        front_picture = binary_to_base64(row[7])
        # on declanche le l'orchestration seamfix treatment
        orchestration_seamfix_treatment(front_picture, card_picture, "passport", "png")    
    logging.info("**** End create_seamfix_treatment ****")
    print("**** End create_seamfix_treatment ****")
    return functional_error.MESSAGE_SUCCESS()


def binary_to_base64(binary_data):
    if binary_data:
        try:
            base64_str = base64.b64encode(binary_data).decode("utf-8")
            return base64_str
        except Exception as e:
            logging.error(f"Erreur lors de la conversion en base64: {e}")
    return None


def orchestration_seamfix_treatment(front_picture, document, documentType, documentFormat):
    logging.info("**** Begin orchestration_seamfix_treatment ****")
    print("**** Begin orchestration_seamfix_treatment ****")
    # on call le ocr seamfix
    ocr = ocr_seamfix_lite(document, documentType, documentFormat)
    if ocr:
        data = ocr.get("data", {})
        if data:
            extractedDataList = data.get("extractedDataList", [])
            item = extractedDataList[11]
            image = item.get("value")
            # on call le face matching
            portrait_seamfix_verify_lite(front_picture, image)
            # on call le liveness
            portrait_seamfix_validate_lite(front_picture)
    logging.info("**** End orchestration_seamfix_treatment ****")
    print("**** End orchestration_seamfix_treatment ****")
    return functional_error.MESSAGE_SUCCESS()


def create_seamfix_treatment_job():
    logging.info("**** Begin create_seamfix_treatment_job ****")
    print("**** Begin create_seamfix_treatment_job ****")
    logging.info("/seamfix_treatment/create")
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
    for row in rows:
        msisdn = str(row[1])  # Assurez-vous que ce soit une string
        def safe_image_save(binary_data, prefix):
            if binary_data:
                try:
                    base64_str = base64.b64encode(binary_data).decode("utf-8")
                    return utilities.save_base64_image_lite(base64_str, f"{prefix}_{msisdn}")
                except Exception as e:
                    logging.error(f"Erreur lors de la sauvegarde de l'image {prefix}: {e}")
            return None
            
        id_card_picture_path = safe_image_save(row[5], "id_card_picture_path")
        id_contrat_picture_path = safe_image_save(row[6], "id_contrat_picture_path")
        id_front_picture_path = safe_image_save(row[7], "id_front_picture_path")
        seamfix_treatment = SeamfixTreatment(
            msisdn=msisdn,
            id_card_picture_path=id_card_picture_path,
            id_contrat_picture_path=id_contrat_picture_path,
            id_front_picture_path=id_front_picture_path,
            created_at=datetime.now(),
            # search_string=utilities.build_search_string(row),
            is_deleted=False,
        )
        db.session.add(seamfix_treatment)
        db.session.commit()

        card_picture = binary_to_base64(row[5])
        front_picture = binary_to_base64(row[7])
        # on declanche le l'orchestration seamfix treatment
        orchestration_seamfix_treatment(front_picture, card_picture, "passport", "png")    
    logging.info("**** End create_seamfix_treatment_job ****")
    print("**** End create_seamfix_treatment_job ****")
    return functional_error.MESSAGE_SUCCESS()

    
    
