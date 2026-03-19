-- ============================================================================
-- Project: Study Focus (Desktop Pomodoro + Incentive System)
-- Database: MySQL 8.0+
-- Purpose : Core schema DDL
-- ============================================================================

CREATE DATABASE IF NOT EXISTS study_focus
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE study_focus;
SET NAMES utf8mb4;

-- Drop tables in reverse dependency order for re-runs
DROP TABLE IF EXISTS feedback_message;
DROP TABLE IF EXISTS redeem_order;
DROP TABLE IF EXISTS daily_question_attempt;
DROP TABLE IF EXISTS point_ledger;
DROP TABLE IF EXISTS focus_session;
DROP TABLE IF EXISTS app_user;
DROP TABLE IF EXISTS dict_college;
DROP TABLE IF EXISTS dict_school;
DROP TABLE IF EXISTS dict_region;

-- 1) Region dictionary
CREATE TABLE dict_region (
  region_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Region ID',
  region_code VARCHAR(32) NOT NULL COMMENT 'Region code',
  region_name VARCHAR(100) NOT NULL COMMENT 'Region name',
  region_level TINYINT UNSIGNED NOT NULL COMMENT '1=province,2=city,3=district',
  parent_region_id BIGINT UNSIGNED NULL COMMENT 'Parent region ID',
  sort_no INT NOT NULL DEFAULT 100 COMMENT 'Sort order',
  is_enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=enabled,0=disabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (region_id),
  UNIQUE KEY uk_region_code (region_code),
  KEY idx_region_parent (parent_region_id),
  CONSTRAINT fk_region_parent
    FOREIGN KEY (parent_region_id) REFERENCES dict_region(region_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Region dictionary';

-- 2) School dictionary
CREATE TABLE dict_school (
  school_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'School ID',
  school_code VARCHAR(32) NOT NULL COMMENT 'School code',
  school_name VARCHAR(150) NOT NULL COMMENT 'School name',
  region_id BIGINT UNSIGNED NOT NULL COMMENT 'Region ID',
  school_type TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1=undergraduate,2=vocational,3=other',
  is_enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=enabled,0=disabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (school_id),
  UNIQUE KEY uk_school_code (school_code),
  UNIQUE KEY uk_school_name (school_name),
  UNIQUE KEY uk_region_school (region_id, school_id),
  KEY idx_school_region (region_id),
  CONSTRAINT fk_school_region
    FOREIGN KEY (region_id) REFERENCES dict_region(region_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='School dictionary';

-- 3) College dictionary
CREATE TABLE dict_college (
  college_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'College ID',
  school_id BIGINT UNSIGNED NOT NULL COMMENT 'School ID',
  college_code VARCHAR(32) NOT NULL COMMENT 'College code',
  college_name VARCHAR(150) NOT NULL COMMENT 'College name',
  is_enabled TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=enabled,0=disabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (college_id),
  UNIQUE KEY uk_college_code (college_code),
  UNIQUE KEY uk_school_college_name (school_id, college_name),
  UNIQUE KEY uk_school_college (school_id, college_id),
  KEY idx_college_school (school_id),
  CONSTRAINT fk_college_school
    FOREIGN KEY (school_id) REFERENCES dict_school(school_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='College dictionary';

-- 4) User table
CREATE TABLE app_user (
  user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  username VARCHAR(50) NOT NULL COMMENT 'Login username',
  password_hash CHAR(60) NOT NULL COMMENT 'Password hash (bcrypt recommended)',
  email VARCHAR(120) NULL COMMENT 'Email',
  phone VARCHAR(20) NULL COMMENT 'Phone',
  nickname VARCHAR(60) NOT NULL COMMENT 'Nickname',
  avatar_url VARCHAR(255) NULL COMMENT 'Avatar URL',
  student_no VARCHAR(64) NULL COMMENT 'Student number (unique per school)',
  grade_year SMALLINT UNSIGNED NULL COMMENT 'Grade year',
  major_name VARCHAR(100) NULL COMMENT 'Major name',
  region_id BIGINT UNSIGNED NOT NULL COMMENT 'Region ID',
  school_id BIGINT UNSIGNED NOT NULL COMMENT 'School ID',
  college_id BIGINT UNSIGNED NOT NULL COMMENT 'College ID',
  total_points INT NOT NULL DEFAULT 0 COMMENT 'Current total points',
  total_focus_minutes INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Accumulated focus minutes',
  status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=active,0=disabled',
  last_login_at DATETIME NULL COMMENT 'Last login time',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  deleted_at DATETIME NULL COMMENT 'Soft delete time',
  PRIMARY KEY (user_id),
  UNIQUE KEY uk_user_username (username),
  UNIQUE KEY uk_user_email (email),
  UNIQUE KEY uk_user_phone (phone),
  UNIQUE KEY uk_school_student_no (school_id, student_no),
  KEY idx_user_region_school (region_id, school_id),
  KEY idx_user_school_college (school_id, college_id),
  KEY idx_user_points (total_points),
  CONSTRAINT fk_user_region
    FOREIGN KEY (region_id) REFERENCES dict_region(region_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_user_school
    FOREIGN KEY (region_id, school_id) REFERENCES dict_school(region_id, school_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_user_college
    FOREIGN KEY (school_id, college_id) REFERENCES dict_college(school_id, college_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User table';

-- 5) Feedback message table
CREATE TABLE feedback_message (
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

-- 6) Pomodoro session table
CREATE TABLE focus_session (
  session_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Session ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
  focus_date DATE NOT NULL COMMENT 'Local date of session start',
  planned_minutes SMALLINT UNSIGNED NOT NULL COMMENT 'Planned minutes',
  actual_minutes SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Actual minutes',
  start_at DATETIME NOT NULL COMMENT 'Start time',
  end_at DATETIME NULL COMMENT 'End time',
  status ENUM('RUNNING','COMPLETED','INTERRUPTED','ABANDONED') NOT NULL DEFAULT 'RUNNING' COMMENT 'Session status',
  lock_mode ENUM('APP_BLOCK','WEB_BLOCK','FULL_LOCK','NONE') NOT NULL DEFAULT 'APP_BLOCK' COMMENT 'Lock mode',
  blocked_apps_json JSON NULL COMMENT 'Blocked apps snapshot',
  blocked_sites_json JSON NULL COMMENT 'Blocked sites snapshot',
  interrupt_count SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Interrupt count',
  awarded_points INT NOT NULL DEFAULT 0 COMMENT 'Awarded points',
  settle_status TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=not settled,1=settled',
  remark VARCHAR(255) NULL COMMENT 'Remark',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (session_id),
  KEY idx_focus_user_date (user_id, focus_date),
  KEY idx_focus_user_start (user_id, start_at),
  KEY idx_focus_status_date (status, focus_date),
  CONSTRAINT fk_focus_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_focus_planned_minutes CHECK (planned_minutes BETWEEN 1 AND 240),
  CONSTRAINT ck_focus_actual_minutes CHECK (actual_minutes <= planned_minutes)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Pomodoro sessions';

-- 7) Point ledger table
CREATE TABLE point_ledger (
  txn_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Transaction ID',
  user_id BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
  change_points INT NOT NULL COMMENT 'Point delta (+/-)',
  balance_before INT NOT NULL COMMENT 'Balance before change',
  balance_after INT NOT NULL COMMENT 'Balance after change',
  biz_type ENUM('FOCUS_REWARD','QUESTION_REWARD','AI_ASSIST_REWARD','PRINT_REDEEM','ORDER_REFUND','MANUAL_ADJUST') NOT NULL COMMENT 'Business type',
  biz_id BIGINT UNSIGNED NULL COMMENT 'Business ID (session/order, etc.)',
  occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Occurred time',
  note VARCHAR(255) NULL COMMENT 'Note',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  PRIMARY KEY (txn_id),
  KEY idx_ledger_user_time (user_id, occurred_at),
  KEY idx_ledger_biz (biz_type, biz_id),
  KEY idx_ledger_time (occurred_at),
  CONSTRAINT fk_ledger_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ck_ledger_balance CHECK (balance_after = balance_before + change_points)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Point ledger';

-- 8) Daily question attempt table
CREATE TABLE daily_question_attempt (
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
  points_txn_id BIGINT UNSIGNED NULL COMMENT 'Related reward transaction',
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

-- 9) Redeem order table
CREATE TABLE redeem_order (
  redeem_order_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Redeem order ID',
  order_no VARCHAR(32) NOT NULL COMMENT 'Business order number',
  user_id BIGINT UNSIGNED NOT NULL COMMENT 'User ID',
  school_id BIGINT UNSIGNED NOT NULL COMMENT 'School ID',
  store_name VARCHAR(120) NOT NULL COMMENT 'Partner print store name',
  points_cost INT UNSIGNED NOT NULL COMMENT 'Consumed points',
  print_quota_pages INT UNSIGNED NOT NULL COMMENT 'Free print pages',
  coupon_token VARCHAR(64) NOT NULL COMMENT 'Redeem token',
  qr_payload VARCHAR(255) NOT NULL COMMENT 'QR payload',
  status ENUM('CREATED','PAID','VERIFIED','CANCELLED','EXPIRED') NOT NULL DEFAULT 'CREATED' COMMENT 'Order status',
  points_txn_id BIGINT UNSIGNED NULL COMMENT 'Related point transaction ID',
  expire_at DATETIME NOT NULL COMMENT 'Expiry time',
  verified_at DATETIME NULL COMMENT 'Verification time',
  verified_by VARCHAR(64) NULL COMMENT 'Verifier account',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created time',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Updated time',
  PRIMARY KEY (redeem_order_id),
  UNIQUE KEY uk_order_no (order_no),
  UNIQUE KEY uk_coupon_token (coupon_token),
  KEY idx_order_user_time (user_id, created_at),
  KEY idx_order_school_status (school_id, status),
  KEY idx_order_expire (expire_at),
  CONSTRAINT fk_order_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_order_school
    FOREIGN KEY (school_id) REFERENCES dict_school(school_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_order_points_txn
    FOREIGN KEY (points_txn_id) REFERENCES point_ledger(txn_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT ck_order_points_cost CHECK (points_cost > 0),
  CONSTRAINT ck_order_print_pages CHECK (print_quota_pages > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Redeem and verification orders';

