#!/usr/bin/env python3
"""
Vérification de Redis Docker sur le serveur
"""

import requests
import json

SERVER_URL = "http://82.112.253.137:8082"

def check_redis_docker():
    """Vérifier l'état de Redis Docker"""
    print("🔍 Vérification de Redis Docker sur le serveur")
    print("=" * 50)
    
    # Test 1: Vérifier si Redis est accessible via localhost
    print("1. Test connexion Redis localhost...")
    try:
        import redis
        r = redis.Redis(host='82.112.253.137', port=6379, decode_responses=True, socket_timeout=5)
        result = r.ping()
        print(f"✅ Redis accessible: {result}")
        
        # Test d'écriture/lecture
        r.set('test_key', 'test_value', ex=60)
        value = r.get('test_key')
        print(f"✅ Test d'écriture/lecture: {value}")
        r.delete('test_key')
        
    except Exception as e:
        print(f"❌ Redis non accessible: {e}")
    
    print()
    
    # Test 2: Vérifier les conteneurs Docker
    print("2. Vérifier les conteneurs Docker...")
    try:
        # Essayer de se connecter au daemon Docker (si accessible)
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker accessible")
            print("Conteneurs actifs:")
            print(result.stdout)
        else:
            print("❌ Docker non accessible ou pas de conteneurs")
    except Exception as e:
        print(f"❌ Erreur Docker: {e}")
    
    print()
    
    # Test 3: Vérifier l'état de l'application
    print("3. Vérifier l'état de l'application...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Application: {data.get('status', 'N/A')}")
            print(f"   Database: {data.get('database', {}).get('status', 'N/A')}")
        else:
            print(f"❌ Application: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur application: {e}")
    
    print()
    print("=" * 50)
    print("✅ Vérification terminée")

if __name__ == "__main__":
    check_redis_docker()
