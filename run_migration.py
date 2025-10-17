#!/usr/bin/env python3
"""
Script pour exécuter les migrations de base de données
"""
import sys
from extensions import db
from app import create_app

def run_migration():
    """Exécute la migration pour ajouter is_active à projects"""
    app = create_app()

    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            result = db.session.execute(db.text("""
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'projects'
                AND COLUMN_NAME = 'is_active'
            """))
            column_exists = result.scalar() > 0

            if column_exists:
                print("✅ La colonne 'is_active' existe déjà dans la table 'projects'")
                return

            print("🔄 Ajout de la colonne 'is_active' à la table 'projects'...")

            # Ajouter la colonne
            db.session.execute(db.text("""
                ALTER TABLE projects
                ADD COLUMN is_active TINYINT(1) DEFAULT 1 AFTER partner_id
            """))

            # Mettre à jour les projets existants
            db.session.execute(db.text("""
                UPDATE projects SET is_active = 1 WHERE is_active IS NULL
            """))

            db.session.commit()
            print("✅ Migration réussie ! La colonne 'is_active' a été ajoutée.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la migration: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    run_migration()
