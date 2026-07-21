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

$ErrorActionPreference = 'Stop'
$PythonEngine = Join-Path $PSScriptRoot 'source.py'

function Test-PythonCommand {
    param([string]$Executable, [string[]]$Prefix = @())
    try {
        & $Executable @Prefix --version *> $null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Find-Python {
    foreach ($name in @('python3','python')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and (Test-PythonCommand -Executable $command.Source)) {
            return [pscustomobject]@{ Executable=$command.Source; Prefix=@() }
        }
    }
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher -and (Test-PythonCommand -Executable $launcher.Source -Prefix @('-3'))) {
        return [pscustomobject]@{ Executable=$launcher.Source; Prefix=@('-3') }
    }
    $localPrograms = Join-Path $env:LOCALAPPDATA 'Programs\Python'
    $candidate = Get-ChildItem -LiteralPath $localPrograms -Recurse -Filter python.exe -File -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1
    if ($candidate -and (Test-PythonCommand -Executable $candidate.FullName)) {
        return [pscustomobject]@{ Executable=$candidate.FullName; Prefix=@() }
    }
    return $null
}

$Python = Find-Python
if (-not $Python -and $Yes -and (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host 'Python 3 not found; installing the signed winget package...'
    & winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw 'Python installation failed.' }
    $Python = Find-Python
}
if (-not $Python) {
    throw 'Python 3 is required. Re-run with -Yes to install it through winget, or install Python 3 manually.'
}

$Arguments = @($Python.Prefix) + @($PythonEngine, '--action', $Action, '--project-root', $ProjectRoot, '--agent', $Agent)
foreach ($pair in @(
    @('--project-name',$ProjectName), @('--commit-message',$CommitMessage),
    @('--connector',$Connector), @('--connector-status',$ConnectorStatus),
    @('--external-id',$ExternalId), @('--note',$Note)
)) {
    if ($pair[1]) { $Arguments += $pair }
}
foreach ($path in $Include) { $Arguments += @('--include', $path) }
if ($Yes) { $Arguments += '--yes' }
if ($DryRun) { $Arguments += '--dry-run' }
if ($SkipGit) { $Arguments += '--skip-git' }
if ($SkipConnectors) { $Arguments += '--skip-connectors' }
if ($CreateRemote) { $Arguments += '--create-remote' }

& $Python.Executable @Arguments
exit $LASTEXITCODE
