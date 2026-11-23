param([Parameter(Mandatory)][ValidateRange(0,100)][int]$SelfAssessedGrade)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$state = Get-Content (Join-Path $root 'submission-state.json') -Raw | ConvertFrom-Json
$missing = @()
foreach ($key in @('hostname_matches_previous_homework','human_review_complete','critique_approved','full_chat_export_attached','k6_raw_json_submission_convention_confirmed')) {
 if (!$state.$key) { $missing += $key }
}
if (!$state.github_public_url) { $missing += 'github_public_url' }
if (!$state.youtube_unlisted_url) { $missing += 'youtube_unlisted_url' }
if ($null -eq $state.self_assessed_grade -or $state.self_assessed_grade -ne $SelfAssessedGrade) { $missing += 'user-approved self_assessed_grade' }
foreach ($profile in @('Load','Stress','Spike')) {
 $path = $state.resource_screenshots.$profile
 if (!$path -or !(Test-Path -LiteralPath (Join-Path $root $path))) { $missing += "$profile combined screenshot" }
 $photoRun = $state.resource_screenshot_runs.$profile
 if (!$photoRun) { $missing += "$profile screenshot/run mapping"; continue }
 $photoManifestPath = Join-Path $root "results/$photoRun/manifest.json"
 if (!(Test-Path -LiteralPath $photoManifestPath)) { $missing += "$profile matched run manifest"; continue }
 $photoRunState = Get-Content -LiteralPath $photoManifestPath -Raw | ConvertFrom-Json
 if ($photoRunState.status -ne 'completed' -or $photoRunState.profile -ne $profile) { $missing += "$profile completed matching run" }
 foreach ($artifact in @('raw.json','summary.json','dashboard.html','verification.json')) {
  if (!(Test-Path -LiteralPath (Join-Path $root "results/$photoRun/$artifact"))) { $missing += "$profile $artifact" }
 }
}
if ($missing.Count) { throw "Submission remains incomplete: $($missing -join ', ')" }
$name = '23120330_HW05_AI_Performance_{0:000}.zip' -f $SelfAssessedGrade
$destination = Join-Path $root "output/$name"
if (Test-Path -LiteralPath $destination) { throw 'ZIP exists; review before replacing' }
$staging = Join-Path $root "tmp/package-$([guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $staging -Force | Out-Null
foreach ($path in @('README.md','submission-state.json','git-commit-log.txt','docs','output/pdf','plans','scripts','skills')) {
 $source = Join-Path $root $path
 if (!(Test-Path -LiteralPath $source)) { throw "Missing $path" }
 $target = Join-Path $staging $path
 New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
 Copy-Item -LiteralPath $source -Destination $target -Recurse
}
$manifests = Get-ChildItem (Join-Path $root 'results') -Filter manifest.json -Recurse | ForEach-Object { Get-Content $_.FullName -Raw | ConvertFrom-Json }
# Select the required runs: primary runs with Task Manager screenshots, soak, skill-demo, smoke, and official
$primaryRunIds = @($state.resource_screenshot_runs.Load, $state.resource_screenshot_runs.Stress, $state.resource_screenshot_runs.Spike)
$chosen = @($manifests | Where-Object { 
    $_.status -eq 'completed' -and (
        $_.run_id -in $primaryRunIds -or 
        $_.kind -in @('soak','skill-demo','smoke') -or 
        ($_.kind -eq 'official' -and $_.run_id -notmatch '20261122')
    )
})
New-Item -ItemType Directory -Path (Join-Path $staging 'results'),(Join-Path $staging 'data') -Force | Out-Null
foreach ($run in $chosen) {
    $src = Join-Path $root "results/$($run.run_id)"
    $dst = Join-Path $staging "results/$($run.run_id)"
    # To keep total package strictly under 20MB, for official runs keep dashboards, summaries, manifests and views
    # while the primary rerun folders provide full raw.json traces.
    if ($run.kind -eq 'official') {
        New-Item -ItemType Directory -Path $dst -Force | Out-Null
        Get-ChildItem -LiteralPath $src | Where-Object { $_.Name -ne 'raw.json' } | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $dst -Recurse
        }
    } else {
        Copy-Item -LiteralPath $src -Destination (Join-Path $staging 'results') -Recurse
    }
    if ($run.csv -and (Test-Path -LiteralPath $run.csv)) {
        Copy-Item -LiteralPath $run.csv -Destination (Join-Path $staging 'data')
    }
}
Copy-Item -LiteralPath (Join-Path $root 'results/hardware') -Destination (Join-Path $staging 'results') -Recurse
Copy-Item -LiteralPath (Join-Path $root 'results/contract-probe.json') -Destination (Join-Path $staging 'results')
if (Test-Path (Join-Path $root 'results/issues')) {
    Copy-Item -LiteralPath (Join-Path $root 'results/issues') -Destination (Join-Path $staging 'results') -Recurse
}
foreach ($profile in @('Load','Stress','Spike')) {
    $screen = $state.resource_screenshots.$profile
    $target = Join-Path $staging $screen
    New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $root $screen) -Destination $target
}

# Compress using Python zipfile with maximum compression (level 9) to guarantee under 20MB
$pyScript = @"
import zipfile, os, sys

staging = sys.argv[1]
dest = sys.argv[2]

with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for root, dirs, files in os.walk(staging):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, staging)
            zf.write(full, rel)
"@
$tmpPy = Join-Path $root "tmp/zip_compress.py"
Set-Content -LiteralPath $tmpPy -Value $pyScript -Encoding utf8
python $tmpPy $staging $destination
Remove-Item -LiteralPath $tmpPy -Force

$zipBytes = (Get-Item -LiteralPath $destination).Length
$zipMB = [math]::Round($zipBytes / 1MB, 2)
if ($zipBytes -gt 20971520) {
    throw "ZIP package exceeds 20MB: $zipMB MB ($zipBytes bytes)"
}
Write-Output "Successfully created ZIP package: $name"
Write-Output "Size: $zipMB MB ($zipBytes bytes) - under 20MB limit"
Get-FileHash -LiteralPath $destination -Algorithm SHA256
Remove-Item -LiteralPath $staging -Recurse -Force
Write-Output 'Created private submission ZIP; no push/upload/publication performed.'
