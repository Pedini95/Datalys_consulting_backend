#!/usr/bin/env python3
"""
Script pour vérifier l'état de Redis sur le serveur distant
"""

import requests
import json

# Configuration du serveur
SERVER_URL = "http://82.112.253.137:8082"

def check_redis_status():
    """Vérifier le statut Redis via l'API"""
    print("🔍 Vérification du statut Redis sur le serveur")
    print("=" * 50)
    
    try:
        # Test de l'endpoint de statut FCM (qui utilise Redis)
        response = requests.get(f"{SERVER_URL}/fcm/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Serveur accessible")
            print(f"   FCM enabled: {data.get('fcm_enabled', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
        else:
            print(f"❌ Erreur serveur: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

def test_login():
    """Test de login pour obtenir un nouveau token"""
    print("\n🔐 Test de login")
    print("=" * 30)
    
    # Remplacez par vos vraies credentials
    login_data = {
        "email": "votre_email@example.com",
        "password": "votre_password"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print("✅ Login réussi")
            print(f"   Token: {token[:20]}..." if token else "   Pas de token")
            return token
        else:
            print(f"❌ Échec login: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_api_with_token(token):
    """Test d'une API avec le nouveau token"""
    print(f"\n🧪 Test API avec nouveau token")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{SERVER_URL}/dashboard/admin/overview", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ API accessible avec le nouveau token")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"❌ API inaccessible: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

def main():
    """Fonction principale"""
    print("🔧 Diagnostic complet du serveur")
    print("=" * 60)
    
    # 1. Vérifier le statut Redis
    check_redis_status()
    
    # 2. Test de login
    token = test_login()
    
    # 3. Test API avec nouveau token
    if token:
        test_api_with_token(token)
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic terminé")

if __name__ == "__main__":
    main()
