#!/usr/bin/env python3
"""
Script pour forcer la mise à jour du cache des admins
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

def force_refresh_admin_cache():
    """Forcer la mise à jour du cache des admins"""
    print("🔄 FORCER LA MISE À JOUR DU CACHE DES ADMINS")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Étape 1: Vérifier le cache avant
        print("📊 Cache avant mise à jour...")
        response = requests.get(f"{BASE_URL}/fcm/cache/status", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache status: {json.dumps(data, indent=2)}")
        
        # Étape 2: Envoyer un message de test qui force la mise à jour
        print("\n📝 Envoi message de test...")
        response = requests.post(f"{BASE_URL}/messages/send", 
                              headers=headers,
                              json={
                                  "title": "Test Cache Refresh",
                                  "description": "Message pour forcer la mise à jour du cache",
                                  "priority": "haute",
                                  "project_id": 2
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Message envoyé: {json.dumps(data, indent=2)}")
            
            # Étape 3: Vérifier le cache après
            print("\n📊 Cache après mise à jour...")
            response = requests.get(f"{BASE_URL}/fcm/cache/status", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cache status: {json.dumps(data, indent=2)}")
            
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_notification_after_cache_refresh():
    """Tester une notification après mise à jour du cache"""
    print("\n🔔 TEST NOTIFICATION APRÈS MISE À JOUR CACHE")
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
    print("🔄 FORCER LA MISE À JOUR DU CACHE FCM")
    print("=" * 50)
    
    # Forcer la mise à jour du cache
    cache_ok = force_refresh_admin_cache()
    
    if cache_ok:
        # Tester une notification après mise à jour
        notification_ok = test_notification_after_cache_refresh()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        print(f"🔄 Mise à jour cache: {'✅ OK' if cache_ok else '❌ ÉCHEC'}")
        print(f"🔔 Test notification: {'✅ OK' if notification_ok else '❌ ÉCHEC'}")
        
        if cache_ok and notification_ok:
            print("\n🎉 SUCCÈS ! Le cache a été mis à jour et les notifications fonctionnent !")
        else:
            print("\n⚠️ Le cache a été mis à jour mais les notifications échouent encore")
    else:
        print("\n❌ Impossible de mettre à jour le cache")

if __name__ == "__main__":
    main()
