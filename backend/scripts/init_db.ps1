param(
  [string]$MysqlExe = "mysql",
  [string]$DbHost = "127.0.0.1",
  [int]$DbPort = 3306,
  [string]$DbUser = "root",
  [string]$DbPassword = "",
  [string]$SchemaFile = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $SchemaFile) {
  $SchemaFile = Join-Path $PSScriptRoot "..\..\db\schema.sql"
}

if (-not (Test-Path $SchemaFile)) {
  Write-Host "FAIL schema file not found: $SchemaFile"
  exit 1
}

$schemaFullPath = (Resolve-Path $SchemaFile).Path
$schemaSql = Get-Content -Path $schemaFullPath -Raw -Encoding UTF8
$oldMysqlPwd = $env:MYSQL_PWD

try {
  if ($DbPassword) {
    $env:MYSQL_PWD = $DbPassword
  }

  $schemaSql | & $MysqlExe --default-character-set=utf8mb4 -h $DbHost -P $DbPort -u $DbUser
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL init database"
    exit $LASTEXITCODE
  }

  Write-Host "PASS init database from $schemaFullPath"
}
finally {
  $env:MYSQL_PWD = $oldMysqlPwd
}
