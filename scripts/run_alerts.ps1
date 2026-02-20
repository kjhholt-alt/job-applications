$ErrorActionPreference = "Stop"

$project = "C:\Users\Kruz\Desktop\Projects\job-applications"
$python = "python"
$script = Join-Path $project "scripts\run_alerts.py"

Set-Location $project

& $python $script
