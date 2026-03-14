-- Incremental demo users and focus records for leaderboard presentation
-- Demo login password for all seeded accounts: StudyFocus123!
USE study_focus;
SET NAMES utf8mb4;

INSERT INTO app_user (
  user_id, username, password_hash, email, nickname, student_no, grade_year, major_name,
  region_id, school_id, college_id, total_points, total_focus_minutes, status, created_at, updated_at
) VALUES
  (9101, 'hubu_mjc_se_101', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.mjc.se101@example.com', 'HUBU MJC SE 101', 'HUBU-MJC-SE-101', 2023, 'Software Engineering', 1, 1, 1, 58, 58, 1, NOW(), NOW()),
  (9102, 'hubu_mjc_eie_102', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.mjc.eie102@example.com', 'HUBU MJC EIE 102', 'HUBU-MJC-EIE-102', 2023, 'Electronic Information Engineering', 1, 1, 1, 46, 46, 1, NOW(), NOW()),
  (9103, 'hubu_biz_bdma_103', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.bdma103@example.com', 'HUBU BIZ BDMA 103', 'HUBU-BIZ-BDMA-103', 2023, 'Big Data Management and Application', 1, 1, 2, 44, 44, 1, NOW(), NOW()),
  (9104, 'hubu_biz_acc_104', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.acc104@example.com', 'HUBU BIZ ACC 104', 'HUBU-BIZ-ACC-104', 2023, 'Accounting', 1, 1, 2, 39, 39, 1, NOW(), NOW()),
  (9105, 'hubu_biz_fin_105', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.fin105@example.com', 'HUBU BIZ FIN 105', 'HUBU-BIZ-FIN-105', 2023, 'Finance', 1, 1, 2, 35, 35, 1, NOW(), NOW()),
  (9201, 'wust_csc_cs_201', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.csc.cs201@example.com', 'WUST CSC CS 201', 'WUST-CSC-CS-201', 2023, 'Computer Science', 1, 2, 3, 62, 62, 1, NOW(), NOW()),
  (9202, 'wust_lit_tcsol_202', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.lit.tcsol202@example.com', 'WUST LIT TCSOL 202', 'WUST-LIT-TCSOL-202', 2023, 'Teaching Chinese to Speakers of Other Languages', 1, 2, 4, 41, 41, 1, NOW(), NOW()),
  (9203, 'wust_lit_cll_203', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.lit.cll203@example.com', 'WUST LIT CLL 203', 'WUST-LIT-CLL-203', 2023, 'Chinese Language and Literature', 1, 2, 4, 33, 33, 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE
  username = VALUES(username),
  password_hash = VALUES(password_hash),
  email = VALUES(email),
  nickname = VALUES(nickname),
  student_no = VALUES(student_no),
  grade_year = VALUES(grade_year),
  major_name = VALUES(major_name),
  region_id = VALUES(region_id),
  school_id = VALUES(school_id),
  college_id = VALUES(college_id),
  total_points = VALUES(total_points),
  total_focus_minutes = VALUES(total_focus_minutes),
  status = VALUES(status),
  updated_at = NOW();

INSERT INTO focus_session (
  session_id, user_id, focus_date, planned_minutes, actual_minutes, start_at, end_at,
  status, lock_mode, blocked_apps_json, blocked_sites_json, interrupt_count,
  awarded_points, settle_status, remark, created_at, updated_at
) VALUES
  (91001, 9101, CURDATE(), 58, 58, TIMESTAMP(CURDATE(), '08:00:00'), TIMESTAMP(CURDATE(), '08:58:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 58, 1, 'Demo leaderboard sample / Software Engineering', NOW(), NOW()),
  (91002, 9102, CURDATE(), 46, 46, TIMESTAMP(CURDATE(), '09:05:00'), TIMESTAMP(CURDATE(), '09:51:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 46, 1, 'Demo leaderboard sample / Electronic Information Engineering', NOW(), NOW()),
  (91003, 9103, CURDATE(), 44, 44, TIMESTAMP(CURDATE(), '10:10:00'), TIMESTAMP(CURDATE(), '10:54:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 44, 1, 'Demo leaderboard sample / Big Data Management and Application', NOW(), NOW()),
  (91004, 9104, CURDATE(), 39, 39, TIMESTAMP(CURDATE(), '11:10:00'), TIMESTAMP(CURDATE(), '11:49:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 39, 1, 'Demo leaderboard sample / Accounting', NOW(), NOW()),
  (91005, 9105, CURDATE(), 35, 35, TIMESTAMP(CURDATE(), '13:30:00'), TIMESTAMP(CURDATE(), '14:05:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 35, 1, 'Demo leaderboard sample / Finance', NOW(), NOW()),
  (92001, 9201, CURDATE(), 62, 62, TIMESTAMP(CURDATE(), '14:20:00'), TIMESTAMP(CURDATE(), '15:22:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 62, 1, 'Demo leaderboard sample / Computer Science', NOW(), NOW()),
  (92002, 9202, CURDATE(), 41, 41, TIMESTAMP(CURDATE(), '15:40:00'), TIMESTAMP(CURDATE(), '16:21:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 41, 1, 'Demo leaderboard sample / TCSOL', NOW(), NOW()),
  (92003, 9203, CURDATE(), 33, 33, TIMESTAMP(CURDATE(), '16:40:00'), TIMESTAMP(CURDATE(), '17:13:00'), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 33, 1, 'Demo leaderboard sample / Chinese Language and Literature', NOW(), NOW())
ON DUPLICATE KEY UPDATE
  user_id = VALUES(user_id),
  focus_date = VALUES(focus_date),
  planned_minutes = VALUES(planned_minutes),
  actual_minutes = VALUES(actual_minutes),
  start_at = VALUES(start_at),
  end_at = VALUES(end_at),
  status = VALUES(status),
  lock_mode = VALUES(lock_mode),
  awarded_points = VALUES(awarded_points),
  settle_status = VALUES(settle_status),
  remark = VALUES(remark),
  updated_at = NOW();

INSERT INTO point_ledger (
  txn_id, user_id, change_points, balance_before, balance_after, biz_type, biz_id, occurred_at, note, created_at
) VALUES
  (910001, 9101, 58, 0, 58, 'FOCUS_REWARD', 91001, TIMESTAMP(CURDATE(), '08:58:00'), 'Demo focus reward / Software Engineering', NOW()),
  (910002, 9102, 46, 0, 46, 'FOCUS_REWARD', 91002, TIMESTAMP(CURDATE(), '09:51:00'), 'Demo focus reward / Electronic Information Engineering', NOW()),
  (910003, 9103, 44, 0, 44, 'FOCUS_REWARD', 91003, TIMESTAMP(CURDATE(), '10:54:00'), 'Demo focus reward / Big Data Management and Application', NOW()),
  (910004, 9104, 39, 0, 39, 'FOCUS_REWARD', 91004, TIMESTAMP(CURDATE(), '11:49:00'), 'Demo focus reward / Accounting', NOW()),
  (910005, 9105, 35, 0, 35, 'FOCUS_REWARD', 91005, TIMESTAMP(CURDATE(), '14:05:00'), 'Demo focus reward / Finance', NOW()),
  (920001, 9201, 62, 0, 62, 'FOCUS_REWARD', 92001, TIMESTAMP(CURDATE(), '15:22:00'), 'Demo focus reward / Computer Science', NOW()),
  (920002, 9202, 41, 0, 41, 'FOCUS_REWARD', 92002, TIMESTAMP(CURDATE(), '16:21:00'), 'Demo focus reward / TCSOL', NOW()),
  (920003, 9203, 33, 0, 33, 'FOCUS_REWARD', 92003, TIMESTAMP(CURDATE(), '17:13:00'), 'Demo focus reward / Chinese Language and Literature', NOW())
ON DUPLICATE KEY UPDATE
  user_id = VALUES(user_id),
  change_points = VALUES(change_points),
  balance_before = VALUES(balance_before),
  balance_after = VALUES(balance_after),
  biz_type = VALUES(biz_type),
  biz_id = VALUES(biz_id),
  occurred_at = VALUES(occurred_at),
  note = VALUES(note);
