#!/usr/bin/env python3
"""
Script pour vérifier les variables d'environnement sur le serveur
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

def check_config_endpoint(token):
    """Vérifier l'endpoint de configuration (si disponible)"""
    print("🔧 Vérification de la configuration...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/config/fcm", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuration FCM: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"❌ Endpoint config non disponible: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return None

def test_fcm_detailed():
    """Test détaillé du service FCM"""
    print("🔍 Test détaillé du service FCM...")
    
    try:
        response = requests.get(f"{BASE_URL}/fcm/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Détails FCM: {json.dumps(data, indent=2)}")
            
            # Analyser les détails
            fcm_data = data.get('data', {})
            print(f"\n📋 Analyse:")
            print(f"  • FCM Enabled: {fcm_data.get('fcm_enabled')}")
            print(f"  • Status: {fcm_data.get('status')}")
            print(f"  • Message: {fcm_data.get('message')}")
            
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_redis_connection():
    """Test de la connexion Redis"""
    print("\n🗄️ Test connexion Redis...")
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/fcm/cache/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Cache Redis: {json.dumps(data, indent=2)}")
            
            cache_data = data.get('data', {})
            print(f"\n📋 Analyse Redis:")
            print(f"  • Status: {cache_data.get('status')}")
            print(f"  • Message: {cache_data.get('message')}")
            
            return data
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        return None

def main():
    """Diagnostic principal"""
    print("🔍 DIAGNOSTIC DÉTAILLÉ DE LA CONFIGURATION")
    print("=" * 50)
    
    # Test détaillé FCM
    fcm_details = test_fcm_detailed()
    
    # Test Redis
    redis_details = test_redis_connection()
    
    # Recommandations spécifiques
    print("\n" + "=" * 50)
    print("💡 RECOMMANDATIONS SPÉCIFIQUES")
    print("=" * 50)
    
    if fcm_details:
        fcm_data = fcm_details.get('data', {})
        if not fcm_data.get('fcm_enabled'):
            print("🚨 PROBLÈME FCM DÉTECTÉ:")
            print("   • Le service FCM est désactivé sur le serveur")
            print("   • Vérifiez la variable FIREBASE_ENABLED sur le serveur")
            print("   • Vérifiez que le fichier firebase-service-account.json existe")
            print("   • Redémarrez l'application après correction")
    
    if redis_details:
        cache_data = redis_details.get('data', {})
        if cache_data.get('status') != 'available':
            print("🚨 PROBLÈME REDIS DÉTECTÉ:")
            print("   • Le cache Redis n'est pas disponible")
            print("   • Vérifiez les variables REDIS_HOST, REDIS_PORT sur le serveur")
            print("   • Vérifiez que Redis est démarré et accessible")
    
    print("\n🔧 ACTIONS À EFFECTUER SUR LE SERVEUR:")
    print("1. Vérifier les variables d'environnement:")
    print("   docker exec datalys-api env | grep -E '(FIREBASE|REDIS)'")
    print("2. Vérifier le fichier Firebase:")
    print("   docker exec datalys-api ls -la /app/config/firebase-service-account.json")
    print("3. Redémarrer l'application:")
    print("   docker restart datalys-api")

if __name__ == "__main__":
    main()
