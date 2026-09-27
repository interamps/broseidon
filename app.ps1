$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$port = (
    Get-Content "$Root\settings.conf" |
    Where-Object { $_ -match '^\s*port\s*=' } |
    ForEach-Object { ($_ -split '=', 2)[1].Trim() }
)

$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Orange"
Clear-Host

Write-Host "[1] Waiting for llama server..."

while ($true) {
    try {
        $null = Invoke-WebRequest "http://127.0.0.1:$port/health" -TimeoutSec 2
        break
    }
    catch {
        Start-Sleep 1
    }
}

Write-Host "[2] Server ready."
Write-Host ""

python main.py

Write-Host ""
Write-Host "[3] Application stopped."
Write-Host "Exit code: $LASTEXITCODE"
Read-Host "Press Enter to close"