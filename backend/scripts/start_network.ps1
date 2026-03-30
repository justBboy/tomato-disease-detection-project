param(
  [string]$CondaEnv = "tomato-ai",
  [int]$Port = 8000
)

Write-Output "Stopping existing tomato API uvicorn processes..."
$existing = Get-CimInstance Win32_Process | Where-Object {
  $_.Name -eq "python.exe" -and (
    $_.CommandLine -like "*uvicorn*backend.app.main:app*" -or
    $_.CommandLine -like "*uvicorn*app.main:app*"
  )
}

foreach ($proc in $existing) {
  try {
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
    Write-Output "Stopped PID $($proc.ProcessId)"
  } catch {
    Write-Output "Could not stop PID $($proc.ProcessId): $($_.Exception.Message)"
  }
}

try {
  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($listener) {
    $listenerPid = $listener.OwningProcess
    Write-Output "Port $Port already in use by PID $listenerPid. Attempting to stop it..."
    taskkill /PID $listenerPid /F | Out-Null
    Start-Sleep -Seconds 1
  }
} catch {
  Write-Output "Could not inspect/clear port $Port: $($_.Exception.Message)"
}

Write-Output ""
Write-Output "Starting API on 0.0.0.0:$Port ..."
Write-Output "Press CTRL+C to stop."
conda run -n $CondaEnv python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $Port --reload
