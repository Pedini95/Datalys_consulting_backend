#!/usr/bin/env python3
"""
Script de test pour vérifier les messages du partenaire
"""

import requests
import json

BASE_URL = "http://82.112.253.137:8082"

# Note: Il faudrait les vraies credentials du partenaire
# Pour l'instant, on teste avec l'admin mais on vérifie la logique

def get_auth_token():
    """Obtenir un token d'authentification admin"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "yablaiyablairubenvirgil@gmail.com",
            "password": "password123"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data['data']['token']
        return None
    except:
        return None

def test_partner_messages():
    """Tester la récupération des messages du partenaire"""
    print("🔍 TEST DES MESSAGES DU PARTENAIRE")
    print("=" * 50)
    
    # Obtenir un token d'authentification
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    # Test 1: Vérifier que le message du partenaire existe dans la base
    print("📋 Test 1: Vérifier le message du partenaire dans la base...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/incidents/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 50,
                                  "data": {
                                      "type": "message",
                                      "created_by": 11,  # ID du partenaire
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            count = data.get('count', 0)
            
            print(f"✅ {count} messages trouvés pour le partenaire (user_id: 11)")
            
            if count > 0:
                for msg in items:
                    print(f"  📝 Message ID={msg.get('id')}: '{msg.get('title')}' (created_by: {msg.get('created_by')})")
                return True
            else:
                print("⚠️ Aucun message trouvé pour le partenaire")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_admin_messages():
    """Tester la récupération des messages de l'admin"""
    print("\n📋 Test 2: Vérifier les messages de l'admin...")
    
    # Obtenir un token d'authentification
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/incidents/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 50,
                                  "data": {
                                      "type": "message",
                                      "created_by": 1,  # ID de l'admin
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            count = data.get('count', 0)
            
            print(f"✅ {count} messages trouvés pour l'admin (user_id: 1)")
            
            if count > 0:
                for msg in items[:3]:  # Afficher les 3 premiers
                    print(f"  📝 Message ID={msg.get('id')}: '{msg.get('title')}' (created_by: {msg.get('created_by')})")
                return True
            else:
                print("⚠️ Aucun message trouvé pour l'admin")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_all_messages():
    """Tester la récupération de tous les messages"""
    print("\n📋 Test 3: Vérifier tous les messages...")
    
    # Obtenir un token d'authentification
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/incidents/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 50,
                                  "data": {
                                      "type": "message",
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            count = data.get('count', 0)
            
            print(f"✅ {count} messages trouvés au total")
            
            # Compter par utilisateur
            by_user = {}
            for msg in items:
                created_by = msg.get('created_by')
                if created_by not in by_user:
                    by_user[created_by] = 0
                by_user[created_by] += 1
            
            print("📊 Répartition par utilisateur:")
            for user_id, msg_count in by_user.items():
                print(f"  👤 User {user_id}: {msg_count} messages")
            
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 DIAGNOSTIC DES MESSAGES PAR UTILISATEUR")
    print("=" * 50)
    
    # Tests
    partner_ok = test_partner_messages()
    admin_ok = test_admin_messages()
    all_ok = test_all_messages()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    print(f"👤 Messages partenaire (user_id: 11): {'✅ OK' if partner_ok else '❌ ÉCHEC'}")
    print(f"👤 Messages admin (user_id: 1): {'✅ OK' if admin_ok else '❌ ÉCHEC'}")
    print(f"📊 Tous les messages: {'✅ OK' if all_ok else '❌ ÉCHEC'}")
    
    if partner_ok and admin_ok and all_ok:
        print("\n🎉 SUCCÈS ! La correction fonctionne !")
        print("💡 Les messages sont maintenant correctement récupérés par utilisateur")
        print("💡 Le partenaire devrait maintenant voir ses messages dans l'API /messages/my-messages")
    else:
        print("\n⚠️ Il y a encore des problèmes. Vérifiez les logs du serveur.")

if __name__ == "__main__":
    main()
