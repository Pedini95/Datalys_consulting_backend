# # define app entities here
# import os,requests,json,random,string
# from datetime import datetime
# from src import db, login, app
# from werkzeug.security import generate_password_hash, check_password_hash
# # from flask_security import UserMixin,RoleMixin
# from flask import session, current_app
# from werkzeug.utils import secure_filename
# # from itsdangerous.jws import TimedJSONWebSignatureSerializer as Serializer
# from sqlalchemy import asc, Index
# from sqlalchemy.dialects.postgresql import TSVECTOR
# import sqlalchemy as sa


# class TSVector(sa.types.TypeDecorator):
#     impl = TSVECTOR
#     cache_ok = True


# with app.app_context():
#     # within this block, current_app points to app.
#     print(current_app.name)

# #genrate ramdom password
# def get_random_string(length=8):
#     # With combination of lower and upper case
#     result_str = ''.join(random.choice("{}{}".format("0123456789#@",string.ascii_letters)) for i in range(length))
#     # print random string
#     print(result_str)
#     return result_str


# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))



# with app.app_context():
#     # within this block, current_app points to app.
#     print(current_app.name)


# class baseModel():
    
#     id = db.Column(db.Integer, primary_key=True)
    
#     date_created = db.Column(db.DateTime(), default=datetime.utcnow)
#     date_modified = db.Column(db.DateTime(), onupdate=datetime.utcnow)
#     dele = db.Column(db.String(255),default="FALSE")
    

#     def file_upload(self,files_data,name):
        
#         uploads_dir = current_app.config['UPLOADS_DIR']

#         if files_data:
#             # save the single "profile" file
#             print(files_data)
#             if files_data[name].filename:
#                 print(files_data)
#                 data = files_data[name]
#                 filename = "{}.{}".format(get_random_string(18).replace("#", "").replace("#", "").replace("?", ""),secure_filename(data.filename).split(".")[-1])
                
#                 data.save(os.path.join(uploads_dir, filename))
#                 return filename

#         return False


# class Names(db.Model, baseModel):
#     first_name = db.Column(db.String(255))
#     last_name = db.Column(db.String(255))
#     ts_vector = db.Column(TSVector(),db.Computed(
#          "to_tsvector('english', first_name || ' ' || last_name)",
#          persisted=True))
#     ts_vector_weight = db.Column(TSVector(), db.Computed("setweight(to_tsvector(first_name), 'A') || setweight(to_tsvector(last_name), 'B')"))
#     __table_args__ = (Index('ix_user___ts_vector__', ts_vector,
#                             postgresql_using='gin'),
#     Index('ts_vector_weight_index', ts_vector_weight, postgresql_using='gin'))



#     def __repr__(self) -> str:
#         return f"Names({self.__dict__})"
    
#     def __str__(self) -> str:
#         return f"Names({self.__dict__})"

# # Request in form data
# class Partners(db.Model,baseModel):
#     fileid = db.Column(db.String(255), nullable=True)
#     refdate = db.Column(db.Date)
#     currencytype = db.Column(db.String(255), nullable=True)
#     userid = db.Column(db.String(255), nullable=True)
#     profile_id = db.Column(db.String(255), nullable=True)
#     parent_id = db.Column(db.String(255), nullable=True)
#     parent_user_msisdn = db.Column(db.String(255), nullable=True)
#     msisdn = db.Column(db.String(255), nullable=True)
#     user_name_prefix = db.Column(db.String(255), nullable=True)
#     username = db.Column(db.String(255), nullable=True)
#     last_name = db.Column(db.String(255), nullable=True)
#     short_name = db.Column(db.String(255), nullable=True)
#     dob = db.Column(db.String(255), nullable=True)
#     registered_on = db.Column(db.String(255), nullable=True)
#     address1 = db.Column(db.String(255), nullable=True)
#     address2 = db.Column(db.String(255), nullable=True)
#     state = db.Column(db.String(255), nullable=True)
#     city = db.Column(db.String(255), nullable=True)
#     country = db.Column(db.String(255), nullable=True)
#     ssn = db.Column(db.String(255), nullable=True)
#     designation = db.Column(db.String(255), nullable=True)
#     division = db.Column(db.String(255), nullable=True)
#     contact_person = db.Column(db.String(255), nullable=True)
#     contact_no = db.Column(db.String(255), nullable=True)
#     employee_code = db.Column(db.String(255), nullable=True)
#     sex = db.Column(db.String(255), nullable=True)
#     id_number = db.Column(db.String(255), nullable=True)
#     e_mail = db.Column(db.String(255), nullable=True)
#     web_login = db.Column(db.String(255), nullable=True)
#     status = db.Column(db.String(255), nullable=True)
#     creation_on = db.Column(db.String(255), nullable=True)
#     created_by = db.Column(db.String(255), nullable=True)
#     created_by_msisdn = db.Column(db.String(255), nullable=True)
#     nomade_created_by = db.Column(db.String(255), nullable=True)
#     level1_approved_on = db.Column(db.String(255), nullable=True)
#     level1_approved_by = db.Column(db.String(255), nullable=True)
#     level2_approved_on = db.Column(db.String(255), nullable=True)
#     level2_approved_by = db.Column(db.String(255), nullable=True)
#     owner_id = db.Column(db.String(255), nullable=True)
#     owner_msisdn = db.Column(db.String(255), nullable=True)
#     user_domain_code = db.Column(db.String(255), nullable=True)
#     category_code = db.Column(db.String(255), nullable=True)
#     user_grade_name = db.Column(db.String(255), nullable=True)
#     modified_by = db.Column(db.String(255), nullable=True)
#     modified_on = db.Column(db.String(255), nullable=True)
#     modify_approved_by = db.Column(db.String(255), nullable=True)
#     modified_approved_on = db.Column(db.String(255), nullable=True)
#     deleted_on = db.Column(db.String(255), nullable=True)
#     deactivation_by = db.Column(db.String(255), nullable=True)
#     department = db.Column(db.String(255), nullable=True)
#     reg_form_num = db.Column(db.String(255), nullable=True)
#     remarks = db.Column(db.String(255), nullable=True)
#     geographical_domain = db.Column(db.String(255), nullable=True)
#     group_role = db.Column(db.String(255), nullable=True)
#     first_transaction_on = db.Column(db.String(255), nullable=True)
#     tango_msisdn = db.Column(db.String(255), nullable=True)
#     company_code = db.Column(db.String(255), nullable=True)
#     company_contact_no = db.Column(db.String(255), nullable=True)
#     company_contact_no_sec = db.Column(db.String(255), nullable=True)
#     user_type = db.Column(db.String(255), nullable=True)
#     action_type = db.Column(db.String(255), nullable=True)
#     agent_code = db.Column(db.String(255), nullable=True)
#     creation_type = db.Column(db.String(255), nullable=True)
#     bulk_id = db.Column(db.String(255), nullable=True)
#     identity_proof_type = db.Column(db.String(255), nullable=True)
#     address_proof_type = db.Column(db.String(255), nullable=True)
#     photo_proof_type = db.Column(db.String(255), nullable=True)
#     id_type = db.Column(db.String(255), nullable=True)
#     id_no = db.Column(db.String(255), nullable=True)
#     id_issue_place = db.Column(db.String(255), nullable=True)
#     id_issue_date = db.Column(db.String(255), nullable=True)
#     id_issue_country = db.Column(db.String(255), nullable=True)
#     id_expiry_date = db.Column(db.String(255), nullable=True)
#     residence_country = db.Column(db.String(255), nullable=True)
#     nationality = db.Column(db.String(255), nullable=True)
#     employer_name = db.Column(db.String(255), nullable=True)
#     postal_code = db.Column(db.String(255), nullable=True)
#     souscription_type = db.Column(db.String(255), nullable=True)
#     mobile_group_role = db.Column(db.String(255), nullable=True)
#     last_login_on = db.Column(db.String(255), nullable=True)
#     user_grade_code = db.Column(db.String(255), nullable=True)
#     parent_first_name = db.Column(db.String(255), nullable=True)
#     parent_last_name = db.Column(db.String(255), nullable=True)
#     owner_first_name = db.Column(db.String(255), nullable=True)
#     owner_last_name = db.Column(db.String(255), nullable=True)
#     correctedstate = db.Column(db.String(255), nullable=True)
#     id_card_image= db.Column(db.Text, nullable=True)
#     business_reg_image= db.Column(db.Text, nullable=True)
#     partner_image= db.Column(db.Text, nullable=True)
#     signature_image= db.Column(db.Text, nullable=True)
#     workflow_state = db.Column(db.String(255)) #APP1-APPn and SCHEDULE
#     payment_authority = db.Column(db.String(255), nullable=True)
#     tax_num = db.Column(db.String(255), nullable=True)
#     business_permit_no = db.Column(db.String(255), nullable=True)
#     type_of_business = db.Column(db.String(255), nullable=True)
#     enterprise_code = db.Column(db.String(255), nullable=True)
#     type_service_requested = db.Column(db.String(255), nullable=True)
#     reason_om = db.Column(db.String(255), nullable=True)
#     region = db.Column(db.String(255), nullable=True)
#     account_number = db.Column(db.String(255), nullable=True)
#     account_name = db.Column(db.String(255), nullable=True)
#     bank_number = db.Column(db.String(255), nullable=True)
#     bank_name = db.Column(db.String(255), nullable=True)
#     account_no_usd = db.Column(db.String(255), nullable=True)
#     account_no_lrd = db.Column(db.String(255), nullable=True)
#     title_authorized_signatory = db.Column(db.String(255), nullable=True)
#     ast_name = db.Column(db.String(255), nullable=True)
#     ast_number = db.Column(db.String(255), nullable=True)
#     benef_name = db.Column(db.String(255), nullable=True)
#     benef_contact = db.Column(db.String(255), nullable=True)
#     business_location= db.Column(db.String(255), nullable=True)
#     occupation= db.Column(db.String(255), nullable=True)
#     id_card = db.Column(db.String(255), nullable=True)
#     date_of_birth = db.Column(db.String(255), nullable=True)
#     bacthID = db.Column(db.String(255), nullable=True)
#     registration_type = db.Column(db.String(255), nullable=True,default="NON-SELF") ### SELF ### NON-SELF
#     partner_type_id = db.Column(db.Integer, db.ForeignKey('partner_type.id'), nullable=True)
#     om_msisdn = db.Column(db.String(255), nullable=True)
#     other_location = db.Column(db.String(255), nullable=True)
#     portrait_image= db.Column(db.Text, nullable=True)
#     search_string= db.Column(db.Text, nullable=True)

    
#     # partner info to dictionary
#     def to_dict(self,partner_type=False,workflows_history=False,partner_name=False):
#         dict_creator = {}
        
#         data = {
#             "id": self.id,
#             "fileid": self.fileid,
#             "refdate": self.refdate,
#             "currencytype": self.currencytype,
#             "userid": self.userid,
#             "profile_id": self.profile_id,
#             "parent_id": self.parent_id,
#             "parent_user_msisdn": self.parent_user_msisdn,
#             "msisdn": self.msisdn,
#             "user_name_prefix": self.user_name_prefix,
#             "username": self.username,
#             "last_name": self.last_name,
#             "short_name": self.short_name,
#             "dob": self.dob,
#             "registered_on": self.registered_on,
#             "address1": self.address1,
#             "address2": self.address2,
#             "state": self.state,
#             "city": self.city,
#             "country": self.country,
#             "ssn": self.ssn,
#             "designation": self.designation,
#             "division": self.division,
#             "contact_person": self.contact_person,
#             "contact_no": self.contact_no,
#             "employee_code": self.employee_code,
#             "sex": self.sex,
#             "id_number": self.id_number,
#             "e_mail": self.e_mail,
#             "web_login": self.web_login,
#             "status": self.status,
#             "creation_on": self.date_created.strftime('%D'),
#             "created_by": self.created_by,
#             "created_by_msisdn": self.created_by_msisdn,
#             "nomade_created_by": self.nomade_created_by,
#             "level1_approved_on": self.level1_approved_on,
#             "level1_approved_by": self.level1_approved_by,
#             "level2_approved_on": self.level2_approved_on,
#             "level2_approved_by": self.level2_approved_by,
#             "owner_id": self.owner_id,
#             "owner_msisdn": self.owner_msisdn,
#             "user_domain_code": self.user_domain_code,
#             "category_code": self.category_code,
#             "user_grade_name": self.user_grade_name,
#             "modified_by": self.modified_by,
#             "modified_on": self.modified_on,
#             "modify_approved_by": self.modify_approved_by,
#             "modified_approved_on": self.modified_approved_on,
#             "deleted_on": self.deleted_on,
#             "deactivation_by": self.deactivation_by,
#             "department": self.department,
#             "reg_form_num": self.reg_form_num,
#             "remarks": self.remarks,
#             "geographical_domain": self.geographical_domain,
#             "group_role": self.group_role,
#             "first_transaction_on": self.first_transaction_on,
#             "tango_msisdn":self.tango_msisdn,
#             "company_code": self.company_code,
#             "company_contact_no":self.company_contact_no,
#             "company_contact_no_sec":self.company_contact_no_sec,
#             "user_type": self.user_type,
#             "action_type": self.action_type,
#             "agent_code": self.agent_code,
#             "creation_type": self.creation_type,
#             "bulk_id": self.bulk_id,
#             "identity_proof_type": self.identity_proof_type,
#             "address_proof_type": self.address_proof_type,
#             "photo_proof_type": self.photo_proof_type,
#             "id_type": self.id_type,
#             "id_no": self.id_no,
#             "id_issue_place": self.id_issue_place,
#             "id_issue_date": self.id_issue_date,
#             "id_issue_country": self.id_issue_country,
#             "id_expiry_date": self.id_expiry_date,
#             "residence_country": self.residence_country,
#             "nationality": self.nationality,
#             "employer_name": self.employer_name,
#             "postal_code": self.postal_code,
#             "souscription_type": self.souscription_type,
#             "mobile_group_role": self.mobile_group_role,
#             "last_login_on": self.last_login_on,
#             "user_grade_code": self.user_grade_code,
#             "parent_first_name": self.parent_first_name,
#             "parent_last_name": self.parent_last_name,
#             "owner_first_name": self.owner_first_name,
#             "owner_last_name": self.owner_last_name,
#             "correctedstate": self.correctedstate,
#             "workflow_state":self.workflow_state,
#             "payment_authority":self.payment_authority,
#             "tax_num":self.tax_num,
#             "business_permit_no":self.business_permit_no,
#             "type_of_business":self.type_of_business,
#             "enterprise_code":self.enterprise_code,
#             "type_service_requested":self.type_service_requested,
#             "reason_om":self.reason_om,
#             "region":self.region,
#             "bacthID":self.bacthID,
#             "registration_type": self.registration_type,
#             "account_number":self.account_number,
#             "account_name":self.account_name,
#             "bank_number":self.bank_number,
#             "bank_number":self.bank_name,
#             "account_no_usd":self.account_no_usd,
#             "account_no_lrd":self.account_no_lrd,
#             "title_authorized_signatory":self.title_authorized_signatory,
#             "ast_name":self.ast_name,
#             "ast_number":self.ast_number,
#             "benef_name":self.benef_name,
#             "benef_contact":self.benef_contact,
#             "business_location":self.business_location,
#             "occupation":self.occupation,
#             "id_card":self.id_card,
#             "date_of_birth":self.date_of_birth,
#             "om_msisdn":self.om_msisdn,
#             "other_location":self.other_location,
#         }   

#         if partner_type:
#             partner_type = PartnerType.query.filter_by(id=self.partner_type_id).first()

#             if partner_type:
#                 data["partner_type"] = partner_type.to_dict()
#                 if partner_name:
#                     data["partner_type"] =data["partner_type"]['title']
#             else:
#                 data["partner_type"] = {}

#         if workflows_history:
#             data["workflows_history"] = [workflow.to_dict(workflows=True,user=True) for workflow in PartnerWorkflows.query.filter_by(partner_id=self.id).order_by(asc(PartnerWorkflows.id)).all()]
       
#         return data

#     # save partner info from dictionary
#     def from_dict(self, data, files, new_partner=False):
#         for field in ["fileid","refdate","currencytype","userid","profile_id","parent_id","parent_user_msisdn","msisdn","user_name_prefix",
#             "username","last_name","short_name","dob","registered_on","address1","address2","state","city","country","ssn","designation","division",
#             "contact_person","contact_no","employee_code","sex","id_number","e_mail","web_login","status","creation_on","created_by","created_by_msisdn",
#             "nomade_created_by","level1_approved_on","level1_approved_by","level2_approved_on","level2_approved_by","owner_id","owner_msisdn",
#             "user_domain_code","category_code","user_grade_name","modified_by","modified_on","modify_approved_by","modified_approved_on","deleted_on",
#             "deactivation_by","department","reg_form_num","remarks","geographical_domain","group_role","first_transaction_on","tango_msisdn","company_code","company_contact_no","company_contact_no_sec","user_type",
#             "action_type","agent_code","creation_type","bulk_id","identity_proof_type","address_proof_type","photo_proof_type","id_type","id_no",
#             "id_issue_place","id_issue_date","id_issue_country","id_expiry_date","residence_country","nationality","employer_name","postal_code",
#             "souscription_type","mobile_group_role","last_login_on","user_grade_code","parent_first_name","parent_last_name","owner_first_name",
#             "owner_last_name","correctedstate","workflow_state","id_card_image","portrait_image","business_reg_image","partner_image","signature_image",'payment_authority',"tax_num",
#             "business_permit_no","type_of_business","enterprise_code","type_service_requested","reason_om","region","account_number","account_name","bank_number","bank_name","registration_type",
#             "account_no_usd","account_no_lrd","title_authorized_signatory","ast_name","ast_number","benef_name","benef_contact","business_location","occupation","id_card","date_of_birth",'partner_type_id','bacthID','om_msisdn','other_location']:
#             if field in data:
#                 setattr(self, field, data[field])
        
#         if "api_password" in data:
#             self.set_api_password(data["api_password"])
        
#         if 'org_logo' in files.to_dict(): 
#             uploads_dir = current_app.config['UPLOADS_DIR']
#             if self.org_logo:
#                 if os.path.exists(os.path.join(uploads_dir,self.org_logo)):
#                     os.remove(os.path.join(uploads_dir,self.org_logo))

#             setattr(self, 'org_logo', self.file_upload(files,'org_logo'))
                    
#     def __repr__(self):
#         return '<Partners {}>'.format(self.contact_email)

# #Partner type entity
# class PartnerType(db.Model,baseModel):
#     # __tablename__ = 'PartnerType'
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(100), nullable=False) 
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(255), nullable=False)

#      # user info to dictionary
#     def to_dict(self,permissions=False,new_partner_type=False):
#         data = {
#             'id': self.id,
#             'code': self.code,
#             'title': self.title,
#             'description': self.description,
#         }

#         if permissions:
#             data["permissions"] = [permission.to_dict(features=True) for permission in self.permissions]

#         if new_partner_type:
#             partner_type = PartnerType.query.filter_by(partner_type=self.id).all()
#             data["partners"] = [partner_type.to_dict(features=True) for partenr in self.partner]

#         return data  

#     # save user info from dictionary
#     def from_dict(self, data, new_partner_type=False):
#         for field in ["dele",'title','description','code']:
#             if field in data:
#                 setattr(self, field, data[field])
    

#     def __repr__(self):
#         return '<UserType {}>'.format(self.title)

# roles_users = db.Table('roles_users',
#         db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#         db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))) 

# #User type entity
# class UserType(db.Model,baseModel):
#     # __tablename__ = 'usertype'
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(100), nullable=False, unique=True) #ORGSU - ORGU - BACKU
#     title = db.Column(db.String(100), nullable=False, unique=True)
#     description = db.Column(db.String(255), nullable=False)
#     permissions = db.relationship('Permissions', backref='user_type_permissions')
#     user = db.relationship('User', backref='user_type_users')
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

#      # user info to dictionary
#     def to_dict(self,permissions=False,users=False):
#         data = {
#             'id': self.id,
#             'code': self.code,
#             'title': self.title,
#             'description': self.description,
#             'created_on': self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
#         }

#         if permissions:
#             data["permissions"] = [permission.to_dict(features=True) for permission in self.permissions]

#         if users:
#             data["users"] = [user.to_dict(features=True) for user in self.user]

#         return data  

#     # save user info from dictionary
#     def from_dict(self, data, new_user_type=False):
#         for field in ["dele",'title','description','code']:
#             if field in data:
#                 setattr(self, field, data[field])
    

#     def __repr__(self):
#         return '<UserType {}>'.format(self.title)

# # user entity for creating new portal user 
# class User(db.Model):
#     __tablename__ = 'user'
#     # id = db.Column(db.Integer, primary_key=True)
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     first_name = db.Column(db.String(56), nullable=False)
#     last_name = db.Column(db.String(56), nullable=False)
#     parent_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
#     email = db.Column(db.String(120), index=True, unique=True)
#     phone = db.Column(db.String(25), index=True, unique=True)
#     password_hash = db.Column(db.String(128))
#     last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     otp_id = db.Column(db.String(20))
#     status = db.Column(db.String(60), default='new') #new - change_password - otp - validated
#     login_token = db.Column(db.String(255))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     user_type_id = db.Column(db.Integer, db.ForeignKey('user_type.id'), nullable=True)
#     rule_id = db.Column(db.Integer, db.ForeignKey('rules.id'), nullable=True)
#     date_pwd_generated = db.Column(db.DateTime(), default=datetime.utcnow)
#     dele = db.Column(db.String(255),default="FALSE")
#     roles = db.relationship('Role', secondary=roles_users, backref='roled')
#     otp_code = db.Column(db.String(6))

    
#     def sendOtpSms(self):
#         data = {
#                 "auth":{"user":current_app.config['SMS_API_USER'], "pwd":current_app.config['SMS_API_PASSWORD'] },
#                 "param":{"msisdn":self.phone, "presms":"OTP"}
#             }

#         res = requests.post('{}TIMM/v1/Subscriber/OTP/Request'.format(current_app.config['TEST_HTTP_API_URLS']), data=json.dumps(data))
#         return res
#     #def sendOtpSms(self):
#     #    return {"exec_code":0 , "exec_msg":"Success", "resultset": {"OTPID":1010}}


#     def validateOtpSms(self,pin):
#         data = {
#                 "auth":{"user":current_app.config['SMS_API_USER'], "pwd":current_app.config['SMS_API_PASSWORD'] },
#                 "param":{"msisdn":self.phone, "pin":"{}".format(pin), "otpid":self.otp_id }
#             }
#         res = requests.post('{}TIMM/v1/Subscriber/OTP/Validation'.format(current_app.config['TEST_HTTP_API_URLS']), data=json.dumps(data))
#         return res

#     def sendSMSNotification(self,password):
#         data = {
#                 "auth":{"user":current_app.config['SMS_API_USER'], "pwd":current_app.config['SMS_API_PASSWORD'] },
#                 "param":{"msisdn":self.phone, "sms":'Hi partner, your account has been created on OM Portal. Use the following details to log in : URL: {}, Email: {}, password: {}. You must change your password'.format(current_app.config['OMP_FRONT_LINK'],self.email,password) }
#             }
#         # print(data)
        
#         res = requests.post('{}TIMM/v1/Subscriber/Notification/SMS'.format(current_app.config['TEST_HTTP_API_URLS']), data=json.dumps(data))
#         return res
    
#     def sendSMSasOTP(self,code):
        
#         data = {
#                 "auth":{"user":current_app.config['SMS_API_USER'], "pwd":current_app.config['SMS_API_PASSWORD'] },
#                 "param":{"msisdn":self.phone, "sms":'Hi partner, you OTP code is : {}'.format(code) }
#             }
#         # print(data)
        
#         res = requests.post('{}TIMM/v1/Subscriber/Notification/SMS'.format(current_app.config['TEST_HTTP_API_URLS']), data=json.dumps(data))
#         return res

#     def sendMailMessage(self,password):
#         send_email(self.email,  "Default Password",self, password)
#         return 'mail status'

#     # user info to dictionary
#     def to_dict(self,rules=False,user_type=False,password=False,partners=False,workflow=False,workflow_stat=False):

#         # print(rules,user_type)
#         data = {
#             'id': self.id,
#             'first_name': self.first_name,
#             'last_name': self.last_name,
#             'email': self.email,
#             'phone': self.phone,
#             'last_seen': self.last_seen.strftime("%Y-%m-%d %H:%M:%S"),
#             'created_on': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#             'status':self.status,
#         }

#         # if rules:
#             # data["rules"] = [rule.to_dict(permission=True) for rule in self.rules]
        
#         if user_type and self.user_type_id:
#             val= UserType.query.get(self.user_type_id)
#             if val:
#                 data["user_type"] = val.to_dict(permissions=True)
#             else:
#                 data["user_type"] = {}
        
#         if password:
#             data["default_password"] = password

#         if rules and self.rule_id:
#             data["rule"] = Rules.query.get(self.rule_id).to_dict(permissions=True)

#         if workflow:
#             data["workflows"] = [ x.to_dict(workflows=True) for x in UserWorkflows.query.filter_by(user_id=self.id).all()]

#         # if workflow_stat:
#         #     data["workflows_state"] = []
#         #     for items in data["workflows"]:
#         #         data["workflows_state"].append({items["code"]:len(Partners.query.filter_by(workflow_state=items["code"]).all())})

#         return data  

#     # save user info from dictionary
#     def from_dict(self, data, new_user=False):
#         for field in ["dele",'first_name', 'last_name', 'email', 'phone','status','user_type_id','rule_id','partner_id','api_user']:
#             if field in data:
#                 setattr(self, field, data[field])
#         if (new_user and 'password' in data) or 'password' in data:
#             #print(data['password'])
#             self.set_password(data['password'])
        

#         # hash user password input
    
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
    
#     # verify user password input hash with existing password hash
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def add_partner(self, partner):
#             self.partners.append(partner)

#     def remove_partner(self, partner):
#             self.partners.remove(partner)

#     # def partner_exists(self, partner):
#     #     return self.user.filter(
#     #         portal_users.c.partner_id == partner.id).count() > 0
    
#     def generate_auth_token(self, expiration=2592000):
#         s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        
#         return s.dumps({'id':self.id,"email":self.email,'state':self.status})
    
#     @staticmethod
#     def allowed(access):
#         print(access)
#         user = User.query.filter_by(email=session['email']).first()
#         if user.user_type_id:
#             user_type = UserType.query.get(user.user_type_id)
#             if user_type:
#                 if user_type.code in access:
#                     return True
#                 else:
#                     return False
#             else:
#                 return False
#         return False

        
#     @staticmethod
#     def verify_auth_token(token):
#         user = User.query.filter_by(login_token=token).first()
#         if user:
#             s = Serializer(current_app.config['SECRET_KEY'])

#             s
#             try:
#                 data = s.loads(token)
#                 print(data)
#             except:
#                 return None
#             # print(User.query.get(data['id']))
#             return user
#         else:
#             return None

#     def __repr__(self):
#         return '<User {}>'.format(self.email)


# class Role(db.Model):
#     __tablename__ = 'role'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
     
# class Permissions(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     definition = db.Column(db.String(255), nullable=False)
#     permission = db.Column(db.String(255), nullable=True)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     user_type_id = db.Column( db.Integer, db.ForeignKey('user_type.id'))
#     feature_id=db.Column(db.Integer, db.ForeignKey('features.id'))
#     # rules = db.relationship('Rules', backref='pemission_rules')
#     rule_id = db.Column( db.Integer, db.ForeignKey('rules.id'))

    
#     # partner info to dictionary
#     def to_dict(self,feature=False,user_type=False):
#         data = {
#             "id":self.id,
#             "definition":self.definition,
#             "permission":self.permission,
#             "created_on": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#             }

#         if feature:
#             data["feature"] = Features.query.get(self.feature_id).to_dict()
        
#         if user_type:
#             data["user_type"] = UserType.query.get(self.user_type_id).to_dict()

#         return data

#     # save partner info from dictionary
#     def from_dict(self, data, new_permission=False):
#         for field in ["dele",'definition', 'permission','user_type_id','feature_id','rule_id']:
#             if field in data:
#                 setattr(self, field, data[field])


#     def __repr__(self):
#         return '<Permission {}>'.format(self.title)


# class Notification(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255))
#     text = db.Column(db.String(255))
#     picture = db.Column(db.String(64))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    
#     # partner info to dictionary
#     def to_dict(self):
#         data = {
#             "id":self.id,
#             "title":self.title,
#             "text":self.text,
#             "picture":self.picture,     
#             "created_on": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
#             }
#         return data

#     # save partner info from dictionary
#     def from_dict(self, data,files, new_notification=False):
#         print()
#         for field in ["dele",'title', 'text', 'picture']:
#             if field in data:
#                 setattr(self, field, data[field][0])
#             elif files and field=='picture':
#                 uploads_dir = current_app.config['UPLOADS_DIR']
#                 if self.picture:
#                     if os.path.exists(os.path.join(uploads_dir,self.picture)):
#                         os.remove(os.path.join(uploads_dir,self.picture))
#                 setattr(self, field, self.file_upload(files,'picture'))



#     def __repr__(self):
#         return '<Notification {}>'.format(self.title)


# class WorkflowSteps(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255))
#     code = db.Column(db.String(255))
#     description = db.Column(db.String(255))


#         # save partner info from dictionary
#     def from_dict(self, data, new_workflowstep=False):
#         for field in ["dele",'title','description','code'] :
#             if field in data:
#                 setattr(self, field, data[field])

#     # partner info to dictionary
#     def to_dict(self,new_workflowstep=False):
#         data = {
#             "id":self.id,
#             "title":self.title,
#             "code":self.code,
#             "description":self.description,
#         }

#         return data


# class PartnerWorkflows(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     workflowstep_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'))
#     partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
#     state = db.Column(db.String(255)) # PENDING - DONE - REJECTED
#     comment = db.Column(db.String(255))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

#     # save partner info from dictionary
#     def from_dict(self, data):
#         for field in ["dele",'template_id','workflowstep_id','state','comment',"user_id"] :
#             if field in data:
#                 setattr(self, field, data[field])

#     # partner info to dictionary
#     def to_dict(self,workflows=False,user=False,partner=False):
#         data = {
#             "id":self.id,
#             "state":self.state,
#             "comment":self.comment,
#         }

#         if workflows:
#             data["workflows"] = WorkflowSteps.query.get(self.workflowstep_id).to_dict()

#         # if user:
#         #     try :
#         #         data["user"] = User.query.get(self.user_id).to_dict()
#         #     except:
#         #         data["user"] = {}

#         if partner and self.partner_id:
#             data['partner'] = Partners.query.get(self.partner_id).to_dict(template_items=True)

#         return data


# class UserWorkflows(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     workflowstep_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'))
    


#         # save partner info from dictionary
#     def from_dict(self, data):
#         for field in ["dele",'user_id','workflowstep_id'] :
#             if field in data:
#                 setattr(self, field, data[field])

#     # partner info to dictionary
#     def to_dict(self,workflows=False,user=False):
#         data = {
#             "id":self.id,
#             "user_id":self.user_id,
#             "workflowstep_id":self.workflowstep_id,
#         }

#         if self.user_id and user:
#             data["user"] = User.query.get(self.user_id).to_dict()

#         if workflows and self.workflowstep_id:
#             data = WorkflowSteps.query.get(self.workflowstep_id).to_dict()

#         return data
  
# #Features type entity
# class Features(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(100), nullable=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(255), nullable=False)
#     permissions = db.relationship('Permissions', backref='feature_permissions')
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)    
#     childs = db.relationship( 'Features')
#     parent_id = db.Column( db.Integer, db.ForeignKey('features.id'))

#     #user info to dictionary
#     def to_dict(self,parent=False,childs=False):
#         data = {
#             'id': self.id,
#             'title': self.title,
#             'code': self.code,
#             'description': self.description,
#             'created_on': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
#         }

#         if self.parent_id  and parent:
#             data["parent"] = Features.query.get(self.parent_id).to_dict()
        
#         if childs:
#             data["childs"] = [child.to_dict(childs=True) for child in self.childs]

#         return data  

#     #save feature info from dictionary
#     def from_dict(self, data, new_feature=False):
#         for field in ["dele",'title','description', 'timestamp',"parent_id","code"]:
#             if field in data:
#                 setattr(self, field, data[field])
    
    
#     def __repr__(self):
#         return '<Feature {}>'.format(self.title)
 
# #Rules type entity
# class Rules(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(255), nullable=False)
#     default = db.Column(db.Boolean, default=False)
#     users = db.relationship('User', backref='rule_users')
#     permissions = db.relationship('Permissions', cascade="all,delete",backref='permissions_rules')
#     user_type_id = db.Column( db.Integer, db.ForeignKey('user_type.id'))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

#      # user info to dictionary
#     def to_dict(self,users=False,permissions=False,user_type=False):
#         data = {
#             'id': self.id,
#             'title': self.title,
#             'description': self.description,
#             'default':self.default,
#             'created_on': self.timestamp
#         }

#         if permissions:
#             data["fonctionalites"] = [Features.query.get(permission.feature_id).to_dict() for permission in self.permissions]
        
#         if users:
#             data["user"] = [ user.to_dict() for user in self.users ]
#         if user_type and self.user_type_id:
#             data["user_type"] = UserType.query.get(self.user_type_id).to_dict()

#         return data  

#     def add_permissions(self,permission):
#         self.permissions.append(permission)
#     # save user info from dictionary

#     def remove_permissions(self,permission):
#         self.permissions.remove(permission)


#     def from_dict(self, data, new_rule=False):
#         for field in ["dele",'title','description', 'timestamp', 'user_type_id', 'default']:
#             if field in data:
#                 setattr(self, field, data[field])
    
#     def __repr__(self):
#         return '<Rule {}>'.format(self.title)
 

# #Histories type entity
# class Histories(db.Model,baseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column( db.Integer, db.ForeignKey('user.id'))
#     urls = db.Column(db.String(255), nullable=False)
#     body = db.Column(db.Text, default=False)
#     response = db.Column(db.Text, default=False)
#     response_code = db.Column(db.String, default=False)
#     uuid = db.Column(db.String(255), default=False)

#     def from_dict(self, data):
#         for field in ["user_id",'urls','body', 'response', 'response_code', 'default',"uuid"]:
#             if field in data:
#                 setattr(self, field, data[field])

#     def to_dict(self,user=False):
#         data = {
#             'id': self.id,
#             'urls': self.urls,
#             'body': self.body,
#             'response':self.response,
#             'response_code': self.response_code,
#             "uuid":self.uuid
#         }

#         if user and self.user_id:
#             data["user"] = User.query.get(self.user_id).to_dict()

#         return data 
