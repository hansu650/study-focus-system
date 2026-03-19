-- Incremental migration for Sprint 4 daily quiz rewards

CREATE TABLE IF NOT EXISTS daily_question_attempt (
  attempt_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Attempt ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
  question_date DATE NOT NULL COMMENT 'Daily quiz date',
  subject VARCHAR(64) NOT NULL COMMENT 'Question subject',
  difficulty VARCHAR(32) NOT NULL COMMENT 'Question difficulty',
  title VARCHAR(120) NOT NULL COMMENT 'Question title',
  selected_option CHAR(1) NOT NULL COMMENT 'Submitted option',
  correct_option CHAR(1) NOT NULL COMMENT 'Correct option',
  is_correct TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=wrong,1=correct',
  awarded_points INT NOT NULL DEFAULT 0 COMMENT 'Awarded points',
  points_txn_id BIGINT UNSIGNED NULL COMMENT 'Related reward ledger row',
  answered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Answer time',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (attempt_id),
  UNIQUE KEY uk_question_attempt_user_date (user_id, question_date),
  KEY idx_question_attempt_answered (answered_at),
  CONSTRAINT fk_question_attempt_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_question_attempt_points
    FOREIGN KEY (points_txn_id) REFERENCES point_ledger(txn_id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Daily quiz answer records';
