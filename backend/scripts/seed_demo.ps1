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
  $sqlPath = Join-Path $repoRoot "db\seed_demo.sql"
  $seedSql = Get-Content $sqlPath -Raw -Encoding UTF8

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