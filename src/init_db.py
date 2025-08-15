#!/usr/bin/env python3
"""
Script pour initialiser la base de données et créer toutes les tables
"""

import os
import sys

# Charger les variables d'environnement directement
# Les variables sont déjà définies dans le conteneur Docker

# Importer l'application Flask
from app import app, db
from models import *

def init_database():
    """Initialiser la base de données et créer toutes les tables"""
    try:
        with app.app_context():
            print("🔧 Initialisation de la base de données...")
            
            # Créer toutes les tables
            db.create_all()
            
            print("✅ Toutes les tables ont été créées avec succès !")
            
            # Vérifier les tables créées
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables créées : {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage de l'initialisation de la base de données...")
    success = init_database()
    
    if success:
        print("🎉 Base de données initialisée avec succès !")
        sys.exit(0)
    else:
        print("💥 Échec de l'initialisation de la base de données")
        sys.exit(1) 