from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities


class OCRSeamfix(db.Model):
    __tablename__ = 'ocr_seamfix'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cardId = db.Column(db.String(255))
    msisdn = db.Column(db.String(255))
    nin = db.Column(db.String(255))
    firstName = db.Column(db.String(255))
    middleName = db.Column(db.String(255))
    lastName = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    birdDate = db.Column(db.String(255))
    status = db.Column(db.String(255))
    expiry = db.Column(db.String(255))
    placeOfBirth = db.Column(db.String(255))
    description = db.Column(db.String(255))
    documentCountryName = db.Column(db.String(255))
    documentDescription = db.Column(db.String(255))
    documentName = db.Column(db.String(255))
    documentType = db.Column(db.String(255))
    documentYear = db.Column(db.String(255))
    photo = db.Column(db.Text)
    search_string = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean)


    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if c.name in ('created_at', 'updated_at') and value:
                data[c.name] = value.strftime("%d/%m/%Y %H:%M:%S")
            elif value is not None:  
                data[c.name] = value
        return data

    
    # Repository
    def find_one(id, is_deleted):
        ocr_seamfix = OCRSeamfix.query.filter_by(id=id, is_deleted=is_deleted).first()
        return ocr_seamfix
        
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
        query = OCRSeamfix.query

        # Définir une liste de conditions
        conditions = [OCRSeamfix.is_deleted == False]
        if 'id' in criteria:
            conditions.append(OCRSeamfix.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(OCRSeamfix.search_string.like(f"%{criteria['search_string']}%"))

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
                    conditions.append(and_(OCRSeamfix.created_at >= start_date_converted, OCRSeamfix.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(OCRSeamfix.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(OCRSeamfix.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(OCRSeamfix.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(OCRSeamfix.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(OCRSeamfix.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(OCRSeamfix.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(OCRSeamfix.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(OCRSeamfix.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items