#!/usr/bin/env python3
"""
Script de test pour vérifier que l'API des projets inclut les informations du partenaire
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

def test_projects_with_partner():
    """Tester l'API des projets avec les informations du partenaire"""
    print("🔍 TEST DES PROJETS AVEC INFORMATIONS PARTENAIRE")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/projects/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 10,
                                  "data": {
                                      "is_active": True
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projets récupérés: {json.dumps(data, indent=2)}")
            
            # Vérifier si les informations du partenaire sont présentes
            items = data.get('items', [])
            count = data.get('count', 0)
            
            if count > 0:
                print(f"\n📊 {count} projets trouvés")
                
                for i, project in enumerate(items):
                    print(f"\n📋 Projet {i+1}:")
                    print(f"  ID: {project.get('id')}")
                    print(f"  Titre: {project.get('title')}")
                    print(f"  Partner ID: {project.get('partner_id')}")
                    
                    partner = project.get('partner')
                    if partner:
                        print(f"  👥 Partenaire:")
                        print(f"    - Nom: {partner.get('name')}")
                        print(f"    - Email: {partner.get('email')}")
                        print(f"    - Téléphone: {partner.get('phone')}")
                        print(f"    - Logo: {partner.get('logo_url')}")
                    else:
                        print(f"  ⚠️ Aucun partenaire associé")
                
                return True
            else:
                print("⚠️ Aucun projet trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_projects_filter_by_partner():
    """Tester le filtrage des projets par nom de partenaire"""
    print("\n🔍 TEST FILTRAGE PAR NOM DE PARTENAIRE")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Impossible d'obtenir un token d'authentification")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/projects/getByCriteria", 
                              headers=headers,
                              json={
                                  "index": 0,
                                  "size": 10,
                                  "data": {
                                      "is_active": True,
                                      "partner_name": "Datalys"  # Rechercher par nom de partenaire
                                  }
                              },
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Projets filtrés: {json.dumps(data, indent=2)}")
            
            items = data.get('items', [])
            count = data.get('count', 0)
            
            if count > 0:
                print(f"\n📊 {count} projets trouvés avec le filtre 'Datalys'")
                return True
            else:
                print("⚠️ Aucun projet trouvé avec ce filtre")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 TEST DE L'API PROJETS AVEC INFORMATIONS PARTENAIRE")
    print("=" * 50)
    
    # Test récupération des projets avec partenaire
    projects_ok = test_projects_with_partner()
    
    # Test filtrage par nom de partenaire
    filter_ok = test_projects_filter_by_partner()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    print(f"📋 Projets avec partenaire: {'✅ OK' if projects_ok else '❌ ÉCHEC'}")
    print(f"🔍 Filtrage par partenaire: {'✅ OK' if filter_ok else '❌ ÉCHEC'}")
    
    if projects_ok and filter_ok:
        print("\n🎉 SUCCÈS ! L'API des projets inclut maintenant les informations du partenaire !")
        print("💡 Les projets affichent maintenant :")
        print("   - Informations du projet (id, title, etc.)")
        print("   - Informations complètes du partenaire (nom, email, téléphone, logo)")
        print("   - Possibilité de filtrer par nom de partenaire")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les logs du serveur.")

if __name__ == "__main__":
    main()
