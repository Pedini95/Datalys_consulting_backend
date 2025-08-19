#!/usr/bin/env python3
"""
Vérifier si la colonne fcm_token existe dans la base de données
"""

import requests
import json

SERVER_URL = "http://82.112.253.137:8082"

def check_fcm_column():
    """Vérifier la colonne fcm_token"""
    print("🔍 Vérification de la colonne fcm_token")
    print("=" * 50)
    
    # 1. Login
    print("1. Login...")
    login_data = {
        "email": "yablaiyablairubenvirgil@gmail.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Login échoué: {response.status_code}")
            return
            
        data = response.json()
        token = data.get('data', {}).get('token')
        
        if not token:
            print("❌ Pas de token reçu")
            return
            
        print(f"✅ Login réussi")
        
        # 2. Vérifier les données utilisateur
        print("\n2. Vérifier les données utilisateur...")
        user_data = data.get('data', {})
        
        print(f"   ID: {user_data.get('id')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Name: {user_data.get('name')}")
        print(f"   FCM Token: {user_data.get('fcm_token', 'NON DÉFINI')}")
        
        # 3. Tester l'enregistrement d'un token FCM
        print("\n3. Test enregistrement token FCM...")
        headers = {"Authorization": f"Bearer {token}"}
        
        fcm_data = {
            "token": "test_fcm_token_12345"
        }
        
        fcm_response = requests.post(f"{SERVER_URL}/fcm/register-token", 
                                   json=fcm_data, 
                                   headers=headers, 
                                   timeout=10)
        
        if fcm_response.status_code == 200:
            fcm_result = fcm_response.json()
            print(f"✅ Token FCM enregistré: {fcm_result}")
        else:
            print(f"❌ Échec enregistrement: {fcm_response.status_code}")
            print(f"   Response: {fcm_response.text}")
        
        print("\n" + "=" * 50)
        print("✅ Vérification terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_fcm_column()
