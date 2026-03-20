-- Showcase demo data for rankings and every major business table
-- Demo login password for all seeded accounts: StudyFocus123!
USE study_focus;
SET NAMES utf8mb4;

INSERT INTO app_user (
  user_id, username, password_hash, email, nickname, student_no, grade_year, major_name,
  region_id, school_id, college_id, total_points, total_focus_minutes, status, created_at, updated_at
) VALUES
  (9101, 'hubu_mjc_se_101', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.mjc.se101@example.com', 'HUBU MJC SE 101', 'HUBU-MJC-SE-101', 2023, 'Software Engineering', 1, 1, 1, 63, 58, 1, NOW(), NOW()),
  (9102, 'hubu_mjc_eie_102', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.mjc.eie102@example.com', 'HUBU MJC EIE 102', 'HUBU-MJC-EIE-102', 2023, 'Electronic Information Engineering', 1, 1, 1, 36, 46, 1, NOW(), NOW()),
  (9103, 'hubu_biz_bdma_103', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.bdma103@example.com', 'HUBU BIZ BDMA 103', 'HUBU-BIZ-BDMA-103', 2023, 'Big Data Management and Application', 1, 1, 2, 49, 44, 1, NOW(), NOW()),
  (9104, 'hubu_biz_acc_104', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.acc104@example.com', 'HUBU BIZ ACC 104', 'HUBU-BIZ-ACC-104', 2023, 'Accounting', 1, 1, 2, 39, 39, 1, NOW(), NOW()),
  (9105, 'hubu_biz_fin_105', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.fin105@example.com', 'HUBU BIZ FIN 105', 'HUBU-BIZ-FIN-105', 2023, 'Finance', 1, 1, 2, 35, 35, 1, NOW(), NOW()),
  (9106, 'hubu_mjc_ai_106', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.mjc.ai106@example.com', 'HUBU MJC AI 106', 'HUBU-MJC-AI-106', 2023, 'Artificial Intelligence', 1, 1, 1, 52, 52, 1, NOW(), NOW()),
  (9107, 'hubu_biz_mkt_107', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'hubu.biz.mkt107@example.com', 'HUBU BIZ MKT 107', 'HUBU-BIZ-MKT-107', 2023, 'Marketing', 1, 1, 2, 28, 28, 1, NOW(), NOW()),
  (9201, 'wust_csc_cs_201', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.csc.cs201@example.com', 'WUST CSC CS 201', 'WUST-CSC-CS-201', 2023, 'Computer Science', 1, 2, 3, 42, 62, 1, NOW(), NOW()),
  (9202, 'wust_lit_tcsol_202', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.lit.tcsol202@example.com', 'WUST LIT TCSOL 202', 'WUST-LIT-TCSOL-202', 2023, 'Teaching Chinese to Speakers of Other Languages', 1, 2, 4, 41, 41, 1, NOW(), NOW()),
  (9203, 'wust_lit_cll_203', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.lit.cll203@example.com', 'WUST LIT CLL 203', 'WUST-LIT-CLL-203', 2023, 'Chinese Language and Literature', 1, 2, 4, 33, 33, 1, NOW(), NOW()),
  (9204, 'wust_csc_se_204', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.csc.se204@example.com', 'WUST CSC SE 204', 'WUST-CSC-SE-204', 2023, 'Software Engineering', 1, 2, 3, 57, 52, 1, NOW(), NOW()),
  (9205, 'wust_lit_jour_205', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.lit.jour205@example.com', 'WUST LIT JOUR 205', 'WUST-LIT-JOUR-205', 2023, 'Journalism', 1, 2, 4, 24, 24, 1, NOW(), NOW()),
  (9206, 'wust_lit_adv_206', '$2b$12$.XyJfJ03PuQFO4t1lpW8AORoIx8Ab82CpzIzRFBP9yXHM864va4M2', 'wust.lit.adv206@example.com', 'WUST LIT ADV 206', 'WUST-LIT-ADV-206', 2023, 'Advertising', 1, 2, 4, 5, 0, 1, NOW(), NOW())
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
  (91001, 9101, CURDATE(), 58, 58, TIMESTAMP(CURDATE(), '08:00:00'), TIMESTAMP(CURDATE(), '08:58:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('steam.exe'), JSON_ARRAY('bilibili.com'), 0, 58, 1, 'Demo showcase / Software Engineering', NOW(), NOW()),
  (91002, 9102, CURDATE(), 46, 46, TIMESTAMP(CURDATE(), '09:05:00'), TIMESTAMP(CURDATE(), '09:51:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('qqmusic.exe'), JSON_ARRAY('youtube.com'), 0, 46, 1, 'Demo showcase / Electronic Information Engineering', NOW(), NOW()),
  (91003, 9103, CURDATE(), 44, 44, TIMESTAMP(CURDATE(), '10:10:00'), TIMESTAMP(CURDATE(), '10:54:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('wechat.exe'), JSON_ARRAY('douyin.com'), 0, 44, 1, 'Demo showcase / Big Data Management and Application', NOW(), NOW()),
  (91004, 9104, CURDATE(), 39, 39, TIMESTAMP(CURDATE(), '11:10:00'), TIMESTAMP(CURDATE(), '11:49:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('steam.exe'), JSON_ARRAY('weibo.com'), 0, 39, 1, 'Demo showcase / Accounting', NOW(), NOW()),
  (91005, 9105, CURDATE(), 35, 35, TIMESTAMP(CURDATE(), '13:30:00'), TIMESTAMP(CURDATE(), '14:05:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('discord.exe'), JSON_ARRAY('iqiyi.com'), 0, 35, 1, 'Demo showcase / Finance', NOW(), NOW()),
  (91006, 9106, CURDATE(), 52, 52, TIMESTAMP(CURDATE(), '14:15:00'), TIMESTAMP(CURDATE(), '15:07:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('wechat.exe'), JSON_ARRAY('xiaohongshu.com'), 0, 52, 1, 'Demo showcase / Artificial Intelligence', NOW(), NOW()),
  (91007, 9107, CURDATE(), 28, 28, TIMESTAMP(CURDATE(), '15:20:00'), TIMESTAMP(CURDATE(), '15:48:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('neteasemusic.exe'), JSON_ARRAY('youku.com'), 0, 28, 1, 'Demo showcase / Marketing', NOW(), NOW()),
  (92001, 9201, CURDATE(), 62, 62, TIMESTAMP(CURDATE(), '08:20:00'), TIMESTAMP(CURDATE(), '09:22:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('steam.exe'), JSON_ARRAY('bilibili.com'), 0, 62, 1, 'Demo showcase / Computer Science', NOW(), NOW()),
  (92002, 9202, CURDATE(), 41, 41, TIMESTAMP(CURDATE(), '10:40:00'), TIMESTAMP(CURDATE(), '11:21:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('wechat.exe'), JSON_ARRAY('youtube.com'), 0, 41, 1, 'Demo showcase / TCSOL', NOW(), NOW()),
  (92003, 9203, CURDATE(), 33, 33, TIMESTAMP(CURDATE(), '13:10:00'), TIMESTAMP(CURDATE(), '13:43:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('steam.exe'), JSON_ARRAY('douyin.com'), 0, 33, 1, 'Demo showcase / Chinese Language and Literature', NOW(), NOW()),
  (92004, 9204, CURDATE(), 52, 52, TIMESTAMP(CURDATE(), '14:35:00'), TIMESTAMP(CURDATE(), '15:27:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('qqmusic.exe'), JSON_ARRAY('bilibili.com'), 0, 52, 1, 'Demo showcase / Software Engineering', NOW(), NOW()),
  (92005, 9205, CURDATE(), 24, 24, TIMESTAMP(CURDATE(), '16:05:00'), TIMESTAMP(CURDATE(), '16:29:00'), 'COMPLETED', 'APP_BLOCK', JSON_ARRAY('wechat.exe'), JSON_ARRAY('weibo.com'), 0, 24, 1, 'Demo showcase / Journalism', NOW(), NOW())
ON DUPLICATE KEY UPDATE
  user_id = VALUES(user_id),
  focus_date = VALUES(focus_date),
  planned_minutes = VALUES(planned_minutes),
  actual_minutes = VALUES(actual_minutes),
  start_at = VALUES(start_at),
  end_at = VALUES(end_at),
  status = VALUES(status),
  lock_mode = VALUES(lock_mode),
  blocked_apps_json = VALUES(blocked_apps_json),
  blocked_sites_json = VALUES(blocked_sites_json),
  interrupt_count = VALUES(interrupt_count),
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
  (910006, 9106, 52, 0, 52, 'FOCUS_REWARD', 91006, TIMESTAMP(CURDATE(), '15:07:00'), 'Demo focus reward / Artificial Intelligence', NOW()),
  (910007, 9107, 28, 0, 28, 'FOCUS_REWARD', 91007, TIMESTAMP(CURDATE(), '15:48:00'), 'Demo focus reward / Marketing', NOW()),
  (920001, 9201, 62, 0, 62, 'FOCUS_REWARD', 92001, TIMESTAMP(CURDATE(), '09:22:00'), 'Demo focus reward / Computer Science', NOW()),
  (920002, 9202, 41, 0, 41, 'FOCUS_REWARD', 92002, TIMESTAMP(CURDATE(), '11:21:00'), 'Demo focus reward / TCSOL', NOW()),
  (920003, 9203, 33, 0, 33, 'FOCUS_REWARD', 92003, TIMESTAMP(CURDATE(), '13:43:00'), 'Demo focus reward / Chinese Language and Literature', NOW()),
  (920004, 9204, 52, 0, 52, 'FOCUS_REWARD', 92004, TIMESTAMP(CURDATE(), '15:27:00'), 'Demo focus reward / Software Engineering', NOW()),
  (920005, 9205, 24, 0, 24, 'FOCUS_REWARD', 92005, TIMESTAMP(CURDATE(), '16:29:00'), 'Demo focus reward / Journalism', NOW()),
  (910011, 9101, 5, 58, 63, 'QUESTION_REWARD', 10001, TIMESTAMP(CURDATE(), '18:10:00'), 'Demo daily question reward / Software Engineering', NOW()),
  (910021, 9102, -10, 46, 36, 'PRINT_REDEEM', 50001, TIMESTAMP(CURDATE(), '18:40:00'), 'Demo print redeem / Campus Print Shop A', NOW()),
  (910031, 9103, 5, 44, 49, 'QUESTION_REWARD', 10003, TIMESTAMP(CURDATE(), '18:15:00'), 'Demo daily question reward / Big Data Management and Application', NOW()),
  (920011, 9201, -20, 62, 42, 'PRINT_REDEEM', 50002, TIMESTAMP(CURDATE(), '18:45:00'), 'Demo print redeem / WUST Print Center', NOW()),
  (920041, 9204, 5, 52, 57, 'QUESTION_REWARD', 10004, TIMESTAMP(CURDATE(), '18:20:00'), 'Demo daily question reward / Software Engineering', NOW()),
  (920061, 9206, 5, 0, 5, 'QUESTION_REWARD', 10005, TIMESTAMP(CURDATE(), '18:25:00'), 'Demo daily question reward / Advertising', NOW())
ON DUPLICATE KEY UPDATE
  user_id = VALUES(user_id),
  change_points = VALUES(change_points),
  balance_before = VALUES(balance_before),
  balance_after = VALUES(balance_after),
  biz_type = VALUES(biz_type),
  biz_id = VALUES(biz_id),
  occurred_at = VALUES(occurred_at),
  note = VALUES(note);

INSERT INTO daily_question_attempt (
  attempt_id, user_id, question_date, subject, difficulty, title,
  selected_option, correct_option, is_correct, awarded_points, points_txn_id,
  answered_at, created_at, updated_at
) VALUES
  (10001, 9101, CURDATE(), 'Grammar', 'Easy', 'Passive Voice Basics', 'A', 'A', 1, 5, 910011, TIMESTAMP(CURDATE(), '18:10:00'), NOW(), NOW()),
  (10002, 9102, CURDATE(), 'Vocabulary', 'Easy', 'Campus Vocabulary Check', 'C', 'B', 0, 0, NULL, TIMESTAMP(CURDATE(), '18:12:00'), NOW(), NOW()),
  (10003, 9103, CURDATE(), 'Grammar', 'Easy', 'Passive Voice Basics', 'A', 'A', 1, 5, 910031, TIMESTAMP(CURDATE(), '18:15:00'), NOW(), NOW()),
  (10004, 9204, CURDATE(), 'Listening', 'Medium', 'Short Campus Announcement', 'D', 'D', 1, 5, 920041, TIMESTAMP(CURDATE(), '18:20:00'), NOW(), NOW()),
  (10005, 9206, CURDATE(), 'Reading', 'Easy', 'Library Schedule Notice', 'B', 'B', 1, 5, 920061, TIMESTAMP(CURDATE(), '18:25:00'), NOW(), NOW())
ON DUPLICATE KEY UPDATE
  user_id = VALUES(user_id),
  question_date = VALUES(question_date),
  subject = VALUES(subject),
  difficulty = VALUES(difficulty),
  title = VALUES(title),
  selected_option = VALUES(selected_option),
  correct_option = VALUES(correct_option),
  is_correct = VALUES(is_correct),
  awarded_points = VALUES(awarded_points),
  points_txn_id = VALUES(points_txn_id),
  answered_at = VALUES(answered_at),
  updated_at = NOW();

INSERT INTO redeem_order (
  redeem_order_id, order_no, user_id, school_id, store_name, points_cost, print_quota_pages,
  coupon_token, qr_payload, status, points_txn_id, expire_at, verified_at, verified_by, created_at, updated_at
) VALUES
  (50001, 'DEMO-REDEEM-9102', 9102, 1, 'Campus Print Shop A', 10, 5, 'DEMO9102TOKEN', 'redeem://demo/9102', 'VERIFIED', 910021, DATE_ADD(NOW(), INTERVAL 7 DAY), NOW(), 'store-demo-a', NOW(), NOW()),
  (50002, 'DEMO-REDEEM-9201', 9201, 2, 'WUST Print Center', 20, 10, 'DEMO9201TOKEN', 'redeem://demo/9201', 'CREATED', 920011, DATE_ADD(NOW(), INTERVAL 7 DAY), NULL, NULL, NOW(), NOW())
ON DUPLICATE KEY UPDATE
  order_no = VALUES(order_no),
  user_id = VALUES(user_id),
  school_id = VALUES(school_id),
  store_name = VALUES(store_name),
  points_cost = VALUES(points_cost),
  print_quota_pages = VALUES(print_quota_pages),
  coupon_token = VALUES(coupon_token),
  qr_payload = VALUES(qr_payload),
  status = VALUES(status),
  points_txn_id = VALUES(points_txn_id),
  expire_at = VALUES(expire_at),
  verified_at = VALUES(verified_at),
  verified_by = VALUES(verified_by),
  updated_at = NOW();

INSERT INTO feedback_message (
  feedback_id, user_id, category, title, content, contact_email, status, created_at, updated_at
) VALUES
  (70001, 9101, 'GENERAL', 'Add a weekly trend card', 'The ranking demo looks good. A weekly trend card on the home page would make the data story stronger.', 'hubu.mjc.se101@example.com', 'NEW', NOW(), NOW()),
  (70002, 9204, 'UI', 'Move the plan notebook closer to the timer', 'The plan notebook is useful, but it feels more natural when it stays visually attached to the countdown block.', 'wust.csc.se204@example.com', 'REVIEWED', NOW(), NOW()),
  (70003, 9202, 'FEATURE', 'Export ranking snapshots', 'Please add an export option so student leaders can save the leaderboard for reports and demos.', 'wust.lit.tcsol202@example.com', 'NEW', NOW(), NOW())
ON DUPLICATE KEY UPDATE
  user_id = VALUES(user_id),
  category = VALUES(category),
  title = VALUES(title),
  content = VALUES(content),
  contact_email = VALUES(contact_email),
  status = VALUES(status),
  updated_at = NOW();
