-- =====================================================
-- Migration: Ajouter incident_id à la table files
-- Date: 2025-10-14
-- Description: Permet d'associer des fichiers aux incidents
-- =====================================================

USE datalys_consulting;

-- 1. Ajouter la colonne incident_id
ALTER TABLE files
ADD COLUMN incident_id INT DEFAULT NULL AFTER folder_id;

-- 2. Ajouter la contrainte de clé étrangère
ALTER TABLE files
ADD CONSTRAINT fk_files_incident
FOREIGN KEY (incident_id) REFERENCES incidents(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- 3. Créer un index pour améliorer les performances de recherche
CREATE INDEX idx_files_incident_id ON files(incident_id);

-- 4. Vérification
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_KEY
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'datalys_consulting'
  AND TABLE_NAME = 'files'
  AND COLUMN_NAME = 'incident_id';

-- =====================================================
-- ROLLBACK (si nécessaire)
-- =====================================================
-- ALTER TABLE files DROP FOREIGN KEY fk_files_incident;
-- ALTER TABLE files DROP INDEX idx_files_incident_id;
-- ALTER TABLE files DROP COLUMN incident_id;
-- =====================================================
