-- ============================================================
-- Migration : Ajout des champs SLA aux incidents
-- Date : 2025-10-12
-- Description : Ajout des champs pour gérer les SLA (délais de prise en charge et de résolution)
-- ============================================================

-- Ajouter les champs SLA
ALTER TABLE incidents ADD COLUMN taken_at DATETIME DEFAULT NULL COMMENT 'Date de prise en charge';
ALTER TABLE incidents ADD COLUMN sla_prise_en_charge_deadline DATETIME DEFAULT NULL COMMENT 'Deadline prise en charge';
ALTER TABLE incidents ADD COLUMN sla_resolution_deadline DATETIME DEFAULT NULL COMMENT 'Deadline résolution';
ALTER TABLE incidents ADD COLUMN sla_prise_en_charge_status VARCHAR(20) DEFAULT 'respecte' COMMENT 'Statut SLA prise en charge: respecte ou depasse';
ALTER TABLE incidents ADD COLUMN sla_resolution_status VARCHAR(20) DEFAULT 'respecte' COMMENT 'Statut SLA résolution: respecte ou depasse';

-- Créer des index pour optimiser les requêtes SLA
CREATE INDEX idx_incidents_sla_prise_en_charge ON incidents(sla_prise_en_charge_status, sla_prise_en_charge_deadline);
CREATE INDEX idx_incidents_sla_resolution ON incidents(sla_resolution_status, sla_resolution_deadline);
CREATE INDEX idx_incidents_taken_at ON incidents(taken_at);

-- ============================================================
-- CONFIGURATION SLA PAR PRIORITÉ
-- ============================================================
/*
P1: Prise en charge: 30 minutes (24/7) | Résolution: 4 heures ouvrées
P2: Prise en charge: 1 heure ouvrée    | Résolution: 1 jour ouvré (8h)
P3: Prise en charge: 4 heures ouvrées  | Résolution: 3 jours ouvrés (24h)
P4: Prise en charge: 1 jour ouvré (8h) | Résolution: 5 jours ouvrés (40h)

Le frontend affichera:
- status='respecte' → Compteur VERT
- status='depasse' → Compteur ROUGE
*/

-- ============================================================
-- NOTES
-- ============================================================
/*
1. Les deadlines SLA sont calculées automatiquement lors de la création d'un incident
2. Le statut est mis à jour automatiquement lors de la récupération des incidents
3. Le frontend gère l'affichage des couleurs en fonction du statut
4. taken_at est mis à jour quand un expert prend en charge l'incident
5. resolved_at (déjà existant) est mis à jour quand l'incident est résolu
*/

