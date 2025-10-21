-- Migration: Ajouter la colonne path à la table folders
-- Date: 2025-10-21
-- Description: Cette migration ajoute la colonne path pour stocker le chemin physique des répertoires

-- Ajouter la colonne path à la table folders
ALTER TABLE folders
ADD COLUMN path VARCHAR(500) DEFAULT NULL AFTER parent_folder_id;

-- Commentaire pour documenter la colonne
ALTER TABLE folders
MODIFY COLUMN path VARCHAR(500) DEFAULT NULL COMMENT 'Chemin physique du répertoire';
