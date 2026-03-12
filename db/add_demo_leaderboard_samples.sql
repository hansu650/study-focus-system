-- Incremental demo users and focus records for leaderboard presentation
USE study_focus;
SET NAMES utf8mb4;

INSERT INTO app_user (
  user_id, username, password_hash, nickname, region_id, school_id, college_id,
  total_points, total_focus_minutes, status, created_at, updated_at
) VALUES
  (9001, 'demo_hubu_cs', RPAD('x', 60, 'x'), 'HUBU CS Demo', 1, 1, 1, 36, 36, 1, NOW(), NOW()),
  (9002, 'demo_hubu_econ', RPAD('x', 60, 'x'), 'HUBU Economics Demo', 1, 1, 2, 22, 22, 1, NOW(), NOW()),
  (9003, 'demo_wust_cs', RPAD('x', 60, 'x'), 'WUST CS Demo', 1, 2, 3, 31, 31, 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE
  nickname = VALUES(nickname),
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
  (90001, 9001, CURDATE(), 36, 36, DATE_SUB(NOW(), INTERVAL 50 MINUTE), DATE_SUB(NOW(), INTERVAL 14 MINUTE), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 36, 1, 'Demo leaderboard sample', NOW(), NOW()),
  (90002, 9002, CURDATE(), 22, 22, DATE_SUB(NOW(), INTERVAL 85 MINUTE), DATE_SUB(NOW(), INTERVAL 63 MINUTE), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 22, 1, 'Demo leaderboard sample', NOW(), NOW()),
  (90003, 9003, CURDATE(), 31, 31, DATE_SUB(NOW(), INTERVAL 130 MINUTE), DATE_SUB(NOW(), INTERVAL 99 MINUTE), 'COMPLETED', 'NONE', JSON_ARRAY(), JSON_ARRAY(), 0, 31, 1, 'Demo leaderboard sample', NOW(), NOW())
ON DUPLICATE KEY UPDATE
  actual_minutes = VALUES(actual_minutes),
  end_at = VALUES(end_at),
  status = VALUES(status),
  awarded_points = VALUES(awarded_points),
  settle_status = VALUES(settle_status),
  remark = VALUES(remark),
  updated_at = NOW();