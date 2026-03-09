-- ========================================
-- MIGRATION v2 : Clôture projet + Historique incidents + Motif attente
-- ========================================

-- 1. Ajout des colonnes de clôture/réouverture sur la table projects
-- -----------------------------------------------------------------------
DROP PROCEDURE IF EXISTS migrate_v2;
DELIMITER $$

CREATE PROCEDURE migrate_v2()
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'projects' AND COLUMN_NAME = 'closed_at') THEN
        ALTER TABLE projects ADD COLUMN closed_at DATETIME NULL AFTER updated_by;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'projects' AND COLUMN_NAME = 'closed_by') THEN
        ALTER TABLE projects ADD COLUMN closed_by INT NULL AFTER closed_at;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'projects' AND COLUMN_NAME = 'closure_reason') THEN
        ALTER TABLE projects ADD COLUMN closure_reason TEXT NULL AFTER closed_by;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'projects' AND COLUMN_NAME = 'reopened_at') THEN
        ALTER TABLE projects ADD COLUMN reopened_at DATETIME NULL AFTER closure_reason;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'projects' AND COLUMN_NAME = 'reopened_by') THEN
        ALTER TABLE projects ADD COLUMN reopened_by INT NULL AFTER reopened_at;
    END IF;
END$$

DELIMITER ;
CALL migrate_v2();
DROP PROCEDURE IF EXISTS migrate_v2;

-- 2. Création de la table incident_history
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incident_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_id INT NOT NULL,
    user_id INT NULL,
    old_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,
    action_type VARCHAR(50) NOT NULL DEFAULT 'status_change',
    comment TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,

    INDEX idx_ih_incident_id (incident_id),
    INDEX idx_ih_created_at (created_at),

    CONSTRAINT fk_ih_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ih_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- FIN DE LA MIGRATION
-- ========================================