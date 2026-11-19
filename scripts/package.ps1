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
$chosen = @($manifests | Where-Object { $_.status -eq 'completed' -and $_.kind -in @('official','soak','skill-demo','smoke','pilot','rerun') })
New-Item -ItemType Directory -Path (Join-Path $staging 'results'),(Join-Path $staging 'data') -Force | Out-Null
foreach ($run in $chosen) {
 Copy-Item -LiteralPath (Join-Path $root "results/$($run.run_id)") -Destination (Join-Path $staging 'results') -Recurse
 Copy-Item -LiteralPath $run.csv -Destination (Join-Path $staging 'data')
}
Copy-Item -LiteralPath (Join-Path $root 'results/hardware') -Destination (Join-Path $staging 'results') -Recurse
Copy-Item -LiteralPath (Join-Path $root 'results/contract-probe.json') -Destination (Join-Path $staging 'results')
foreach ($profile in @('Load','Stress','Spike')) {
 $screen = $state.resource_screenshots.$profile
 $target = Join-Path $staging $screen
 New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
 Copy-Item -LiteralPath (Join-Path $root $screen) -Destination $target
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($staging,$destination)
Get-FileHash -LiteralPath $destination -Algorithm SHA256
Write-Output 'Created private submission ZIP; no push/upload/publication performed.'
