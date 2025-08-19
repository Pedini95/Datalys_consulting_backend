#!/usr/bin/env python3
"""
Script de test pour vérifier la correction du problème des messages
"""

import requests
import json

BASE_URL = "http://82.112.253.137:8082"
ADMIN_EMAIL = "yablaiyablairubenvirgil@gmail.com"
ADMIN_PASSWORD = "password123"

def get_auth_token(email, password):
    """Obtenir un token d'authentification"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data['data']['token']
        return None
    except:
        return None

def test_send_message():
    """Tester l'envoi d'un message"""
    print("📝 Test envoi message...")
    
    token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print("❌ Impossible d'obtenir un token")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/messages/send", 
                              headers=headers,
                              json={
                                  "title": "Test Correction Messages",
                                  "description": "Ce message teste la correction du problème de récupération",
                                  "priority": "moyenne",
                                  "project_id": 2
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Message envoyé: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur envoi message: {e}")
        return False

def test_get_my_messages():
    """Tester la récupération des messages"""
    print("\n📋 Test récupération messages...")
    
    token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print("❌ Impossible d'obtenir un token")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/messages/my-messages", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 50
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Messages récupérés: {json.dumps(data, indent=2)}")
            
            # Vérifier s'il y a des messages
            items = data.get('items', [])
            count = data.get('count', 0)
            
            if count > 0:
                print(f"✅ SUCCÈS ! {count} messages trouvés")
                return True
            else:
                print("⚠️ Aucun message trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur récupération messages: {e}")
        return False

def test_get_all_messages():
    """Tester la récupération de tous les messages via l'API incidents"""
    print("\n🔍 Test récupération tous les messages...")
    
    token = get_auth_token(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        print("❌ Impossible d'obtenir un token")
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
            print(f"✅ Tous les messages: {json.dumps(data, indent=2)}")
            
            # Vérifier s'il y a des messages
            items = data.get('items', [])
            count = data.get('count', 0)
            
            if count > 0:
                print(f"✅ SUCCÈS ! {count} messages trouvés dans la base")
                
                # Afficher les détails des messages
                for i, msg in enumerate(items[:3]):  # Afficher les 3 premiers
                    print(f"  Message {i+1}: ID={msg.get('id')}, Titre='{msg.get('title')}', Created_by={msg.get('created_by')}")
                
                return True
            else:
                print("⚠️ Aucun message trouvé dans la base")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur récupération tous messages: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 TEST DE CORRECTION DU PROBLÈME DES MESSAGES")
    print("=" * 50)
    
    # Tester l'envoi d'un nouveau message
    send_ok = test_send_message()
    
    # Tester la récupération des messages
    get_ok = test_get_my_messages()
    
    # Tester la récupération de tous les messages
    all_ok = test_get_all_messages()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    print(f"📝 Envoi message: {'✅ OK' if send_ok else '❌ ÉCHEC'}")
    print(f"📋 Récupération mes messages: {'✅ OK' if get_ok else '❌ ÉCHEC'}")
    print(f"🔍 Récupération tous messages: {'✅ OK' if all_ok else '❌ ÉCHEC'}")
    
    if send_ok and get_ok and all_ok:
        print("\n🎉 SUCCÈS ! Le problème des messages est résolu !")
        print("💡 Les partenaires peuvent maintenant voir leurs messages envoyés")
    else:
        print("\n⚠️ Le problème persiste. Vérifiez les logs du serveur.")

if __name__ == "__main__":
    main()
