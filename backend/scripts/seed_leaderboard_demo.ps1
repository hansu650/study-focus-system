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

  $scriptDir = Split-Path -Parent $PSCommandPath
  $repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
  $dictSqlPath = Join-Path $repoRoot "db\add_demo_leaderboard_dicts.sql"
  $sampleSqlPath = Join-Path $repoRoot "db\add_demo_leaderboard_samples.sql"

  $dictSql = Get-Content $dictSqlPath -Raw -Encoding UTF8
  $sampleSql = Get-Content $sampleSqlPath -Raw -Encoding UTF8

  & $MysqlExe --default-character-set=utf8mb4 -h $DbHost -P $DbPort -u $DbUser -e $dictSql
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL seed leaderboard dictionaries"
    exit $LASTEXITCODE
  }

  & $MysqlExe --default-character-set=utf8mb4 -h $DbHost -P $DbPort -u $DbUser -e $sampleSql
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL seed leaderboard samples"
    exit $LASTEXITCODE
  }

  Write-Host "PASS seed leaderboard demo data"
}
finally {
  $env:MYSQL_PWD = $oldMysqlPwd
}