#!/usr/bin/env python3
"""
Script pour tester la connexion Redis sur le serveur distant
"""

import redis
import os

# Configuration Redis du serveur
REDIS_HOST = "82.112.253.137"  # Adresse IP de votre serveur
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # Ajustez si vous avez un mot de passe

def test_redis_server():
    """Test de connexion Redis sur le serveur"""
    print("🔍 Test de connexion Redis sur le serveur")
    print("=" * 50)
    print(f"Host: {REDIS_HOST}")
    print(f"Port: {REDIS_PORT}")
    print(f"DB: {REDIS_DB}")
    
    try:
        # Créer la connexion Redis
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=10,
            socket_timeout=10
        )
        
        # Test de ping
        print("\n1. Test de ping...")
        result = redis_client.ping()
        print(f"✅ Ping réussi: {result}")
        
        # Test d'écriture/lecture
        print("\n2. Test d'écriture/lecture...")
        test_key = "test:logout_security"
        test_value = "test_value_123"
        
        redis_client.set(test_key, test_value, ex=60)
        print(f"✅ Écriture réussie: {test_key} = {test_value}")
        
        value = redis_client.get(test_key)
        print(f"✅ Lecture réussie: {test_key} = {value}")
        
        # Test de suppression
        print("\n3. Test de suppression...")
        deleted = redis_client.delete(test_key)
        print(f"✅ Suppression réussie: {deleted} clé(s) supprimée(s)")
        
        # Vérifier que la clé n'existe plus
        value_after = redis_client.get(test_key)
        print(f"✅ Vérification après suppression: {test_key} = {value_after}")
        
        # Lister les clés de session existantes
        print("\n4. Sessions existantes...")
        session_keys = redis_client.keys("session:*")
        print(f"✅ Nombre de sessions trouvées: {len(session_keys)}")
        
        for key in session_keys[:3]:  # Afficher les 3 premières
            print(f"  - {key}")
            
        if len(session_keys) > 3:
            print(f"  ... et {len(session_keys) - 3} autres")
        
        print("\n" + "=" * 50)
        print("✅ Redis sur le serveur fonctionne correctement!")
        print("   Le problème de logout devrait être résolu avec cette configuration.")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Erreur de connexion Redis: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que Redis est installé et démarré sur le serveur")
        print("2. Vérifiez que le port 6379 est ouvert")
        print("3. Vérifiez la configuration firewall")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    test_redis_server()
