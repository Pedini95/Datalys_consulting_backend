from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities


class SeamfixTreatment(db.Model):
    __tablename__ = 'seamfix_treatment'

    id = db.Column(db.Integer, primary_key=True)
    # msidn = db.Column(db.String(255), nullable=True)
    msisdn = db.Column(db.String(255))
    id_card_picture_path = db.Column(db.String(255), nullable=True)
    id_contrat_picture_path = db.Column(db.String(255), nullable=True)
    id_front_picture_path = db.Column(db.String(255), nullable=True)
    search_string = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)


    def as_dict(self):
        data = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if c.name in ('created_at', 'updated_at') and value:
                data[c.name] = value.strftime("%d/%m/%Y %H:%M:%S")
            elif value is not None:  
                data[c.name] = value
        return data



    @staticmethod
    def get_by_criteria(criteria, index=None, size=None):
        query = SeamfixTreatment.query

        # Définir une liste de conditions
        conditions = [SeamfixTreatment.is_deleted == False]
        if 'id' in criteria:
            conditions.append(SeamfixTreatment.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(SeamfixTreatment.search_string.like(f"%{criteria['search_string']}%"))

        if 'msisdn' in criteria:
            conditions.append(SeamfixTreatment.msisdn.like(f"%{criteria['msisdn']}%"))

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
                    conditions.append(and_(SeamfixTreatment.created_at >= start_date_converted, SeamfixTreatment.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(SeamfixTreatment.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(SeamfixTreatment.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(SeamfixTreatment.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(SeamfixTreatment.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(SeamfixTreatment.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(SeamfixTreatment.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(SeamfixTreatment.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(SeamfixTreatment.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        if index is not None and size is not None:
            query = query.offset(index * size).limit(size)
        return query.all(), total_items