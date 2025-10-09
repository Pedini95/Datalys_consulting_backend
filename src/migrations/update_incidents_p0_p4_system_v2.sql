-- ============================================================
-- Migration : Système de criticité P0-P4 pour les incidents
-- Date : 2025-10-09
-- Description : Mise à jour du modèle Incident selon cahier des charges
-- Version : 2 (compatible MySQL 8.0)
-- ============================================================

-- 1. Ajouter les nouveaux champs (sans IF NOT EXISTS)
ALTER TABLE incidents ADD COLUMN impact VARCHAR(50) DEFAULT NULL COMMENT 'Impact: arret_service, service_degrade, majeur, mineur';
ALTER TABLE incidents ADD COLUMN domain VARCHAR(50) DEFAULT NULL COMMENT 'Domaine: reseau, infrastructure, cloud, energie';
ALTER TABLE incidents ADD COLUMN declarant_name VARCHAR(255) DEFAULT NULL COMMENT 'Nom du déclarant';
ALTER TABLE incidents ADD COLUMN motif_attente TEXT DEFAULT NULL COMMENT 'Motif de mise en attente';

-- 2. Sauvegarder les anciennes valeurs de priorité
ALTER TABLE incidents ADD COLUMN priority_old VARCHAR(20);
UPDATE incidents SET priority_old = priority WHERE priority_old IS NULL;

-- 3. Mapper les anciennes priorités vers P0-P4
UPDATE incidents 
SET priority = CASE 
    WHEN priority = 'critique' THEN 'P0'
    WHEN priority = 'haute' THEN 'P1'
    WHEN priority = 'moyenne' THEN 'P2'
    WHEN priority = 'basse' THEN 'P3'
    ELSE 'P3'
END
WHERE priority IN ('critique', 'haute', 'moyenne', 'basse');

-- 4. Mapper les anciens statuts vers les nouveaux
UPDATE incidents 
SET status = CASE 
    WHEN status = 'ouvert' THEN 'nouveau'
    WHEN status = 'en_cours' THEN 'en_cours'
    WHEN status = 'resolu' THEN 'resolu'
    WHEN status = 'ferme' THEN 'ferme'
    ELSE 'nouveau'
END
WHERE status IN ('ouvert', 'en_cours', 'resolu', 'ferme');

-- 5. Modifier les colonnes pour définir les nouvelles valeurs par défaut
ALTER TABLE incidents MODIFY COLUMN priority VARCHAR(20) DEFAULT 'P3' COMMENT 'Priorité: P0, P1, P2, P3, P4';
ALTER TABLE incidents MODIFY COLUMN status VARCHAR(20) DEFAULT 'nouveau' COMMENT 'Statut: nouveau, en_cours, en_attente, en_arbitrage, resolu, ferme';

-- 6. Créer des index pour améliorer les performances
CREATE INDEX idx_incidents_priority ON incidents(priority);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_impact ON incidents(impact);
CREATE INDEX idx_incidents_domain ON incidents(domain);
CREATE INDEX idx_incidents_declarant ON incidents(declarant_name);

-- ============================================================
-- Vérifications post-migration
-- ============================================================

-- Vérifier la structure de la table
DESCRIBE incidents;

-- Vérifier le nombre d'incidents par priorité
SELECT priority, COUNT(*) as count 
FROM incidents 
WHERE is_deleted = FALSE 
GROUP BY priority;

-- Vérifier le nombre d'incidents par statut
SELECT status, COUNT(*) as count 
FROM incidents 
WHERE is_deleted = FALSE 
GROUP BY status;

-- ============================================================
-- Fin de la migration
-- ============================================================

