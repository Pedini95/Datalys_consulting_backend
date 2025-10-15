-- Migration: Ajouter les colonnes phone et country_code à la table partners
-- Date: 2025-10-15
-- Description: Ajout des colonnes manquantes pour la gestion des numéros de téléphone des partenaires

-- Vérifier si les colonnes existent déjà avant de les ajouter
-- Cela permet d'exécuter le script de manière idempotente

-- 1. Ajouter la colonne phone si elle n'existe pas
SET @phone_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'phone'
);

SET @sql_phone = IF(@phone_exists = 0,
    'ALTER TABLE partners ADD COLUMN phone VARCHAR(50) NULL AFTER email',
    'SELECT "La colonne phone existe déjà" AS message'
);

PREPARE stmt_phone FROM @sql_phone;
EXECUTE stmt_phone;
DEALLOCATE PREPARE stmt_phone;

-- 2. Ajouter la colonne country_code si elle n'existe pas
SET @country_code_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'country_code'
);

SET @sql_country_code = IF(@country_code_exists = 0,
    'ALTER TABLE partners ADD COLUMN country_code VARCHAR(10) NULL DEFAULT "+237" AFTER phone',
    'SELECT "La colonne country_code existe déjà" AS message'
);

PREPARE stmt_country_code FROM @sql_country_code;
EXECUTE stmt_country_code;
DEALLOCATE PREPARE stmt_country_code;

-- 3. Créer les index si les colonnes ont été ajoutées
SET @idx_phone_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND INDEX_NAME = 'idx_partners_phone'
);

SET @sql_idx_phone = IF(@idx_phone_exists = 0,
    'CREATE INDEX idx_partners_phone ON partners(phone)',
    'SELECT "L\'index idx_partners_phone existe déjà" AS message'
);

PREPARE stmt_idx_phone FROM @sql_idx_phone;
EXECUTE stmt_idx_phone;
DEALLOCATE PREPARE stmt_idx_phone;

-- 4. Créer l'index composite pour phone et country_code
SET @idx_phone_country_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND INDEX_NAME = 'idx_partner_phone_country'
);

SET @sql_idx_phone_country = IF(@idx_phone_country_exists = 0,
    'CREATE INDEX idx_partner_phone_country ON partners(phone, country_code)',
    'SELECT "L\'index idx_partner_phone_country existe déjà" AS message'
);

PREPARE stmt_idx_phone_country FROM @sql_idx_phone_country;
EXECUTE stmt_idx_phone_country;
DEALLOCATE PREPARE stmt_idx_phone_country;

-- Afficher un message de confirmation
SELECT 'Migration terminée avec succès! Les colonnes phone et country_code ont été ajoutées à la table partners.' AS status;
