-- Migration: Ajouter les colonnes manquantes restantes à la table partners
-- Date: 2025-10-15
-- Description: Ajout de address, logo_url, is_deleted, created_at, created_by, updated_at, updated_by

-- 1. Ajouter la colonne address si elle n'existe pas
SET @address_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'address'
);

SET @sql_address = IF(@address_exists = 0,
    'ALTER TABLE partners ADD COLUMN address TEXT NULL AFTER country_code',
    'SELECT "La colonne address existe déjà" AS message'
);

PREPARE stmt_address FROM @sql_address;
EXECUTE stmt_address;
DEALLOCATE PREPARE stmt_address;

-- 2. Ajouter la colonne logo_url si elle n'existe pas
SET @logo_url_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'logo_url'
);

SET @sql_logo_url = IF(@logo_url_exists = 0,
    'ALTER TABLE partners ADD COLUMN logo_url VARCHAR(255) NULL AFTER address',
    'SELECT "La colonne logo_url existe déjà" AS message'
);

PREPARE stmt_logo_url FROM @sql_logo_url;
EXECUTE stmt_logo_url;
DEALLOCATE PREPARE stmt_logo_url;

-- 3. Ajouter la colonne is_deleted si elle n'existe pas
SET @is_deleted_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'is_deleted'
);

SET @sql_is_deleted = IF(@is_deleted_exists = 0,
    'ALTER TABLE partners ADD COLUMN is_deleted TINYINT(1) DEFAULT 0 AFTER is_active',
    'SELECT "La colonne is_deleted existe déjà" AS message'
);

PREPARE stmt_is_deleted FROM @sql_is_deleted;
EXECUTE stmt_is_deleted;
DEALLOCATE PREPARE stmt_is_deleted;

-- 4. Ajouter la colonne created_at si elle n'existe pas
SET @created_at_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'created_at'
);

SET @sql_created_at = IF(@created_at_exists = 0,
    'ALTER TABLE partners ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER is_deleted',
    'SELECT "La colonne created_at existe déjà" AS message'
);

PREPARE stmt_created_at FROM @sql_created_at;
EXECUTE stmt_created_at;
DEALLOCATE PREPARE stmt_created_at;

-- 5. Ajouter la colonne created_by si elle n'existe pas
SET @created_by_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'created_by'
);

SET @sql_created_by = IF(@created_by_exists = 0,
    'ALTER TABLE partners ADD COLUMN created_by INT NULL AFTER created_at',
    'SELECT "La colonne created_by existe déjà" AS message'
);

PREPARE stmt_created_by FROM @sql_created_by;
EXECUTE stmt_created_by;
DEALLOCATE PREPARE stmt_created_by;

-- 6. Ajouter la colonne updated_at si elle n'existe pas
SET @updated_at_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'updated_at'
);

SET @sql_updated_at = IF(@updated_at_exists = 0,
    'ALTER TABLE partners ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_by',
    'SELECT "La colonne updated_at existe déjà" AS message'
);

PREPARE stmt_updated_at FROM @sql_updated_at;
EXECUTE stmt_updated_at;
DEALLOCATE PREPARE stmt_updated_at;

-- 7. Ajouter la colonne updated_by si elle n'existe pas
SET @updated_by_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND COLUMN_NAME = 'updated_by'
);

SET @sql_updated_by = IF(@updated_by_exists = 0,
    'ALTER TABLE partners ADD COLUMN updated_by INT NULL AFTER updated_at',
    'SELECT "La colonne updated_by existe déjà" AS message'
);

PREPARE stmt_updated_by FROM @sql_updated_by;
EXECUTE stmt_updated_by;
DEALLOCATE PREPARE stmt_updated_by;

-- 8. Créer l'index composite pour name et address (si pas déjà existant)
SET @idx_name_address_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND INDEX_NAME = 'idx_partner_name_address'
);

SET @sql_idx_name_address = IF(@idx_name_address_exists = 0,
    'CREATE INDEX idx_partner_name_address ON partners(name, address(255))',
    'SELECT "L\'index idx_partner_name_address existe déjà" AS message'
);

PREPARE stmt_idx_name_address FROM @sql_idx_name_address;
EXECUTE stmt_idx_name_address;
DEALLOCATE PREPARE stmt_idx_name_address;

-- 9. Créer l'index pour email (si pas déjà existant)
SET @idx_email_exists = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'partners'
    AND INDEX_NAME = 'idx_partners_email'
);

SET @sql_idx_email = IF(@idx_email_exists = 0,
    'CREATE INDEX idx_partners_email ON partners(email)',
    'SELECT "L\'index idx_partners_email existe déjà" AS message'
);

PREPARE stmt_idx_email FROM @sql_idx_email;
EXECUTE stmt_idx_email;
DEALLOCATE PREPARE stmt_idx_email;

-- Afficher un message de confirmation
SELECT 'Migration 002 terminée avec succès! Toutes les colonnes manquantes ont été ajoutées à la table partners.' AS status;
