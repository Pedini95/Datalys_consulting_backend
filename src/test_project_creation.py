#!/usr/bin/env python3
"""
Script de test pour la création de projets avec nom de partenaire
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8081"
LOGIN_URL = f"{BASE_URL}/auth/login"
PROJECTS_URL = f"{BASE_URL}/projects/create"

def test_login():
    """Test de connexion pour obtenir un token"""
    print("🔐 Test de connexion...")
    
    login_data = {
        "email": "yablaiyablairubenvirgil@gmail.com",
        "password": "password123"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('data', {}).get('token')
        print(f"✅ Connexion réussie, token obtenu: {token[:20]}...")
        return token
    else:
        print(f"❌ Échec de connexion: {response.status_code}")
        print(response.text)
        return None

def test_create_project_with_partner_name(token):
    """Test création projet avec nom de partenaire"""
    print("\n🏢 Test création projet avec nom de partenaire...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "user": {"id": 1},
        "datas": [{
            "title": "E-commerce Platform",
            "partner_name": "TechCorp Logo"  # Utiliser le nom au lieu de l'ID
        }]
    }
    
    response = requests.post(PROJECTS_URL, json=project_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Projet créé avec succès (nom de partenaire)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Titre: {data.get('items', [{}])[0].get('title')}")
        print(f"   Partner ID: {data.get('items', [{}])[0].get('partner_id')}")
        print(f"   Actif: {data.get('items', [{}])[0].get('is_active')}")
    else:
        print("❌ Échec création projet (nom de partenaire)")
        print(response.text)

def test_create_project_with_partner_id(token):
    """Test création projet avec ID de partenaire"""
    print("\n🏢 Test création projet avec ID de partenaire...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "user": {"id": 1},
        "datas": [{
            "title": "Mobile App Development",
            "partner_id": 3  # Utiliser l'ID directement
        }]
    }
    
    response = requests.post(PROJECTS_URL, json=project_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Projet créé avec succès (ID de partenaire)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Titre: {data.get('items', [{}])[0].get('title')}")
        print(f"   Partner ID: {data.get('items', [{}])[0].get('partner_id')}")
        print(f"   Actif: {data.get('items', [{}])[0].get('is_active')}")
    else:
        print("❌ Échec création projet (ID de partenaire)")
        print(response.text)

def test_create_project_without_partner(token):
    """Test création projet sans partenaire"""
    print("\n🏢 Test création projet sans partenaire...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "user": {"id": 1},
        "datas": [{
            "title": "Internal Project"
            # Pas de partner_name ni partner_id
        }]
    }
    
    response = requests.post(PROJECTS_URL, json=project_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Projet créé avec succès (sans partenaire)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Titre: {data.get('items', [{}])[0].get('title')}")
        print(f"   Partner ID: {data.get('items', [{}])[0].get('partner_id')}")
        print(f"   Actif: {data.get('items', [{}])[0].get('is_active')}")
    else:
        print("❌ Échec création projet (sans partenaire)")
        print(response.text)

def test_create_project_invalid_partner(token):
    """Test création projet avec partenaire invalide"""
    print("\n🏢 Test création projet avec partenaire invalide...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "user": {"id": 1},
        "datas": [{
            "title": "Invalid Partner Project",
            "partner_name": "Partenaire Inexistant"  # Nom qui n'existe pas
        }]
    }
    
    response = requests.post(PROJECTS_URL, json=project_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Erreur attendue (partenaire invalide)")
        print(response.text)
    else:
        print("❌ Erreur inattendue")
        print(response.text)

def main():
    """Fonction principale"""
    print("🧪 Test de Création de Projets avec Nom de Partenaire")
    print("=" * 60)
    
    # Test de connexion
    token = test_login()
    if not token:
        print("❌ Impossible de continuer sans token")
        return
    
    # Tests de création
    test_create_project_with_partner_name(token)
    test_create_project_with_partner_id(token)
    test_create_project_without_partner(token)
    test_create_project_invalid_partner(token)
    
    print("\n" + "=" * 60)
    print("🏁 Tests terminés")

if __name__ == "__main__":
    main() 