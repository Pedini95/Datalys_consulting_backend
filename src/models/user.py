
from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities
from .role import Role



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    born_on = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    date_send_code_otp_at = db.Column(db.DateTime)
    email = db.Column(db.String(255))
    first_connection = db.Column(db.DateTime)
    first_name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    is_connected = db.Column(db.Boolean)
    is_default_password = db.Column(db.Boolean)
    is_ldap_user = db.Column(db.Boolean)
    is_locked = db.Column(db.Boolean)
    is_valid_pass_code = db.Column(db.Boolean)
    is_valid_token = db.Column(db.String(255))
    last_activity_date = db.Column(db.DateTime)
    last_connection_date = db.Column(db.DateTime)
    last_lock_date = db.Column(db.DateTime)
    last_name = db.Column(db.String(255))
    login = db.Column(db.String(255))
    login_attempts = db.Column(db.Integer)
    otp_code = db.Column(db.String(50))
    pass_code = db.Column(db.String(255))
    pass_code_created_at = db.Column(db.DateTime)
    pass_code_expire_at = db.Column(db.DateTime)
    password = db.Column(db.String(255))
    search_string = db.Column(db.Text)
    telephone = db.Column(db.String(255))
    token = db.Column(db.String(500))
    token_created_at = db.Column(db.DateTime)
    token_expire_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    file_path = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users', lazy=True)
    


    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if c.name == 'created_at' and value:
                data[c.name] = value.strftime("%d/%m/%Y %H:%M:%S")
            elif c.name == 'updated_at' and value:
                data[c.name] = value.strftime("%d/%m/%Y %H:%M:%S")
            elif value is not None:  # Exclure les champs nulls
                data[c.name] = value
        return data
    

    # repository methods
    @staticmethod
    def find_one(id, is_deleted):
        return User.query.filter_by(id=id, is_deleted=is_deleted).first()
    
    @staticmethod
    def find_by_email(email, is_deleted):
        return User.query.filter_by(email=email, is_deleted=is_deleted).first()
    
    @staticmethod
    def find_by_login(login, is_deleted):
        return User.query.filter_by(login=login, is_deleted=is_deleted).first()
    
    @staticmethod
    def find_by_is_deleted(is_deleted):
        return User.query.filter_by(is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_created_by(created_by, is_deleted):
        return User.query.filter_by(created_by=created_by, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_updated_by(updated_by, is_deleted):
        return User.query.filter_by(updated_by=updated_by, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_role_id(role_id, is_deleted):
        return User.query.filter_by(role_id=role_id, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_is_active(is_active, is_deleted):
        return User.query.filter_by(is_active=is_active, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_is_locked(is_locked, is_deleted):
        return User.query.filter_by(is_locked=is_locked, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_is_valid_pass_code(is_valid_pass_code, is_deleted):
        return User.query.filter_by(is_valid_pass_code=is_valid_pass_code, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_is_valid_token(is_valid_token, is_deleted):
        return User.query.filter_by(is_valid_token=is_valid_token, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_is_connected(is_connected, is_deleted):
        return User.query.filter_by(is_connected=is_connected, is_deleted=is_deleted).all() 
    
    @staticmethod
    def find_by_is_default_password(is_default_password, is_deleted):
        return User.query.filter_by(is_default_password=is_default_password, is_deleted=is_deleted).all()
    
    @staticmethod
    def find_by_is_ldap_user(is_ldap_user, is_deleted):
        return User.query.filter_by(is_ldap_user=is_ldap_user, is_deleted=is_deleted).all()
    
    
    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = User.query

        # Définir une liste de conditions
        conditions = [User.is_deleted == False]
        if 'id' in criteria:
            conditions.append(User.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(User.search_string.like(f"%{criteria['search_string']}%"))

        # **Gestion du filtre par date**
        if 'date_param' in criteria:
            date_param = criteria['date_param']
            operator = date_param.get('operator', '')
            start_date = date_param.get('start_date', '')
            end_date = date_param.get('end_date', '')
            
            # Convertir les dates au format YYYY-MM-DD HH:MM:SS
            def convert_date(date_str):
                try:
                    return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    return None
            start_date_converted = convert_date(start_date)
            end_date_converted = convert_date(end_date)
            if start_date_converted or end_date_converted:
                if operator == "[]" and start_date_converted and end_date_converted:
                    # conditions.append(Registration.created_at.between(start_date_converted, end_date_converted))
                    conditions.append(and_(User.created_at >= start_date_converted, User.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(User.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(User.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(User.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(User.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(User.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(User.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(User.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(User.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items
    
