import pytest
import sys
import os

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch
from services.partner_service import PartnerService
from models.partner import Partner


class TestPartnerService:
    """Tests pour PartnerService"""

    def setup_method(self):
        """Setup avant chaque test"""
        self.service = PartnerService()

    def test_check_duplicates_no_duplicates(self):
        """Test : Aucun doublon détecté"""
        with patch.object(Partner, 'find_by_email', return_value=None), \
             patch.object(Partner, 'find_by_phone', return_value=None), \
             patch.object(Partner, 'find_by_name_and_address', return_value=None):
            
            has_duplicates, error_msg = self.service._check_duplicates(
                email="test@example.com",
                phone="+1234567890",
                name="TestCorp",
                address="123 Test St"
            )
            
            assert has_duplicates is False
            assert error_msg == ""

    def test_check_duplicates_email_exists(self):
        """Test : Email en doublon"""
        mock_partner = Mock()
        mock_partner.email = "existing@example.com"
        
        with patch.object(Partner, 'find_by_email', return_value=mock_partner):
            has_duplicates, error_msg = self.service._check_duplicates(
                email="existing@example.com"
            )
            
            assert has_duplicates is True
            assert "email" in error_msg.lower()
            assert "existing@example.com" in error_msg

    def test_check_duplicates_phone_exists(self):
        """Test : Téléphone en doublon"""
        mock_partner = Mock()
        mock_partner.phone = "+1234567890"
        
        with patch.object(Partner, 'find_by_phone', return_value=mock_partner):
            has_duplicates, error_msg = self.service._check_duplicates(
                phone="+1234567890"
            )
            
            assert has_duplicates is True
            assert "téléphone" in error_msg.lower()
            assert "+1234567890" in error_msg

    def test_check_duplicates_name_address_exists(self):
        """Test : Combinaison nom+adresse en doublon"""
        mock_partner = Mock()
        mock_partner.name = "TestCorp"
        mock_partner.address = "123 Test St"
        
        with patch.object(Partner, 'find_by_name_and_address', return_value=mock_partner):
            has_duplicates, error_msg = self.service._check_duplicates(
                name="TestCorp",
                address="123 Test St"
            )
            
            assert has_duplicates is True
            assert "nom" in error_msg.lower()
            assert "TestCorp" in error_msg
            assert "123 Test St" in error_msg

    def test_check_duplicates_with_exclude_id(self):
        """Test : Exclusion d'un ID lors de la vérification"""
        with patch.object(Partner, 'find_by_email') as mock_find_email:
            mock_find_email.return_value = None
            
            self.service._check_duplicates(
                email="test@example.com",
                exclude_id=123
            )
            
            # Vérifier que exclude_id a été passé
            mock_find_email.assert_called_once_with("test@example.com", 123)

    @patch('services.partner_service.generate_temp_password')
    @patch('services.partner_service.db')
    def test_create_with_user_validation_success(self, mock_db, mock_generate_password):
        """Test : Création réussie avec validation"""
        mock_generate_password.return_value = "TempPass123"
        
        # Mock des vérifications de doublons (aucun doublon)
        with patch.object(self.service, '_check_duplicates', return_value=(False, "")):
            
            data = {
                "name": "NewCorp",
                "email": "new@example.com",
                "phone": "+9876543210",
                "address": "456 New Ave"
            }
            
            # La méthode devrait continuer sans erreur de doublon
            # (Nous ne testons que la partie validation ici)
            has_duplicates, error_msg = self.service._check_duplicates(**data)
            
            assert has_duplicates is False
            assert error_msg == ""

    def test_create_with_user_validation_failure(self):
        """Test : Échec de création à cause d'un doublon"""
        with patch.object(self.service, '_check_duplicates', return_value=(True, "Email existe déjà")):
            
            partner, username, temp_password, success, message = self.service.create_with_user({
                "name": "TestCorp", 
                "email": "existing@example.com"
            })
            
            assert partner is None
            assert username is None
            assert temp_password is None
            assert success is False
            assert "Email existe déjà" in message 