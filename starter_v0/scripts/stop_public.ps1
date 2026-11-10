$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent $PSScriptRoot
$labStatePath = Join-Path $labRoot '.runtime\public_tunnel.json'
if (-not (Test-Path -LiteralPath $labStatePath)) {
    Write-Output 'No managed public tunnel.'
    return
}
$labState = Get-Content -LiteralPath $labStatePath -Raw -Encoding UTF8 | ConvertFrom-Json
$labProcess = Get-Process -Id $labState.pid -ErrorAction SilentlyContinue
if ($labProcess) {
    if ($labProcess.ProcessName -ne 'cloudflared' -or $labProcess.Path -ne $labState.executable -or
        $labProcess.StartTime.ToUniversalTime().Ticks -ne ([datetime]$labState.started_utc).ToUniversalTime().Ticks) {
        throw 'Process identity differs from the saved tunnel. Nothing was stopped.'
    }
    Stop-Process -Id $labProcess.Id
}
Remove-Item -LiteralPath $labStatePath
Write-Output 'Public tunnel stopped. Streamlit was left running.'
