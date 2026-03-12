-- Incremental migration for Sprint 2 feedback collection
USE study_focus;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS feedback_message (
  feedback_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Feedback ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
  category VARCHAR(32) NOT NULL DEFAULT 'GENERAL' COMMENT 'Feedback category',
  title VARCHAR(120) NOT NULL COMMENT 'Feedback title',
  content TEXT NOT NULL COMMENT 'Feedback content',
  contact_email VARCHAR(120) NULL COMMENT 'Optional follow-up email',
  status ENUM('NEW','REVIEWED') NOT NULL DEFAULT 'NEW' COMMENT 'Processing status',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (feedback_id),
  KEY idx_feedback_user_time (user_id, created_at),
  KEY idx_feedback_category_status (category, status),
  CONSTRAINT fk_feedback_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User product feedback';