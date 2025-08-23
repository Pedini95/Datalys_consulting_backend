-- Migration: Ajouter le champ country_code à la table partners
-- Date: 2025-08-20

-- Ajouter la colonne country_code
ALTER TABLE partners ADD COLUMN country_code VARCHAR(10) DEFAULT '+237';

-- Créer un index composite pour optimiser les recherches par téléphone et pays
CREATE INDEX idx_partner_phone_country ON partners(phone, country_code);

-- Mettre à jour les numéros existants pour extraire le code pays si possible
-- (Cette partie peut être exécutée manuellement si nécessaire)

-- Exemple de mise à jour pour les numéros camerounais existants
-- UPDATE partners 
-- SET phone = SUBSTRING(phone, 5), 
--     country_code = '+237' 
-- WHERE phone LIKE '+237%' AND country_code = '+237';

-- Exemple de mise à jour pour les numéros français existants  
-- UPDATE partners 
-- SET phone = SUBSTRING(phone, 4), 
--     country_code = '+33' 
-- WHERE phone LIKE '+33%' AND country_code = '+237';
