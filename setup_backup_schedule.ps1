# 注册每日自动备份计划任务（开发规范 3.4）
# 用法: powershell -ExecutionPolicy Bypass -File setup_backup_schedule.ps1
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument '-ExecutionPolicy Bypass -File D:\Claude_code\backup.ps1' `
    -WorkingDirectory 'D:\Claude_code'
$trigger = New-ScheduledTaskTrigger -Daily -At 09:05
Register-ScheduledTask -TaskName 'QuantumIntel_DailyBackup' -Action $action -Trigger $trigger -Force
Write-Host "Task 'QuantumIntel_DailyBackup' created successfully (每日 09:05)"
