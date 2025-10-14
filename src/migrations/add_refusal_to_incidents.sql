-- =====================================================
-- Migration: Ajouter les champs de refus de solution à la table incidents
-- Date: 2025-10-14
-- Description: Permet de tracker les refus de solution par les clients
-- =====================================================

USE datalys_consulting;

-- 1. Ajouter la colonne refusal_count (compteur de refus)
ALTER TABLE incidents
ADD COLUMN refusal_count INT DEFAULT 0 AFTER resolved_at;

-- 2. Ajouter la colonne refusal_reason (raison du dernier refus)
ALTER TABLE incidents
ADD COLUMN refusal_reason TEXT DEFAULT NULL AFTER refusal_count;

-- 3. Ajouter la colonne last_refusal_at (date du dernier refus)
ALTER TABLE incidents
ADD COLUMN last_refusal_at DATETIME DEFAULT NULL AFTER refusal_reason;

-- 4. Créer un index pour améliorer les performances de recherche sur les incidents refusés
CREATE INDEX idx_incidents_refusal_count ON incidents(refusal_count);

-- 5. Vérification
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_KEY
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'datalys_consulting'
  AND TABLE_NAME = 'incidents'
  AND COLUMN_NAME IN ('refusal_count', 'refusal_reason', 'last_refusal_at')
ORDER BY ORDINAL_POSITION;

-- 6. Statistiques après migration
SELECT
    COUNT(*) as total_incidents,
    COUNT(CASE WHEN refusal_count > 0 THEN 1 END) as incidents_with_refusals,
    MAX(refusal_count) as max_refusals
FROM incidents
WHERE is_deleted = FALSE;

-- =====================================================
-- ROLLBACK (si nécessaire)
-- =====================================================
-- ALTER TABLE incidents DROP INDEX idx_incidents_refusal_count;
-- ALTER TABLE incidents DROP COLUMN last_refusal_at;
-- ALTER TABLE incidents DROP COLUMN refusal_reason;
-- ALTER TABLE incidents DROP COLUMN refusal_count;
-- =====================================================
