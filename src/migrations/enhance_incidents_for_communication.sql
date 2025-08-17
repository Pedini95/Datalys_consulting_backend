-- Migration: Améliorer la table incidents pour la communication
-- Date: 2025-08-17
-- Description: Ajouter champs pour messages, support et notifications

-- Ajouter les nouveaux champs à la table incidents
ALTER TABLE incidents 
ADD COLUMN type VARCHAR(50) DEFAULT 'incident' AFTER description,
ADD COLUMN priority VARCHAR(20) DEFAULT 'moyenne' AFTER type,
ADD COLUMN status VARCHAR(20) DEFAULT 'ouvert' AFTER priority,
ADD COLUMN category VARCHAR(50) NULL AFTER status,
ADD COLUMN assigned_to INT NULL AFTER project_id,
ADD COLUMN parent_id INT NULL AFTER assigned_to,
ADD COLUMN resolution_notes TEXT NULL AFTER parent_id,
ADD COLUMN is_read BOOLEAN DEFAULT FALSE AFTER resolution_notes,
ADD COLUMN read_at DATETIME NULL AFTER is_read;

-- Ajouter les contraintes de clés étrangères
ALTER TABLE incidents 
ADD CONSTRAINT fk_incidents_assigned_to 
FOREIGN KEY (assigned_to) REFERENCES users(id);

ALTER TABLE incidents 
ADD CONSTRAINT fk_incidents_parent_id 
FOREIGN KEY (parent_id) REFERENCES incidents(id);

-- Ajouter des index pour améliorer les performances
CREATE INDEX idx_incidents_type ON incidents (type);
CREATE INDEX idx_incidents_status ON incidents (status);
CREATE INDEX idx_incidents_priority ON incidents (priority);
CREATE INDEX idx_incidents_assigned_to ON incidents (assigned_to);
CREATE INDEX idx_incidents_parent_id ON incidents (parent_id);
CREATE INDEX idx_incidents_is_read ON incidents (is_read);
CREATE INDEX idx_incidents_user_project ON incidents (user_id, project_id);

-- Mettre à jour les incidents existants avec les nouvelles valeurs par défaut
UPDATE incidents 
SET 
    type = 'incident',
    priority = 'moyenne', 
    status = 'ouvert',
    category = 'technique',
    is_read = FALSE
WHERE type IS NULL; 