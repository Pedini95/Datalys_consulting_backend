#!/usr/bin/env python3
"""
Script simple pour ajouter la colonne path à la table folders
"""

import pymysql

def add_path_column():
    """Ajouter la colonne path à la table folders"""
    
    try:
        # Connexion à la base de données
        connection = pymysql.connect(
            host='82.112.253.137',
            user='datalys',
            password='datalysconsulting',
            database='datalys_consulting',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Ajouter la colonne path
            cursor.execute("""
                ALTER TABLE folders 
                ADD COLUMN path VARCHAR(500) NULL 
                COMMENT 'Chemin physique du répertoire'
            """)
            
            connection.commit()
            print("✅ Colonne 'path' ajoutée avec succès à la table 'folders'")
        
        connection.close()
        
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("✅ La colonne 'path' existe déjà")
        else:
            print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    print("🔄 Ajout de la colonne 'path' à la table folders")
    add_path_column() 