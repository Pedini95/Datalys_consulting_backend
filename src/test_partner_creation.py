#!/usr/bin/env python3
"""
Script de test pour la création de partenaires avec upload de logo intégré
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8081"
LOGIN_URL = f"{BASE_URL}/auth/login"
PARTNERS_URL = f"{BASE_URL}/partners/create"

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

def test_create_partner_json(token):
    """Test création partenaire en mode JSON (sans logo)"""
    print("\n📝 Test création partenaire en mode JSON...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    partner_data = {
        "user": {"id": 1},
        "datas": [{
            "name": "TechCorp JSON",
            "email": "contact@techcorp-json.com",
            "phone": "+1234567890",
            "address": "123 Tech Street, JSON City",
            "is_active": True
        }]
    }
    
    response = requests.post(PARTNERS_URL, json=partner_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Partenaire créé avec succès (JSON)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Nom: {data.get('items', [{}])[0].get('name')}")
    else:
        print("❌ Échec création partenaire (JSON)")
        print(response.text)

def test_create_partner_with_logo(token):
    """Test création partenaire avec logo intégré"""
    print("\n🖼️ Test création partenaire avec logo...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Données du partenaire
    partner_data = {
        "name": "TechCorp Logo",
        "email": "contact@techcorp-logo.com",
        "phone": "+1234567890",
        "address": "123 Tech Street, Logo City",
        "is_active": True
    }
    
    user_data = {"id": 1}
    
    # Préparer les données multipart
    files = {}
    data = {
        "data": json.dumps(partner_data),
        "user": json.dumps(user_data)
    }
    
    # Ajouter un fichier logo de test (si disponible)
    test_logo_path = "test_logo.png"
    if os.path.exists(test_logo_path):
        files["logo"] = open(test_logo_path, "rb")
        print(f"   Logo trouvé: {test_logo_path}")
    else:
        print(f"   ⚠️ Logo de test non trouvé: {test_logo_path}")
        print("   Création sans logo...")
    
    response = requests.post(PARTNERS_URL, data=data, files=files, headers=headers)
    
    # Fermer le fichier si ouvert
    if "logo" in files:
        files["logo"].close()
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Partenaire créé avec succès (avec logo)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Nom: {data.get('items', [{}])[0].get('name')}")
        print(f"   Logo URL: {data.get('items', [{}])[0].get('logo_url')}")
    else:
        print("❌ Échec création partenaire (avec logo)")
        print(response.text)

def test_create_partner_with_logo_url(token):
    """Test création partenaire avec URL de logo"""
    print("\n🔗 Test création partenaire avec URL de logo...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    partner_data = {
        "user": {"id": 1},
        "datas": [{
            "name": "TechCorp URL",
            "email": "contact@techcorp-url.com",
            "phone": "+1234567890",
            "address": "123 Tech Street, URL City",
            "logo_url": "https://example.com/logo.png",
            "is_active": True
        }]
    }
    
    response = requests.post(PARTNERS_URL, json=partner_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Partenaire créé avec succès (URL logo)")
        print(f"   ID: {data.get('items', [{}])[0].get('id')}")
        print(f"   Nom: {data.get('items', [{}])[0].get('name')}")
        print(f"   Logo URL: {data.get('items', [{}])[0].get('logo_url')}")
    else:
        print("❌ Échec création partenaire (URL logo)")
        print(response.text)

def main():
    """Fonction principale"""
    print("🧪 Test de Création de Partenaires avec Logo Intégré")
    print("=" * 60)
    
    # Test de connexion
    token = test_login()
    if not token:
        print("❌ Impossible de continuer sans token")
        return
    
    # Tests de création
    test_create_partner_json(token)
    test_create_partner_with_logo_url(token)
    test_create_partner_with_logo(token)
    
    print("\n" + "=" * 60)
    print("🏁 Tests terminés")

if __name__ == "__main__":
    main() 