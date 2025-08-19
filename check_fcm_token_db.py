#!/usr/bin/env python3
"""
Script pour vérifier le token FCM dans la base de données
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

def check_admin_fcm_token_in_db():
    """Vérifier le token FCM de l'admin dans la base de données"""
    print("🔍 VÉRIFICATION DU TOKEN FCM DANS LA BASE DE DONNÉES")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Récupérer les informations de l'admin
        response = requests.post(f"{BASE_URL}/users/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 10,
                                  "data": {
                                      "id": 1,  # Admin 1
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin récupéré: {json.dumps(data, indent=2)}")
            
            items = data.get('items', [])
            if items:
                admin = items[0]
                fcm_token = admin.get('fcm_token')
                
                if fcm_token and fcm_token != "NON DÉFINI":
                    print(f"✅ Token FCM trouvé: {fcm_token[:20]}...")
                    return True
                else:
                    print(f"❌ Pas de token FCM dans la base de données")
                    return False
            else:
                print("❌ Admin non trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def force_token_save():
    """Forcer la sauvegarde du token FCM dans la base de données"""
    print("\n💾 FORCER LA SAUVEGARDE DU TOKEN FCM")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Enregistrer un nouveau token FCM
        real_fcm_token = "cgbkDq2OxGdnEqw9iKgSm4:APA91bHQLdjc9nFOT39yLhf853ctoz-P7jpw39e9RSOPYTSGl8rry6lccbfIlyh9ervlefAI-WxzCuLAydJQJZygsGOnvNX1Z-RS6F2HnGym21l6-uXYiO8"
        
        response = requests.post(f"{BASE_URL}/fcm/register-token", 
                              headers=headers,
                              json={
                                  "token": real_fcm_token
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token enregistré: {json.dumps(data, indent=2)}")
            
            # Vérifier immédiatement après
            print("\n🔍 Vérification après enregistrement...")
            return check_admin_fcm_token_in_db()
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 DIAGNOSTIC COMPLET DU TOKEN FCM")
    print("=" * 50)
    
    # Vérifier le token dans la DB
    token_in_db = check_admin_fcm_token_in_db()
    
    if not token_in_db:
        # Forcer la sauvegarde
        save_ok = force_token_save()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📋 RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 50)
        
        print(f"🔍 Token dans DB: {'✅ OK' if token_in_db else '❌ ÉCHEC'}")
        print(f"💾 Sauvegarde forcée: {'✅ OK' if save_ok else '❌ ÉCHEC'}")
        
        if save_ok:
            print("\n🎉 SUCCÈS ! Le token FCM est maintenant dans la base de données")
            print("💡 Les notifications push devraient maintenant fonctionner")
        else:
            print("\n⚠️ Impossible de sauvegarder le token FCM")
    else:
        print("\n🎉 SUCCÈS ! Le token FCM est déjà dans la base de données")

if __name__ == "__main__":
    main()
