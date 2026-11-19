param(
  [ValidateSet('Load','Stress','Spike')][string]$Profile = 'Load',
  [ValidateSet('smoke','pilot','official','rerun','soak')][string]$Kind = 'smoke',
  [int]$Rows = 20000,
  [string]$StagesJson = '',
  [int]$Vus = 5,
  [string]$Duration = '10m',
  [int]$BackendPid = 0,
  [int]$DashboardPort = -1
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$stamp = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'SE Asia Standard Time').ToString('yyyyMMdd-HHmmss')
$runId = "$Kind-$($Profile.ToLower())-$stamp-$([guid]::NewGuid().ToString('N').Substring(0,8))"
$outDir = Join-Path $root "results/$runId"
New-Item -ItemType Directory -Path $outDir | Out-Null
$csv = Join-Path $root "data/$runId.csv"
python (Join-Path $PSScriptRoot 'new-data.py') --run-id $runId --rows $Rows --output $csv
if ($LASTEXITCODE -ne 0) { throw 'CSV generation failed' }
$env:RUN_ID = $runId
$env:CSV_PATH = $csv
$env:BASE_URL = 'http://127.0.0.1:3000'
$env:MODE = if ($Kind -eq 'smoke') {'smoke'} elseif ($Kind -eq 'soak') {'soak'} else {'profile'}
$env:STAGES_JSON = $StagesJson
$env:VUS = "$Vus"
$env:DURATION = $Duration
$env:THINK_SECONDS = '1'
$env:SUMMARY_PATH = Join-Path $outDir 'summary.json'
$env:K6_WEB_DASHBOARD = 'true'
$env:K6_WEB_DASHBOARD_PORT = "$DashboardPort"
$env:K6_WEB_DASHBOARD_PERIOD = '1s'
$env:K6_WEB_DASHBOARD_EXPORT = Join-Path $outDir 'dashboard.html'
$manifest = [ordered]@{
 run_id=$runId; kind=$Kind; profile=$Profile; start=(Get-Date -Format o);
 timezone='Asia/Ho_Chi_Minh'; hostname=[Environment]::MachineName;
 base_url=$env:BASE_URL; csv=$csv; rows=$Rows; mode=$env:MODE;
 stages_override=$StagesJson; vus=$Vus; duration=$Duration; think_seconds=1;
 k6=(& k6 version | Out-String).Trim(); node=(& node --version | Out-String).Trim();
 sut_commit=$null; sut_commit_reason='Input archive has no .git; SHA256 used instead';
 sut_hashes=@(Get-FileHash (Join-Path $root '../backend/server.js'),(Join-Path $root '../backend/database.js') | Select-Object Path,Hash);
 backend_pid=$BackendPid; status='running'
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $outDir 'manifest.json') -Encoding utf8
python (Join-Path $PSScriptRoot 'db-state.py') (Join-Path $root 'runtime/backend/database.sqlite') | Set-Content (Join-Path $outDir 'db-before.json') -Encoding utf8
$sampler = $null
if ($BackendPid -gt 0) {
 $sampler = Start-Job -ArgumentList $BackendPid,(Join-Path $outDir 'resources.csv') -ScriptBlock {
  param($targetPid,$destination)
  'time,cpu_seconds,working_set_bytes,private_bytes,k6_cpu_seconds,k6_working_set_bytes,system_cpu_percent,system_available_bytes' | Set-Content $destination
  while ($true) {
   $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
   if (!$proc) { break }
   $loadProc = @(Get-Process k6 -ErrorAction SilentlyContinue)
   $loadCpu = ($loadProc | Measure-Object CPU -Sum).Sum
   $loadRam = ($loadProc | Measure-Object WorkingSet64 -Sum).Sum
   $systemCpu = (Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'" -ErrorAction SilentlyContinue).PercentProcessorTime
   $systemMem = (Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory -ErrorAction SilentlyContinue).AvailableBytes
   "$(Get-Date -Format o),$($proc.CPU),$($proc.WorkingSet64),$($proc.PrivateMemorySize64),$loadCpu,$loadRam,$systemCpu,$systemMem" | Add-Content $destination
   Start-Sleep -Seconds 1
  }
 }
}
try {
 & k6 run --out "json=$(Join-Path $outDir 'raw.json')" (Join-Path $root "plans/23120330_${Profile}_20261119.js") 2>&1 | Tee-Object -FilePath (Join-Path $outDir 'cli.txt')
 $manifest.exit_code = $LASTEXITCODE
 $manifest.status = if ($LASTEXITCODE -eq 0) {'completed'} else {'failed_or_threshold_failed'}
} finally {
 if ($sampler) { Stop-Job $sampler; Remove-Job $sampler }
 $manifest.end = Get-Date -Format o
 python (Join-Path $PSScriptRoot 'db-state.py') (Join-Path $root 'runtime/backend/database.sqlite') --namespace $runId | Set-Content (Join-Path $outDir 'db-after.json') -Encoding utf8
 $manifest | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $outDir 'manifest.json') -Encoding utf8
}
Write-Output "Artifacts: $outDir"
if ($manifest.exit_code -ne 0) { throw "k6 exit $($manifest.exit_code); inspect artifacts" }
