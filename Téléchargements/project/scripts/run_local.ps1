# Run helper for local development on Windows (PowerShell)
# Usage: .\scripts\run_local.ps1 [command]
# Examples:
#   .\scripts\run_local.ps1 python run.py
#   .\scripts\run_local.ps1 python scripts/init_templates.py

param(
    [string[]]$Args
)

$projectRoot = Split-Path -Parent $PSScriptRoot
Write-Host "Project root: $projectRoot"

# Set PYTHONPATH for the session
$env:PYTHONPATH = $projectRoot
Write-Host "PYTHONPATH set to $env:PYTHONPATH"

if ($Args.Count -eq 0) {
    Write-Host "No command provided. Launching interactive PowerShell with PYTHONPATH set."
    pwsh
} else {
    $command = $Args -join ' '
    Write-Host "Running: $command"
    & cmd /c $command
}
