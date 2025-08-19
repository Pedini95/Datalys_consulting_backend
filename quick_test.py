#!/usr/bin/env python3
"""
Test rapide pour vérifier le login et l'API
"""

import requests
import json

SERVER_URL = "http://82.112.253.137:8082"

def quick_test():
    print("🚀 Test rapide login + API")
    print("=" * 40)
    
    # 1. Login
    print("1. Login...")
    login_data = {
        "email": "votre_email@example.com",  # Remplacez par votre email
        "password": "votre_password"         # Remplacez par votre mot de passe
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Login réussi - Token: {token[:30]}...")
            
            # 2. Test API avec nouveau token
            print("\n2. Test API...")
            headers = {"Authorization": f"Bearer {token}"}
            
            api_response = requests.get(f"{SERVER_URL}/dashboard/partner/2", headers=headers, timeout=10)
            
            if api_response.status_code == 200:
                print("✅ API accessible avec le nouveau token")
                print(f"   Response: {api_response.text[:100]}...")
            else:
                print(f"❌ API inaccessible: {api_response.status_code}")
                print(f"   Response: {api_response.text}")
                
        else:
            print(f"❌ Login échoué: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    quick_test()
