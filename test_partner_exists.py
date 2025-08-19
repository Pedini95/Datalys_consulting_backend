#!/usr/bin/env python3
"""
Script pour vérifier si le partenaire existe
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

def test_partner_exists():
    """Tester si le partenaire existe"""
    print("🔍 TEST EXISTENCE DU PARTENAIRE")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/partners/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 50,
                                  "data": {
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Partenaires récupérés: {json.dumps(data, indent=2)}")
            
            items = data.get('items', [])
            count = data.get('count', 0)
            
            if count > 0:
                print(f"\n📊 {count} partenaires trouvés")
                
                # Chercher le partenaire avec ID 24
                partner_24 = None
                for partner in items:
                    if partner.get('id') == 24:
                        partner_24 = partner
                        break
                
                if partner_24:
                    print(f"\n✅ Partenaire ID 24 trouvé:")
                    print(f"  Nom: {partner_24.get('name')}")
                    print(f"  Email: {partner_24.get('email')}")
                    print(f"  Téléphone: {partner_24.get('phone')}")
                    return True
                else:
                    print(f"\n❌ Partenaire ID 24 non trouvé")
                    print("Partenaires disponibles:")
                    for partner in items:
                        print(f"  - ID: {partner.get('id')}, Nom: {partner.get('name')}")
                    return False
            else:
                print("⚠️ Aucun partenaire trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 VÉRIFICATION DE L'EXISTENCE DU PARTENAIRE")
    print("=" * 50)
    
    partner_exists = test_partner_exists()
    
    if partner_exists:
        print("\n✅ Le partenaire existe, le problème vient de la relation")
    else:
        print("\n❌ Le partenaire n'existe pas, c'est pourquoi les informations ne s'affichent pas")

if __name__ == "__main__":
    main()
