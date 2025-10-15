-- Migration: Ajouter les colonnes de refus de solution à la table incidents
-- Date: 2025-10-15
-- Description: Ajout de refusal_count, refusal_reason, last_refusal_at

-- 1. Ajouter la colonne refusal_count si elle n'existe pas
SET @refusal_count_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'incidents'
    AND COLUMN_NAME = 'refusal_count'
);

SET @sql_refusal_count = IF(@refusal_count_exists = 0,
    'ALTER TABLE incidents ADD COLUMN refusal_count INT DEFAULT 0 AFTER resolved_at',
    'SELECT "La colonne refusal_count existe déjà" AS message'
);

PREPARE stmt_refusal_count FROM @sql_refusal_count;
EXECUTE stmt_refusal_count;
DEALLOCATE PREPARE stmt_refusal_count;

-- 2. Ajouter la colonne refusal_reason si elle n'existe pas
SET @refusal_reason_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'incidents'
    AND COLUMN_NAME = 'refusal_reason'
);

SET @sql_refusal_reason = IF(@refusal_reason_exists = 0,
    'ALTER TABLE incidents ADD COLUMN refusal_reason TEXT NULL AFTER refusal_count',
    'SELECT "La colonne refusal_reason existe déjà" AS message'
);

PREPARE stmt_refusal_reason FROM @sql_refusal_reason;
EXECUTE stmt_refusal_reason;
DEALLOCATE PREPARE stmt_refusal_reason;

-- 3. Ajouter la colonne last_refusal_at si elle n'existe pas
SET @last_refusal_at_exists = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'incidents'
    AND COLUMN_NAME = 'last_refusal_at'
);

SET @sql_last_refusal_at = IF(@last_refusal_at_exists = 0,
    'ALTER TABLE incidents ADD COLUMN last_refusal_at DATETIME NULL AFTER refusal_reason',
    'SELECT "La colonne last_refusal_at existe déjà" AS message'
);

PREPARE stmt_last_refusal_at FROM @sql_last_refusal_at;
EXECUTE stmt_last_refusal_at;
DEALLOCATE PREPARE stmt_last_refusal_at;

-- Afficher un message de confirmation
SELECT 'Migration 003 terminée avec succès! Les colonnes de refus ont été ajoutées à la table incidents.' AS status;
