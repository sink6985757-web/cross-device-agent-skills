[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$PythonTest = Join-Path $PSScriptRoot 'source.tests.py'

$Python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) { throw 'Python 3 is required for cross-platform tests.' }

& $Python.Source $PythonTest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& (Join-Path $RepoRoot 'source.ps1') -Action next -ProjectRoot $RepoRoot
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'PASS: Windows PowerShell adapter -> portable Python engine'
