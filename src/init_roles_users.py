#!/usr/bin/env python3
"""
Script pour initialiser les rôles et créer un utilisateur administrateur
"""

import sys
from utils import utilities

from app import app
from extensions import db
from models.role import Role
from models.user import User


def init_roles():
    """Créer les rôles de base"""
    print("🔧 Création des rôles...")
    
    roles_data = ['Admin', 'Manager', 'User']
    
    created_roles = {}
    for role_name in roles_data:
        existing = Role.query.filter_by(name=role_name, is_deleted=False).first()
        if not existing:
            role = Role(
                name=role_name,
                is_active=True,
                is_deleted=False
            )
            db.session.add(role)
            db.session.flush()  # Pour obtenir l'ID
            created_roles[role_name] = role
            print(f"  ✅ Rôle créé: {role_name} (ID: {role.id})")
        else:
            created_roles[role_name] = existing
            print(f"  ℹ️  Rôle existe déjà: {role_name} (ID: {existing.id})")
    
    db.session.commit()
    return created_roles


def create_admin_user(admin_role):
    """Créer un utilisateur administrateur par défaut"""
    print("🔧 Création de l'utilisateur administrateur...")
    
    admin_email = "admin@datalys.com"
    admin_password = "Admin@123"
    
    # Vérifier si l'admin existe déjà
    existing_admin = User.query.filter_by(email=admin_email, is_deleted=False).first()
    if existing_admin:
        print(f"  ℹ️  Administrateur existe déjà: {admin_email}")
        return existing_admin
    
    # Créer l'administrateur
    admin = User(
        name="Administrateur",
        email=admin_email,
        password_hash=utilities.encrypt(admin_password),
        role_id=admin_role.id,
        is_active=True,
        is_deleted=False,
        is_temp_password=True  # Forcer le changement de mot de passe
    )
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"  ✅ Administrateur créé: {admin_email}")
    print(f"  🔑 Mot de passe: {admin_password}")
    print(f"  ⚠️  IMPORTANT: Changez ce mot de passe lors de la première connexion!")
    
    return admin


def create_test_users(roles):
    """Créer quelques utilisateurs de test"""
    print("🔧 Création des utilisateurs de test...")
    
    test_users = [
        {
            'name': 'Jean Dupont',
            'email': 'jean.dupont@datalys.com',
            'password': 'Test@123',
            'role': 'Manager'
        },
        {
            'name': 'Marie Martin',
            'email': 'marie.martin@datalys.com',
            'password': 'Test@123',
            'role': 'User'
        }
    ]
    
    for user_data in test_users:
        existing = User.query.filter_by(email=user_data['email'], is_deleted=False).first()
        if not existing:
            role = roles.get(user_data['role'])
            if role:
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=utilities.encrypt(user_data['password']),
                    role_id=role.id,
                    is_active=True,
                    is_deleted=False,
                    is_temp_password=True
                )
                db.session.add(user)
                print(f"  ✅ Utilisateur créé: {user_data['email']} ({user_data['role']})")
        else:
            print(f"  ℹ️  Utilisateur existe déjà: {user_data['email']}")
    
    db.session.commit()


def main():
    """Fonction principale"""
    try:
        print("🚀 Démarrage de l'initialisation des rôles et utilisateurs...")
        
        with app.app_context():
            # Créer les rôles
            roles = init_roles()
            
            # Créer l'utilisateur admin
            admin_role = roles.get('Admin')
            if admin_role:
                create_admin_user(admin_role)
            else:
                print("❌ Impossible de créer l'admin: rôle Admin introuvable")
                return False
            
            # Créer quelques utilisateurs de test
            create_test_users(roles)
            
            # Afficher le résumé
            print("\n" + "="*60)
            print("🎉 Initialisation terminée avec succès!")
            print("="*60)
            print("\n📊 Résumé:")
            
            total_roles = Role.query.filter_by(is_deleted=False).count()
            total_users = User.query.filter_by(is_deleted=False).count()
            
            print(f"  - Rôles: {total_roles}")
            print(f"  - Utilisateurs: {total_users}")
            
            print("\n🔑 Identifiants de connexion:")
            print("  Admin: admin@datalys.com / Admin@123")
            print("  Manager: jean.dupont@datalys.com / Test@123")
            print("  User: marie.martin@datalys.com / Test@123")
            print("\n⚠️  N'oubliez pas de changer ces mots de passe!")
            print("="*60 + "\n")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

