param(
    [int]$Port = 8501,
    [string]$CloudflaredExe = ''
)

$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent $PSScriptRoot
$labWorkspace = [System.IO.Path]::GetFullPath((Join-Path $labRoot '..\..'))
$labRuntime = Join-Path $labRoot '.runtime'
$labStatePath = Join-Path $labRuntime 'public_tunnel.json'

if (-not $CloudflaredExe) {
    $labPortable = Join-Path $labWorkspace '.tools\cloudflared.exe'
    if (Test-Path -LiteralPath $labPortable) {
        $CloudflaredExe = $labPortable
    } else {
        $labCommand = Get-Command cloudflared -ErrorAction SilentlyContinue
        if ($labCommand) { $CloudflaredExe = $labCommand.Source }
    }
}
if (-not $CloudflaredExe -or -not (Test-Path -LiteralPath $CloudflaredExe)) {
    throw 'cloudflared not found. Install it or pass -CloudflaredExe with its path.'
}
$CloudflaredExe = (Resolve-Path -LiteralPath $CloudflaredExe).Path
$labOrigin = 'http://127.0.0.1:' + $Port
$labHealth = Invoke-WebRequest -Uri ($labOrigin + '/_stcore/health') -UseBasicParsing -TimeoutSec 10
if ($labHealth.StatusCode -ne 200) { throw 'Start the Streamlit UI before creating the tunnel.' }
New-Item -ItemType Directory -Path $labRuntime -Force | Out-Null

$labState = $null
if (Test-Path -LiteralPath $labStatePath) {
    $labPrevious = Get-Content -LiteralPath $labStatePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $labExisting = Get-Process -Id $labPrevious.pid -ErrorAction SilentlyContinue
    if ($labExisting) {
        if ($labExisting.Path -ne $CloudflaredExe -or
            $labExisting.StartTime.ToUniversalTime().Ticks -ne ([datetime]$labPrevious.started_utc).ToUniversalTime().Ticks) {
            throw 'Saved PID belongs to another process. Inspect .runtime/public_tunnel.json before proceeding.'
        }
        if ($labPrevious.origin -ne $labOrigin) { throw 'Existing tunnel points to another origin. Stop it first.' }
        $labState = $labPrevious
    }
}

if (-not $labState) {
    $labStamp = Get-Date -Format 'yyyyMMddTHHmmssfff'
    $labStdout = Join-Path $labRuntime ('cloudflared-' + $labStamp + '.stdout.log')
    $labStderr = Join-Path $labRuntime ('cloudflared-' + $labStamp + '.stderr.log')
    $labProcess = Start-Process -FilePath $CloudflaredExe -ArgumentList @(
        'tunnel', '--url', $labOrigin, '--protocol', 'http2', '--no-autoupdate'
    ) -WorkingDirectory $labRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $labStdout -RedirectStandardError $labStderr
    $labState = [pscustomobject]@{
        pid = $labProcess.Id
        executable = $CloudflaredExe
        started_utc = $labProcess.StartTime.ToUniversalTime().ToString('o')
        origin = $labOrigin
        url = ''
        stdout_log = $labStdout
        stderr_log = $labStderr
    }
    $labState | ConvertTo-Json | Set-Content -LiteralPath $labStatePath -Encoding UTF8
}

for ($labAttempt = 0; $labAttempt -lt 35; $labAttempt++) {
    $labLogs = ''
    foreach ($labLogPath in @($labState.stdout_log, $labState.stderr_log)) {
        if (Test-Path -LiteralPath $labLogPath) {
            $labLogs += Get-Content -LiteralPath $labLogPath -Raw -Encoding UTF8
        }
    }
    $labUrlMatch = [regex]::Match($labLogs, 'https://[a-z0-9-]+\.trycloudflare\.com\b')
    if ($labUrlMatch.Success) {
        $labState.url = $labUrlMatch.Value
        $labState | ConvertTo-Json | Set-Content -LiteralPath $labStatePath -Encoding UTF8
        Write-Output ('Public URL: ' + $labState.url)
        Write-Output ('Tunnel PID: ' + $labState.pid)
        Write-Output 'Keep the Streamlit UI running. Stop the tunnel with scripts/stop_public.ps1.'
        return
    }
    if (-not (Get-Process -Id $labState.pid -ErrorAction SilentlyContinue)) {
        throw ('Tunnel exited. Read log: ' + $labState.stderr_log)
    }
    Start-Sleep -Seconds 1
}
throw ('Tunnel URL not available yet. Read log: ' + $labState.stderr_log)
