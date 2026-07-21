[CmdletBinding()]
param(
    [string]$Action = 'auto',
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$ProjectName,
    [string]$WorkspaceRole,
    [string]$HubRoot,
    [string]$ChildName,
    [string]$ChildPath,
    [int]$LeaseHours = 12,
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
    throw 'Source engine is not installed. Clone cross-device-agent-skills, then run source.ps1 -Action bootstrap -ProjectRoot <path> -Yes.'
}

& $Engine @PSBoundParameters
exit $LASTEXITCODE
