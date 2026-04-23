param(
    [string]$SourceScript = (Join-Path $PSScriptRoot "setup-jira-agent.ps1"),
    [string]$OutputPath = (Join-Path (Split-Path -Parent $PSScriptRoot) "output\JiraMCPInstaller.exe"),
    [switch]$InstallPs2Exe,
    [switch]$NoConsole
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[Jira Installer Build] $Message" -ForegroundColor Cyan
}

if (-not (Test-Path $SourceScript)) {
    throw "Source script was not found: $SourceScript"
}

if ($InstallPs2Exe) {
    Write-Step "Installing ps2exe module"
    Install-Module ps2exe -Scope CurrentUser -Force -AllowClobber
}

if (-not (Get-Module -ListAvailable -Name ps2exe)) {
    throw "ps2exe module was not found. Run this script with -InstallPs2Exe first."
}

Import-Module ps2exe -ErrorAction Stop

$outputDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Write-Step "Building EXE"
Invoke-PS2EXE `
    -InputFile $SourceScript `
    -OutputFile $OutputPath `
    -Title "Jira MCP Installer" `
    -Description "Install Jira MCP for Codex, Cursor, OpenClaw, or Hermes" `
    -Company "HTEK" `
    -Product "Jira MCP Installer" `
    -Version "1.0.0" `
    -NoConsole:$NoConsole

Write-Step ("EXE built: {0}" -f $OutputPath)
