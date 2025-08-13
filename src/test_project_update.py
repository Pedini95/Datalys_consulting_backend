#!/usr/bin/env python3
"""
Script de test pour la mise à jour de projets
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8081"
LOGIN_URL = f"{BASE_URL}/auth/login"
PROJECTS_UPDATE_URL = f"{BASE_URL}/projects/update"

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

def test_update_project_with_existing_fields(token):
    """Test mise à jour projet avec champs existants"""
    print("\n🏢 Test mise à jour projet (champs existants)...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "user": {"id": 1},
        "datas": [{
            "id": 1,
            "title": "E-commerce Platform v2",  # Utiliser 'title' au lieu de 'name'
            "is_active": True
        }]
    }
    
    response = requests.post(PROJECTS_UPDATE_URL, json=project_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Projet mis à jour avec succès")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Titre: {data.get('items', [{}])[0].get('title')}")
        print(f"   Actif: {data.get('items', [{}])[0].get('is_active')}")
    else:
        print("❌ Échec mise à jour projet")
        print(response.text)

def test_update_project_with_partner_name(token):
    """Test mise à jour projet avec nom de partenaire"""
    print("\n🏢 Test mise à jour projet avec nom de partenaire...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_data = {
        "user": {"id": 1},
        "datas": [{
            "id": 1,
            "title": "E-commerce Platform v3",
            "partner_name": "TechCorp Logo"  # Utiliser le nom au lieu de l'ID
        }]
    }
    
    response = requests.post(PROJECTS_UPDATE_URL, json=project_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Projet mis à jour avec succès (nom de partenaire)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Titre: {data.get('items', [{}])[0].get('title')}")
        print(f"   Partner ID: {data.get('items', [{}])[0].get('partner_id')}")
    else:
        print("❌ Échec mise à jour projet (nom de partenaire)")
        print(response.text)

def main():
    """Fonction principale"""
    print("🧪 Test de Mise à Jour de Projets")
    print("=" * 50)
    
    # Test de connexion
    token = test_login()
    if not token:
        print("❌ Impossible de continuer sans token")
        return
    
    # Tests de mise à jour
    test_update_project_with_existing_fields(token)
    test_update_project_with_partner_name(token)
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")

if __name__ == "__main__":
    main() 