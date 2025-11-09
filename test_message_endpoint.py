#!/usr/bin/env python3
"""
Script pour tester l'endpoint /messages/send localement
"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app
from services.incident_service import IncidentService
import logging

logging.basicConfig(level=logging.DEBUG)

def test_create_message():
    """Test de création d'un message"""
    app = create_app()

    with app.app_context():
        incident_service = IncidentService()

        # Données de test
        data = {
            "title": "Question sur l'incident",
            "description": "Bonjour, j'ai une question concernant la résolution de l'incident...",
            "recipient_id": 16
        }

        user_id = 5  # ID de l'utilisateur connecté

        print("\n" + "="*60)
        print("TEST: Création d'un message")
        print("="*60)
        print(f"\nDonnées d'entrée:")
        print(f"  - user_id: {user_id}")
        print(f"  - data: {data}")

        try:
            message, success, message_text = incident_service.create_message(data, user_id)

            print(f"\nRésultat:")
            print(f"  - success: {success}")
            print(f"  - message: {message_text}")

            if success and message:
                print(f"\n✅ Message créé avec succès!")
                print(f"  - ID: {message.id}")
                print(f"  - Numéro: {message.incident_number}")
                print(f"  - Titre: {message.title}")
                print(f"  - Type: {message.type}")
                print(f"  - user_id: {message.user_id}")
                print(f"  - assigned_to: {message.assigned_to}")
                print(f"  - Détails complets:")
                print(f"    {message.as_dict()}")
            else:
                print(f"\n❌ Échec de création du message")
                print(f"  - Raison: {message_text}")

        except Exception as e:
            print(f"\n❌ Erreur lors du test:")
            print(f"  - Type: {type(e).__name__}")
            print(f"  - Message: {str(e)}")
            import traceback
            traceback.print_exc()

        print("\n" + "="*60)

if __name__ == '__main__':
    test_create_message()
