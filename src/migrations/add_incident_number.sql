-- ============================================================
-- Migration : Ajout du numéro d'incident auto-généré
-- Date : 2025-10-09
-- Description : Ajouter incident_number avec génération automatique
-- ============================================================

-- 1. Ajouter la colonne incident_number (temporairement nullable)
ALTER TABLE incidents ADD COLUMN incident_number VARCHAR(50) DEFAULT NULL;

-- 2. Générer les numéros pour les incidents existants
-- Format : INC-YYYY-NNNNN (ex: INC-2025-00001)

SET @row_number = 0;
SET @current_year = YEAR(NOW());

UPDATE incidents
SET incident_number = CONCAT('INC-', @current_year, '-', LPAD((@row_number := @row_number + 1), 5, '0'))
WHERE incident_number IS NULL
ORDER BY id ASC;

-- 3. Rendre la colonne NOT NULL et UNIQUE maintenant qu'elle est remplie
ALTER TABLE incidents MODIFY COLUMN incident_number VARCHAR(50) NOT NULL;
ALTER TABLE incidents ADD UNIQUE KEY uk_incident_number (incident_number);

-- 4. Créer un index pour améliorer les performances
CREATE INDEX idx_incident_number ON incidents(incident_number);

-- ============================================================
-- Vérifications post-migration
-- ============================================================

-- Vérifier que tous les incidents ont un numéro
SELECT COUNT(*) as total_incidents,
       COUNT(incident_number) as incidents_with_number,
       COUNT(*) - COUNT(incident_number) as incidents_without_number
FROM incidents
WHERE is_deleted = FALSE;

-- Afficher quelques exemples
SELECT id, incident_number, title, created_at
FROM incidents
WHERE is_deleted = FALSE
ORDER BY id ASC
LIMIT 10;

-- Vérifier l'unicité
SELECT incident_number, COUNT(*) as count
FROM incidents
GROUP BY incident_number
HAVING COUNT(*) > 1;

-- ============================================================
-- Rollback (en cas de problème)
-- ============================================================

-- Pour revenir en arrière (décommenter si nécessaire):
/*
DROP INDEX idx_incident_number ON incidents;
ALTER TABLE incidents DROP INDEX uk_incident_number;
ALTER TABLE incidents DROP COLUMN incident_number;
*/

-- ============================================================
-- Notes importantes
-- ============================================================

-- 1. Cette migration génère des numéros séquentiels pour l'année en cours
-- 2. Les nouveaux incidents auront des numéros générés automatiquement par le backend
-- 3. Le format est : INC-YYYY-NNNNN (ex: INC-2025-00001)
-- 4. La colonne est UNIQUE pour garantir qu'il n'y a pas de doublons
-- 5. Un index est créé pour améliorer les performances des recherches

-- ============================================================
-- Fin de la migration
-- ============================================================

