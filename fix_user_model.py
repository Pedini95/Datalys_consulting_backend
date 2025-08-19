#!/usr/bin/env python3
"""
Script pour corriger le modèle User dans le conteneur Docker
"""

import subprocess
import sys

def run_ssh_command(command):
    """Exécute une commande SSH"""
    try:
        result = subprocess.run(
            f'ssh root@82.112.253.137 "{command}"',
            shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur SSH: {e}")
        return None

def fix_user_model():
    """Corrige le modèle User dans le conteneur"""
    
    # Contenu corrigé du modèle User (sans relations problématiques)
    corrected_content = '''from extensions import db
from sqlalchemy import and_
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)  # Changed from username to name
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_temp_password = db.Column(db.Boolean, default=False)  # Gestion des mots de passe temporaires
    fcm_token = db.Column(db.String(255), nullable=True)  # Token Firebase Cloud Messaging pour notifications push

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(255), nullable=True)

    def as_dict(self):
        data = {}
        # Utiliser les attributs de la classe directement
        columns = ['id', 'name', 'email', 'password_hash', 'is_temp_password', 'fcm_token', 'role_id', 
                  'is_active', 'is_deleted', 'created_at', 'created_by', 'updated_at', 'updated_by']
        
        for column in columns:
            value = getattr(self, column, None)
            if value is not None:
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value
            elif column == 'fcm_token':
                # Toujours inclure fcm_token même si None
                data[column] = value
        
        # Ajouter un champ username pour la compatibilité (alias de name)
        data['username'] = data.get('name', '')
        
        return data

    @staticmethod
    def get_by_criteria(criteria, index, size):
        query = User.query
        conditions = [User.is_deleted == False]
        
        if 'id' in criteria:
            conditions.append(User.id == criteria['id'])
        if 'name' in criteria:
            # Rechercher dans name seulement
            conditions.append(User.name.like(f"%{criteria['name']}%"))
        if 'email' in criteria:
            conditions.append(User.email.like(f"%{criteria['email']}%"))
        if 'role_id' in criteria:
            conditions.append(User.role_id == criteria['role_id'])
        if 'is_active' in criteria:
            conditions.append(User.is_active == criteria['is_active'])
        if 'fcm_token' in criteria:
            conditions.append(User.fcm_token == criteria['fcm_token'])

        query = query.filter(and_(*conditions))
        query = query.order_by(User.id.desc())
        
        total_items = query.count()
        query = query.offset(index * size).limit(size)
        return query.all(), total_items

    def __repr__(self):
        return f'<User {self.email}>'
'''
    
    # Sauvegarder le contenu dans un fichier temporaire
    with open('user_model_fixed.py', 'w') as f:
        f.write(corrected_content)
    
    # Copier le fichier corrigé dans le conteneur
    print("📝 Copie du modèle User corrigé dans le conteneur...")
    result = run_ssh_command("docker cp user_model_fixed.py datalys-api:/app/src/models/user.py")
    
    if result is not None:
        print("✅ Modèle User corrigé avec succès")
        
        # Vérifier que le fichier a été copié correctement
        print("🔍 Vérification du fichier corrigé...")
        check_result = run_ssh_command("docker exec datalys-api grep -A 5 -B 5 'fcm_token.*None' /app/src/models/user.py")
        
        if check_result and 'fcm_token' in check_result:
            print("✅ Vérification réussie - le modèle User inclut maintenant fcm_token")
            return True
        else:
            print("❌ Vérification échouée")
            return False
    else:
        print("❌ Échec de la copie du fichier")
        return False

if __name__ == "__main__":
    print("🔧 CORRECTION DU MODÈLE USER")
    print("=" * 50)
    
    success = fix_user_model()
    
    if success:
        print("\n🎉 SUCCÈS ! Le modèle User a été corrigé")
        print("Le champ fcm_token sera maintenant inclus dans les réponses API")
    else:
        print("\n❌ ÉCHEC ! Impossible de corriger le modèle User")
        sys.exit(1)
