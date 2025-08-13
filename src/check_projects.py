#!/usr/bin/env python3
"""
Script pour vérifier les projets existants en base de données
"""

import pymysql

def check_projects():
    """Vérifier les projets existants"""
    
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
            # Récupérer tous les projets
            cursor.execute("""
                SELECT id, title, is_active, created_at 
                FROM projects 
                WHERE is_deleted = 0 
                ORDER BY id
            """)
            
            projects = cursor.fetchall()
            
            print("📋 Projets existants en base de données:")
            print("=" * 50)
            
            if projects:
                for project in projects:
                    print(f"   ID: {project[0]}")
                    print(f"   Titre: {project[1]}")
                    print(f"   Actif: {project[2]}")
                    print(f"   Créé le: {project[3]}")
                    print("-" * 30)
            else:
                print("   ❌ Aucun projet trouvé")
            
            # Vérifier les dossiers existants
            cursor.execute("""
                SELECT id, name, project_id, parent_folder_id, is_active 
                FROM folders 
                WHERE is_deleted = 0 
                ORDER BY id
            """)
            
            folders = cursor.fetchall()
            
            print("\n📁 Dossiers existants en base de données:")
            print("=" * 50)
            
            if folders:
                for folder in folders:
                    print(f"   ID: {folder[0]}")
                    print(f"   Nom: {folder[1]}")
                    print(f"   Project ID: {folder[2]}")
                    print(f"   Parent Folder ID: {folder[3]}")
                    print(f"   Actif: {folder[4]}")
                    print("-" * 30)
            else:
                print("   ❌ Aucun dossier trouvé")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    print("🔍 Vérification des projets et dossiers existants")
    check_projects() 