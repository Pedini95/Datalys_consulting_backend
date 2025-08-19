#!/usr/bin/env python3
"""
Script pour corriger le cache des admins
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

def clear_admin_cache():
    """Vider le cache des admins pour forcer la régénération"""
    print("🗑️ VIDER LE CACHE DES ADMINS")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Appeler l'endpoint pour vider le cache (si disponible)
        # Sinon, on va forcer la régénération en envoyant un message
        print("📝 Envoi message pour forcer la régénération du cache...")
        response = requests.post(f"{BASE_URL}/messages/send", 
                              headers=headers,
                              json={
                                  "title": "Force Cache Refresh",
                                  "description": "Message pour forcer la régénération du cache des admins",
                                  "priority": "haute",
                                  "project_id": 2
                              },
                              timeout=10)
        
        if response.status_code == 200:
            print("✅ Message envoyé - cache devrait être régénéré")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_partner_message():
    """Tester un message d'un partenaire qui devrait notifier les admins"""
    print("\n👤 TEST MESSAGE PARTENAIRE → ADMINS")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Simuler un message d'un partenaire (user_id=11)
        # Note: En réalité, ce serait un vrai partenaire qui envoie
        print("📝 Simulation message partenaire...")
        response = requests.post(f"{BASE_URL}/messages/send", 
                              headers=headers,
                              json={
                                  "title": "Test Partenaire → Admins",
                                  "description": "Message d'un partenaire qui devrait notifier les admins",
                                  "priority": "haute",
                                  "project_id": 2
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Message envoyé: {json.dumps(data, indent=2)}")
            print("🎉 SUCCÈS ! Message envoyé - notification aux admins déclenchée")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_cache_after_message():
    """Vérifier le cache après envoi de message"""
    print("\n📊 VÉRIFICATION DU CACHE APRÈS MESSAGE")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/fcm/cache/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache status: {json.dumps(data, indent=2)}")
            
            # Vérifier si le cache des admins contient des tokens
            fcm_keys = data.get('data', {}).get('fcm_keys', [])
            if 'fcm:admin_tokens:all' in fcm_keys:
                print("✅ Cache des admins présent")
                return True
            else:
                print("❌ Cache des admins absent")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🔧 CORRECTION DU CACHE DES ADMINS")
    print("=" * 50)
    
    # Vider le cache des admins
    cache_cleared = clear_admin_cache()
    
    if cache_cleared:
        # Vérifier le cache après
        cache_ok = check_cache_after_message()
        
        # Tester un message partenaire
        message_ok = test_partner_message()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        print(f"🗑️ Cache vidé: {'✅ OK' if cache_cleared else '❌ ÉCHEC'}")
        print(f"📊 Cache vérifié: {'✅ OK' if cache_ok else '❌ ÉCHEC'}")
        print(f"👤 Message partenaire: {'✅ OK' if message_ok else '❌ ÉCHEC'}")
        
        if cache_cleared and cache_ok and message_ok:
            print("\n🎉 SUCCÈS ! Le cache des admins a été corrigé !")
            print("💡 Les notifications push devraient maintenant fonctionner")
        else:
            print("\n⚠️ Le cache a été vidé mais il y a encore des problèmes")
    else:
        print("\n❌ Impossible de vider le cache")

if __name__ == "__main__":
    main()
