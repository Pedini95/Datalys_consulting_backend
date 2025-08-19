#!/usr/bin/env python3
"""
Vérification de Redis sur le serveur
"""

import requests
import json

SERVER_URL = "http://82.112.253.137:8082"

def check_server_redis():
    """Vérifier l'état de Redis sur le serveur"""
    print("🔍 Vérification de Redis sur le serveur")
    print("=" * 50)
    
    # Test 1: Endpoint de statut FCM (utilise Redis)
    print("1. Test endpoint FCM status...")
    try:
        response = requests.get(f"{SERVER_URL}/fcm/status", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ FCM Status: {data}")
        else:
            print(f"❌ FCM Status échoué: {response.text}")
    except Exception as e:
        print(f"❌ Erreur FCM: {e}")
    
    print()
    
    # Test 2: Endpoint de santé général
    print("2. Test endpoint de santé...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data}")
        else:
            print(f"❌ Health échoué: {response.text}")
    except Exception as e:
        print(f"❌ Erreur Health: {e}")
    
    print()
    
    # Test 3: Endpoint de cache FCM
    print("3. Test endpoint cache FCM...")
    try:
        response = requests.get(f"{SERVER_URL}/fcm/cache/status", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache FCM: {data}")
        else:
            print(f"❌ Cache FCM échoué: {response.text}")
    except Exception as e:
        print(f"❌ Erreur Cache: {e}")
    
    print()
    print("=" * 50)
    print("✅ Vérification terminée")

if __name__ == "__main__":
    check_server_redis()
