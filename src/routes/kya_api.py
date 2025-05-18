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
import uuid
from .seamfix_api import portrait_seamfix_verify_lite

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


