param(
  [string]$MysqlExe = "mysql",
  [string]$DbHost = "127.0.0.1",
  [int]$DbPort = 3306,
  [string]$DbUser = "root",
  [string]$DbPassword = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$oldMysqlPwd = $env:MYSQL_PWD

try {
  if ($DbPassword) {
    $env:MYSQL_PWD = $DbPassword
  }

  $seedSql = @(
    "USE study_focus;",
    "INSERT INTO dict_region (region_id, region_code, region_name, region_level, parent_region_id, sort_no, is_enabled) VALUES (1, 'CN-TEST-001', 'Test Region', 1, NULL, 1, 1) ON DUPLICATE KEY UPDATE region_name=VALUES(region_name), is_enabled=VALUES(is_enabled);",
    "INSERT INTO dict_school (school_id, school_code, school_name, region_id, school_type, is_enabled) VALUES (1, 'TEST-SCHOOL-001', 'Test University', 1, 1, 1) ON DUPLICATE KEY UPDATE school_name=VALUES(school_name), region_id=VALUES(region_id), is_enabled=VALUES(is_enabled);",
    "INSERT INTO dict_college (college_id, school_id, college_code, college_name, is_enabled) VALUES (1, 1, 'TEST-COLLEGE-001', 'Computer College', 1) ON DUPLICATE KEY UPDATE college_name=VALUES(college_name), school_id=VALUES(school_id), is_enabled=VALUES(is_enabled);"
  ) -join "`n"

  & $MysqlExe --default-character-set=utf8mb4 -h $DbHost -P $DbPort -u $DbUser -e $seedSql
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL seed demo data"
    exit $LASTEXITCODE
  }

  Write-Host "PASS seed demo data"
}
finally {
  $env:MYSQL_PWD = $oldMysqlPwd
}
