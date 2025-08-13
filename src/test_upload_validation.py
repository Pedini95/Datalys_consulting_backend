#!/usr/bin/env python3
"""
Script de test pour vérifier la validation des extensions de fichiers
"""

from utils.file_upload import file_upload_manager

def test_file_validation():
    """Tester la validation des extensions de fichiers"""
    
    print("=== TEST DE VALIDATION DES EXTENSIONS ===\n")
    
    # Test avec différents types de fichiers
    test_files = [
        "document.xlsx",
        "rapport.docx", 
        "presentation.pptx",
        "image.png",
        "fichier.txt",
        "archive.zip",
        "script.py",
        "test.xyz",  # Extension non autorisée
        # Test avec extensions malformées
        "document.xlsx_",
        "rapport.docx-",
        "image.png.",
        "fichier.txt___",
        "all_transactions_20250808.xlsx_"  # Le fichier problématique
    ]
    
    print("Extensions autorisées pour upload générique:")
    print(f"{', '.join(sorted(file_upload_manager.allowed_extensions))}\n")
    
    print("Extensions autorisées pour images uniquement:")
    print(f"{', '.join(sorted(file_upload_manager.image_extensions))}\n")
    
    print("=== TESTS DE VALIDATION ===\n")
    
    for filename in test_files:
        # Test upload générique
        is_allowed_generic = file_upload_manager.allowed_file(filename, image_only=False)
        
        # Test upload image
        is_allowed_image = file_upload_manager.allowed_file(filename, image_only=True)
        
        # Extraire l'extension pour debug
        if '.' in filename:
            extension = filename.rsplit('.', 1)[1].lower()
            clean_extension = extension.rstrip('_').rstrip('-').rstrip('.')
        else:
            extension = "aucune"
            clean_extension = "aucune"
        
        print(f"Fichier: {filename}")
        print(f"  - Extension brute: '{extension}'")
        print(f"  - Extension nettoyée: '{clean_extension}'")
        print(f"  - Upload générique: {'✅ AUTORISÉ' if is_allowed_generic else '❌ REFUSÉ'}")
        print(f"  - Upload image: {'✅ AUTORISÉ' if is_allowed_image else '❌ REFUSÉ'}")
        print()
    
    # Test spécifique pour le fichier problématique
    print("=== TEST SPÉCIFIQUE FICHIER PROBLÉMATIQUE ===")
    problem_file = "all_transactions_20250808.xlsx_"
    extension = problem_file.rsplit('.', 1)[1].lower() if '.' in problem_file else ''
    clean_extension = extension.rstrip('_').rstrip('-').rstrip('.')
    print(f"Fichier: {problem_file}")
    print(f"Extension brute: '{extension}'")
    print(f"Extension nettoyée: '{clean_extension}'")
    print(f"Extension dans allowed_extensions: {clean_extension in file_upload_manager.allowed_extensions}")
    print(f"Validation complète: {file_upload_manager.allowed_file(problem_file, image_only=False)}")

if __name__ == "__main__":
    test_file_validation() 