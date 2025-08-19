#!/usr/bin/env python3
"""
Test des notifications avec le vrai token FCM du frontend
"""

import requests
import json

BASE_URL = "http://82.112.253.137:8082"
LOGIN_EMAIL = "yablaiyablairubenvirgil@gmail.com"
LOGIN_PASSWORD = "password123"

def get_auth_token():
    """Obtenir un token d'authentification"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": LOGIN_EMAIL,
            "password": LOGIN_PASSWORD
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data['data']['token']
        return None
    except:
        return None

def test_real_notification():
    """Test d'envoi de notification avec le vrai token FCM"""
    print("🔔 Test notification avec vrai token FCM...")
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/fcm/test-notification", 
                               headers=headers,
                               json={
                                   "title": "Test Notification Réelle",
                                   "body": "Ceci est un test avec le vrai token FCM"
                               },
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notification test: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur notification test: {e}")
        return None

def test_message_with_notification():
    """Test d'envoi d'un message avec priorité haute pour déclencher une notification"""
    print("\n📝 Test envoi message avec notification...")
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/messages/send", 
                               headers=headers,
                               json={
                                   "title": "Test Notification Push",
                                   "description": "Ce message devrait déclencher une notification push",
                                   "priority": "haute",
                                   "project_id": 2
                               },
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Message envoyé: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur envoi message: {e}")
        return None

def main():
    """Test principal"""
    print("🔍 TEST DES NOTIFICATIONS AVEC VRAI TOKEN FCM")
    print("=" * 50)
    
    # Test notification directe
    notification_result = test_real_notification()
    
    # Test message avec notification automatique
    message_result = test_message_with_notification()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    print(f"🔔 Notification directe: {'✅ OK' if notification_result and notification_result.get('data', {}).get('notification_sent') else '❌ ÉCHEC'}")
    print(f"📝 Message avec notification: {'✅ OK' if message_result else '❌ ÉCHEC'}")
    
    if notification_result and notification_result.get('data', {}).get('notification_sent'):
        print("\n🎉 SUCCÈS ! Les notifications push fonctionnent !")
    else:
        print("\n⚠️ Les notifications ne fonctionnent pas encore. Vérifiez les logs du serveur.")

if __name__ == "__main__":
    main()
