#!/usr/bin/env python3
"""
Script de test pour le cache Redis FCM
Teste toutes les fonctionnalités du cache et affiche les résultats
"""

import sys
import os
import logging
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_fcm_cache():
    """Test complet du cache Redis FCM"""
    
    print("🔔 Test du Cache Redis FCM")
    print("=" * 50)
    
    try:
        # Test 1: Import du cache
        print("\n1️⃣ Test d'import du cache...")
        from utils.fcm_cache import fcm_cache
        
        if fcm_cache.is_available():
            print("✅ Cache Redis FCM disponible")
        else:
            print("❌ Cache Redis FCM non disponible")
            return False
        
        # Test 2: Informations du cache
        print("\n2️⃣ Informations du cache...")
        cache_info = fcm_cache.get_cache_info()
        print(f"Status: {cache_info.get('status')}")
        print(f"Clés FCM: {cache_info.get('fcm_keys_count')}")
        print(f"Mémoire Redis: {cache_info.get('redis_used_memory')}")
        
        # Test 3: Cache des tokens admin
        print("\n3️⃣ Test cache tokens admin...")
        test_admin_tokens = [
            "test_token_admin_1_123456789",
            "test_token_admin_2_987654321",
            "test_token_admin_3_555666777"
        ]
        
        # Mettre en cache
        success = fcm_cache.cache_admin_tokens(test_admin_tokens, ttl=60)
        print(f"Mise en cache: {'✅' if success else '❌'}")
        
        # Récupérer du cache
        cached_tokens = fcm_cache.get_cached_admin_tokens()
        if cached_tokens:
            print(f"Récupération: ✅ {len(cached_tokens)} tokens")
            print(f"Tokens: {cached_tokens}")
        else:
            print("Récupération: ❌ Aucun token trouvé")
        
        # Test 4: Cache token utilisateur
        print("\n4️⃣ Test cache token utilisateur...")
        test_user_id = 999
        test_user_token = "test_token_user_999_abcdef123"
        
        # Mettre en cache
        success = fcm_cache.cache_user_token(test_user_id, test_user_token, ttl=60)
        print(f"Mise en cache: {'✅' if success else '❌'}")
        
        # Récupérer du cache
        cached_token = fcm_cache.get_cached_user_token(test_user_id)
        if cached_token:
            print(f"Récupération: ✅ Token: {cached_token}")
        else:
            print("Récupération: ❌ Token non trouvé")
        
        # Test 5: Cache statistiques
        print("\n5️⃣ Test cache statistiques...")
        test_stats = {
            "total_notifications": 150,
            "success_rate": 0.95,
            "active_tokens": 25,
            "last_24h": 45
        }
        
        # Mettre en cache
        success = fcm_cache.cache_notification_stats(test_stats, ttl=60)
        print(f"Mise en cache: {'✅' if success else '❌'}")
        
        # Récupérer du cache
        cached_stats = fcm_cache.get_cached_notification_stats()
        if cached_stats:
            print(f"Récupération: ✅ Stats: {cached_stats}")
        else:
            print("Récupération: ❌ Stats non trouvées")
        
        # Test 6: Invalidation
        print("\n6️⃣ Test invalidation...")
        
        # Invalider token utilisateur
        success = fcm_cache.invalidate_user_token(test_user_id)
        print(f"Invalidation token utilisateur: {'✅' if success else '❌'}")
        
        # Vérifier que le token est supprimé
        cached_token = fcm_cache.get_cached_user_token(test_user_id)
        if not cached_token:
            print("✅ Token utilisateur correctement invalidé")
        else:
            print("❌ Token utilisateur toujours en cache")
        
        # Invalider tokens admin
        success = fcm_cache.invalidate_admin_tokens()
        print(f"Invalidation tokens admin: {'✅' if success else '❌'}")
        
        # Test 7: Informations finales
        print("\n7️⃣ Informations finales du cache...")
        final_info = fcm_cache.get_cache_info()
        print(f"Clés FCM restantes: {final_info.get('fcm_keys_count')}")
        
        # Test 8: Vidage complet
        print("\n8️⃣ Test vidage complet...")
        success = fcm_cache.clear_all_fcm_cache()
        print(f"Vidage complet: {'✅' if success else '❌'}")
        
        # Vérifier que tout est vidé
        final_info = fcm_cache.get_cache_info()
        print(f"Clés FCM après vidage: {final_info.get('fcm_keys_count')}")
        
        print("\n🎉 Tests terminés avec succès!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        logger.error(f"Erreur test cache FCM: {e}")
        return False

def test_integration_with_push_service():
    """Test d'intégration avec le service push"""
    
    print("\n🔔 Test d'Intégration avec le Service Push")
    print("=" * 50)
    
    try:
        # Test 1: Import du service push
        print("\n1️⃣ Test d'import du service push...")
        from services.push_notification_service import push_service
        
        if push_service:
            print("✅ Service push disponible")
            
            # Vérifier si le cache est intégré
            if hasattr(push_service, 'fcm_cache') and push_service.fcm_cache:
                print("✅ Cache FCM intégré au service push")
                
                # Test du cache via le service
                cache_info = push_service.fcm_cache.get_cache_info()
                print(f"Status cache via service: {cache_info.get('status')}")
                
            else:
                print("❌ Cache FCM non intégré au service push")
        else:
            print("❌ Service push non disponible")
            return False
        
        print("\n🎉 Test d'intégration terminé!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test d'intégration: {e}")
        logger.error(f"Erreur test intégration: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🚀 Démarrage des tests du Cache Redis FCM")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test du cache
    cache_success = test_fcm_cache()
    
    # Test d'intégration
    integration_success = test_integration_with_push_service()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Cache Redis FCM: {'✅ SUCCÈS' if cache_success else '❌ ÉCHEC'}")
    print(f"Intégration Service: {'✅ SUCCÈS' if integration_success else '❌ ÉCHEC'}")
    
    if cache_success and integration_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("Le cache Redis FCM est opérationnel.")
        return 0
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez la configuration Redis et les logs.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 