-- Migration: Ajouter le champ is_temp_password à la table users
-- Date: 2025-08-17
-- Description: Permet de gérer les mots de passe temporaires pour les nouveaux partenaires

-- Ajouter la colonne is_temp_password
ALTER TABLE users ADD COLUMN is_temp_password BOOLEAN DEFAULT FALSE;

-- Mettre à jour tous les utilisateurs existants pour qu'ils n'aient pas de mot de passe temporaire
UPDATE users SET is_temp_password = FALSE WHERE is_temp_password IS NULL;

-- Commentaire pour documentation
ALTER TABLE users MODIFY COLUMN is_temp_password BOOLEAN DEFAULT FALSE COMMENT 'Indique si l utilisateur a un mot de passe temporaire qui doit être changé à la première connexion'; 