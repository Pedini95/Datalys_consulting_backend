#!/usr/bin/env python3
"""
Script pour vérifier et appliquer la migration des incidents
"""

import os
import sys
import logging

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import text, inspect
from app import app
from extensions import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_column_exists(table_name, column_name):
    """Vérifier si une colonne existe dans une table"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            columns = inspector.get_columns(table_name)
            return any(col['name'] == column_name for col in columns)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la colonne {column_name}: {e}")
        return False

def apply_migration():
    """Appliquer la migration des incidents"""
    try:
        with app.app_context():
            migration_sql = """
            -- Ajouter les nouveaux champs à la table incidents
            ALTER TABLE incidents 
            ADD COLUMN type VARCHAR(50) DEFAULT 'incident' AFTER description,
            ADD COLUMN priority VARCHAR(20) DEFAULT 'moyenne' AFTER type,
            ADD COLUMN status VARCHAR(20) DEFAULT 'ouvert' AFTER priority,
            ADD COLUMN category VARCHAR(50) NULL AFTER status,
            ADD COLUMN assigned_to INT NULL AFTER project_id,
            ADD COLUMN parent_id INT NULL AFTER assigned_to,
            ADD COLUMN resolution_notes TEXT NULL AFTER parent_id,
            ADD COLUMN is_read BOOLEAN DEFAULT FALSE AFTER resolution_notes,
            ADD COLUMN read_at DATETIME NULL AFTER is_read;
            """
            
            # Exécuter la migration
            db.session.execute(text(migration_sql))
            
            # Ajouter les contraintes de clés étrangères
            constraints_sql = """
            ALTER TABLE incidents 
            ADD CONSTRAINT fk_incidents_assigned_to 
            FOREIGN KEY (assigned_to) REFERENCES users(id);
            
            ALTER TABLE incidents 
            ADD CONSTRAINT fk_incidents_parent_id 
            FOREIGN KEY (parent_id) REFERENCES incidents(id);
            """
            
            db.session.execute(text(constraints_sql))
            
            # Ajouter les index
            indexes_sql = """
            CREATE INDEX idx_incidents_type ON incidents (type);
            CREATE INDEX idx_incidents_status ON incidents (status);
            CREATE INDEX idx_incidents_priority ON incidents (priority);
            CREATE INDEX idx_incidents_assigned_to ON incidents (assigned_to);
            CREATE INDEX idx_incidents_parent_id ON incidents (parent_id);
            CREATE INDEX idx_incidents_is_read ON incidents (is_read);
            CREATE INDEX idx_incidents_user_project ON incidents (user_id, project_id);
            """
            
            db.session.execute(text(indexes_sql))
            
            # Mettre à jour les données existantes
            update_sql = """
            UPDATE incidents 
            SET 
                type = 'incident',
                priority = 'moyenne', 
                status = 'ouvert',
                category = 'technique',
                is_read = FALSE
            WHERE type IS NULL;
            """
            
            db.session.execute(text(update_sql))
            
            db.session.commit()
            logger.info("✅ Migration appliquée avec succès")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'application de la migration: {e}")
        db.session.rollback()
        return False

def main():
    """Fonction principale"""
    print("🔍 Vérification du statut de la migration des incidents...")
    
    # Vérifier si la colonne priority existe
    if check_column_exists('incidents', 'priority'):
        print("✅ La migration a déjà été appliquée (colonne 'priority' trouvée)")
        return True
    
    print("❌ La migration n'a pas été appliquée (colonne 'priority' manquante)")
    print("🔧 Application de la migration...")
    
    if apply_migration():
        print("✅ Migration appliquée avec succès!")
        return True
    else:
        print("❌ Échec de l'application de la migration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 