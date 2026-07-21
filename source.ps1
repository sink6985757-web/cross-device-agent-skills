[CmdletBinding()]
param(
    [string]$Action = 'auto',
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$ProjectName,
    [string]$Agent = 'Agent',
    [string]$CommitMessage,
    [string[]]$Include = @(),
    [string]$Connector,
    [string]$ConnectorStatus = 'VERIFIED',
    [string]$ExternalId,
    [string]$Note,
    [switch]$Yes,
    [switch]$DryRun,
    [switch]$SkipGit,
    [switch]$SkipConnectors,
    [switch]$CreateRemote
)

$LocalEngine = Join-Path $PSScriptRoot 'source\scripts\source.ps1'
$GlobalEngine = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.agents\skills\source\scripts\source.ps1'
$Engine = if (Test-Path -LiteralPath $LocalEngine) { $LocalEngine } elseif (Test-Path -LiteralPath $GlobalEngine) { $GlobalEngine } else { $null }

if (-not $Engine) {
    throw 'Source engine 未安裝。先以已登入的 GitHub CLI clone cross-device-agent-skills，再執行該 repo 的 source.ps1 -Action bootstrap -ProjectRoot <專案路徑> -Yes。'
}

& $Engine @PSBoundParameters
exit $LASTEXITCODE
