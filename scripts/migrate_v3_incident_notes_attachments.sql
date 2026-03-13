-- ============================================================
-- Migration v3 : Notes de résolution + Pièces jointes incidents
-- Date : 2026-03-13
-- ============================================================

-- Table des notes de résolution horodatées
CREATE TABLE IF NOT EXISTS incident_notes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    incident_id     INT NOT NULL,
    content         TEXT NOT NULL,
    is_deleted      TINYINT(1) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by      INT NULL,
    updated_at      DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      INT NULL,

    CONSTRAINT fk_inote_incident FOREIGN KEY (incident_id) REFERENCES incidents(id),
    CONSTRAINT fk_inote_created_by FOREIGN KEY (created_by) REFERENCES users(id),

    INDEX idx_inote_incident (incident_id),
    INDEX idx_inote_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table des pièces jointes liées aux notes
CREATE TABLE IF NOT EXISTS incident_attachments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    note_id         INT NOT NULL,
    incident_id     INT NOT NULL,
    file_name       VARCHAR(255) NOT NULL,
    file_url        VARCHAR(500) NOT NULL,
    file_type       VARCHAR(100) NULL,
    file_size       INT NULL,
    is_deleted      TINYINT(1) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by      INT NULL,

    CONSTRAINT fk_iattach_note FOREIGN KEY (note_id) REFERENCES incident_notes(id) ON DELETE CASCADE,
    CONSTRAINT fk_iattach_incident FOREIGN KEY (incident_id) REFERENCES incidents(id),
    CONSTRAINT fk_iattach_created_by FOREIGN KEY (created_by) REFERENCES users(id),

    INDEX idx_iattach_note (note_id),
    INDEX idx_iattach_incident (incident_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
