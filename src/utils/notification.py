from flask import request, jsonify, render_template, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app import app
import os, requests, json, random, string
import logging
from flask_mail import Mail, Message

mail = Mail(app)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def send_email(to_email, subject, body):
    from_email = app.config['MAIL_USERNAME']
    from_password = app.config['MAIL_PASSWORD']
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        return jsonify({'message': 'ERROR', 'details': str(e)}), 500



def send_mail_registration(datas, emails):
    logo_url = url_for('static', filename='image/logo.png', _external=True)
    msg = Message("REGISTRATION FIBER",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=emails)
    msg.html = render_template('email_template.html', datas=datas, logo_url=logo_url)
    mail.send(msg)

def send_mail_login(emails, password):
    logo_url = url_for('static', filename='image/logo.png', _external=True)
    msg = Message("IDENTIFIER",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=emails)
    msg.html = render_template('email_template_identifiant.html', emails=emails,  password=password, logo_url=logo_url)
    mail.send(msg)

def send_sms(to_phone, body):
    url = 'https://192.168.19.200:11003/TIMM/v1/Subscriber/Notification/SMS'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "auth": {
            "user": "HRIS",
            "pwd": "d4VygWQ12u3uSkUg"
        },
        "param": {
            "msisdn": to_phone,
            "sms": body
        }
    }
    print("******** data %s *******", data)
    print("******** Url %s *******", url)
    try:
        response = requests.post(url, json=data, headers=headers, verify=False)
        if response.status_code == 200:
            print("******** SMS envoyé *******")
            return True
        else:
            print("******** SMS non envoyé *******")
            return False
    except Exception as e:
        return jsonify({'message': 'ERROR', 'details': str(e)}), 500