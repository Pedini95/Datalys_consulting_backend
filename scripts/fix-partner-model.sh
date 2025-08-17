#!/bin/bash

echo "🔧 CORRECTION DU MODÈLE PARTNER"
echo "================================"

# Vérifier si on est sur le serveur
if [ ! -f "/opt/Datalys_consulting_backend/docker-compose.deploy.yml" ]; then
    echo "❌ Ce script doit être exécuté sur le serveur"
    exit 1
fi

cd /opt/Datalys_consulting_backend

echo "📝 Mise à jour du fichier partner.py..."

# Créer le fichier partner.py avec le bon contenu
cat > src/models/partner.py << 'EOF'
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from extensions import db

Base = declarative_base()

class Partner(db.Model):
    __tablename__ = 'partners'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relations
    creator = relationship('User', foreign_keys=[created_by], backref='created_partners')
    updater = relationship('User', foreign_keys=[updated_by], backref='updated_partners')
    
    def __repr__(self):
        return f'<Partner {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'is_active': self.is_active,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def get_by_criteria(cls, criteria, index, size):
        query = cls.query
        conditions = [cls.is_deleted == False]
        
        if criteria.get('name'):
            conditions.append(cls.name.like(f'%{criteria['name']}%'))
        if criteria.get('email'):
            conditions.append(cls.email.like(f'%{criteria['email']}%'))
        if criteria.get('phone'):
            conditions.append(cls.phone.like(f'%{criteria['phone']}%'))
        if criteria.get('is_active') is not None:
            conditions.append(cls.is_active == criteria['is_active'])
        
        query = query.filter(*conditions)
        total_items = query.count()
        
        # Pagination
        if index is not None and size is not None:
            query = query.offset(index).limit(size)
        
        return query.all(), total_items
    
    @classmethod
    def check_duplicates(cls, email=None, phone=None, name=None, address=None, exclude_id=None):
        """
        Vérifier s'il existe des doublons pour les champs uniques
        """
        query = cls.query.filter(cls.is_deleted == False)
        
        if exclude_id:
            query = query.filter(cls.id != exclude_id)
        
        # Vérifier l'email (unique)
        if email:
            existing_email = query.filter(cls.email == email).first()
            if existing_email:
                return True, f"Un partenaire avec l'email '{email}' existe déjà"
        
        # Vérifier le téléphone (unique)
        if phone:
            existing_phone = query.filter(cls.phone == phone).first()
            if existing_phone:
                return True, f"Un partenaire avec le téléphone '{phone}' existe déjà"
        
        # Vérifier le nom (unique)
        if name:
            existing_name = query.filter(cls.name == name).first()
            if existing_name:
                return True, f"Un partenaire avec le nom '{name}' existe déjà"
        
        return False, ""
    
    @classmethod
    def get_by_id(cls, partner_id):
        return cls.query.filter(cls.id == partner_id, cls.is_deleted == False).first()
    
    @classmethod
    def get_all_active(cls):
        return cls.query.filter(cls.is_active == True, cls.is_deleted == False).all()
    
    @classmethod
    def soft_delete(cls, partner_id, user_id=None):
        partner = cls.get_by_id(partner_id)
        if partner:
            partner.is_deleted = True
            partner.updated_by = user_id
            partner.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
EOF

echo "✅ Fichier partner.py mis à jour"
echo "📊 Nombre de lignes: $(wc -l < src/models/partner.py)"

echo "🔄 Redémarrage du conteneur..."
docker-compose -f docker-compose.deploy.yml restart datalys-api

echo "⏳ Attente du redémarrage..."
sleep 15

echo "🔍 Vérification..."
docker exec datalys-api python -c "
from models.partner import Partner
print('✅ Partner.check_duplicates disponible:', hasattr(Partner, 'check_duplicates'))
print('✅ Partner.get_by_criteria disponible:', hasattr(Partner, 'get_by_criteria'))
"

echo "🎉 Correction terminée !" 