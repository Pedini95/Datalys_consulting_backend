#!/usr/bin/env python3
"""
Test simple pour vérifier l'API des projets
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

def test_single_project():
    """Tester un projet spécifique"""
    print("🔍 TEST PROJET SPÉCIFIQUE")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/projects/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 1,
                                  "data": {
                                      "id": 4  # Projet avec partner_id: 24
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse complète: {json.dumps(data, indent=2)}")
            
            items = data.get('items', [])
            if items:
                project = items[0]
                print(f"\n📋 Détails du projet:")
                print(f"  ID: {project.get('id')}")
                print(f"  Titre: {project.get('title')}")
                print(f"  Partner ID: {project.get('partner_id')}")
                
                # Vérifier si le champ partner existe
                if 'partner' in project:
                    partner = project['partner']
                    if partner:
                        print(f"  👥 Partenaire trouvé:")
                        print(f"    - Nom: {partner.get('name')}")
                        print(f"    - Email: {partner.get('email')}")
                    else:
                        print(f"  ⚠️ Champ 'partner' présent mais null")
                else:
                    print(f"  ❌ Champ 'partner' absent de la réponse")
            else:
                print("⚠️ Aucun projet trouvé")
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_single_project()
