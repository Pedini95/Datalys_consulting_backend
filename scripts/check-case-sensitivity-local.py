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
    
    # Vérifier que le répertoire models existe
    models_dir = Path('src/models')
    if models_dir.exists():
        print("✅ Répertoire models trouvé!")
        
        # Vérifier que __init__.py existe
        init_file = models_dir / '__init__.py'
        if init_file.exists():
            print("✅ __init__.py trouvé!")
            
            # Lire le contenu de __init__.py pour vérifier __all__
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Chercher la définition de __all__
                import re
                all_match = re.search(r'__all__\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if all_match:
                    all_content = all_match.group(1)
                    # Extraire les noms des modèles
                    model_names = re.findall(r"'([^']+)'", all_content)
                    print(f"✅ __all__ trouvé: {model_names}")
                    
                    # Vérifier que tous les modèles attendus sont dans __all__
                    expected_models = ['Role', 'User', 'Partner', 'Project', 'Incident', 'Folder', 'File', 'UserProjectPermission', 'ActionHistory']
                    for model in expected_models:
                        if model in model_names:
                            print(f"✅ {model} dans __all__")
                        else:
                            errors.append(f"❌ {model} manquant dans __all__")
                else:
                    print("⚠️ __all__ non trouvé dans __init__.py")
                    errors.append("❌ __all__ non défini dans models/__init__.py")
                    
            except Exception as e:
                errors.append(f"❌ Erreur lors de la lecture de __init__.py: {e}")
        else:
            errors.append("❌ __init__.py manquant dans models")
    else:
        errors.append("❌ Répertoire models manquant")
    
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