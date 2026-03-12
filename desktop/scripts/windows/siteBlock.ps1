param(
  [ValidateSet("Apply", "Clear")]
  [string]$Mode = "Apply",
  [string]$DomainsCsv = ""
)

$hostsPath = Join-Path $env:SystemRoot "System32\drivers\etc\hosts"
$startMarker = "# STUDY_FOCUS_BLOCK_START"
$endMarker = "# STUDY_FOCUS_BLOCK_END"

function Test-IsAdministrator {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = New-Object Security.Principal.WindowsPrincipal($identity)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Remove-ManagedBlock {
  param([string[]]$Content)

  $result = New-Object System.Collections.Generic.List[string]
  $skip = $false

  foreach ($line in $Content) {
    if ($line -eq $startMarker) {
      $skip = $true
      continue
    }

    if ($line -eq $endMarker) {
      $skip = $false
      continue
    }

    if (-not $skip) {
      $result.Add($line)
    }
  }

  return $result.ToArray()
}

function Normalize-Domain {
  param([string]$Value)

  return ($Value.Trim().ToLower() -replace "^https?://", "" -replace "^www\\.", "" -replace "/.*$", "")
}

function Write-HostsContent {
  param(
    [string]$Path,
    [string[]]$Lines
  )

  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllLines($Path, $Lines, $utf8NoBom)
}

if (-not (Test-IsAdministrator)) {
  Write-Error "Administrator permission is required to modify the Windows hosts file."
  exit 1
}

$content = @()
if (Test-Path $hostsPath) {
  $content = Get-Content -Path $hostsPath -Encoding utf8
}

$filtered = Remove-ManagedBlock -Content $content

if ($Mode -eq "Apply" -and -not [string]::IsNullOrWhiteSpace($DomainsCsv)) {
  $domains = $DomainsCsv.Split(",") |
    ForEach-Object { Normalize-Domain -Value $_ } |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
    Select-Object -Unique

  if ($domains.Count -gt 0) {
    $block = New-Object System.Collections.Generic.List[string]
    $block.Add("")
    $block.Add($startMarker)

    foreach ($domain in $domains) {
      $block.Add("127.0.0.1 $domain")
      if (-not $domain.StartsWith("www.")) {
        $block.Add("127.0.0.1 www.$domain")
      }
    }

    $block.Add($endMarker)
    $filtered += $block.ToArray()
  }
}

try {
  Write-HostsContent -Path $hostsPath -Lines $filtered
  ipconfig /flushdns | Out-Null
} catch {
  Write-Error ("Failed to update the Windows hosts file: " + $_.Exception.Message)
  exit 1
}

Write-Output ("SITE_BLOCK_" + $Mode.ToUpper())