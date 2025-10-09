-- ============================================================================
-- Migration: Ajout du code client unique pour les utilisateurs
-- Date: 2025-10-09
-- Description: Ajoute le champ client_code pour permettre le login sans email
--              Format: DATALYS-2025-001, DATALYS-2025-002, etc.
-- ============================================================================

-- 1. Ajouter la colonne client_code
ALTER TABLE users
ADD COLUMN client_code VARCHAR(50) DEFAULT NULL COMMENT 'Code client unique pour login (ex: DATALYS-2025-001)';

-- 2. Créer un index unique sur client_code
CREATE UNIQUE INDEX idx_users_client_code ON users(client_code);

-- 3. Générer des codes clients pour les utilisateurs existants
-- Note: Cette partie doit être exécutée avec prudence en production
-- Elle génère des codes au format DATALYS-2025-XXX pour tous les utilisateurs existants

SET @counter = 0;
SET @current_year = YEAR(NOW());

UPDATE users
SET client_code = CONCAT('DATALYS-', @current_year, '-', LPAD((@counter := @counter + 1), 3, '0'))
WHERE client_code IS NULL AND is_deleted = FALSE
ORDER BY id ASC;

-- 4. Vérifier les résultats
SELECT 
    id,
    name,
    email,
    client_code,
    created_at
FROM users
WHERE is_deleted = FALSE
ORDER BY id ASC;

-- ============================================================================
-- NOTES D'UTILISATION
-- ============================================================================
-- 
-- 1. LOGIN AVEC CODE CLIENT :
--    - Les utilisateurs peuvent maintenant se connecter avec :
--      * Leur email : user@example.com
--      * Leur code client : DATALYS-2025-001
-- 
-- 2. GÉNÉRATION AUTOMATIQUE :
--    - Chaque nouvel utilisateur reçoit automatiquement un code client unique
--    - Format : DATALYS-YYYY-NNN (année + numéro séquentiel sur 3 chiffres)
-- 
-- 3. AVANTAGES :
--    - Évite les problèmes de changement d'email
--    - Facilite la mobilité des clients entre entreprises
--    - Code permanent et mémorisable
-- 
-- 4. EXEMPLE D'UTILISATION API :
--    POST /auth/login
--    {
--      "identifier": "DATALYS-2025-001",  // ou "user@example.com"
--      "password": "MotDePasse123"
--    }
-- 
-- ============================================================================

