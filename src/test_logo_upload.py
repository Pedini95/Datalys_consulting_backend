#!/usr/bin/env python3
"""
Test du système d'upload de logos
"""

import os
import tempfile
from PIL import Image

def create_test_image():
    """Créer une image de test"""
    # Créer une image simple
    img = Image.new('RGB', (100, 100), color='red')
    
    # Sauvegarder temporairement
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    temp_file.close()
    
    return temp_file.name

def test_logo_upload():
    """Tester l'upload de logo"""
    print("🚀 Test du système d'upload de logos")
    print("=" * 50)
    
    try:
        from app import app
        
        with app.test_request_context():
            from utils.file_upload import file_upload_manager
            
            # Créer une image de test
            test_image_path = create_test_image()
            
            print(f"✅ Image de test créée: {test_image_path}")
            
            # Simuler un fichier Flask
            class MockFile:
                def __init__(self, file_path):
                    self.file_path = file_path
                    self.filename = os.path.basename(file_path)
                
                def seek(self, offset, whence=0):
                    pass
                
                def tell(self):
                    return os.path.getsize(self.file_path)
                
                def save(self, path):
                    import shutil
                    shutil.copy2(self.file_path, path)
            
            mock_file = MockFile(test_image_path)
            
            # Test 1: Upload de logo
            print("\n🔐 Test 1: Upload de logo...")
            
            success, message, file_path = file_upload_manager.save_file(mock_file, subfolder='logos')
            
            if success:
                print("✅ Logo uploadé avec succès")
                print(f"   Chemin: {file_path}")
                
                # Générer l'URL
                file_url = file_upload_manager.get_file_url(file_path)
                print(f"   URL: {file_url}")
                
                # Test 2: Vérifier que le fichier existe
                print("\n📁 Test 2: Vérification du fichier...")
                
                absolute_path = os.path.join(app.root_path, file_path)
                if os.path.exists(absolute_path):
                    print("✅ Fichier existe sur le disque")
                    file_size = os.path.getsize(absolute_path)
                    print(f"   Taille: {file_size} bytes")
                else:
                    print("❌ Fichier non trouvé sur le disque")
                    return False
                
                # Test 3: Supprimer le fichier
                print("\n🗑️ Test 3: Suppression du fichier...")
                
                delete_success = file_upload_manager.delete_file(file_path)
                
                if delete_success:
                    print("✅ Fichier supprimé avec succès")
                    
                    # Vérifier que le fichier n'existe plus
                    if not os.path.exists(absolute_path):
                        print("✅ Fichier correctement supprimé du disque")
                    else:
                        print("❌ Fichier toujours présent sur le disque")
                        return False
                else:
                    print("❌ Échec de suppression du fichier")
                    return False
                
                # Nettoyage
                os.unlink(test_image_path)
                print("✅ Image de test nettoyée")
                
                print("\n🎉 Tous les tests sont passés avec succès !")
                print("✅ Le système d'upload de logos fonctionne parfaitement !")
                return True
                
            else:
                print(f"❌ Échec de l'upload: {message}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_file_validation():
    """Tester la validation des fichiers"""
    print("\n🔍 Test de validation des fichiers...")
    
    try:
        from utils.file_upload import file_upload_manager
        
        # Test avec un fichier valide
        test_image_path = create_test_image()
        
        class MockFile:
            def __init__(self, file_path):
                self.file_path = file_path
                self.filename = os.path.basename(file_path)
        
        mock_file = MockFile(test_image_path)
        
        is_valid, message = file_upload_manager.validate_image_file(mock_file)
        
        if is_valid:
            print("✅ Validation de fichier image réussie")
        else:
            print(f"❌ Échec de validation: {message}")
            return False
        
        # Nettoyage
        os.unlink(test_image_path)
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de validation: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test complet du système d'upload de logos")
    print("=" * 60)
    
    # Test de validation
    validation_test = test_file_validation()
    
    # Test d'upload
    upload_test = test_logo_upload()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    print(f"Test de validation: {'✅ SUCCÈS' if validation_test else '❌ ÉCHEC'}")
    print(f"Test d'upload: {'✅ SUCCÈS' if upload_test else '❌ ÉCHEC'}")
    
    if validation_test and upload_test:
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("✅ Le système d'upload de logos est entièrement fonctionnel !")
        print("\n📝 Utilisation :")
        print("   1. Upload: POST /api/upload/logo")
        print("   2. Suppression: POST /api/upload/delete")
        print("   3. Accès: GET /api/upload/uploads/logos/filename")
    else:
        print("\n⚠️  Certains tests ont échoué.")

if __name__ == "__main__":
    main() 