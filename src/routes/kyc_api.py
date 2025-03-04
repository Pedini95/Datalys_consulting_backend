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


@app.route('/kyc/header/enrichement', methods=['GET'])
@cross_origin()
def get_header_enrichement():
    logging.info("**** Begin get_header_enrichement ****")
    logging.info("/kyc/header/enrichement")
    logging.info("**** End get_header_enrichement ****")
    return "OK"