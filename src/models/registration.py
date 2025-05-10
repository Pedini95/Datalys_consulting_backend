from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities


class Registration(db.Model):
    __tablename__ = 'registration'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    address_types_id = db.Column(db.String(255))
    country_id = db.Column(db.String(255))
    county_id = db.Column(db.String(255))
    agent_pin = db.Column(db.String(255))
    agentdeviceId = db.Column(db.String(255))
    agenticcid = db.Column(db.String(255))
    agentimei = db.Column(db.String(255))
    agentmsisdn = db.Column(db.String(255))
    birth_date = db.Column(db.String(255))
    birth_place = db.Column(db.String(255))
    cell_id = db.Column(db.String(255))
    email = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    gender_id = db.Column(db.String(255))
    iccid = db.Column(db.String(255))
    id_card_Number = db.Column(db.String(255))
    id_card_type_id = db.Column(db.String(255))
    k_name = db.Column(db.String(255))
    kin_email = db.Column(db.String(255))
    kin_name = db.Column(db.String(255))
    kin_phone = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    latitude = db.Column(db.String(255))
    longitude = db.Column(db.String(255))
    msisdn = db.Column(db.String(255))
    occupation_id = db.Column(db.String(255))
    reg_date = db.Column(db.String(255))
    reg_type = db.Column(db.String(255))
    workaddress = db.Column(db.String(255))
    app_version = db.Column(db.String(50))
    contract_image = db.Column(db.String(255))
    agent_signature = db.Column(db.String(255))
    reg_uuid = db.Column(db.String(255))
    statut = db.Column(db.String(255))
    id_document_image = db.Column(db.String(255))
    id_document_image_back = db.Column(db.String(255))
    customer_image = db.Column(db.String(255))
    customer_image_ocr = db.Column(db.String(255))
    search_string = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    
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


    def find_by_id(id):
        return Registration.query.get(id)

    @staticmethod
    def find_by_reg_uuid(reg_uuid, is_deleted):
        return Registration.query.filter_by(reg_uuid=reg_uuid, is_deleted=is_deleted).first()


    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = Registration.query

        # Définir une liste de conditions
        conditions = [Registration.is_deleted == False]
        if 'id' in criteria:
            conditions.append(Registration.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(Registration.search_string.like(f"%{criteria['search_string']}%"))

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
                    conditions.append(and_(Registration.created_at >= start_date_converted, Registration.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(Registration.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(Registration.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(Registration.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(Registration.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(Registration.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(Registration.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(Registration.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(Registration.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def update_registration(uid: str,  statut: str):
        registration = Registration.find_by_reg_uuid(uid, False)
        logging.info("**** registration : {}".format(registration))
        if registration:
            registration.statut = statut
            registration.updated_at = datetime.utcnow()
            db.session.commit()


    def save_registration(data: dict, uid: str):
        """
        Enregistre une nouvelle ligne dans la table registration avec traitement d’images.
        """
        try:
            # Nettoyage des données
            cleaned_data = {k: (v if v not in ("", None) else None) for k, v in data.items()}

            # Liste des champs images à traiter
            image_fields = [
                "contract_image",
                "agent_signature",
                "id_document_image",
                "id_document_image_back",
                "customer_image",
                "customer_image_ocr"
            ]

            for field in image_fields:
                if cleaned_data.get(field):
                    # Appel d'une fonction qui sauvegarde l'image et retourne le chemin du fichier
                    cleaned_data[field] = utilities.save_base64_image_lite(
                        cleaned_data[field],
                        prefix=field  # permet d’avoir un nom clair pour chaque fichier
                    )

            # Valeurs par défaut
            cleaned_data.setdefault("created_at", datetime.utcnow())
            cleaned_data.setdefault("updated_at", datetime.utcnow())
            cleaned_data.setdefault("is_deleted", False)
            cleaned_data["agent_pin"] = "****"
            cleaned_data["birth_date"] = datetime.strptime(cleaned_data['birth_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d"),
            cleaned_data["reg_date"] = datetime.strptime(cleaned_data['reg_date'], "%a %b %d %Y %H:%M:%S GMT%z").strftime("%Y-%m-%d %H:%M:%S"),
            cleaned_data["reg_uuid"] = uid
            cleaned_data["search_string"] = utilities.build_search_string(cleaned_data)

            # Création de l'entité SQLAlchemy
            registration = Registration(**cleaned_data)
            db.session.add(registration)
            db.session.commit()

            return registration
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erreur lors de l’enregistrement : {str(e)}")

    

