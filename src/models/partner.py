from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities


class Patner(db.Model):
    __tablename__ = 'patner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agent_name = db.Column(db.String(255))
    agent_location = db.Column(db.String(255))
    district = db.Column(db.String(255))
    county = db.Column(db.String(255))
    id_number = db.Column(db.String(255))
    date_of_birth = db.Column(db.DateTime)
    place_of_birth = db.Column(db.String(255))
    occupation = db.Column(db.String(255))
    beneficiary_name = db.Column(db.String(255))
    beneficiary_contact = db.Column(db.String(255))
    contact_mobile = db.Column(db.String(255))
    nationality = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    whatsapp_number = db.Column(db.String(255))
    territory_name = db.Column(db.String(255))
    tsa_name = db.Column(db.String(255))
    tsa_contact = db.Column(db.String(255))
    rsm_name = db.Column(db.String(255))
    manager_name = db.Column(db.String(255))
    super_agent_name = db.Column(db.String(255))
    super_agent_contact = db.Column(db.String(255))
    super_agent_parent_number = db.Column(db.String(255))
    signature_and_date = db.Column(db.String(255))
    signature_date = db.Column(db.DateTime)
    indirect_manager_approval = db.Column(db.String(255))
    date_manager_approval = db.Column(db.DateTime)
    id_document_image = db.Column(db.String(255))
    id_document_image_back = db.Column(db.String(255))
    agent_image = db.Column(db.String(255))
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
        partner = Patner.query.filter_by(id=id, is_deleted=is_deleted).first()
        return partner

    
    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = Patner.query

        # Définir une liste de conditions
        conditions = [Patner.is_deleted == False]
        if 'id' in criteria:
            conditions.append(Patner.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(Patner.search_string.like(f"%{criteria['search_string']}%"))

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
                    # conditions.append(Patner.created_at.between(start_date_converted, end_date_converted))
                    conditions.append(and_(Patner.created_at >= start_date_converted, Patner.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(Patner.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(Patner.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(Patner.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(Patner.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(Patner.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(Patner.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(Patner.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(Patner.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items
        