#!/usr/bin/env python3
"""
Script de vérification de la sensibilité à la casse des imports
Spécialement conçu pour détecter les problèmes sur Linux
"""

import os
import sys
from pathlib import Path

def check_case_sensitivity():
    """Vérifie la sensibilité à la casse des imports"""
    print("🔍 Vérification de la sensibilité à la casse...")
    
    # Répertoire des modèles
    models_dir = Path("/app/src/models")
    if not models_dir.exists():
        print(f"❌ Le répertoire {models_dir} n'existe pas")
        return False
    
    # Liste des modèles attendus avec leur casse exacte
    expected_models = {
        'Role': 'Role.py',
        'User': 'User.py', 
        'Partner': 'Partner.py',
        'Project': 'Project.py',
        'Incident': 'Incident.py',
        'Folder': 'Folder.py',
        'File': 'File.py',
        'UserProjectPermission': 'UserProjectPermission.py',
        'ActionHistory': 'ActionHistory.py'
    }
    
    errors = []
    
    # Vérifier chaque modèle
    for model_name, expected_file in expected_models.items():
        file_path = models_dir / expected_file
        
        # Vérifier si le fichier existe avec la bonne casse
        if not file_path.exists():
            # Chercher le fichier avec une casse différente
            found_files = list(models_dir.glob(f"*{model_name.lower()}*"))
            found_files.extend(list(models_dir.glob(f"*{model_name.upper()}*")))
            found_files.extend(list(models_dir.glob(f"*{model_name}*")))
            
            if found_files:
                found_file = found_files[0].name
                errors.append(f"❌ Erreur de casse: '{model_name}' attendu, trouvé '{found_file}'")
            else:
                errors.append(f"❌ Fichier manquant: {expected_file}")
        else:
            print(f"✅ {expected_file} - OK")
    
    # Vérifier les imports
    print("\n🔍 Test des imports...")
    
    # Ajouter /app/src au PYTHONPATH
    sys.path.insert(0, '/app/src')
    
    try:
        # Test d'import de tous les modèles
        from models import Role, User, Partner, Project, Incident, Folder, File, UserProjectPermission, ActionHistory
        print("✅ Tous les imports fonctionnent correctement!")
        
        # Vérifier que les classes sont bien importées
        models = [Role, User, Partner, Project, Incident, Folder, File, UserProjectPermission, ActionHistory]
        for model in models:
            print(f"✅ {model.__name__} importé avec succès")
            
    except ImportError as e:
        errors.append(f"❌ Erreur d'import: {e}")
        print(f"❌ Erreur d'import détectée: {e}")
        
        # Debug supplémentaire
        print("\n🔍 Debug des imports...")
        try:
            import models
            print(f"✅ Package 'models' trouvé: {models}")
            print(f"📁 Contenu du package: {dir(models)}")
        except Exception as e2:
            print(f"❌ Impossible d'importer le package 'models': {e2}")
    
    # Afficher les erreurs
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) trouvée(s):")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n🎉 Aucune erreur de casse détectée!")
        return True

def main():
    """Fonction principale"""
    print("🐧 Vérification de la sensibilité à la casse sur Linux")
    print("=" * 50)
    
    # Vérifier l'environnement
    print(f"🔍 Système d'exploitation: {os.name}")
    print(f"🔍 Répertoire de travail: {os.getcwd()}")
    print(f"🔍 PYTHONPATH: {os.environ.get('PYTHONPATH', 'Non défini')}")
    
    # Vérifier la structure des fichiers
    success = check_case_sensitivity()
    
    if success:
        print("\n✅ Vérification terminée avec succès!")
        sys.exit(0)
    else:
        print("\n❌ Des erreurs ont été détectées!")
        sys.exit(1)

if __name__ == "__main__":
    main() 