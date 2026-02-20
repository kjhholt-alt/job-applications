$ErrorActionPreference = "Stop"

$taskName = "JobFinderAlerts"
$project = "C:\Users\Kruz\Desktop\Projects\job-applications"
$script = Join-Path $project "scripts\run_alerts.ps1"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -Hourly -At (Get-Date).Date.AddHours(8)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description "Run Job Finder alerts hourly" -Force

Write-Output "Scheduled task '$taskName' created."
