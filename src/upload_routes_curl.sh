#!/bin/bash

# Configuration
BASE_URL="http://localhost:8081"
AUTH_TOKEN="your_auth_token_here"

echo "🚀 File Upload Routes - cURL Commands"
echo "======================================"
echo ""

# 1. Upload Logo
echo "📤 1. Upload Logo"
echo "curl -X POST \\"
echo "  -H \"Authorization: Bearer $AUTH_TOKEN\" \\"
echo "  -F \"file=@/path/to/your/logo.png\" \\"
echo "  \"$BASE_URL/files/upload/logo\""
echo ""

# 2. Upload File
echo "📤 2. Upload File"
echo "curl -X POST \\"
echo "  -H \"Authorization: Bearer $AUTH_TOKEN\" \\"
echo "  -F \"file=@/path/to/your/file.pdf\" \\"
echo "  -F \"subfolder=files\" \\"
echo "  \"$BASE_URL/files/upload\""
echo ""

# 3. Delete Uploaded File
echo "🗑️  3. Delete Uploaded File"
echo "curl -X POST \\"
echo "  -H \"Authorization: Bearer $AUTH_TOKEN\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"file_path\": \"uploads/logos/20241201_123456_uuid.jpg\"}' \\"
echo "  \"$BASE_URL/files/upload/delete\""
echo ""

# 4. Serve File
echo "📥 4. Serve File"
echo "curl -X GET \\"
echo "  \"$BASE_URL/files/serve/logos/20241201_123456_uuid.jpg\""
echo ""

echo "======================================"
echo "📝 Instructions:"
echo "1. Remplacez 'your_auth_token_here' par votre vrai token"
echo "2. Remplacez '/path/to/your/file' par le vrai chemin de votre fichier"
echo "3. Remplacez '20241201_123456_uuid.jpg' par le vrai nom de fichier retourné par l'upload"
echo "4. Exécutez les commandes une par une"
echo ""

# Exemples avec des valeurs réelles
echo "🔧 Exemples d'utilisation:"
echo ""

echo "# Upload d'un logo"
echo "curl -X POST \\"
echo "  -H \"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\" \\"
echo "  -F \"file=@./logo.png\" \\"
echo "  \"http://localhost:8081/files/upload/logo\""
echo ""

echo "# Upload d'un fichier PDF"
echo "curl -X POST \\"
echo "  -H \"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\" \\"
echo "  -F \"file=@./document.pdf\" \\"
echo "  -F \"subfolder=files\" \\"
echo "  \"http://localhost:8081/files/upload\""
echo ""

echo "# Supprimer un fichier"
echo "curl -X POST \\"
echo "  -H \"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"file_path\": \"uploads/logos/20241201_143022_abc123.png\"}' \\"
echo "  \"http://localhost:8081/files/upload/delete\""
echo ""

echo "# Accéder à un fichier"
echo "curl -X GET \\"
echo "  \"http://localhost:8081/files/serve/logos/20241201_143022_abc123.png\""
echo "" 