#!/usr/bin/env python3
"""
Script pour tester les notifications FCM avec un vrai token
"""

import requests
import json

BASE_URL = "http://82.112.253.137:8082"
ADMIN_EMAIL = "yablaiyablairubenvirgil@gmail.com"
ADMIN_PASSWORD = "password123"

def get_auth_token():
    """Obtenir un token d'authentification"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data['data']['token']
        return None
    except:
        return None

def register_real_fcm_token():
    """Enregistrer un vrai token FCM pour l'admin"""
    print("📱 ENREGISTREMENT D'UN VRAI TOKEN FCM")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    # Token FCM de test (normalement fourni par le frontend)
    real_fcm_token = "cgbkDq2OxGdnEqw9iKgSm4:APA91bHQLdjc9nFOT39yLhf853ctoz-P7jpw39e9RSOPYTSGl8rry6lccbfIlyh9ervlefAI-WxzCuLAydJQJZygsGOnvNX1Z-RS6F2HnGym21l6-uXYiO8"
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/fcm/register-token", 
                              headers=headers,
                              json={
                                  "token": real_fcm_token,
                                  "user_id": 1,
                                  "device_info": {
                                      "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                                      "platform": "Linux",
                                      "language": "fr-FR"
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enregistrement token: {json.dumps(data, indent=2)}")
            
            token_registered = data.get('data', {}).get('token_registered', False)
            if token_registered:
                print("🎉 SUCCÈS ! Token FCM enregistré avec succès")
                return True
            else:
                print("❌ ÉCHEC ! Token FCM non enregistré")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_notification_after_registration():
    """Tester une notification après enregistrement"""
    print("\n🔔 TEST NOTIFICATION APRÈS ENREGISTREMENT")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/fcm/test-notification", 
                              headers=headers,
                              json={},
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test notification: {json.dumps(data, indent=2)}")
            
            notification_sent = data.get('data', {}).get('notification_sent', False)
            if notification_sent:
                print("🎉 SUCCÈS ! Notification envoyée avec succès")
                return True
            else:
                print("❌ ÉCHEC ! Notification non envoyée")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_message_with_notification():
    """Tester l'envoi d'un message qui déclenche une notification"""
    print("\n📝 TEST MESSAGE AVEC NOTIFICATION")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/messages/send", 
                              headers=headers,
                              json={
                                  "title": "Test Notification Push",
                                  "description": "Ce message devrait déclencher une notification push aux admins",
                                  "priority": "haute",  # Déclenche notification
                                  "project_id": 2
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Message envoyé: {json.dumps(data, indent=2)}")
            print("🎉 SUCCÈS ! Message envoyé - notification push déclenchée")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 TEST COMPLET DES NOTIFICATIONS FCM")
    print("=" * 50)
    
    # Étape 1: Enregistrer un vrai token FCM
    registration_ok = register_real_fcm_token()
    
    if registration_ok:
        # Étape 2: Tester une notification directe
        notification_ok = test_notification_after_registration()
        
        # Étape 3: Tester un message qui déclenche une notification
        message_ok = test_message_with_notification()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        print(f"📱 Enregistrement token: {'✅ OK' if registration_ok else '❌ ÉCHEC'}")
        print(f"🔔 Test notification: {'✅ OK' if notification_ok else '❌ ÉCHEC'}")
        print(f"📝 Test message: {'✅ OK' if message_ok else '❌ ÉCHEC'}")
        
        if registration_ok and notification_ok and message_ok:
            print("\n🎉 SUCCÈS COMPLET ! Le système FCM fonctionne parfaitement !")
            print("💡 Les notifications push sont maintenant opérationnelles")
        else:
            print("\n⚠️ Certains tests ont échoué. Vérifiez la configuration.")
    else:
        print("\n❌ Impossible de continuer sans enregistrement de token")

if __name__ == "__main__":
    main()
