from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities


class Fonctionalite(db.Model):
    __tablename__ = 'fonctionalite'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer)
    is_available_for_user = db.Column(db.Boolean)
    is_deleted = db.Column(db.Boolean, default=False)
    libelle = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey('fonctionalite.id'))
    search_string = db.Column(db.Text)

    parent = db.relationship('Fonctionalite', remote_side=[id], backref='children')

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
    

    # Repository
    def find_one(id, is_deleted):
        fonctionalite = Fonctionalite.query.filter_by(id=id, is_deleted=is_deleted).first()
        return fonctionalite
    
    def find_by_code(code, is_deleted):
        fonctionalite = Fonctionalite.query.filter_by(code=code, is_deleted=is_deleted).first()
        return fonctionalite
    
    def find_by_libelle(libelle, is_deleted):
        fonctionalite = Fonctionalite.query.filter_by(libelle=libelle, is_deleted=is_deleted).first()
        return fonctionalite
    
    def find_by_is_available_for_user(is_available_for_user, is_deleted):
        fonctionalites = Fonctionalite.query.filter_by(is_available_for_user=is_available_for_user, is_deleted=is_deleted).all()
        return fonctionalites
    
    def find_by_created_by(created_by, is_deleted):
        fonctionalites = Fonctionalite.query.filter_by(created_by=created_by, is_deleted=is_deleted).all()
        return fonctionalites
    
    def find_by_is_deleted(is_deleted):
        fonctionalites = Fonctionalite.query.filter_by(is_deleted=is_deleted).all()
        return fonctionalites
    
    def find_by_parent_id(parent_id, is_deleted):
        fonctionalites = Fonctionalite.query.filter_by(parent_id=parent_id, is_deleted=is_deleted).all()
        return fonctionalites
    
    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = Fonctionalite.query

        # Définir une liste de conditions
        conditions = [Fonctionalite.is_deleted == False]
        if 'id' in criteria:
            conditions.append(Fonctionalite.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(Fonctionalite.search_string.like(f"%{criteria['search_string']}%"))

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
                    conditions.append(and_(Fonctionalite.created_at >= start_date_converted, Fonctionalite.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(Fonctionalite.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(Fonctionalite.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(Fonctionalite.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(Fonctionalite.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(Fonctionalite.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(Fonctionalite.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(Fonctionalite.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(Fonctionalite.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items