-- ========================================
-- DATALYS CONSULTING - SCRIPT D'INITIALISATION BASE DE DONNÉES
-- ========================================
-- Généré le: 2026-02-01
-- Base: MySQL 8.0
-- ========================================

-- ========================================
-- 1. CRÉATION DE LA BASE ET UTILISATEUR
-- ========================================

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS datalys_consulting
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur avec mot de passe fort
CREATE USER IF NOT EXISTS 'datalys'@'%' IDENTIFIED BY 'jn9zAiwCZo7V5rpcVeugQKJaZR5cMpl';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON datalys_consulting.* TO 'datalys'@'%';
FLUSH PRIVILEGES;

-- Utiliser la base
USE datalys_consulting;

-- ========================================
-- 2. CRÉATION DES TABLES
-- ========================================

-- -----------------------------------------
-- Table: roles (pas de dépendances)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_roles_name (name),
    INDEX idx_roles_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: permissions (pas de dépendances)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(150) NOT NULL,
    description VARCHAR(255) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_permissions_key (`key`),
    INDEX idx_permissions_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: role_permissions (dépend de: roles, permissions)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,

    UNIQUE KEY uq_role_permission (role_id, permission_id),
    INDEX idx_role_permissions_role_id (role_id),
    INDEX idx_role_permissions_permission_id (permission_id),
    CONSTRAINT fk_role_permissions_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_role_permissions_permission FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: partners (pas de dépendances)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS partners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(50) NULL,
    country_code VARCHAR(10) DEFAULT '+237',
    address TEXT NULL,
    logo_url VARCHAR(255) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_partners_email (email),
    INDEX idx_partners_phone (phone),
    INDEX idx_partners_name_address (name, address(255)),
    INDEX idx_partners_phone_country (phone, country_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: users (dépend de: roles)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_temp_password BOOLEAN DEFAULT FALSE,
    fcm_token VARCHAR(255) NULL,
    client_code VARCHAR(50) NULL UNIQUE,

    -- Champs MFA
    mfa_enabled BOOLEAN DEFAULT TRUE,
    mfa_code VARCHAR(10) NULL,
    mfa_code_expiry DATETIME NULL,
    mfa_code_attempts INT DEFAULT 0,

    role_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(255) NULL,

    INDEX idx_users_email (email),
    INDEX idx_users_client_code (client_code),
    INDEX idx_users_role_id (role_id),

    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: projects (dépend de: partners)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    partner_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    -- Clôture manuelle
    closed_at DATETIME NULL,
    closed_by INT NULL,
    closure_reason TEXT NULL,
    reopened_at DATETIME NULL,
    reopened_by INT NULL,

    INDEX idx_projects_title (title),
    INDEX idx_projects_partner_id (partner_id),

    CONSTRAINT fk_projects_partner FOREIGN KEY (partner_id) REFERENCES partners(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: incidents (dépend de: users, projects)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_number VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    type VARCHAR(50) DEFAULT 'incident',
    priority VARCHAR(20) DEFAULT 'P3',
    impact VARCHAR(50) NULL,
    domain VARCHAR(50) NULL,
    declarant_name VARCHAR(255) NULL,
    status VARCHAR(20) DEFAULT 'nouveau',
    motif_attente TEXT NULL,
    category VARCHAR(50) NULL,

    -- Relations
    user_id INT NULL,
    project_id INT NULL,
    assigned_to INT NULL,
    parent_id INT NULL,

    -- Communication
    resolution_notes TEXT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME NULL,

    -- Résolution
    resolved_by INT NULL,
    resolved_at DATETIME NULL,

    -- Refus de solution
    refusal_count INT DEFAULT 0,
    refusal_reason TEXT NULL,
    last_refusal_at DATETIME NULL,

    -- SLA
    taken_at DATETIME NULL,
    sla_prise_en_charge_deadline DATETIME NULL,
    sla_resolution_deadline DATETIME NULL,
    sla_prise_en_charge_status VARCHAR(20) DEFAULT 'respecte',
    sla_resolution_status VARCHAR(20) DEFAULT 'respecte',

    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_incidents_number (incident_number),
    INDEX idx_incidents_status (status),
    INDEX idx_incidents_priority (priority),
    INDEX idx_incidents_user_id (user_id),
    INDEX idx_incidents_project_id (project_id),
    INDEX idx_incidents_assigned_to (assigned_to),
    INDEX idx_incidents_parent_id (parent_id),

    CONSTRAINT fk_incidents_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_incidents_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_incidents_assigned FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_incidents_parent FOREIGN KEY (parent_id) REFERENCES incidents(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_incidents_resolver FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: folders (dépend de: projects, self-reference)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    project_id INT NULL,
    parent_folder_id INT NULL,
    path VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_folders_name (name),
    INDEX idx_folders_project_id (project_id),
    INDEX idx_folders_parent_id (parent_folder_id),

    CONSTRAINT fk_folders_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_folders_parent FOREIGN KEY (parent_folder_id) REFERENCES folders(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: files (dépend de: folders, incidents)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    folder_id INT NULL,
    incident_id INT NULL,
    file_url VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_files_name (name),
    INDEX idx_files_folder_id (folder_id),
    INDEX idx_files_incident_id (incident_id),

    CONSTRAINT fk_files_folder FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_files_incident FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: user_project_permissions (dépend de: users, projects, roles)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS user_project_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    role_id INT NULL,
    can_read BOOLEAN DEFAULT TRUE,
    can_write BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,

    INDEX idx_upp_user_id (user_id),
    INDEX idx_upp_project_id (project_id),
    INDEX idx_upp_role_id (role_id),
    UNIQUE INDEX idx_upp_user_project (user_id, project_id),

    CONSTRAINT fk_upp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_upp_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_upp_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: action_history (dépend de: users)
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS action_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NULL,
    description TEXT NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_ah_user_id (user_id),
    INDEX idx_ah_action_type (action_type),
    INDEX idx_ah_entity_type (entity_type),
    INDEX idx_ah_created_at (created_at),

    CONSTRAINT fk_ah_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------
-- Table: incident_history (dépend de: incidents, users)
-- -----------------------------------------
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
-- 3. DONNÉES INITIALES
-- ========================================

-- -----------------------------------------
-- Rôles par défaut
-- -----------------------------------------
INSERT INTO roles (name, is_active, is_deleted) VALUES
    ('Admin', TRUE, FALSE),
    ('Manager', TRUE, FALSE),
    ('User', TRUE, FALSE)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- -----------------------------------------
-- Catalogue des permissions
-- -----------------------------------------
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

-- -----------------------------------------
-- Attribution de toutes les permissions au rôle Admin
-- -----------------------------------------
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.`key` IN (
    'users.view', 'users.create', 'users.update', 'users.delete',
    'roles.manage', 'permissions.manage', 'audit.view',
    'incidents.delete', 'incidents.export'
)
WHERE r.name = 'Admin';

-- -----------------------------------------
-- Utilisateur administrateur par défaut
-- -----------------------------------------
-- Mot de passe: Admin@123 (hashé avec bcrypt)
-- IMPORTANT: Changez ce mot de passe après la première connexion !
INSERT INTO users (name, email, password_hash, role_id, is_active, is_deleted, is_temp_password, client_code)
SELECT
    'Administrateur',
    'admin@datalys.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.3KPOvZJHJbzJXe',  -- Admin@123 en bcrypt
    (SELECT id FROM roles WHERE name = 'Admin' LIMIT 1),
    TRUE,
    FALSE,
    TRUE,
    'DTLSADMIN1'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'admin@datalys.com'
);

-- ========================================
-- 4. VÉRIFICATION
-- ========================================

-- Afficher les tables créées
SELECT TABLE_NAME, TABLE_ROWS, ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'datalys_consulting'
ORDER BY TABLE_NAME;

-- Afficher les rôles
SELECT * FROM roles;

-- Afficher l'utilisateur admin
SELECT id, name, email, role_id, is_active, is_temp_password FROM users;

-- ========================================
-- FIN DU SCRIPT
-- ========================================
--
-- INSTRUCTIONS D'EXÉCUTION SUR LE SERVEUR:
--
-- 1. Connectez-vous au serveur:
--    ssh root@152.228.130.133
--
-- 2. Connectez-vous à MySQL:
--    docker exec -it mysql-db mysql -u root -p
--
-- 3. Exécutez ce script:
--    source /path/to/init_database.sql
--
-- OU en une seule commande:
--    docker exec -i mysql-db mysql -u root -pVOTRE_ROOT_PASSWORD < init_database.sql
--
-- ========================================
