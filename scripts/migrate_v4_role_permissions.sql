-- ============================================================
-- Migration v4 : Système de permissions par rôle
-- Date : 2026-07-30
-- ============================================================
-- Remplace les vérifications de rôle codées en dur (@require_role)
-- par un système de permissions en base : role_permissions.
-- Idempotent : peut être rejouée sans risque.
-- ============================================================

-- Catalogue des permissions
CREATE TABLE IF NOT EXISTS permissions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    `key`           VARCHAR(100) NOT NULL UNIQUE,
    label           VARCHAR(150) NOT NULL,
    description     VARCHAR(255) NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by      INT NULL,
    updated_at      DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      INT NULL,

    INDEX idx_permissions_key (`key`),
    INDEX idx_permissions_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Association rôle <-> permission
CREATE TABLE IF NOT EXISTS role_permissions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    role_id         INT NOT NULL,
    permission_id   INT NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by      INT NULL,

    UNIQUE KEY uq_role_permission (role_id, permission_id),
    INDEX idx_role_permissions_role_id (role_id),
    INDEX idx_role_permissions_permission_id (permission_id),
    CONSTRAINT fk_role_permissions_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_role_permissions_permission FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catalogue initial des permissions
INSERT INTO permissions (`key`, label, is_active, is_deleted) VALUES
    ('users.view', 'Voir la liste des utilisateurs', TRUE, FALSE),
    ('users.create', 'Créer des utilisateurs', TRUE, FALSE),
    ('users.update', 'Modifier des utilisateurs', TRUE, FALSE),
    ('users.delete', 'Supprimer des utilisateurs', TRUE, FALSE),
    ('roles.manage', 'Créer/modifier/supprimer des rôles', TRUE, FALSE),
    ('permissions.manage', 'Gérer les permissions projet/utilisateur', TRUE, FALSE),
    ('audit.view', 'Consulter le journal d''audit', TRUE, FALSE),
    ('incidents.delete', 'Supprimer des incidents', TRUE, FALSE),
    ('incidents.export', 'Exporter les incidents', TRUE, FALSE)
ON DUPLICATE KEY UPDATE label = VALUES(label);

-- Attribution de toutes les permissions au rôle Admin
-- (comportement équivalent à l'ancien @require_role('admin') / (['admin','manager'])
--  mais sans 'manager', qui n'est pas un rôle réellement utilisé)
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.`key` IN (
    'users.view', 'users.create', 'users.update', 'users.delete',
    'roles.manage', 'permissions.manage', 'audit.view',
    'incidents.delete', 'incidents.export'
)
WHERE r.name = 'Admin';
