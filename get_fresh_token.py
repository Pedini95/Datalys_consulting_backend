#!/usr/bin/env python3
"""
Obtenir un nouveau token frais et tester l'API
"""

import requests
import json

SERVER_URL = "http://82.112.253.137:8082"

def get_fresh_token_and_test():
    """Obtenir un nouveau token et tester l'API"""
    print("🔄 Obtenir un nouveau token frais")
    print("=" * 50)
    
    # 1. Login pour obtenir un nouveau token
    print("1. Login...")
    login_data = {
        "email": "yablaiyablairubenvirgil@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', {}).get('token')
            
            if token:
                print(f"✅ Login réussi - Token: {token[:30]}...")
                
                # 2. Test de l'API avec le nouveau token
                print("\n2. Test de l'API avec le nouveau token...")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test dashboard partner
                api_response = requests.get(f"{SERVER_URL}/dashboard/partner/2", headers=headers, timeout=10)
                
                if api_response.status_code == 200:
                    print("✅ SUCCÈS - API accessible avec le nouveau token!")
                    print(f"   Response: {api_response.text[:200]}...")
                    
                    # Test admin overview
                    admin_response = requests.get(f"{SERVER_URL}/dashboard/admin/overview", headers=headers, timeout=10)
                    if admin_response.status_code == 200:
                        print("✅ SUCCÈS - Admin overview accessible!")
                    else:
                        print(f"⚠️  Admin overview: {admin_response.status_code}")
                        
                else:
                    print(f"❌ API inaccessible: {api_response.status_code}")
                    print(f"   Response: {api_response.text}")
                    
            else:
                print("❌ Pas de token dans la réponse")
                print(f"   Response: {data}")
                
        else:
            print(f"❌ Login échoué: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    get_fresh_token_and_test()
