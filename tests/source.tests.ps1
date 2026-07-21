[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Engine = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\source\scripts\source.ps1'))
$TempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\') + '\'
$TestRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('source-e2e-' + [Guid]::NewGuid().ToString('N'))

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "ASSERT FAILED: $Message" }
}

try {
    New-Item -ItemType Directory -Path $TestRoot | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $TestRoot 'SOURCE.md'), "SENTINEL`n", [System.Text.UTF8Encoding]::new($false))

    & $Engine -Action init -ProjectRoot $TestRoot -ProjectName 'Source E2E' -Agent 'TestAgent'
    Assert-True (Test-Path (Join-Path $TestRoot '.source\config.json')) 'config created'
    Assert-True (Test-Path (Join-Path $TestRoot '.source\state.json')) 'state created'
    Assert-True ((Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot 'SOURCE.md')).Trim() -eq 'SENTINEL') 'existing SOURCE.md preserved'

    $state = Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot '.source\state.json') | ConvertFrom-Json
    Assert-True ($state.phase -eq 'READY') 'init reaches READY'

    & $Engine -Action start -ProjectRoot $TestRoot -Agent 'TestAgent'
    $working = Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot '.source\state.json') | ConvertFrom-Json
    Assert-True ($working.phase -eq 'WORKING') 'start reaches WORKING'
    $revision = [int]$working.revision
    $session = $working.session_id

    & $Engine -Action auto -ProjectRoot $TestRoot -Agent 'TestAgent'
    $resumed = Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot '.source\state.json') | ConvertFrom-Json
    Assert-True ([int]$resumed.revision -eq $revision) 'auto resume is read-only'
    Assert-True ($resumed.session_id -eq $session) 'auto resume preserves session'

    & git -C $TestRoot config user.name 'Source Test'
    & git -C $TestRoot config user.email 'source-test@example.invalid'
    $approved = @('.source','SOURCE.md','AGENTS.md','handoff.md','source.ps1','.gitignore','.gitattributes')
    & $Engine -Action finish -ProjectRoot $TestRoot -Agent 'TestAgent' -SkipConnectors -CommitMessage '驗證 Source E2E' -Include $approved
    $finished = Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot '.source\state.json') | ConvertFrom-Json
    Assert-True ($finished.phase -eq 'READY') 'finish returns READY'
    Assert-True ($finished.session_id -eq $null) 'finish clears session'
    Assert-True ([bool]$finished.git.last_push) 'finish records primary commit'
    Assert-True ([int](& git -C $TestRoot rev-list --count HEAD) -eq 2) 'finish creates primary and status-backfill commits'
    Assert-True (-not @(& git -C $TestRoot status --porcelain).Count) 'finish leaves clean worktree'

    $portableText = (Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot '.source\config.json')) + (Get-Content -Raw -Encoding utf8 (Join-Path $TestRoot '.source\state.json'))
    Assert-True ($portableText -notmatch '(?i)"[A-Z]:\\') 'canonical JSON has no drive-absolute path'
    Assert-True ($portableText -notmatch '"\\\\[^"\\]+') 'canonical JSON has no UNC path'

    & $Engine -Action doctor -ProjectRoot $TestRoot
    Write-Host 'PASS: init -> start -> interrupted resume -> finish -> doctor'
} finally {
    $resolved = [System.IO.Path]::GetFullPath($TestRoot)
    if ($resolved.StartsWith($TempBase, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $resolved)) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
