#!/usr/bin/env python3
"""
Script de test pour vérifier la sécurité du logout
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"  # Ajustez selon votre configuration
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_logout_security():
    """Test de sécurité du logout"""
    
    print("🔒 Test de sécurité du logout")
    print("=" * 50)
    
    # 1. Login pour obtenir un token
    print("1. Connexion...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Échec de la connexion: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_result = login_response.json()
    token = login_result.get('token')
    
    if not token:
        print("❌ Aucun token reçu")
        return
    
    print(f"✅ Connexion réussie - Token: {token[:20]}...")
    
    # 2. Test d'une API protégée avec le token
    print("\n2. Test d'une API protégée...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test avec une API simple (par exemple, récupérer le profil utilisateur)
    profile_response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
    
    if profile_response.status_code == 200:
        print("✅ API protégée accessible avec le token")
    else:
        print(f"❌ API protégée inaccessible: {profile_response.status_code}")
    
    # 3. Logout
    print("\n3. Déconnexion...")
    logout_data = {"token": token}
    logout_response = requests.post(f"{BASE_URL}/auth/logout", json=logout_data)
    
    if logout_response.status_code == 200:
        print("✅ Logout réussi")
    else:
        print(f"❌ Échec du logout: {logout_response.status_code}")
        print(logout_response.text)
    
    # 4. Test de la même API protégée APRÈS logout
    print("\n4. Test de la même API APRÈS logout...")
    profile_response_after = requests.get(f"{BASE_URL}/users/profile", headers=headers)
    
    if profile_response_after.status_code == 401:
        print("✅ Sécurité OK - Token invalide après logout")
    else:
        print(f"❌ PROBLÈME DE SÉCURITÉ - Token encore valide après logout!")
        print(f"   Status: {profile_response_after.status_code}")
        print(f"   Response: {profile_response_after.text}")
    
    print("\n" + "=" * 50)
    print("Test terminé")

if __name__ == "__main__":
    test_logout_security()
