$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$cfg = Get-Content "$Root\settings.conf" | Where-Object {
    $_ -match '^\s*[^#=\[]+=.*$'
} | ForEach-Object {
    $p = $_ -split '=', 2
    [PSCustomObject]@{
        Key   = $p[0].Trim()
        Value = $p[1].Trim()
    }
}

function Get-Setting($key) {
    ($cfg | Where-Object Key -eq $key).Value
}

$bg = Get-Setting "background"
$fg = Get-Setting "foreground"
$model = Get-Setting "name"
$gpu = Get-Setting "gpu_layers"
$ctx = Get-Setting "ctx_size"
$batch = Get-Setting "batch_size"
$fit = Get-Setting "fit_target"
$port = Get-Setting "port"

$Host.UI.RawUI.BackgroundColor = $bg
$Host.UI.RawUI.ForegroundColor = $fg
Clear-Host

Write-Host "[1] Starting llama server..."
Write-Host "Model: backend\models\$model"
Write-Host "GPU layers: $gpu"
Write-Host "Context: $ctx"
Write-Host "Batch: $batch"
Write-Host "Fit target: $fit"
Write-Host "Port: $port"
Write-Host ""

llama serve `
    --model "backend\models\$model" `
    --gpu-layers "$gpu" `
    --ctx-size "$ctx" `
    --batch-size "$batch" `
    --fit-target "$fit" `
    --port "$port"

Write-Host ""
Write-Host "[2] Server stopped."
Write-Host "Exit code: $LASTEXITCODE"
Read-Host "Press Enter to close"