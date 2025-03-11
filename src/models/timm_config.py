from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities


class TimmConfig(db.Model):
    __tablename__ = 'timm_config'

    id = db.Column(db.Integer, primary_key=True)
    projet_name = db.Column(db.String(255))
    timm_user = db.Column(db.String(255))
    timm_password = db.Column(db.String(255))
    timm_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    is_deleted = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    search_string = db.Column(db.Text)


    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            if c.name == 'timm_password':
                continue
            value = getattr(self, c.name)
            if c.name in ('created_at', 'updated_at') and value:
                data[c.name] = value.strftime("%d/%m/%Y %H:%M:%S")
            elif value is not None:  
                data[c.name] = value
        return data

    # Repository
    def find_one(id, is_deleted):
        tIMMConfig = TimmConfig.query.filter_by(id=id, is_deleted=is_deleted).first()
        return tIMMConfig

    def find_by_projet_name(projet_name, is_deleted):
        tIMMConfig = TimmConfig.query.filter_by(projet_name=projet_name, is_deleted=is_deleted).first()
        return tIMMConfig

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
        

    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = TimmConfig.query
        
        # Définir une liste de conditions
        conditions = [TimmConfig.is_deleted == False]
        if 'id' in criteria:
            conditions.append(TimmConfig.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(TimmConfig.search_string.like(f"%{criteria['search_string']}%"))

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(TimmConfig.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items