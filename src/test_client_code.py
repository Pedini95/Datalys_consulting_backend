#!/usr/bin/env python3
"""
Script de test pour la fonctionnalité Code Client Unique

Ce script teste :
1. La génération automatique du code client lors de la création d'utilisateur
2. La connexion avec email
3. La connexion avec code client
4. L'unicité du code client

Usage:
    python src/test_client_code.py
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app
from extensions import db
from models.user import User
from models.role import Role
from services.user_service import UserService
from services.auth_service import AuthService
from utils import utilities

def test_client_code_generation():
    """Test 1 : Génération automatique du code client"""
    print("\n" + "="*80)
    print("TEST 1 : Génération automatique du code client")
    print("="*80)
    
    with app.app_context():
        # Générer un code client
        code1 = User.generate_client_code()
        print(f"✅ Code client généré : {code1}")
        
        # Vérifier le format
        assert code1.startswith("DATALYS-"), "Le code doit commencer par 'DATALYS-'"
        assert len(code1.split('-')) == 3, "Le code doit avoir 3 parties séparées par '-'"
        
        year = code1.split('-')[1]
        number = code1.split('-')[2]
        
        assert year.isdigit() and len(year) == 4, "L'année doit être sur 4 chiffres"
        assert number.isdigit() and len(number) == 3, "Le numéro doit être sur 3 chiffres"
        
        print(f"✅ Format validé : DATALYS-{year}-{number}")
        print("✅ TEST 1 RÉUSSI\n")


def test_user_creation_with_client_code():
    """Test 2 : Création d'utilisateur avec génération automatique du code"""
    print("\n" + "="*80)
    print("TEST 2 : Création d'utilisateur avec code client automatique")
    print("="*80)
    
    with app.app_context():
        user_service = UserService()
        
        # Créer un utilisateur de test
        test_email = f"test_client_code_{utilities.generate_numeric_code(6)}@datalys.com"
        
        # Récupérer le rôle User
        roles, _ = Role.get_by_criteria({'name': 'User'}, 0, 1)
        if not roles:
            print("❌ Rôle 'User' non trouvé. Créez d'abord les rôles.")
            return False
        
        user_data = {
            'name': 'Test Client Code',
            'email': test_email,
            'password': 'Test@123',
            'role_id': roles[0].id,
            'is_active': True,
            'is_deleted': False
        }
        
        user, success, message = user_service.create(user_data)
        
        if success:
            print(f"✅ Utilisateur créé : {user.email}")
            print(f"✅ Code client généré : {user.client_code}")
            
            # Vérifier que le code client existe
            assert user.client_code is not None, "Le code client doit être généré"
            assert user.client_code.startswith("DATALYS-"), "Le code doit commencer par 'DATALYS-'"
            
            print("✅ TEST 2 RÉUSSI\n")
            return user
        else:
            print(f"❌ Échec de création : {message}")
            return None


def test_login_with_email(user):
    """Test 3 : Connexion avec email"""
    print("\n" + "="*80)
    print("TEST 3 : Connexion avec email")
    print("="*80)
    
    with app.app_context():
        auth_service = AuthService()
        
        # Désactiver temporairement le MFA pour ce test
        user.mfa_enabled = False
        db.session.commit()
        
        # Tenter de se connecter avec l'email
        user_data, success, message = auth_service.login(user.email, 'Test@123')
        
        if success:
            print(f"✅ Connexion réussie avec email : {user.email}")
            print(f"✅ Token JWT généré : {user_data.get('token', '')[:50]}...")
            print("✅ TEST 3 RÉUSSI\n")
            return True
        else:
            print(f"❌ Échec de connexion : {message}")
            return False


def test_login_with_client_code(user):
    """Test 4 : Connexion avec code client"""
    print("\n" + "="*80)
    print("TEST 4 : Connexion avec code client")
    print("="*80)
    
    with app.app_context():
        auth_service = AuthService()
        
        # Tenter de se connecter avec le code client
        user_data, success, message = auth_service.login(user.client_code, 'Test@123')
        
        if success:
            print(f"✅ Connexion réussie avec code client : {user.client_code}")
            print(f"✅ Token JWT généré : {user_data.get('token', '')[:50]}...")
            print(f"✅ Email récupéré : {user_data.get('email')}")
            print("✅ TEST 4 RÉUSSI\n")
            return True
        else:
            print(f"❌ Échec de connexion : {message}")
            return False


def test_client_code_uniqueness():
    """Test 5 : Unicité du code client"""
    print("\n" + "="*80)
    print("TEST 5 : Unicité du code client")
    print("="*80)
    
    with app.app_context():
        # Générer plusieurs codes
        codes = set()
        for i in range(5):
            code = User.generate_client_code()
            codes.add(code)
            print(f"  Code {i+1} : {code}")
        
        # Vérifier qu'ils sont tous différents
        if len(codes) == 5:
            print("✅ Tous les codes sont uniques")
            print("✅ TEST 5 RÉUSSI\n")
            return True
        else:
            print(f"❌ Collision détectée : {5 - len(codes)} doublons")
            return False


def cleanup_test_users():
    """Nettoyer les utilisateurs de test"""
    print("\n" + "="*80)
    print("NETTOYAGE : Suppression des utilisateurs de test")
    print("="*80)
    
    with app.app_context():
        # Supprimer les utilisateurs de test (soft delete)
        test_users = User.query.filter(
            User.email.like('%test_client_code_%@datalys.com')
        ).all()
        
        for user in test_users:
            user.is_deleted = True
            print(f"  Supprimé : {user.email} ({user.client_code})")
        
        db.session.commit()
        print(f"✅ {len(test_users)} utilisateur(s) de test supprimé(s)\n")


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*80)
    print("🧪 TESTS DE LA FONCTIONNALITÉ CODE CLIENT UNIQUE")
    print("="*80)
    
    try:
        # Test 1 : Génération du code
        test_client_code_generation()
        
        # Test 2 : Création d'utilisateur
        user = test_user_creation_with_client_code()
        if not user:
            print("❌ Impossible de continuer les tests sans utilisateur")
            return
        
        # Test 3 : Connexion avec email
        test_login_with_email(user)
        
        # Test 4 : Connexion avec code client
        test_login_with_client_code(user)
        
        # Test 5 : Unicité
        test_client_code_uniqueness()
        
        # Nettoyage
        cleanup_test_users()
        
        print("\n" + "="*80)
        print("✅ TOUS LES TESTS SONT RÉUSSIS !")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS : {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

