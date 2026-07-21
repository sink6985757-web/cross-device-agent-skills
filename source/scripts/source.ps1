[CmdletBinding()]
param(
    [ValidateSet('auto','bootstrap','init','status','next','start','finish','doctor','deploy-skills','sync-dotfiles','complete')]
    [string]$Action = 'auto',
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$ProjectName,
    [string]$Agent = 'Agent',
    [string]$CommitMessage,
    [string[]]$Include = @(),
    [ValidateSet('notion','obsidian','cdn')]
    [string]$Connector,
    [ValidateSet('VERIFIED','PARTIAL','BLOCKED','SKIPPED')]
    [string]$ConnectorStatus = 'VERIFIED',
    [string]$ExternalId,
    [string]$Note,
    [switch]$Yes,
    [switch]$DryRun,
    [switch]$SkipGit,
    [switch]$SkipConnectors,
    [switch]$CreateRemote
)

$ErrorActionPreference = 'Stop'
$script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$script:AssetRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\assets'))
$script:DistributionRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))

function Get-NowIso {
    (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Get-RelativePath {
    param([string]$Base, [string]$Path)
    $baseUri = [Uri](([System.IO.Path]::GetFullPath($Base).TrimEnd('\') + '\'))
    $pathUri = [Uri][System.IO.Path]::GetFullPath($Path)
    [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($pathUri).ToString()).Replace('\','/')
}

function Resolve-Root {
    param([string]$Start, [switch]$ForInit)
    $resolved = [System.IO.Path]::GetFullPath($Start)
    if ($ForInit) { return $resolved }
    $cursor = Get-Item -LiteralPath $resolved
    if (-not $cursor.PSIsContainer) { $cursor = $cursor.Directory }
    while ($cursor) {
        if (Test-Path -LiteralPath (Join-Path $cursor.FullName '.source\state.json')) {
            return $cursor.FullName
        }
        $cursor = $cursor.Parent
    }
    return $resolved
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    Get-Content -Raw -Encoding utf8 -LiteralPath $Path | ConvertFrom-Json
}

function Write-JsonAtomic {
    param([string]$Path, $Value)
    if ($DryRun) { return }
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temp = Join-Path $directory ('.tmp-' + [Guid]::NewGuid().ToString('N') + '.json')
    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($temp, $json + "`n", $script:Utf8NoBom)
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Write-TextAtomic {
    param([string]$Path, [string]$Text)
    if ($DryRun) { return }
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temp = Join-Path $directory ('.tmp-' + [Guid]::NewGuid().ToString('N'))
    [System.IO.File]::WriteAllText($temp, $Text.TrimEnd() + "`n", $script:Utf8NoBom)
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Get-ConfigPath { param([string]$Root) Join-Path $Root '.source\config.json' }
function Get-StatePath { param([string]$Root) Join-Path $Root '.source\state.json' }

function Write-Handoff {
    param([string]$Root, $Config, $State)
    $steps = @($State.next_steps)
    $stepText = if ($steps.Count) {
        (($steps | ForEach-Object -Begin { $n = 0 } -Process { $n++; "$n. $_" }) -join "`n")
    } else { '1. 執行 `./source.ps1 -Action next`。' }
    $connectorLines = @()
    foreach ($property in $State.connectors.PSObject.Properties) {
        $connectorLines += "- $($property.Name)：$($property.Value.status)"
    }
    $gitLine = if ($State.git.enabled) {
        "$($State.git.status)；branch=$($State.git.branch)；last_push=$($State.git.last_push)"
    } else { 'NOT_CONFIGURED' }
    $text = @"
# Handoff

> 本檔由 source.ps1 產生；canonical 狀態是 .source/state.json。

## 目前做到哪

$($State.summary)

## 狀態

- Phase：$($State.phase)
- Revision：$($State.revision)
- Last action：$($State.last_action)
- Git：$gitLine

## 下一步

$stepText

## Connectors

$($connectorLines -join "`n")

## 最後更新

- $($State.updated_at)
- $($State.actor.agent) @ $($State.actor.device)
"@
    Write-TextAtomic -Path (Join-Path $Root 'handoff.md') -Text $text
}

function Save-Checkpoint {
    param([string]$Root, $Config, $State, [string]$LastAction, [string[]]$NextSteps)
    $State.revision = [int]$State.revision + 1
    $State.last_action = $LastAction
    $State.updated_at = Get-NowIso
    $State.actor.agent = $Agent
    $State.actor.device = $env:COMPUTERNAME
    if ($null -ne $NextSteps) { $State.next_steps = @($NextSteps) }
    Write-JsonAtomic -Path (Get-StatePath $Root) -Value $State
    Write-Handoff -Root $Root -Config $Config -State $State
}

function Copy-TemplateIfMissing {
    param([string]$TemplateName, [string]$Destination)
    if (Test-Path -LiteralPath $Destination) { return $false }
    $source = Join-Path $script:AssetRoot $TemplateName
    if (-not (Test-Path -LiteralPath $source)) { throw "Template missing: $source" }
    if (-not $DryRun) { Copy-Item -LiteralPath $source -Destination $Destination }
    return $true
}

function Merge-GitIgnore {
    param([string]$Root)
    $path = Join-Path $Root '.gitignore'
    $required = @('desktop.ini','*.tmp','~$*','.env','.env.*','*.key','*.pem','credentials.*','.source/backups/')
    $existing = if (Test-Path -LiteralPath $path) { @(Get-Content -Encoding utf8 -LiteralPath $path) } else { @() }
    $missing = @($required | Where-Object { $existing -notcontains $_ })
    if ($missing.Count -gt 0) {
        Write-TextAtomic -Path $path -Text ((@($existing) + $missing) -join "`n")
    }
}

function Get-DirectoryHash {
    param([string]$Path)
    $builder = [System.Text.StringBuilder]::new()
    foreach ($file in Get-ChildItem -LiteralPath $Path -Recurse -File -Force | Sort-Object FullName) {
        $relative = Get-RelativePath -Base $Path -Path $file.FullName
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        [void]$builder.AppendLine("$relative`:$hash")
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = $script:Utf8NoBom.GetBytes($builder.ToString())
        ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','')
    } finally { $sha.Dispose() }
}

function Assert-ChildPath {
    param([string]$Parent, [string]$Child)
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    $childFull = [System.IO.Path]::GetFullPath($Child)
    if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe target outside managed root: $childFull"
    }
}

function Install-ManagedSkills {
    param([string]$SourceRoot)
    $userRoot = [Environment]::GetFolderPath('UserProfile')
    $destinationRoot = Join-Path $userRoot '.agents\skills'
    $backupRoot = Join-Path $userRoot ('.agents\skill-backups\source-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    $managed = @('source','project-init','startup','shutdown','notion-conversation-log')
    $results = @()
    if (-not $DryRun) { New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null }
    foreach ($name in $managed) {
        $source = Join-Path $SourceRoot $name
        $destination = Join-Path $destinationRoot $name
        if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) { throw "Skill source missing: $source" }
        if ([System.IO.Path]::GetFullPath($source) -ieq [System.IO.Path]::GetFullPath($destination)) {
            $results += "$name=CANONICAL"
            continue
        }
        if (Test-Path -LiteralPath $destination) {
            $same = (Get-DirectoryHash $source) -eq (Get-DirectoryHash $destination)
            if ($same) { $results += "$name=MATCH"; continue }
            if (-not $Yes) { throw "Skill conflict: $name differs. Re-run with -Yes to back up and replace the installed copy." }
            Assert-ChildPath -Parent $destinationRoot -Child $destination
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
                Copy-Item -LiteralPath $destination -Destination (Join-Path $backupRoot $name) -Recurse -Force
                Remove-Item -LiteralPath $destination -Recurse -Force
            }
        }
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
            Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $destination -Recurse -Force
        }
        $results += if ($DryRun) { "$name=WOULD_INSTALL" } else { "$name=INSTALLED" }
    }
    $adapterScript = Join-Path $userRoot '.agents\scripts\install-agent-adapters.ps1'
    if ((-not $DryRun) -and (Test-Path -LiteralPath $adapterScript)) { & $adapterScript }
    $results
}

function Get-ChezmoiExecutable {
    $command = Get-Command chezmoi -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $userPath = [Environment]::GetEnvironmentVariable('Path','User')
    foreach ($entry in @($userPath -split ';' | Where-Object { $_ })) {
        $candidate = Join-Path $entry 'chezmoi.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    $packageRoot = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
    $package = Get-ChildItem -LiteralPath $packageRoot -Directory -Filter 'twpayne.chezmoi*' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($package) {
        $candidate = Join-Path $package.FullName 'chezmoi.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    $null
}

function Sync-Dotfiles {
    param([string]$Message)
    $command = Get-ChezmoiExecutable
    if (-not $command) {
        return [pscustomobject]@{ status='BLOCKED'; detail='chezmoi 不在 PATH；執行 winget install --id twpayne.chezmoi -e 後重試。' }
    }
    $userRoot = [Environment]::GetFolderPath('UserProfile')
    $targets = @(
        (Join-Path $userRoot '.agents'),
        (Join-Path $userRoot '.codex\AGENTS.md'),
        (Join-Path $userRoot '.claude\CLAUDE.md'),
        (Join-Path $userRoot '.gemini\GEMINI.md')
    ) | Where-Object { Test-Path -LiteralPath $_ }
    $sourcePath = (& $command source-path).Trim()
    if (-not $DryRun) {
        foreach ($name in @('source','project-init','startup','shutdown','notion-conversation-log')) {
            $liveSkill = Join-Path $userRoot ".agents\skills\$name"
            $sourceManifest = Join-Path $sourcePath "dot_agents\skills\$name\SKILL.md"
            if ((Test-Path -LiteralPath $liveSkill) -and (-not (Test-Path -LiteralPath $sourceManifest))) {
                & $command add --force --no-tty $liveSkill
                if ($LASTEXITCODE -ne 0) { throw "chezmoi add failed for skill: $name" }
            }
            foreach ($managedPath in @(& $command managed --include files --path-style absolute $liveSkill)) {
                if ($managedPath -and (-not (Test-Path -LiteralPath $managedPath))) {
                    & $command forget --force --no-tty $managedPath
                    if ($LASTEXITCODE -ne 0) { throw "chezmoi forget failed for stale path: $managedPath" }
                }
            }
        }
        & $command re-add --force --no-tty @targets
        if ($LASTEXITCODE -ne 0) { throw 'chezmoi re-add failed.' }
    }
    $dirty = @(& git -C $sourcePath status --porcelain)
    if ($dirty.Count -eq 0) { return [pscustomobject]@{ status='VERIFIED'; detail='dotfiles already current' } }
    if (-not $Yes) { return [pscustomobject]@{ status='PARTIAL'; detail="dotfiles changed at runtime; re-run with -Yes to commit and push" } }
    if (-not $DryRun) {
        & git -C $sourcePath add --all
        & git -C $sourcePath commit -m $Message
        if ($LASTEXITCODE -ne 0) { throw 'dotfiles commit failed.' }
        & git -C $sourcePath push origin HEAD
        if ($LASTEXITCODE -ne 0) { throw 'dotfiles push failed.' }
    }
    [pscustomobject]@{ status='VERIFIED'; detail='dotfiles committed and pushed' }
}

function Get-GitSnapshot {
    param([string]$Root, [switch]$Fetch)
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return [pscustomobject]@{ enabled=$false; status='BLOCKED'; branch=$null; remote=$null; ahead=0; behind=0 }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) {
        return [pscustomobject]@{ enabled=$false; status='NOT_CONFIGURED'; branch=$null; remote=$null; ahead=0; behind=0 }
    }
    $inside = (& git -C $Root rev-parse --is-inside-work-tree 2>$null)
    if ($LASTEXITCODE -ne 0 -or $inside -ne 'true') {
        return [pscustomobject]@{ enabled=$false; status='NOT_CONFIGURED'; branch=$null; remote=$null; ahead=0; behind=0 }
    }
    $branch = (& git -C $Root branch --show-current).Trim()
    $remotes = @(& git -C $Root remote)
    $remote = if ($remotes -contains 'origin') { (& git -C $Root remote get-url origin).Trim() } else { $null }
    if ($Fetch -and $remote) {
        $fetchHead = Join-Path $Root '.git\FETCH_HEAD'
        $fresh = (Test-Path -LiteralPath $fetchHead) -and ((Get-Date) - (Get-Item $fetchHead).LastWriteTime).TotalMinutes -lt 30
        if (-not $fresh) { & git -C $Root fetch origin 2>$null | Out-Null }
    }
    $ahead = 0; $behind = 0
    if ($remote) {
        $upstream = (& git -C $Root for-each-ref --format='%(upstream:short)' "refs/heads/$branch").Trim()
        if ($upstream) {
            $counts = ((& git -C $Root rev-list --left-right --count "HEAD...$upstream").Trim() -split '\s+')
            if ($counts.Count -ge 2) { $ahead=[int]$counts[0]; $behind=[int]$counts[1] }
        }
    }
    $dirty = @(& git -C $Root status --porcelain)
    $status = if ($dirty.Count) { 'DIRTY' } elseif ($behind -gt 0) { 'BEHIND' } else { 'CLEAN' }
    [pscustomobject]@{ enabled=$true; status=$status; branch=$branch; remote=$remote; ahead=$ahead; behind=$behind }
}

function Update-GitState {
    param([string]$Root, $State, [switch]$Fetch)
    $snapshot = Get-GitSnapshot -Root $Root -Fetch:$Fetch
    $State.git.enabled = $snapshot.enabled
    $State.git.status = $snapshot.status
    $State.git.branch = $snapshot.branch
    $State.git.remote = $snapshot.remote
    $State.git.ahead = $snapshot.ahead
    $State.git.behind = $snapshot.behind
}

function Assert-NoSensitiveChanges {
    param([string]$Root)
    $sensitive = '(?i)(^|[\\/])(\.env(?:\..*)?|credentials[^\\/]*|id_rsa|id_ed25519|[^\\/]+\.(key|pem|pfx|p12))$'
    foreach ($line in @(& git -C $Root status --porcelain)) {
        $path = if ($line.Length -gt 3) { $line.Substring(3).Trim('"') } else { '' }
        if ($path -match $sensitive) { throw "Sensitive path must not be committed: $path" }
    }
}

function Invoke-GitFinish {
    param([string]$Root, [string]$Message, [string[]]$ExtraIncludes)
    $snapshot = Get-GitSnapshot -Root $Root
    if (-not $snapshot.enabled) { return [pscustomobject]@{ status='NOT_CONFIGURED'; commit=$null; pushed=$false } }
    Assert-NoSensitiveChanges -Root $Root
    $changes = @(& git -C $Root status --porcelain)
    if ($changes.Count -eq 0) { return [pscustomobject]@{ status='NO_CHANGES'; commit=$null; pushed=$true } }
    if ($DryRun) { return [pscustomobject]@{ status='DRY_RUN'; commit=$null; pushed=$false } }
    & git -C $Root add -u
    foreach ($path in $ExtraIncludes) {
        $full = [System.IO.Path]::GetFullPath((Join-Path $Root $path))
        Assert-ChildPath -Parent $Root -Child $full
        & git -C $Root add -- $path
    }
    $unstagedUntracked = @(& git -C $Root ls-files --others --exclude-standard)
    if ($unstagedUntracked.Count -gt 0) {
        throw "Untracked files remain. Review them and pass approved paths with -Include: $($unstagedUntracked -join ', ')"
    }
    $cached = @(& git -C $Root diff --cached --name-only)
    if ($cached.Count -eq 0) { return [pscustomobject]@{ status='NO_STAGED_CHANGES'; commit=$null; pushed=$false } }
    & git -C $Root diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw 'git diff --cached --check failed.' }
    & git -C $Root commit -m $Message
    if ($LASTEXITCODE -ne 0) { throw 'git commit failed.' }
    $commit = (& git -C $Root rev-parse HEAD).Trim()
    $remotes = @(& git -C $Root remote)
    if ($remotes -notcontains 'origin') {
        return [pscustomobject]@{ status='COMMITTED_NOT_PUSHED'; commit=$commit; pushed=$false }
    }
    & git -C $Root push origin HEAD
    if ($LASTEXITCODE -ne 0) { return [pscustomobject]@{ status='PUSH_FAILED'; commit=$commit; pushed=$false } }
    [pscustomobject]@{ status='VERIFIED'; commit=$commit; pushed=$true }
}

function New-ProjectConfig {
    param([string]$Name, [string]$Root)
    $snapshot = Get-GitSnapshot -Root $Root
    [ordered]@{
        schema_version = 1
        project_name = $Name
        project_kind = 'standard'
        default_branch = if ($snapshot.branch) { $snapshot.branch } else { 'main' }
        git = [ordered]@{ private_by_default=$true; remote=$snapshot.remote; include_paths=@('.source','SOURCE.md','AGENTS.md','handoff.md','source.ps1','.gitattributes') }
        skills = [ordered]@{ managed=@('source','project-init','startup','shutdown','notion-conversation-log'); sync_dotfiles=$true }
        connectors = [ordered]@{
            gdrive = [ordered]@{ enabled=$true; mode='RUNTIME_DETECT' }
            obsidian = [ordered]@{ enabled=$false; mode='AGENT'; relative_note=$null }
            notion = [ordered]@{ enabled=$false; mode='AGENT'; knowledge_master=$null; topic=$null; prompt=$null; period_page=$null }
            cdn = [ordered]@{ enabled=$false; mode='AGENT'; provider=$null; target=$null }
        }
    }
}

function New-ProjectState {
    param([string]$Name)
    [ordered]@{
        schema_version = 1
        project_id = [Guid]::NewGuid().ToString()
        project_name = $Name
        phase = 'INITIALIZING'
        revision = 0
        session_id = $null
        summary = '正在建立 Source pipeline。'
        last_action = 'init'
        updated_at = Get-NowIso
        actor = [ordered]@{ agent=$Agent; device=$env:COMPUTERNAME }
        next_steps = @('完成初始化檢查。')
        git = [ordered]@{ enabled=$false; status='NOT_CONFIGURED'; branch=$null; remote=$null; ahead=0; behind=0; last_push=$null }
        connectors = [ordered]@{
            github = [ordered]@{ status='NOT_CONFIGURED'; external_id=$null; note=$null }
            skills = [ordered]@{ status='READY'; external_id=$null; note=$null }
            gdrive = [ordered]@{ status='RUNTIME'; external_id=$null; note=$null }
            obsidian = [ordered]@{ status='NOT_CONFIGURED'; external_id=$null; note=$null }
            notion = [ordered]@{ status='NOT_CONFIGURED'; external_id=$null; note=$null }
            cdn = [ordered]@{ status='NOT_CONFIGURED'; external_id=$null; note=$null }
        }
    }
}

function Initialize-Project {
    param([string]$Root)
    if (-not (Test-Path -LiteralPath $Root)) {
        if ($DryRun) { Write-Host "DRY_RUN: create $Root" } else { New-Item -ItemType Directory -Path $Root -Force | Out-Null }
    }
    $statePath = Get-StatePath $Root
    if (Test-Path -LiteralPath $statePath) {
        Write-Host 'Source pipeline 已初始化；不覆寫。'
        Show-Status -Root $Root
        return
    }
    $name = if ($ProjectName) { $ProjectName } else { Split-Path -Leaf $Root }
    $config = New-ProjectConfig -Name $name -Root $Root
    $state = New-ProjectState -Name $name
    if (-not $DryRun) { New-Item -ItemType Directory -Path (Join-Path $Root '.source') -Force | Out-Null }
    Write-JsonAtomic -Path (Get-ConfigPath $Root) -Value $config
    Write-JsonAtomic -Path $statePath -Value $state
    Copy-TemplateIfMissing -TemplateName 'SOURCE.template.md' -Destination (Join-Path $Root 'SOURCE.md') | Out-Null
    Copy-TemplateIfMissing -TemplateName 'AGENTS.template.md' -Destination (Join-Path $Root 'AGENTS.md') | Out-Null
    Copy-TemplateIfMissing -TemplateName 'handoff.template.md' -Destination (Join-Path $Root 'handoff.md') | Out-Null
    Copy-TemplateIfMissing -TemplateName 'source.launcher.ps1' -Destination (Join-Path $Root 'source.ps1') | Out-Null
    Copy-TemplateIfMissing -TemplateName 'gitattributes.template' -Destination (Join-Path $Root '.gitattributes') | Out-Null
    Merge-GitIgnore -Root $Root
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        $state.connectors.github.status = 'BLOCKED'
        $state.connectors.github.note = 'git 不在 PATH'
    } elseif (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) {
        if (-not $DryRun) { & git -C $Root init -b main | Out-Null }
    }
    Update-GitState -Root $Root -State $state
    if ($state.git.enabled) { $state.connectors.github.status = if ($state.git.remote) { 'READY' } else { 'LOCAL_ONLY' } }
    if ($CreateRemote -and -not $state.git.remote) {
        if (-not $Yes) { throw 'Creating a private GitHub repo requires -Yes.' }
        $gh = Get-Command gh -ErrorAction SilentlyContinue
        if (-not $gh) { throw 'GitHub CLI is unavailable.' }
        & $gh.Source auth status 2>$null
        if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI is not authenticated. Run gh auth login.' }
        $owner = (& $gh.Source api user --jq .login).Trim()
        $slug = ($name.ToLowerInvariant() -replace '[^a-z0-9-]+','-').Trim('-')
        if (-not $DryRun) { & $gh.Source repo create "$owner/$slug" --private --source $Root --remote origin }
        Update-GitState -Root $Root -State $state
        $state.connectors.github.status = 'READY'
    }
    $state.phase = 'READY'
    $state.summary = 'Source pipeline 初始化完成；可開始工作。'
    Save-Checkpoint -Root $Root -Config $config -State $state -LastAction 'init' -NextSteps @('執行 `./source.ps1` 自動開工。')
    Show-Status -Root $Root
}

function Show-Status {
    param([string]$Root)
    $config = Read-JsonFile (Get-ConfigPath $Root)
    $state = Read-JsonFile (Get-StatePath $Root)
    if (-not $state) {
        Write-Host "NOT_INITIALIZED: $Root"
        Write-Host 'NEXT: ./source.ps1 -Action init'
        return
    }
    Write-Host "SOURCE $($state.project_name) | phase=$($state.phase) | revision=$($state.revision)"
    Write-Host "STATUS: $($state.summary)"
    Write-Host "GIT: $($state.git.status) | branch=$($state.git.branch) | ahead=$($state.git.ahead) | behind=$($state.git.behind)"
    foreach ($property in $state.connectors.PSObject.Properties) {
        Write-Host ("{0}: {1}" -f $property.Name.ToUpperInvariant(), $property.Value.status)
    }
    $steps = @($state.next_steps)
    if ($steps.Count) {
        Write-Host 'NEXT:'
        $n = 0; $steps | ForEach-Object { $n++; Write-Host "  $n. $_" }
    }
}

function Start-Project {
    param([string]$Root)
    $config = Read-JsonFile (Get-ConfigPath $Root)
    $state = Read-JsonFile (Get-StatePath $Root)
    if (-not $state) { Initialize-Project -Root $Root; return }
    if ($state.phase -eq 'WORKING') { Write-Host '既有工作 session 尚未收工；沿用原 checkpoint。'; Show-Status -Root $Root; return }
    $previousDevice = $state.actor.device
    Update-GitState -Root $Root -State $state -Fetch
    foreach ($name in @('obsidian','notion')) {
        if ($config.connectors.$name.enabled -and $state.connectors.$name.status -eq 'NOT_CONFIGURED') {
            $state.connectors.$name.status = 'READY_AGENT'
        }
    }
    $state.connectors.gdrive.status = if ($Root -match '(?i)雲端硬碟|My Drive|Google Drive') { 'DETECTED' } else { 'RUNTIME' }
    $state.phase = 'WORKING'
    $state.session_id = [Guid]::NewGuid().ToString()
    $state.summary = if ($previousDevice -and $previousDevice -ne $env:COMPUTERNAME) { "已由另一台電腦接續；先確認雲端同步，再執行下一步。" } else { '已開工，可依下一步繼續。' }
    $steps = @($state.next_steps)
    if (-not $steps.Count -or $steps[0] -match 'source.ps1') { $steps = @('在本次任務中完成一個可驗證成果。') }
    if ($state.git.behind -gt 0) { $steps = @("遠端領先 $($state.git.behind) commits；檢查本地變更後再決定是否 pull。") + $steps }
    Save-Checkpoint -Root $Root -Config $config -State $state -LastAction 'start' -NextSteps $steps
    Show-Status -Root $Root
}

function Get-PendingConnectors {
    param($State)
    @($State.connectors.PSObject.Properties | Where-Object { $_.Value.status -eq 'PENDING_AGENT' } | ForEach-Object Name)
}

function Finish-Project {
    param([string]$Root)
    $config = Read-JsonFile (Get-ConfigPath $Root)
    $state = Read-JsonFile (Get-StatePath $Root)
    if (-not $state) { throw 'Project is not initialized.' }
    $state.phase = 'FINISHING'
    $state.summary = '正在保存 checkpoint 與同步可用層級。'
    $steps = @()
    if ($config.project_kind -eq 'skill-distribution') {
        try {
            $installResult = @(Install-ManagedSkills -SourceRoot $Root)
            $state.connectors.skills.status = 'VERIFIED'
            $state.connectors.skills.note = $installResult -join '; '
            $dotfiles = Sync-Dotfiles -Message '同步 Source pipeline 與相容技能'
            if ($dotfiles.status -ne 'VERIFIED') { $steps += $dotfiles.detail }
        } catch {
            $state.connectors.skills.status = 'BLOCKED'
            $state.connectors.skills.note = $_.Exception.Message
            $steps += $_.Exception.Message
        }
    }
    if (-not $SkipConnectors) {
        foreach ($name in @('obsidian','notion','cdn')) {
            if ($config.connectors.$name.enabled) {
                $state.connectors.$name.status = 'PENDING_AGENT'
                $steps += "完成 $name connector，再執行 source.ps1 -Action complete -Connector $name -ConnectorStatus VERIFIED。"
            } elseif ($name -eq 'cdn') {
                $state.connectors.cdn.status = 'NOT_CONFIGURED'
            }
        }
    }
    $pending = Get-PendingConnectors $state
    $state.phase = if ($pending.Count) { 'AWAITING_EXTERNAL' } else { 'READY' }
    $state.session_id = $null
    $state.summary = if ($pending.Count) { "本地收工完成；等待 connector：$($pending -join ', ')。" } else { '收工完成，可安全換電腦或 Agent。' }
    if (-not $steps.Count) {
        $steps = if ($pending.Count) {
            @($pending | ForEach-Object { "完成 $_ connector。" })
        } else {
            @('下次執行 `./source.ps1` 自動開工。')
        }
    }
    Update-GitState -Root $Root -State $state
    Save-Checkpoint -Root $Root -Config $config -State $state -LastAction 'finish-preflight' -NextSteps $steps
    if (-not $SkipGit) {
        $message = if ($CommitMessage) { $CommitMessage } else { "收工：$($state.project_name)" }
        $first = Invoke-GitFinish -Root $Root -Message $message -ExtraIncludes $Include
        if ($first.commit) {
            $state.git.last_push = $first.commit.Substring(0,7)
            $state.git.status = $first.status
            Save-Checkpoint -Root $Root -Config $config -State $state -LastAction 'finish' -NextSteps $steps
            $null = Invoke-GitFinish -Root $Root -Message '回填 Source 收工狀態' -ExtraIncludes @()
        }
    }
    Show-Status -Root $Root
}

function Complete-Connector {
    param([string]$Root)
    if (-not $Connector) { throw '-Connector is required.' }
    $config = Read-JsonFile (Get-ConfigPath $Root)
    $state = Read-JsonFile (Get-StatePath $Root)
    if (-not $state) { throw 'Project is not initialized.' }
    $state.connectors.$Connector.status = $ConnectorStatus
    $state.connectors.$Connector.external_id = $ExternalId
    $state.connectors.$Connector.note = $Note
    $pending = Get-PendingConnectors $state
    $state.phase = if ($pending.Count) { 'AWAITING_EXTERNAL' } else { 'READY' }
    $state.summary = if ($pending.Count) { "尚待 connector：$($pending -join ', ')。" } else { '全部收工 connector 已完成。' }
    $steps = if ($pending.Count) { @($pending | ForEach-Object { "完成 $_ connector。" }) } else { @('下次執行 `./source.ps1` 自動開工。') }
    Save-Checkpoint -Root $Root -Config $config -State $state -LastAction "complete-$Connector" -NextSteps $steps
    if (-not $SkipGit) { $null = Invoke-GitFinish -Root $Root -Message "回填 $Connector connector 狀態" -ExtraIncludes @() }
    Show-Status -Root $Root
}

function Invoke-Doctor {
    param([string]$Root)
    $checks = @()
    $checks += [pscustomobject]@{ check='powershell'; status=if($PSVersionTable.PSVersion.Major -ge 5){'PASS'}else{'BLOCKED'}; detail=$PSVersionTable.PSVersion.ToString() }
    foreach ($name in @('git','gh','winget')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        $checks += [pscustomobject]@{ check=$name; status=if($command){'PASS'}else{'OPTIONAL_MISSING'}; detail=if($command){$command.Source}else{$null} }
    }
    $chezmoi = Get-ChezmoiExecutable
    $checks += [pscustomobject]@{ check='chezmoi'; status=if($chezmoi){'PASS'}else{'OPTIONAL_MISSING'}; detail=$chezmoi }
    $configPath = Get-ConfigPath $Root; $statePath = Get-StatePath $Root
    $checks += [pscustomobject]@{ check='config'; status=if(Test-Path $configPath){'PASS'}else{'NOT_INITIALIZED'}; detail='.source/config.json' }
    $checks += [pscustomobject]@{ check='state'; status=if(Test-Path $statePath){'PASS'}else{'NOT_INITIALIZED'}; detail='.source/state.json' }
    $stateDirectory = Join-Path $Root '.source'
    if (Test-Path -LiteralPath $stateDirectory) {
        $writeProbe = Join-Path $stateDirectory ('.write-probe-' + [Guid]::NewGuid().ToString('N'))
        try {
            if (-not $DryRun) { [System.IO.File]::WriteAllText($writeProbe, 'probe', $script:Utf8NoBom); Remove-Item -LiteralPath $writeProbe -Force }
            $checks += [pscustomobject]@{ check='state-write'; status='PASS'; detail='.source is writable' }
        } catch {
            $checks += [pscustomobject]@{ check='state-write'; status='BLOCKED'; detail=$_.Exception.Message }
        }
    }
    $launcher = Join-Path $Root 'source.ps1'
    $launcherTemplate = Join-Path $script:AssetRoot 'source.launcher.ps1'
    if ((Test-Path $launcher) -and (Test-Path $launcherTemplate)) {
        $sameLauncher = (Get-FileHash $launcher -Algorithm SHA256).Hash -eq (Get-FileHash $launcherTemplate -Algorithm SHA256).Hash
        $checks += [pscustomobject]@{ check='launcher'; status=if($sameLauncher){'PASS'}else{'STALE'}; detail='source.ps1 matches installed engine launcher' }
    }
    foreach ($path in @($configPath,$statePath) | Where-Object { Test-Path $_ }) {
        $text = Get-Content -Raw -Encoding utf8 -LiteralPath $path
        $hasAbsolute = $text -match '(?i)"[A-Z]:\\' -or $text -match '"\\\\[^"\\]+'
        $checks += [pscustomobject]@{ check=('portable:' + (Split-Path -Leaf $path)); status=if($hasAbsolute){'BLOCKED'}else{'PASS'}; detail='persisted_absolute_path=0' }
    }
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        & gh auth status 2>$null
        $checks += [pscustomobject]@{ check='github-auth'; status=if($LASTEXITCODE -eq 0){'PASS'}else{'BLOCKED'}; detail='gh auth status' }
    }
    $checks | Format-Table -AutoSize
    if (Test-Path $statePath) { Show-Status -Root $Root }
}

try {
    $root = Resolve-Root -Start $ProjectRoot -ForInit:($Action -in @('init','bootstrap'))
    if ($Action -eq 'auto') {
        $state = Read-JsonFile (Get-StatePath $root)
        if (-not $state) { $Action = 'init' }
        elseif ($state.phase -eq 'READY') { $Action = 'start' }
        else { $Action = 'next' }
    }
    switch ($Action) {
        'bootstrap' {
            Install-ManagedSkills -SourceRoot $script:DistributionRoot | ForEach-Object { Write-Host $_ }
            Initialize-Project -Root $root
        }
        'init' { Initialize-Project -Root $root }
        'status' { Show-Status -Root $root }
        'next' { Show-Status -Root $root }
        'start' { Start-Project -Root $root }
        'finish' { Finish-Project -Root $root }
        'doctor' { Invoke-Doctor -Root $root }
        'deploy-skills' { Install-ManagedSkills -SourceRoot $script:DistributionRoot | ForEach-Object { Write-Host $_ } }
        'sync-dotfiles' {
            $result = Sync-Dotfiles -Message '同步 Source pipeline 與共用 Agent 核心'
            Write-Host "$($result.status): $($result.detail)"
        }
        'complete' { Complete-Connector -Root $root }
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
