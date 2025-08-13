#!/usr/bin/env python3
"""
Script de test pour vérifier le modèle Folder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.Folder import Folder

def test_folder_model():
    """Test du modèle Folder"""
    print("🔍 Test du modèle Folder...")
    
    with app.app_context():
        try:
            # Test 1: Vérifier que la classe existe
            print("✅ Classe Folder importée avec succès")
            
            # Test 2: Vérifier les attributs
            folder = Folder()
            print(f"✅ Attributs du modèle:")
            print(f"   - id: {hasattr(folder, 'id')}")
            print(f"   - name: {hasattr(folder, 'name')}")
            print(f"   - project_id: {hasattr(folder, 'project_id')}")
            print(f"   - parent_folder_id: {hasattr(folder, 'parent_folder_id')}")
            print(f"   - path: {hasattr(folder, 'path')}")
            print(f"   - is_active: {hasattr(folder, 'is_active')}")
            print(f"   - is_deleted: {hasattr(folder, 'is_deleted')}")
            print(f"   - created_at: {hasattr(folder, 'created_at')}")
            print(f"   - created_by: {hasattr(folder, 'created_by')}")
            print(f"   - updated_at: {hasattr(folder, 'updated_at')}")
            print(f"   - updated_by: {hasattr(folder, 'updated_by')}")
            
            # Test 3: Vérifier la méthode as_dict
            folder.name = "Test Folder"
            folder.path = "/test/path"
            folder.is_active = True
            
            folder_dict = folder.as_dict()
            print(f"✅ Méthode as_dict:")
            print(f"   - Résultat: {folder_dict}")
            print(f"   - Contient 'path': {'path' in folder_dict}")
            print(f"   - Valeur de 'path': {folder_dict.get('path')}")
            
            # Test 4: Vérifier la méthode get_by_criteria
            folders, count = Folder.get_by_criteria({}, 0, 5)
            print(f"✅ Méthode get_by_criteria:")
            print(f"   - Nombre de dossiers trouvés: {count}")
            print(f"   - Type de retour: {type(folders)}")
            
            if folders:
                first_folder = folders[0]
                print(f"   - Premier dossier: {first_folder.name}")
                print(f"   - A un attribut 'path': {hasattr(first_folder, 'path')}")
                if hasattr(first_folder, 'path'):
                    print(f"   - Valeur de 'path': {first_folder.path}")
            
            print("🎉 Tous les tests du modèle Folder sont passés !")
            
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_folder_model() 