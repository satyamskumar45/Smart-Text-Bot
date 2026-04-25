-- SmartTextBot MySQL schema for production-safe authentication, guest mode, history, and usage tracking

CREATE DATABASE IF NOT EXISTS smarttextbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smarttextbot;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(80) NOT NULL DEFAULT 'Learner',
    role ENUM('user','admin') NOT NULL DEFAULT 'user',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    token_hash CHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    revoked TINYINT(1) NOT NULL DEFAULT 0,
    revoked_at DATETIME NULL,
    user_agent VARCHAR(512) NULL,
    ip_address VARCHAR(45) NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY idx_refresh_token_hash (token_hash),
    KEY idx_refresh_user_id (user_id),
    CONSTRAINT fk_refresh_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS guest_sessions (
    id INT NOT NULL AUTO_INCREMENT,
    session_id CHAR(32) NOT NULL UNIQUE,
    usage_counts JSON NOT NULL,
    converted_to_user_id INT NULL,
    last_used_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    KEY idx_guest_session_id (session_id),
    KEY idx_guest_converted_user (converted_to_user_id),
    CONSTRAINT fk_guest_converted_user FOREIGN KEY (converted_to_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS history (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NULL,
    guest_session_id CHAR(32) NULL,
    module_type VARCHAR(64) NOT NULL,
    input_text LONGTEXT NOT NULL,
    output_text LONGTEXT NOT NULL,
    metadata JSON NOT NULL,
    favorite TINYINT(1) NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'complete',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY idx_history_user (user_id),
    KEY idx_history_guest (guest_session_id),
    KEY idx_history_module (module_type),
    CONSTRAINT fk_history_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_guest FOREIGN KEY (guest_session_id) REFERENCES guest_sessions(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS favorites (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    history_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY idx_user_history (user_id, history_id),
    KEY idx_favorite_user (user_id),
    CONSTRAINT fk_favorites_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_favorites_history FOREIGN KEY (history_id) REFERENCES history(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usage_stats (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    module_type VARCHAR(64) NOT NULL,
    period_date DATE NOT NULL,
    usage_count INT NOT NULL DEFAULT 0,
    limit_count INT NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY idx_usage_user_period (user_id, module_type, period_date),
    CONSTRAINT fk_usage_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS learning_progress (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    level INT NOT NULL DEFAULT 1,
    xp INT NOT NULL DEFAULT 0,
    completed_quizzes INT NOT NULL DEFAULT 0,
    vocabulary_count INT NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY idx_learning_user (user_id),
    CONSTRAINT fk_learning_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS streak_tracking (
    id BIGINT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    current_streak INT NOT NULL DEFAULT 0,
    best_streak INT NOT NULL DEFAULT 0,
    last_activity_date DATE NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY idx_streak_user (user_id),
    CONSTRAINT fk_streak_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
