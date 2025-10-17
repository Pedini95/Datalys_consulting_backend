-- Migration: Ajouter la colonne is_active à la table projects
-- Date: 2025-10-17

ALTER TABLE projects
ADD COLUMN is_active TINYINT(1) DEFAULT 1 AFTER partner_id;

-- Mettre à jour les projets existants pour qu'ils soient actifs par défaut
UPDATE projects SET is_active = 1 WHERE is_active IS NULL;
