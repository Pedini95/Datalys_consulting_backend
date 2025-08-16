#!/usr/bin/env python3
"""
Script de vérification automatique des imports Python
Détecte les erreurs de casse et les imports manquants avant le build
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set

class ImportChecker:
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.errors = []
        self.warnings = []
        
    def check_file_imports(self, file_path: Path) -> List[str]:
        """Vérifie les imports d'un fichier Python"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Impossible de lire {file_path}: {e}")
            return errors
            
        # Patterns pour détecter les imports
        import_patterns = [
            r'from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+(?:\s*,\s*\w+)*)',
            r'import\s+(\w+(?:\.\w+)*)',
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if 'from' in pattern:
                    module_path = match.group(1)
                    imports = [imp.strip() for imp in match.group(2).split(',')]
                else:
                    module_path = match.group(1)
                    imports = []
                
                # Vérifier les imports relatifs au projet
                if module_path.startswith('models.') or module_path == 'models':
                    errors.extend(self._check_models_import(module_path, imports, file_path))
                elif module_path.startswith('routes.') or module_path == 'routes':
                    errors.extend(self._check_routes_import(module_path, imports, file_path))
                elif module_path.startswith('services.') or module_path == 'services':
                    errors.extend(self._check_services_import(module_path, imports, file_path))
                    
        return errors
    
    def _check_models_import(self, module_path: str, imports: List[str], file_path: Path) -> List[str]:
        """Vérifie les imports des modèles"""
        errors = []
        
        if module_path == 'models':
            # Import de tous les modèles
            models_dir = self.src_dir / 'models'
            if not models_dir.exists():
                errors.append(f"Le répertoire models n'existe pas dans {self.src_dir}")
                return errors
                
            # Vérifier que __init__.py existe
            init_file = models_dir / '__init__.py'
            if not init_file.exists():
                errors.append(f"Le fichier __init__.py manque dans {models_dir}")
                
        elif module_path.startswith('models.'):
            # Import d'un modèle spécifique
            model_name = module_path.split('.')[-1]
            model_file = self.src_dir / 'models' / f'{model_name}.py'
            
            if not model_file.exists():
                errors.append(f"Le fichier {model_file} n'existe pas pour l'import '{module_path}'")
            else:
                # Vérifier la casse du nom de fichier
                actual_name = model_file.stem
                if actual_name != model_name:
                    errors.append(f"Erreur de casse: l'import '{module_path}' fait référence à '{model_name}' mais le fichier s'appelle '{actual_name}.py'")
                    
        return errors
    
    def _check_routes_import(self, module_path: str, imports: List[str], file_path: Path) -> List[str]:
        """Vérifie les imports des routes"""
        errors = []
        
        if module_path == 'routes':
            routes_dir = self.src_dir / 'routes'
            if not routes_dir.exists():
                errors.append(f"Le répertoire routes n'existe pas dans {self.src_dir}")
                return errors
                
            init_file = routes_dir / '__init__.py'
            if not init_file.exists():
                errors.append(f"Le fichier __init__.py manque dans {routes_dir}")
                
        elif module_path.startswith('routes.'):
            route_name = module_path.split('.')[-1]
            route_file = self.src_dir / 'routes' / f'{route_name}.py'
            
            if not route_file.exists():
                errors.append(f"Le fichier {route_file} n'existe pas pour l'import '{module_path}'")
                
        return errors
    
    def _check_services_import(self, module_path: str, imports: List[str], file_path: Path) -> List[str]:
        """Vérifie les imports des services"""
        errors = []
        
        if module_path == 'services':
            services_dir = self.src_dir / 'services'
            if not services_dir.exists():
                errors.append(f"Le répertoire services n'existe pas dans {self.src_dir}")
                return errors
                
            init_file = services_dir / '__init__.py'
            if not init_file.exists():
                errors.append(f"Le fichier __init__.py manque dans {services_dir}")
                
        elif module_path.startswith('services.'):
            service_name = module_path.split('.')[-1]
            service_file = self.src_dir / 'services' / f'{service_name}.py'
            
            if not service_file.exists():
                errors.append(f"Le fichier {service_file} n'existe pas pour l'import '{module_path}'")
                
        return errors
    
    def check_all_files(self) -> Tuple[List[str], List[str]]:
        """Vérifie tous les fichiers Python du projet"""
        python_files = list(self.src_dir.rglob('*.py'))
        
        for file_path in python_files:
            if file_path.name == '__init__.py':
                continue  # Ignorer les __init__.py pour l'instant
                
            file_errors = self.check_file_imports(file_path)
            for error in file_errors:
                self.errors.append(f"{file_path}: {error}")
                
        return self.errors, self.warnings
    
    def check_dockerfile(self) -> List[str]:
        """Vérifie la configuration du Dockerfile"""
        dockerfile_path = self.src_dir / 'Dockerfile'
        errors = []
        
        if not dockerfile_path.exists():
            errors.append("Le fichier Dockerfile n'existe pas dans src/")
            return errors
            
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifier le WORKDIR
            if 'WORKDIR /app' not in content:
                errors.append("Le WORKDIR dans Dockerfile doit être '/app'")
                
            # Vérifier le PYTHONPATH
            if 'PYTHONPATH="${PYTHONPATH}:/app/src"' not in content:
                errors.append("Le PYTHONPATH dans Dockerfile doit être 'PYTHONPATH=\"${PYTHONPATH}:/app/src\"'")
                
        except Exception as e:
            errors.append(f"Impossible de lire le Dockerfile: {e}")
            
        return errors

def main():
    print("🔍 Vérification des imports Python...")
    
    checker = ImportChecker()
    
    # Vérifier les imports
    errors, warnings = checker.check_all_files()
    
    # Vérifier le Dockerfile
    dockerfile_errors = checker.check_dockerfile()
    errors.extend(dockerfile_errors)
    
    # Afficher les résultats
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) trouvée(s):")
        for error in errors:
            print(f"  • {error}")
        print("\n🚨 Corrections nécessaires avant le build!")
        sys.exit(1)
    else:
        print("✅ Aucune erreur d'import détectée!")
        
    if warnings:
        print(f"\n⚠️ {len(warnings)} avertissement(s):")
        for warning in warnings:
            print(f"  • {warning}")
            
    print("\n🎉 Vérification terminée avec succès!")

if __name__ == "__main__":
    main() 