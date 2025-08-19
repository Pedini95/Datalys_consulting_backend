#!/usr/bin/env python3
"""
Script de diagnostic complet pour le système FCM
"""

import requests
import json
import os
import sys

# Configuration
BASE_URL = "http://82.112.253.137:8082"
LOGIN_EMAIL = "yablaiyablairubenvirgil@gmail.com"
LOGIN_PASSWORD = "password123"

def test_login():
    """Test de connexion pour obtenir un token"""
    print("🔐 Test de connexion...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": LOGIN_EMAIL,
            "password": LOGIN_PASSWORD
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                token = data['data']['token']
                print(f"✅ Login réussi - Token: {token[:50]}...")
                return token
            else:
                print(f"❌ Login échoué: {data.get('message')}")
                return None
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_fcm_status():
    """Test du statut FCM (sans authentification)"""
    print("\n🔔 Test statut FCM (public)...")
    
    try:
        response = requests.get(f"{BASE_URL}/fcm/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ FCM Status: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur FCM status: {e}")
        return None

def test_fcm_cache(token):
    """Test du cache FCM (avec authentification)"""
    print("\n🗄️ Test cache FCM...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/fcm/cache/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache FCM: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur cache FCM: {e}")
        return None

def test_fcm_notification(token):
    """Test d'envoi de notification FCM"""
    print("\n📱 Test notification FCM...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/fcm/test-notification", 
                               headers=headers,
                               json={
                                   "title": "Test Diagnostic",
                                   "body": "Test de notification depuis le diagnostic"
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

def test_register_token(token):
    """Test d'enregistrement de token FCM"""
    print("\n📝 Test enregistrement token FCM...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        test_token = "test_fcm_token_diagnostic_12345"
        
        response = requests.post(f"{BASE_URL}/fcm/register-token", 
                               headers=headers,
                               json={"token": test_token},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enregistrement token: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur enregistrement token: {e}")
        return None

def test_health_endpoint():
    """Test de l'endpoint de santé"""
    print("\n🏥 Test endpoint santé...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur health check: {e}")
        return None

def main():
    """Diagnostic principal"""
    print("🔍 DIAGNOSTIC COMPLET DU SYSTÈME FCM")
    print("=" * 50)
    
    # Test de santé général
    health = test_health_endpoint()
    
    # Test de connexion
    token = test_login()
    if not token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return
    
    # Tests FCM
    fcm_status = test_fcm_status()
    fcm_cache = test_fcm_cache(token)
    fcm_notification = test_fcm_notification(token)
    fcm_register = test_register_token(token)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    print(f"🏥 Health Check: {'✅ OK' if health else '❌ ÉCHEC'}")
    print(f"🔐 Authentification: {'✅ OK' if token else '❌ ÉCHEC'}")
    print(f"🔔 Statut FCM: {'✅ OK' if fcm_status and fcm_status.get('data', {}).get('fcm_enabled') else '❌ ÉCHEC'}")
    print(f"🗄️ Cache FCM: {'✅ OK' if fcm_cache and fcm_cache.get('data', {}).get('status') == 'available' else '❌ ÉCHEC'}")
    print(f"📱 Notification Test: {'✅ OK' if fcm_notification and fcm_notification.get('data', {}).get('notification_sent') else '❌ ÉCHEC'}")
    print(f"📝 Enregistrement Token: {'✅ OK' if fcm_register else '❌ ÉCHEC'}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    
    if not fcm_status or not fcm_status.get('data', {}).get('fcm_enabled'):
        print("  • Vérifier la configuration Firebase sur le serveur")
        print("  • Vérifier que FIREBASE_ENABLED=True dans les variables d'environnement")
        print("  • Vérifier que le fichier firebase-service-account.json existe")
    
    if not fcm_cache or fcm_cache.get('data', {}).get('status') != 'available':
        print("  • Vérifier la connexion Redis pour le cache FCM")
        print("  • Vérifier les variables REDIS_HOST, REDIS_PORT, REDIS_DB")
    
    if not fcm_notification or not fcm_notification.get('data', {}).get('notification_sent'):
        print("  • Le service FCM n'arrive pas à envoyer des notifications")
        print("  • Vérifier les logs du serveur pour plus de détails")

if __name__ == "__main__":
    main()
