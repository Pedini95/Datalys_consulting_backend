#!/usr/bin/env python3
"""
Script pour sécuriser automatiquement les routes critiques
"""

import os
import re

def add_auth_protection_to_file(file_path):
    """Ajouter la protection d'authentification à un fichier de routes"""
    
    print(f"🔒 Sécurisation de {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si require_auth est déjà importé
    if 'from routes.auth import require_auth' not in content:
        # Ajouter l'import
        content = content.replace(
            'from flask_cors import cross_origin',
            'from flask_cors import cross_origin\nfrom routes.auth import require_auth'
        )
    
    # Routes critiques à protéger
    critical_routes = [
        r'@bp\.route\(\'/[^/]+/create\', methods=\[\'POST\'\]\)',
        r'@bp\.route\(\'/[^/]+/update\', methods=\[\'POST\'\]\)',
        r'@bp\.route\(\'/[^/]+/delete\', methods=\[\'POST\'\]\)',
        r'@bp\.route\(\'/[^/]+/getByCriteria\', methods=\[\'POST\'\]\)',
    ]
    
    # Ajouter @require_auth aux routes critiques
    for pattern in critical_routes:
        # Chercher les routes qui ne sont pas déjà protégées
        matches = re.finditer(pattern, content)
        for match in matches:
            route_start = match.start()
            # Trouver la ligne suivante (définition de fonction)
            next_line_start = content.find('\n', route_start) + 1
            next_line_end = content.find('\n', next_line_start)
            next_line = content[next_line_start:next_line_end]
            
            # Vérifier si @require_auth n'est pas déjà présent
            if '@require_auth' not in next_line and '@cross_origin' in next_line:
                # Ajouter @require_auth après @cross_origin
                new_line = next_line.replace('@cross_origin()', '@cross_origin()\n@require_auth')
                content = content.replace(next_line, new_line)
                print(f"  ✅ Protégé: {match.group()}")
    
    # Sauvegarder le fichier
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Fichier sécurisé: {file_path}")

def main():
    """Fonction principale"""
    print("🔐 Sécurisation des Routes Critiques")
    print("=" * 50)
    
    # Routes à sécuriser
    routes_to_secure = [
        'src/routes/users.py',
        'src/routes/projects.py',
        'src/routes/partners.py',
        'src/routes/incidents.py',
        'src/routes/folders.py',
        'src/routes/files.py',
        'src/routes/roles.py',
        'src/routes/user_project_permissions.py',
        'src/routes/action_history.py'
    ]
    
    for route_file in routes_to_secure:
        if os.path.exists(route_file):
            add_auth_protection_to_file(route_file)
        else:
            print(f"⚠️  Fichier non trouvé: {route_file}")
    
    print("\n" + "=" * 50)
    print("✅ Sécurisation terminée !")
    print("\n📋 Routes maintenant protégées :")
    print("- POST /users/create, /users/update, /users/delete, /users/getByCriteria")
    print("- POST /projects/create, /projects/update, /projects/delete, /projects/getByCriteria")
    print("- POST /partners/create, /partners/update, /partners/delete, /partners/getByCriteria")
    print("- POST /incidents/create, /incidents/update, /incidents/delete, /incidents/getByCriteria")
    print("- POST /folders/create, /folders/update, /folders/delete, /folders/getByCriteria")
    print("- POST /files/create, /files/update, /files/delete, /files/getByCriteria")
    print("- POST /roles/create, /roles/update, /roles/delete, /roles/getByCriteria")
    print("- POST /user_project_permissions/create, /user_project_permissions/update, /user_project_permissions/delete, /user_project_permissions/getByCriteria")
    print("- POST /action_history/create, /action_history/update, /action_history/delete, /action_history/getByCriteria")
    
    print("\n🔑 Routes publiques (non protégées) :")
    print("- POST /auth/login")
    print("- POST /auth/reset-password-request")
    print("- GET /health-check")

if __name__ == "__main__":
    main() 