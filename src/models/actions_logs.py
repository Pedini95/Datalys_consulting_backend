from app import db, app
from flask import Flask, jsonify, request
from sqlalchemy import or_, and_
import re
from datetime import datetime, date
import logging
import utils.utilities as utilities

class ActionsLogs(db.Model):
    __tablename__ = 'actions_logs'

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(255))
    uri = db.Column(db.String(255))
    request = db.Column(db.Text)
    response = db.Column(db.Text)
    statut = db.Column(db.String(255))
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

    
    # Repository
    def find_one(id, is_deleted):
        actions_logs = ActionsLogs.query.filter_by(id=id, is_deleted=is_deleted).first()
        return actions_logs

    def find_by_libelle(libelle, is_deleted):
        actions_logs = ActionsLogs.query.filter_by(libelle=libelle, is_deleted=is_deleted).first()
        return actions_logs

    def action_logs_init_save(libelle, uri, request, response=None):
        actions_log = ActionsLogs(
            libelle=libelle,
            uri=uri,
            request=request,
            is_deleted=False,
            response=response,
            statut="Init",
            created_at=datetime.now(),
        )
        db.session.add(actions_log)
        db.session.commit()

    def action_logs_final_save(libelle, response=None, statut=None):
        action_log = ActionsLogs.find_by_libelle(libelle, False)
        action_log.response = response
        action_log.statut = statut
        action_log.updated_at = datetime.now()
        db.session.commit()

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
        query = ActionsLogs.query

        # Définir une liste de conditions
        conditions = [ActionsLogs.is_deleted == False]
        if 'id' in criteria:
            conditions.append(ActionsLogs.id == criteria['id'])
        if 'search_string' in criteria:
            conditions.append(ActionsLogs.search_string.like(f"%{criteria['search_string']}%"))

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
                    conditions.append(and_(ActionsLogs.created_at >= start_date_converted, ActionsLogs.created_at <= end_date_converted))
                elif operator == "][" and start_date_converted and end_date_converted:
                    conditions.append(ActionsLogs.created_at.not_between(start_date_converted, end_date_converted))
                elif operator == ">" and start_date_converted:
                    conditions.append(ActionsLogs.created_at > start_date_converted)
                elif operator == "<" and end_date_converted:
                    conditions.append(ActionsLogs.created_at < end_date_converted)
                elif operator == ">=" and start_date_converted:
                    conditions.append(ActionsLogs.created_at >= start_date_converted)
                elif operator == "<=" and end_date_converted:
                    conditions.append(ActionsLogs.created_at <= end_date_converted)
                elif operator == "==" and start_date_converted:
                    conditions.append(ActionsLogs.created_at == start_date_converted)
                elif operator == "!=" and start_date_converted:
                    conditions.append(ActionsLogs.created_at != start_date_converted)

        # Appliquer toutes les conditions à la requête
        query = query.filter(and_(*conditions))
        # Ajouter l'ordre de tri par ID décroissant
        query = query.order_by(ActionsLogs.id.desc())
        # Ajouter la pagination
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    