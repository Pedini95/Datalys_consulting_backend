-- ============================================================
-- Migration: Ajout des champs MFA (Multi-Factor Authentication)
-- Date: 2025-10-09
-- Description: Ajoute les champs nécessaires pour l'authentification multi-facteurs
-- ============================================================

USE datalys_consulting;

-- Ajouter les colonnes MFA à la table users
ALTER TABLE users 
ADD COLUMN mfa_enabled TINYINT(1) DEFAULT 1 COMMENT 'MFA activé (1) ou désactivé (0)',
ADD COLUMN mfa_code VARCHAR(10) DEFAULT NULL COMMENT 'Code MFA temporaire (6 chiffres)',
ADD COLUMN mfa_code_expiry DATETIME DEFAULT NULL COMMENT 'Date d\'expiration du code MFA (5 minutes)',
ADD COLUMN mfa_code_attempts INT DEFAULT 0 COMMENT 'Nombre de tentatives échouées de saisie du code MFA';

-- Ajouter un index sur mfa_code pour optimiser les recherches
CREATE INDEX idx_users_mfa_code ON users(mfa_code);

-- Ajouter un index sur mfa_code_expiry pour optimiser les requêtes de nettoyage
CREATE INDEX idx_users_mfa_expiry ON users(mfa_code_expiry);

-- ============================================================
-- Vérification
-- ============================================================
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE, 
    COLUMN_DEFAULT, 
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'datalys_consulting'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME IN ('mfa_enabled', 'mfa_code', 'mfa_code_expiry', 'mfa_code_attempts');

-- ============================================================
-- Notes
-- ============================================================
-- 1. mfa_enabled = 1 par défaut (MFA activé pour tous les utilisateurs)
-- 2. mfa_code = Code temporaire à 6 chiffres généré lors du login
-- 3. mfa_code_expiry = Date d'expiration (5 minutes après génération)
-- 4. mfa_code_attempts = Compteur de tentatives (max 3)
-- 
-- Workflow MFA:
-- 1. Login avec email/password → génère mfa_code + mfa_code_expiry
-- 2. Email envoyé avec le code
-- 3. Utilisateur entre le code
-- 4. Vérification du code → génère token JWT
-- 5. Nettoyage: mfa_code = NULL, mfa_code_expiry = NULL, mfa_code_attempts = 0
-- ============================================================

