-- Migration: Add unique constraints to partner email and phone
-- Date: 2025-08-16
-- Description: Prevent duplicate partners with same email or phone

-- Ajouter contrainte d'unicité pour l'email (en ignorant les valeurs NULL)
ALTER TABLE partners ADD CONSTRAINT uk_partners_email 
UNIQUE (email);

-- Ajouter contrainte d'unicité pour le téléphone (en ignorant les valeurs NULL)  
ALTER TABLE partners ADD CONSTRAINT uk_partners_phone 
UNIQUE (phone);

-- Ajouter index pour améliorer les performances de recherche
CREATE INDEX idx_partners_name ON partners (name);
CREATE INDEX idx_partners_email ON partners (email);
CREATE INDEX idx_partners_phone ON partners (phone);
CREATE INDEX idx_partners_name_address ON partners (name, address);

-- Ajouter index pour les requêtes fréquentes
CREATE INDEX idx_partners_active ON partners (is_active, is_deleted); 