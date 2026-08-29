param(
  [ValidateSet("web", "native", "canvas")]
  [string]$Mode = "web",
  [string]$ApiUrl = $env:TERRARIUM_API_URL,
  [string]$GatewayUrl = $env:TERRARIUM_PRESENTATION_URL,
  [int]$GatewayPort = 8766,
  [string]$GodotBin = $env:GODOT_BIN
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $Repo "display/godot_reference_v2"

function Test-TerrariumFrameEndpoint([string]$BaseUrl) {
  try {
    $frame = Invoke-RestMethod -Uri ($BaseUrl.TrimEnd('/') + "/api/frame") -Method Get -TimeoutSec 2
    return $frame.schema -eq "terrarium.frame.v1"
  } catch {
    return $false
  }
}

if ([string]::IsNullOrWhiteSpace($ApiUrl)) {
  foreach ($port in @((8765..8799) + 8080)) {
    $candidate = "http://127.0.0.1:$port"
    if (Test-TerrariumFrameEndpoint $candidate) {
      $ApiUrl = $candidate
      break
    }
  }
}

if ($Mode -eq "web") {
  if ([string]::IsNullOrWhiteSpace($GatewayUrl)) {
    if ([string]::IsNullOrWhiteSpace($ApiUrl)) {
      throw "Set TERRARIUM_PRESENTATION_URL=https://host:8766 or TERRARIUM_API_URL=http://host:port so the browser gateway URL can be derived."
    }
    $api = [Uri]$ApiUrl
    $GatewayUrl = "https://$($api.Host):$GatewayPort/"
  }
  Write-Host "Terrarium presentation: Godot Web"
  Write-Host "Browser URL: $GatewayUrl"
  Write-Host "The OptiPlex must already be running the presentation gateway."
  Start-Process $GatewayUrl
  exit 0
}

if ([string]::IsNullOrWhiteSpace($ApiUrl) -or -not (Test-TerrariumFrameEndpoint $ApiUrl)) {
  throw "No readable terrarium.frame.v1 endpoint found. Start/reuse the canonical world separately and set TERRARIUM_API_URL=http://host:port."
}
$ApiUrl = $ApiUrl.TrimEnd('/')

if ($Mode -eq "canvas") {
  Write-Host "Terrarium presentation: Canvas fallback"
  Write-Host "Canonical API (read-only): $ApiUrl"
  Start-Process ($ApiUrl + "/")
  exit 0
}

if (-not (Test-Path (Join-Path $Project "project.godot")) -or -not (Test-Path (Join-Path $Project "art/hero_manifest.json"))) {
  throw "Godot presentation candidate is not generated/validated in this checkout."
}

if ([string]::IsNullOrWhiteSpace($GodotBin)) {
  foreach ($name in @("godot4", "godot", "godot.exe")) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command) {
      $GodotBin = $command.Source
      break
    }
  }
}
if ([string]::IsNullOrWhiteSpace($GodotBin) -or -not (Test-Path $GodotBin)) {
  throw "Godot 4 not found. Set GODOT_BIN to the Godot 4 executable path for explicit -Mode native use."
}

Write-Host "Terrarium presentation: native Godot development/UAT client"
Write-Host "Canonical API (read-only): $ApiUrl"
Write-Host "Canvas rollback: .\scripts\run_presentation.ps1 -Mode canvas -ApiUrl $ApiUrl"
Write-Host "This process owns presentation only; closing/failing it does not stop Moss's world."

& $GodotBin --path $Project -- --live --api-url $ApiUrl
exit $LASTEXITCODE
