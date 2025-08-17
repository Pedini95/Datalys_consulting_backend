-- Migration: Ajouter colonne FCM token pour notifications push
-- Date: 2025-01-17
-- Description: Permet de stocker les tokens Firebase Cloud Messaging des utilisateurs

-- Ajouter la colonne fcm_token à la table users
ALTER TABLE users 
ADD COLUMN fcm_token VARCHAR(255) NULL AFTER email;

-- Ajouter un index pour les recherches rapides
CREATE INDEX idx_users_fcm_token ON users (fcm_token);

-- Commentaire pour documenter la colonne
ALTER TABLE users 
MODIFY COLUMN fcm_token VARCHAR(255) NULL 
COMMENT 'Token Firebase Cloud Messaging pour notifications push'; 