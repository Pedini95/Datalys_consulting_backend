#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier l'état de Redis et des sessions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.session_utils import session_manager, is_user_session_valid, create_user_session, delete_user_session
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_redis_connection():
    """Test de la connexion Redis"""
    print("🔍 Test de la connexion Redis")
    print("=" * 50)
    
    if session_manager.redis_client is None:
        print("❌ Redis n'est pas connecté!")
        return False
    
    try:
        # Test de ping
        result = session_manager.redis_client.ping()
        print(f"✅ Redis ping: {result}")
        
        # Test d'écriture/lecture
        test_key = "test:connection"
        session_manager.redis_client.set(test_key, "test_value", ex=60)
        value = session_manager.redis_client.get(test_key)
        print(f"✅ Test d'écriture/lecture: {value}")
        
        # Nettoyer
        session_manager.redis_client.delete(test_key)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        return False

def test_session_creation():
    """Test de création de session"""
    print("\n🔍 Test de création de session")
    print("=" * 50)
    
    test_user_id = 999
    test_user_data = {
        'id': test_user_id,
        'email': 'test@example.com',
        'name': 'Test User'
    }
    test_token = "test_token_12345"
    
    # Créer une session
    print(f"Création de session pour user_id={test_user_id}, token={test_token}")
    success = create_user_session(test_user_id, test_user_data, test_token)
    print(f"✅ Session créée: {success}")
    
    # Vérifier que la session existe
    is_valid = is_user_session_valid(test_token)
    print(f"✅ Session valide: {is_valid}")
    
    # Supprimer la session
    deleted = delete_user_session(test_token)
    print(f"✅ Session supprimée: {deleted}")
    
    # Vérifier que la session n'existe plus
    is_valid_after = is_user_session_valid(test_token)
    print(f"✅ Session valide après suppression: {is_valid_after}")
    
    return success and is_valid and deleted and not is_valid_after

def list_all_sessions():
    """Lister toutes les sessions Redis"""
    print("\n🔍 Sessions Redis existantes")
    print("=" * 50)
    
    try:
        # Chercher toutes les clés de session
        session_keys = session_manager.redis_client.keys("session:*")
        print(f"Nombre de sessions trouvées: {len(session_keys)}")
        
        for key in session_keys[:5]:  # Afficher les 5 premières
            print(f"  - {key}")
            
        if len(session_keys) > 5:
            print(f"  ... et {len(session_keys) - 5} autres")
            
    except Exception as e:
        print(f"❌ Erreur lors de la liste des sessions: {e}")

def main():
    """Fonction principale de diagnostic"""
    print("🔧 Diagnostic Redis et Sessions")
    print("=" * 60)
    
    # Test de connexion Redis
    redis_ok = test_redis_connection()
    
    if not redis_ok:
        print("\n❌ Redis n'est pas disponible. Le système fonctionne en mode dégradé.")
        print("   Cela explique pourquoi les tokens restent valides après logout.")
        return
    
    # Test de création/suppression de sessions
    sessions_ok = test_session_creation()
    
    if not sessions_ok:
        print("\n❌ Problème avec la gestion des sessions Redis.")
        return
    
    # Lister les sessions existantes
    list_all_sessions()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic terminé")
    
    if redis_ok and sessions_ok:
        print("✅ Redis et sessions fonctionnent correctement")
        print("   Le problème de logout devrait maintenant être résolu.")
    else:
        print("❌ Problèmes détectés - vérifiez la configuration Redis")

if __name__ == "__main__":
    main()
