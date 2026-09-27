$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# ─────────────────────────────────────────────
# llama server window
# ─────────────────────────────────────────────

$ServerCommand = @'
$Host.UI.RawUI.BackgroundColor = 'Black'
$Host.UI.RawUI.ForegroundColor = 'White'
Clear-Host

Write-Host ""
Write-Host "  BROSEIDON :: LLAMA SERVER" -ForegroundColor Cyan
Write-Host "  ==========================" -ForegroundColor DarkGray
Write-Host ""

Write-Host "  [PROCESSING] Starting llama server..." -ForegroundColor Yellow
Write-Host "  Model: backend\models\a9b.gguf" -ForegroundColor DarkGray
Write-Host ""

try {
    & llama serve `
        --model "backend\models\a9b.gguf" `
        --n-gpu-layers auto `
        --ctx-size 4096 `
        --batch-size 128 `
        --fit-target 512 `
        --port 8080

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  [ERROR] llama server exited with code $LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to close"
    }
}
catch {
    Write-Host ""
    Write-Host "  [ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
}
'@

# ─────────────────────────────────────────────
# application window
# ─────────────────────────────────────────────

$AppCommand = @'
$Host.UI.RawUI.BackgroundColor = 'Black'
$Host.UI.RawUI.ForegroundColor = 'White'
Clear-Host

Write-Host ""
Write-Host "  BROSEIDON :: APPLICATION" -ForegroundColor Cyan
Write-Host "  ========================" -ForegroundColor DarkGray
Write-Host ""

Write-Host "  [PROCESSING] Waiting for llama server..." -ForegroundColor Yellow

$ready = $false
$timeout = 60
$start = Get-Date

while (((Get-Date) - $start).TotalSeconds -lt $timeout) {
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:8080/health" -TimeoutSec 2
        $ready = $true
        break
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host ""
    Write-Host "  [ERROR] llama server did not become ready within $timeout seconds." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "  [RUNNING] llama server is ready." -ForegroundColor Green
Write-Host ""

try {
    python main.py

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  [ERROR] main.py exited with code $LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to close"
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host ""
    Write-Host "  [ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close"
    exit 1
}
'@

# ─────────────────────────────────────────────
# launch windows
# ─────────────────────────────────────────────

Start-Process powershell.exe `
    -WorkingDirectory $Root `
    -ArgumentList @(
        "-NoExit",
        "-Command",
        $ServerCommand
    )

Start-Sleep -Milliseconds 500

Start-Process powershell.exe `
    -WorkingDirectory $Root `
    -ArgumentList @(
        "-NoExit",
        "-Command",
        $AppCommand
    )