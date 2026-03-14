-- Minimal seed data for local API testing
-- Run after db/schema.sql

SET NAMES utf8mb4;
USE study_focus;

INSERT INTO dict_region (
  region_id, region_code, region_name, region_level, parent_region_id, sort_no, is_enabled
) VALUES (
  1, 'CN-HB', 'Hubei Province', 1, NULL, 1, 1
)
ON DUPLICATE KEY UPDATE
  region_name = VALUES(region_name),
  is_enabled = VALUES(is_enabled);

INSERT INTO dict_school (
  school_id, school_code, school_name, region_id, school_type, is_enabled
) VALUES
  (1, 'HUBU', 'Hubei University', 1, 1, 1),
  (2, 'WUST', 'Wuhan University of Science and Technology', 1, 1, 1)
ON DUPLICATE KEY UPDATE
  school_name = VALUES(school_name),
  region_id = VALUES(region_id),
  is_enabled = VALUES(is_enabled);

INSERT INTO dict_college (
  college_id, school_id, college_code, college_name, is_enabled
) VALUES
  (1, 1, 'HUBU-MJC', 'Manchester Joint College', 1),
  (2, 1, 'HUBU-BIZ', 'Business School', 1),
  (3, 2, 'WUST-CSC', 'School of Computer Science and Technology', 1),
  (4, 2, 'WUST-LIT', 'School of Liberal Arts', 1)
ON DUPLICATE KEY UPDATE
  college_name = VALUES(college_name),
  school_id = VALUES(school_id);