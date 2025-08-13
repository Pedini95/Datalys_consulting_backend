-- Migration pour ajouter les colonnes email, phone, address à la table partners
-- Exécutez ce script dans votre base de données MySQL

USE datalys_consulting;

-- Ajouter les nouvelles colonnes
ALTER TABLE partners 
ADD COLUMN email VARCHAR(255) NULL AFTER name,
ADD COLUMN phone VARCHAR(50) NULL AFTER email,
ADD COLUMN address TEXT NULL AFTER phone;

-- Vérifier que les colonnes ont été ajoutées
DESCRIBE partners;

-- Afficher un exemple de données
SELECT id, name, email, phone, address, logo_url, is_active FROM partners LIMIT 5; 