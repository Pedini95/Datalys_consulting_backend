#!/usr/bin/env python3
"""
Script pour initialiser la base de données et créer toutes les tables
- Crée la base si elle n'existe pas
- Crée toutes les tables définies par les modèles SQLAlchemy
"""

import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.url import make_url

# Importer l'application Flask et les modèles
from app import app, db
from models import *  # noqa: F401,F403

def ensure_database_exists(sqlalchemy_uri: str) -> None:
    """Crée la base MySQL si elle n'existe pas encore."""
    url = make_url(sqlalchemy_uri)
    database_name = url.database

    # Construire une URL sans la base de données
    server_url = url.set(database=None)
    engine = create_engine(server_url)

    with engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database_name}`"))
        # Optionnel: définir charset/collation si nécessaire
        # connection.execute(text(f"ALTER DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        connection.commit()


def init_database() -> bool:
    """Initialiser la base de données et créer toutes les tables"""
    try:
        sqlalchemy_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not sqlalchemy_uri:
            print("❌ SQLALCHEMY_DATABASE_URI manquant dans la configuration")
            return False

        print("🔧 Vérification/création de la base de données...")
        try:
            ensure_database_exists(sqlalchemy_uri)
            print("✅ Base de données prête")
        except SQLAlchemyError as db_err:
            print(f"⚠️ Impossible de créer/vérifier la base: {db_err}")
            # On continue: si la base existe déjà mais sans droits CREATE, create_all peut fonctionner

        with app.app_context():
            print("🔧 Création des tables (si manquantes)...")
            db.create_all()
            print("✅ Tables créées ou déjà présentes")

            # Afficher la liste des tables pour vérification
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables détectées: {', '.join(tables) if tables else '(aucune)'}")

            return True

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {str(e)}")
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