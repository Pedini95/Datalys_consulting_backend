#!/usr/bin/env python3
"""
Test complet du système FCM
"""

import requests
import json

SERVER_URL = "http://82.112.253.137:8082"

def test_fcm_system():
    """Test complet du système FCM"""
    print("🔔 Test du système FCM")
    print("=" * 50)
    
    # 1. Login pour obtenir un token
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
            
        print(f"✅ Login réussi - Token: {token[:30]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test statut FCM
        print("\n2. Test statut FCM...")
        try:
            fcm_response = requests.get(f"{SERVER_URL}/fcm/status", timeout=10)
            if fcm_response.status_code == 200:
                fcm_data = fcm_response.json()
                print(f"✅ FCM Status: {fcm_data}")
            else:
                print(f"❌ FCM Status: {fcm_response.status_code}")
        except Exception as e:
            print(f"❌ Erreur FCM status: {e}")
        
        # 3. Test cache FCM (admin uniquement)
        print("\n3. Test cache FCM...")
        try:
            cache_response = requests.get(f"{SERVER_URL}/fcm/cache/status", headers=headers, timeout=10)
            if cache_response.status_code == 200:
                cache_data = cache_response.json()
                print(f"✅ Cache FCM: {cache_data}")
            else:
                print(f"❌ Cache FCM: {cache_response.status_code} - {cache_response.text}")
        except Exception as e:
            print(f"❌ Erreur cache FCM: {e}")
        
        # 4. Test notification (admin uniquement)
        print("\n4. Test notification...")
        notification_data = {
            "title": "Test Notification",
            "body": "Ceci est une notification de test depuis le script",
            "user_id": 1
        }
        
        try:
            notif_response = requests.post(f"{SERVER_URL}/fcm/test-notification", 
                                         json=notification_data, 
                                         headers=headers, 
                                         timeout=10)
            if notif_response.status_code == 200:
                notif_data = notif_response.json()
                print(f"✅ Notification envoyée: {notif_data}")
            else:
                print(f"❌ Notification: {notif_response.status_code} - {notif_response.text}")
        except Exception as e:
            print(f"❌ Erreur notification: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Test FCM terminé")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    test_fcm_system()
