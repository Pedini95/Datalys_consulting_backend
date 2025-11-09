#!/usr/bin/env python3
"""
Script pour tester l'endpoint /dashboard/partner/<id> localement
"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app
from flask import g
from models import User
import logging

logging.basicConfig(level=logging.DEBUG)

def test_partner_dashboard():
    """Test du dashboard partenaire"""
    app = create_app()

    with app.app_context():
        # Simuler un utilisateur connecté
        # Récupérer l'utilisateur avec l'ID 21 (depuis le token JWT)
        user = User.query.get(21)

        if not user:
            print("❌ Utilisateur non trouvé (ID: 21)")
            return

        print(f"\n✅ Utilisateur trouvé: {user.name} (ID: {user.id})")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role.name if user.role else 'None'}")

        # Simuler g.current_user
        g.current_user = user

        # Tester avec le partner_id 15
        partner_id = 15

        print(f"\n{'='*60}")
        print(f"TEST: Dashboard Partner ID={partner_id}")
        print(f"{'='*60}")

        try:
            # Importer la fonction
            from routes.dashboard import get_partner_dashboard

            # Appeler la fonction
            response = get_partner_dashboard(partner_id)

            print(f"\n✅ Réponse reçue:")
            print(f"   Status: {response[1] if len(response) > 1 else 200}")
            print(f"   Data: {response[0].get_json()}")

        except Exception as e:
            print(f"\n❌ Erreur lors du test:")
            print(f"   Type: {type(e).__name__}")
            print(f"   Message: {str(e)}")
            import traceback
            traceback.print_exc()

        print(f"\n{'='*60}")

if __name__ == '__main__':
    test_partner_dashboard()
