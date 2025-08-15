#!/usr/bin/env python3
import os
import sys

print("🔍 Test des permissions et chemins...")

# Test 1: Vérifier le répertoire courant
print(f"📁 Répertoire courant: {os.getcwd()}")

# Test 2: Vérifier les permissions du répertoire courant
try:
    os.access(os.getcwd(), os.W_OK)
    print("✅ Permissions d'écriture OK sur le répertoire courant")
except Exception as e:
    print(f"❌ Erreur permissions répertoire courant: {e}")

# Test 3: Créer le dossier logs avec chemin relatif
try:
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    print(f"📁 Tentative de création: {log_dir}")
    os.makedirs(log_dir, exist_ok=True)
    print("✅ Dossier logs créé avec succès")
except Exception as e:
    print(f"❌ Erreur création dossier logs: {e}")

# Test 4: Vérifier les variables d'environnement
print(f"👤 Utilisateur: {os.getenv('USER', 'N/A')}")
print(f"🏠 HOME: {os.getenv('HOME', 'N/A')}")

# Test 5: Vérifier les permissions du dossier /app si il existe
if os.path.exists('/app'):
    try:
        os.access('/app', os.W_OK)
        print("✅ Permissions d'écriture OK sur /app")
    except Exception as e:
        print(f"❌ Erreur permissions /app: {e}")
else:
    print("ℹ️  Dossier /app n'existe pas (normal en local)")

print("✅ Test terminé") 