#!/usr/bin/env python3
"""
Script de vérification de la sensibilité à la casse des imports (version locale)
Pour tester avant le déploiement
"""

import os
import sys
from pathlib import Path

def check_case_sensitivity():
    """Vérifie la sensibilité à la casse des imports"""
    print("🔍 Vérification de la sensibilité à la casse (locale)...")
    
    # Répertoire des modèles
    models_dir = Path("src/models")
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
    
    # Vérifier la structure du package
    print("\n🔍 Test de la structure du package...")
    
    # Ajouter src au PYTHONPATH
    sys.path.insert(0, 'src')
    
    try:
        # Test d'import du package models seulement
        import models
        print("✅ Package 'models' trouvé!")
        print(f"📁 Contenu du package: {dir(models)}")
        
        # Vérifier que les modules sont listés dans __all__
        if hasattr(models, '__all__'):
            print(f"✅ __all__ défini: {models.__all__}")
            
            # Vérifier que tous les modèles attendus sont dans __all__
            expected_models = ['Role', 'User', 'Partner', 'Project', 'Incident', 'Folder', 'File', 'UserProjectPermission', 'ActionHistory']
            for model in expected_models:
                if model in models.__all__:
                    print(f"✅ {model} dans __all__")
                else:
                    errors.append(f"❌ {model} manquant dans __all__")
        else:
            print("⚠️ __all__ non défini dans models")
            
    except ImportError as e:
        errors.append(f"❌ Erreur d'import du package models: {e}")
        print(f"❌ Erreur d'import détectée: {e}")
        
        # Debug supplémentaire
        print("\n🔍 Debug des imports...")
        print(f"🔍 PYTHONPATH: {sys.path}")
        print(f"🔍 Répertoire models existe: {Path('src/models').exists()}")
        print(f"🔍 __init__.py existe: {Path('src/models/__init__.py').exists()}")
    
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
    print("🐧 Vérification de la sensibilité à la casse (locale)")
    print("=" * 50)
    
    # Vérifier l'environnement
    print(f"🔍 Système d'exploitation: {os.name}")
    print(f"🔍 Répertoire de travail: {os.getcwd()}")
    print(f"🔍 PYTHONPATH: {os.environ.get('PYTHONPATH', 'Non défini')}")
    
    # Vérifier la structure des fichiers
    success = check_case_sensitivity()
    
    if success:
        print("\n✅ Vérification terminée avec succès!")
        print("💡 Les imports devraient fonctionner sur Linux aussi!")
        sys.exit(0)
    else:
        print("\n❌ Des erreurs ont été détectées!")
        print("🚨 Corrigez ces erreurs avant le déploiement!")
        sys.exit(1)

if __name__ == "__main__":
    main() 