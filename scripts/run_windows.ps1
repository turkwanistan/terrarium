$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$Python = (Get-Command python).Source
$Args = @("-m", "terrarium.api.server", "--host", "127.0.0.1", "--port", "8080", "--data-dir", "data/live", "--seed", "1701", "--tick-seconds", "1")
$Process = Start-Process -FilePath $Python -ArgumentList $Args -WorkingDirectory $Repo -PassThru
try {
  for ($i = 0; $i -lt 30; $i++) {
    try { Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8080/api/health" | Out-Null; break } catch { Start-Sleep -Milliseconds 250 }
  }
  Start-Process "http://127.0.0.1:8080/"
  Write-Host "Terrarium is running at http://127.0.0.1:8080/"
  Write-Host "Snapshot gallery: http://127.0.0.1:8080/snapshots/"
  Write-Host "Close this window or press Ctrl+C to stop the local world process."
  Wait-Process -Id $Process.Id
} finally {
  if (-not $Process.HasExited) { Stop-Process -Id $Process.Id -Force }
}
