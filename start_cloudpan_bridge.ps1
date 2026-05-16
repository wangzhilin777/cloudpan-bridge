$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$venvDir = ".venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"
$configFile = ".work\openlist-config.json"
$appUrl = "http://127.0.0.1:8765"
$existing = $null

try {
    $existing = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction Stop | Select-Object -First 1
} catch {
    $existing = $null
}

if ($existing) {
    Write-Host "[0/4] Existing service detected on 127.0.0.1:8765, opening browser..."
    Start-Process $appUrl
    return
}

if (-not (Test-Path -LiteralPath $pythonExe)) {
    Write-Host "[1/4] Creating virtual environment..."
    py -3 -m venv $venvDir
}

Write-Host "[2/4] Installing or refreshing project dependencies..."
& $pythonExe -m pip install -e .

if (-not (Test-Path -LiteralPath $configFile)) {
    Write-Host "[3/4] Creating example config..."
    & $pythonExe -m cloudpan_bridge.cli init-config --path $configFile
} else {
    Write-Host "[3/4] Config already exists: $configFile"
}

Write-Host "[4/4] Starting local web console..."
Write-Host "Browser will open automatically after the server is ready: $appUrl"

$job = Start-Job -ScriptBlock {
    param($url)
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 | Out-Null
            Start-Process $url
            return
        } catch {
            Start-Sleep -Seconds 1
        }
    }
} -ArgumentList $appUrl

try {
    & $pythonExe -m cloudpan_bridge.cli serve --config $configFile
} catch {
    Write-Host ""
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press Enter to close this window..."
    Read-Host | Out-Null
} finally {
    if ($job) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue | Out-Null
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue | Out-Null
    }
}
