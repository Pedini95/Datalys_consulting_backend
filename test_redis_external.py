#!/usr/bin/env python3
"""
Test de connexion Redis externe
"""

import redis
import json

# Configuration Redis externe
REDIS_HOST = "82.112.253.137"
REDIS_PORT = 6379
REDIS_PASSWORD = None

def test_redis_external():
    """Test de connexion Redis externe"""
    print("🔍 Test de connexion Redis externe")
    print("=" * 50)
    print(f"Host: {REDIS_HOST}")
    print(f"Port: {REDIS_PORT}")
    print(f"Password: {'Aucun' if REDIS_PASSWORD is None else REDIS_PASSWORD[:10] + '...'}")
    print()
    
    try:
        # Connexion Redis sans mot de passe
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=10
        )
        
        # Test de ping
        print("1. Test de ping...")
        result = r.ping()
        print(f"✅ Ping réussi: {result}")
        
        # Test d'écriture/lecture
        print("\n2. Test d'écriture/lecture...")
        test_key = "test:external_redis"
        test_value = "test_value_123"
        
        r.set(test_key, test_value, ex=60)
        print(f"✅ Écriture réussie: {test_key} = {test_value}")
        
        value = r.get(test_key)
        print(f"✅ Lecture réussie: {test_key} = {value}")
        
        # Test de suppression
        print("\n3. Test de suppression...")
        deleted = r.delete(test_key)
        print(f"✅ Suppression réussie: {deleted} clé(s) supprimée(s)")
        
        # Vérifier que la clé n'existe plus
        value_after = r.get(test_key)
        print(f"✅ Vérification après suppression: {test_key} = {value_after}")
        
        # Lister les clés de session
        print("\n4. Sessions existantes...")
        session_keys = r.keys("session:*")
        print(f"✅ Nombre de sessions trouvées: {len(session_keys)}")
        
        for key in session_keys[:3]:  # Afficher les 3 premières
            print(f"  - {key}")
            
        if len(session_keys) > 3:
            print(f"  ... et {len(session_keys) - 3} autres")
        
        print("\n" + "=" * 50)
        print("✅ Redis externe fonctionne correctement!")
        print("   Votre API devrait maintenant fonctionner avec Redis.")
        
        return True
        
    except redis.AuthenticationError:
        print("❌ Erreur d'authentification Redis")
        print("   Vérifiez le mot de passe Redis")
        return False
        
    except redis.ConnectionError as e:
        print(f"❌ Erreur de connexion Redis: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que Redis est démarré")
        print("2. Vérifiez que le port 6379 est ouvert")
        print("3. Vérifiez la configuration firewall")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    test_redis_external()
