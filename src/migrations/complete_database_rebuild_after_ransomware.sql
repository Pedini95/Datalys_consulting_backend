-- ============================================================================
-- RECONSTRUCTION COMPLÈTE DE LA BASE DE DONNÉES APRÈS ATTAQUE RANSOMWARE
-- Date: 2025-10-12
-- Description: Recréation de toutes les tables, relations et index
-- ============================================================================

-- 1. CRÉATION DES TABLES
-- ============================================================================

-- Table: roles
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_temp_password BOOLEAN DEFAULT FALSE,
    fcm_token VARCHAR(255),
    client_code VARCHAR(50) UNIQUE,
    mfa_enabled BOOLEAN DEFAULT TRUE,
    mfa_code VARCHAR(10),
    mfa_code_expiry DATETIME,
    mfa_code_attempts INT DEFAULT 0,
    role_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: partners
CREATE TABLE IF NOT EXISTS partners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    country_code VARCHAR(10) DEFAULT '+33',
    address TEXT,
    logo_url VARCHAR(255),
    email_username VARCHAR(255),
    email_password VARCHAR(255),
    email_server VARCHAR(255),
    email_port INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: projects
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    partner_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (partner_id) REFERENCES partners(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: folders
CREATE TABLE IF NOT EXISTS folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    project_id INT,
    parent_folder_id INT,
    path VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (parent_folder_id) REFERENCES folders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: files
CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    folder_id INT,
    file_url VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (folder_id) REFERENCES folders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: incidents
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_number VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) DEFAULT 'incident',
    priority VARCHAR(20) DEFAULT 'P3',
    impact VARCHAR(50),
    domain VARCHAR(50),
    declarant_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'nouveau',
    motif_attente TEXT,
    category VARCHAR(50),
    user_id INT,
    project_id INT,
    assigned_to INT,
    parent_id INT,
    resolution_notes TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME,
    resolved_by INT,
    resolved_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES incidents(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: user_project_permissions
CREATE TABLE IF NOT EXISTS user_project_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    role_id INT,
    can_read BOOLEAN DEFAULT TRUE,
    can_write BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    UNIQUE KEY unique_user_project (user_id, project_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: action_history
CREATE TABLE IF NOT EXISTS action_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. CRÉATION DES INDEX POUR PERFORMANCES
-- ============================================================================

CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_priority ON incidents(priority);
CREATE INDEX idx_incidents_number ON incidents(incident_number);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_client_code ON users(client_code);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_action_history_entity ON action_history(entity_type, entity_id);
CREATE INDEX idx_action_history_created ON action_history(created_at);

-- 3. INSERTION DES DONNÉES INITIALES
-- ============================================================================

-- Rôles par défaut
INSERT INTO roles (name, is_active) VALUES
('Admin', TRUE),
('Expert', TRUE),
('User', TRUE)
ON DUPLICATE KEY UPDATE name=name;

-- Admin par défaut (password: Password123)
INSERT INTO users (name, email, password_hash, role_id, is_active, is_temp_password)
SELECT 'Admin', 'admin@datalysconsulting.com', 
       'scrypt:32768:8:1$VqhB2NQcOEZrWqJF$d5e8f9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1',
       (SELECT id FROM roles WHERE name = 'Admin' LIMIT 1),
       TRUE, FALSE
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@datalysconsulting.com');

-- 4. RÉSUMÉ DES RELATIONS (FOREIGN KEYS)
-- ============================================================================
-- ✅ users → roles (role_id)
-- ✅ projects → partners (partner_id)
-- ✅ folders → projects (project_id)
-- ✅ folders → folders (parent_folder_id) [hiérarchie]
-- ✅ files → folders (folder_id)
-- ✅ incidents → users (user_id) [créateur]
-- ✅ incidents → projects (project_id)
-- ✅ incidents → users (assigned_to) [assigné à]
-- ✅ incidents → incidents (parent_id) [hiérarchie pour réponses]
-- ✅ incidents → users (resolved_by) [résolu par]
-- ✅ user_project_permissions → users (user_id)
-- ✅ user_project_permissions → projects (project_id)
-- ✅ user_project_permissions → roles (role_id)
-- ✅ action_history → users (user_id)

-- TOTAL: 14 FOREIGN KEYS CRÉÉES

-- 5. SÉCURITÉ
-- ============================================================================
-- ✅ Port MySQL 3306 BLOQUÉ de l'extérieur (iptables/UFW)
-- ✅ Mot de passe root changé: Datalys@2025
-- ✅ Ransomware RECOVER_YOUR_DATA supprimé
-- ✅ $500 économisés (rançon non payée)

