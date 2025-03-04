from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities



class RoleFonctionalite(db.Model):
    __tablename__ = 'role_fonctionalite'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    is_deleted = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    fonctionnalite_id = db.Column(db.Integer, db.ForeignKey('fonctionalite.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    search_string = db.Column(db.Text)

    fonctionnalite = db.relationship('Fonctionalite', backref='role_fonctionnalites')
    role = db.relationship('Role', backref='role_fonctionnalites')


    def as_dict(self):
        return {
            'id': self.id,
            'is_deleted': self.is_deleted,
            'fonctionnalite_id': self.fonctionnalite_id,
            'role_id': self.role_id,
            'fonctionnalite': self.fonctionnalite.as_dict() if self.fonctionnalite else None,
            'role': self.role.as_dict() if self.role else None,
        }

    @staticmethod
    def find_by_fonctionnalite_id(fonctionnalite_id, is_deleted):
        return RoleFonctionalite.query.filter_by(fonctionnalite_id=fonctionnalite_id, is_deleted=is_deleted).first()
    
    @staticmethod
    def find_by_role_id(role_id, is_deleted):
        return RoleFonctionalite.query.filter_by(role_id=role_id, is_deleted=is_deleted).first()
    
    @staticmethod
    def find_by_fonctionnalite_id_and_role_id(fonctionnalite_id, role_id, is_deleted):
        return RoleFonctionalite.query.filter_by(fonctionnalite_id=fonctionnalite_id, role_id=role_id, is_deleted=is_deleted).first()
    
    @staticmethod
    def find_by_is_deleted(is_deleted):
        return RoleFonctionalite.query.filter_by(is_deleted=is_deleted).all()
    

    @staticmethod
    def find_one(id, is_deleted):
        role_fonctionalite = RoleFonctionalite.query.filter_by(id=id, is_deleted=is_deleted).first()
        return role_fonctionalite
    
    @staticmethod
    def find_by_created_by(created_by, is_deleted):
        role_fonctionalites = RoleFonctionalite.query.filter_by(created_by=created_by, is_deleted=is_deleted).all()
        return role_fonctionalites
    

    @staticmethod
    def find_by_is_deleted(is_deleted):
        role_fonctionalites = RoleFonctionalite.query.filter_by(is_deleted=is_deleted).all()
        return role_fonctionalites
    
    
    @staticmethod
    def find_by_role_id(role_id, is_deleted):
        role_fonctionalites = RoleFonctionalite.query.filter_by(role_id=role_id, is_deleted=is_deleted).all()
        return role_fonctionalites
    

    @staticmethod
    def find_by_fonctionnalite_id(fonctionnalite_id, is_deleted):
        role_fonctionalites = RoleFonctionalite.query.filter_by(fonctionnalite_id=fonctionnalite_id, is_deleted=is_deleted).all()
        return role_fonctionalites
    


    