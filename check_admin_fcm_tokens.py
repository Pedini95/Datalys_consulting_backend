#!/usr/bin/env python3
"""
Script pour vérifier les tokens FCM des admins
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

def check_admin_fcm_tokens():
    """Vérifier les tokens FCM des admins"""
    print("🔍 VÉRIFICATION DES TOKENS FCM DES ADMINS")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Vérifier les utilisateurs admins
        response = requests.post(f"{BASE_URL}/users/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 50,
                                  "data": {
                                      "role_id": 1,  # Admins
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admins récupérés: {json.dumps(data, indent=2)}")
            
            items = data.get('items', [])
            count = data.get('count', 0)
            
            if count > 0:
                print(f"\n📊 {count} admins trouvés")
                
                admins_with_tokens = 0
                for admin in items:
                    fcm_token = admin.get('fcm_token')
                    if fcm_token and fcm_token != "NON DÉFINI":
                        print(f"✅ Admin {admin.get('id')} ({admin.get('email')}): Token FCM présent")
                        admins_with_tokens += 1
                    else:
                        print(f"❌ Admin {admin.get('id')} ({admin.get('email')}): Pas de token FCM")
                
                print(f"\n📱 Résumé: {admins_with_tokens}/{count} admins ont un token FCM")
                return admins_with_tokens > 0
            else:
                print("⚠️ Aucun admin trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_notification_with_real_token():
    """Tester une notification avec un vrai token"""
    print("\n🔔 TEST NOTIFICATION AVEC VRAI TOKEN")
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

def main():
    """Test principal"""
    print("🔍 DIAGNOSTIC DES TOKENS FCM DES ADMINS")
    print("=" * 50)
    
    # Vérifier les tokens FCM des admins
    tokens_ok = check_admin_fcm_tokens()
    
    # Tester une notification
    notification_ok = test_notification_with_real_token()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    print(f"📱 Tokens FCM admins: {'✅ OK' if tokens_ok else '❌ ÉCHEC'}")
    print(f"🔔 Test notification: {'✅ OK' if notification_ok else '❌ ÉCHEC'}")
    
    if tokens_ok and notification_ok:
        print("\n🎉 SUCCÈS ! Le système FCM fonctionne parfaitement !")
    elif not tokens_ok:
        print("\n⚠️ PROBLÈME: Les admins n'ont pas de tokens FCM")
        print("💡 Solution: Les admins doivent s'enregistrer pour recevoir des notifications")
    else:
        print("\n⚠️ PROBLÈME: Erreur lors de l'envoi de notifications")
        print("💡 Vérifiez la configuration Firebase")

if __name__ == "__main__":
    main()
