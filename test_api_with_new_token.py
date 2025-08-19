#!/usr/bin/env python3
"""
Test de l'API avec le nouveau token obtenu
"""

import requests
import json

# Configuration
SERVER_URL = "http://82.112.253.137:8082"
NEW_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InlhYmxhaXlhYmxhaXJ1YmVudmlyZ2lsQGdtYWlsLmNvbSIsIm5hbWUiOiJKb2huIERvZSBVcGRhdGVkIiwiZXhwIjoxNzU1NTczNjgwfQ.TrOyl_hzozxonHo4IGKRAxPRYmcrxsbdbYCtpqN1fWs"

def test_api_with_new_token():
    """Test de l'API avec le nouveau token"""
    print("🧪 Test de l'API avec le nouveau token")
    print("=" * 50)
    print(f"Token: {NEW_TOKEN[:50]}...")
    print()
    
    headers = {
        "Authorization": f"Bearer {NEW_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Dashboard partner
    print("1. Test GET /dashboard/partner/2")
    print("-" * 30)
    
    try:
        response = requests.get(f"{SERVER_URL}/dashboard/partner/2", headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS - API accessible avec le nouveau token!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"❌ ÉCHEC - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    
    # Test 2: Dashboard admin overview
    print("2. Test GET /dashboard/admin/overview")
    print("-" * 35)
    
    try:
        response = requests.get(f"{SERVER_URL}/dashboard/admin/overview", headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS - Admin overview accessible!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"❌ ÉCHEC - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    
    # Test 3: User profile
    print("3. Test GET /users/profile")
    print("-" * 25)
    
    try:
        response = requests.get(f"{SERVER_URL}/users/profile", headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS - Profile utilisateur accessible!")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"❌ ÉCHEC - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    print("=" * 50)
    print("✅ Test terminé!")

if __name__ == "__main__":
    test_api_with_new_token()
