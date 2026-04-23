param(
    [string]$RepoRoot,
    [string]$JiraBaseUrl,
    [string]$JiraUsername,
    [string]$JiraPassword,
    [ValidateSet("codex", "cursor", "openclaw", "hermes")]
    [string]$Agent,
    [ValidateSet("project", "global")]
    [string]$CursorInstallScope,
    [switch]$ImportSkills,
    [switch]$InstallPythonDeps,
    [switch]$NonInteractive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[Jira Installer] $Message" -ForegroundColor Cyan
}

function Write-WarnLine {
    param([string]$Message)
    Write-Host "[Jira Installer] $Message" -ForegroundColor Yellow
}

function Get-RepoRoot {
    param([string]$RequestedRepoRoot)

    if ($RequestedRepoRoot) {
        return (Resolve-Path -LiteralPath $RequestedRepoRoot).Path
    }
    return (Split-Path -Parent $PSScriptRoot)
}

function Assert-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "Python was not found. Please install Python and ensure python is in PATH."
    }
    return $python.Source
}

function Escape-TomlString {
    param([string]$Value)

    $result = $Value.Replace('\', '\\')
    $result = $result.Replace('"', ([string][char]92 + [char]34))
    return $result
}

function Set-TomlBlock {
    param(
        [string]$ConfigPath,
        [string]$SectionName,
        [string[]]$BlockLines
    )

    $content = ""
    if (Test-Path $ConfigPath) {
        $content = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8
    }

    $blockText = ($BlockLines -join "`r`n") + "`r`n"
    $escapedSectionName = [regex]::Escape($SectionName)
    $regex = '(?ms)^\[' + $escapedSectionName + '\]\r?\n.*?(?=^\[|\z)'

    if ([regex]::IsMatch($content, $regex)) {
        $content = [regex]::Replace($content, $regex, $blockText)
    } else {
        if ($content -and -not $content.EndsWith("`n")) {
            $content += "`r`n"
        }
        if ($content) {
            $content += "`r`n"
        }
        $content += $blockText
    }

    Set-Content -LiteralPath $ConfigPath -Value $content -Encoding UTF8
}

function Read-TextOrDefault {
    param(
        [string]$Prompt,
        [string]$DefaultValue = ""
    )

    while ($true) {
        if ($DefaultValue) {
            $value = Read-Host "$Prompt [$DefaultValue]"
            if ([string]::IsNullOrWhiteSpace($value)) {
                return $DefaultValue
            }
        } else {
            $value = Read-Host $Prompt
        }

        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value.Trim()
        }

        Write-WarnLine "This value is required."
    }
}

function Read-Password {
    param([string]$Prompt)

    while ($true) {
        $secure = Read-Host $Prompt -AsSecureString
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        try {
            $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
        } finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        }

        if (-not [string]::IsNullOrWhiteSpace($plain)) {
            return $plain
        }

        Write-WarnLine "Password is required."
    }
}

function Read-MenuChoice {
    param(
        [string]$Title,
        [string[]]$Items
    )

    Write-Host ""
    Write-Host $Title -ForegroundColor Green
    for ($i = 0; $i -lt $Items.Count; $i++) {
        Write-Host ("  {0}. {1}" -f ($i + 1), $Items[$i])
    }

    while ($true) {
        $choice = Read-Host "Enter option number"
        $index = 0
        if ([int]::TryParse($choice, [ref]$index)) {
            if ($index -ge 1 -and $index -le $Items.Count) {
                return $index
            }
        }
        Write-WarnLine "Invalid option."
    }
}

function Read-YesNo {
    param(
        [string]$Prompt,
        [bool]$DefaultValue
    )

    $suffix = if ($DefaultValue) { "[Y/n]" } else { "[y/N]" }
    while ($true) {
        $value = (Read-Host "$Prompt $suffix").Trim().ToLowerInvariant()
        if ([string]::IsNullOrWhiteSpace($value)) {
            return $DefaultValue
        }
        if ($value -in @("y", "yes")) {
            return $true
        }
        if ($value -in @("n", "no")) {
            return $false
        }
        Write-WarnLine "Please enter y or n."
    }
}

function Set-JiraEnvVars {
    param(
        [string]$BaseUrl,
        [string]$Username,
        [string]$Password
    )

    [Environment]::SetEnvironmentVariable("HTEK_JIRA_BASE_URL", $BaseUrl, "User")
    [Environment]::SetEnvironmentVariable("HTEK_JIRA_USERNAME", $Username, "User")
    [Environment]::SetEnvironmentVariable("HTEK_JIRA_PASSWORD", $Password, "User")
    Write-Step "User environment variables were updated."
}

function Install-CodexSkills {
    param([string]$ResolvedRepoRoot)

    $sourceSkillsDir = Join-Path $ResolvedRepoRoot "skills"
    $targetSkillsDir = Join-Path $HOME ".codex\skills"

    if (-not (Test-Path $sourceSkillsDir)) {
        throw "skills directory was not found: $sourceSkillsDir"
    }

    New-Item -ItemType Directory -Force -Path $targetSkillsDir | Out-Null

    Get-ChildItem -LiteralPath $sourceSkillsDir -Directory | ForEach-Object {
        $target = Join-Path $targetSkillsDir $_.Name
        if (Test-Path $target) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
        Copy-Item -LiteralPath $_.FullName -Destination $targetSkillsDir -Recurse -Force
        Write-Step ("Imported skill: {0}" -f $_.Name)
    }
}

function Ensure-CodexConfig {
    param([string]$ResolvedRepoRoot)

    $codexHome = Join-Path $HOME ".codex"
    $configPath = Join-Path $codexHome "config.toml"
    $scriptPath = Join-Path $ResolvedRepoRoot "tools\jira_server_mcp.py"
    $escapedScriptPath = Escape-TomlString $scriptPath

    New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
    if (-not (Test-Path $configPath)) {
        Set-Content -LiteralPath $configPath -Value "" -Encoding UTF8
    }

    Set-TomlBlock -ConfigPath $configPath -SectionName "mcp_servers.htek_jira_server" -BlockLines @(
        "[mcp_servers.htek_jira_server]",
        'command = "python"',
        "args = [""$escapedScriptPath""]",
        'enabled = true'
    )

    Write-Step ("Codex config updated: {0}" -f $configPath)
}

function Get-JsonObject {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return @{}
    }

    $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return @{}
    }

    return ($raw | ConvertFrom-Json -AsHashtable)
}

function Save-JsonObject {
    param(
        [string]$Path,
        [hashtable]$Data
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    Set-Content -LiteralPath $Path -Value ($Data | ConvertTo-Json -Depth 20) -Encoding UTF8
}

function Ensure-CursorConfig {
    param(
        [string]$ResolvedRepoRoot,
        [string]$Scope
    )

    if ($Scope -eq "project") {
        $configPath = Join-Path $ResolvedRepoRoot ".cursor\mcp.json"
        $scriptPath = '${workspaceFolder}/tools/jira_server_mcp.py'
    } else {
        $configPath = Join-Path $HOME ".cursor\mcp.json"
        $scriptPath = (Join-Path $ResolvedRepoRoot "tools\jira_server_mcp.py") -replace '\\', '/'
    }

    $data = Get-JsonObject -Path $configPath
    if (-not $data.ContainsKey("mcpServers")) {
        $data["mcpServers"] = @{}
    }

    $data["mcpServers"]["htek_jira_server"] = @{
        command = "python"
        args = @($scriptPath)
    }

    Save-JsonObject -Path $configPath -Data $data
    Write-Step ("Cursor config updated: {0}" -f $configPath)
}

function Ensure-OpenClawConfig {
    param([string]$ResolvedRepoRoot)

    $configPath = Join-Path $HOME ".openclaw\openclaw.json"
    $scriptPath = (Join-Path $ResolvedRepoRoot "tools\jira_server_mcp.py") -replace '\\', '/'
    $data = Get-JsonObject -Path $configPath

    if (-not $data.ContainsKey("mcp")) {
        $data["mcp"] = @{}
    }
    if (-not $data["mcp"].ContainsKey("servers")) {
        $data["mcp"]["servers"] = @{}
    }

    $data["mcp"]["servers"]["htek_jira_server"] = @{
        command = "python"
        args = @($scriptPath)
    }

    Save-JsonObject -Path $configPath -Data $data
    Write-Step ("OpenClaw config updated: {0}" -f $configPath)
}

function Ensure-HermesConfig {
    param([string]$ResolvedRepoRoot)

    $configDir = Join-Path $HOME ".hermes"
    $configPath = Join-Path $configDir "config.yaml"
    $scriptPath = (Join-Path $ResolvedRepoRoot "tools\jira_server_mcp.py") -replace '\\', '/'

    New-Item -ItemType Directory -Force -Path $configDir | Out-Null

    $block = @(
        "mcp_servers:",
        "  htek_jira_server:",
        '    command: "python"',
        "    args:",
        "      - ""$scriptPath"""
    )

    $content = ""
    if (Test-Path $configPath) {
        $content = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8
    }

    if ([string]::IsNullOrWhiteSpace($content)) {
        $content = ($block -join "`r`n") + "`r`n"
    } else {
        $regex = "(?ms)^mcp_servers:\r?\n(?:  .*?(?:\r?\n|$))*"
        $replacement = ($block -join "`r`n") + "`r`n"
        if ([regex]::IsMatch($content, $regex)) {
            $content = [regex]::Replace($content, $regex, $replacement, 1)
        } else {
            if (-not $content.EndsWith("`n")) {
                $content += "`r`n"
            }
            $content += "`r`n" + $replacement
        }
    }

    Set-Content -LiteralPath $configPath -Value $content -Encoding UTF8
    Write-Step ("Hermes config updated: {0}" -f $configPath)
}

function Show-NextSteps {
    param(
        [string]$SelectedAgent,
        [bool]$SkillsImported,
        [string]$CursorScope
    )

    Write-Host ""
    Write-Host "Install complete. Next steps:" -ForegroundColor Green

    switch ($SelectedAgent) {
        "codex" {
            Write-Host "1. Restart Codex Desktop"
            Write-Host "2. Ask Codex: list the Jira projects I can access"
            if ($SkillsImported) {
                Write-Host "3. Try using `$jira-server-status-report"
            }
        }
        "cursor" {
            Write-Host "1. Restart Cursor"
            if ($CursorScope -eq "project") {
                Write-Host "2. Make sure Cursor is opened at this repository"
            }
            Write-Host "3. Ask Cursor: list the Jira projects I can access"
        }
        "openclaw" {
            Write-Host "1. Restart OpenClaw or reload MCP config"
            Write-Host "2. Verify htek_jira_server is available"
        }
        "hermes" {
            Write-Host "1. Restart Hermes or run /reload-mcp"
            Write-Host "2. Verify htek_jira_server is available"
        }
    }
}

$resolvedRepoRoot = Get-RepoRoot -RequestedRepoRoot $RepoRoot
$pythonPath = Assert-Python

Write-Step ("Repository root: {0}" -f $resolvedRepoRoot)
Write-Step ("Python path: {0}" -f $pythonPath)

if ($InstallPythonDeps) {
    Write-Step "Installing Python dependencies: mcp, PyYAML"
    & python -m pip install mcp PyYAML
}

if (-not $NonInteractive) {
    if (-not $JiraBaseUrl) {
        $JiraBaseUrl = Read-TextOrDefault -Prompt "Enter Jira base URL" -DefaultValue "http://oa.htek.com:8088/secure/Dashboard.jspa"
    }
    if (-not $JiraUsername) {
        $JiraUsername = Read-TextOrDefault -Prompt "Enter Jira username"
    }
    if (-not $JiraPassword) {
        $JiraPassword = Read-Password -Prompt "Enter Jira password"
    }
    if (-not $Agent) {
        $agentChoice = Read-MenuChoice -Title "Choose target agent" -Items @("Codex", "Cursor", "OpenClaw", "Hermes")
        switch ($agentChoice) {
            1 { $Agent = "codex" }
            2 { $Agent = "cursor" }
            3 { $Agent = "openclaw" }
            4 { $Agent = "hermes" }
        }
    }
    if (-not $PSBoundParameters.ContainsKey("ImportSkills")) {
        $ImportSkills = Read-YesNo -Prompt "Import Codex skills" -DefaultValue ($Agent -eq "codex")
    }
    if ($Agent -eq "cursor" -and -not $CursorInstallScope) {
        $scopeChoice = Read-MenuChoice -Title "Choose Cursor config scope" -Items @("Project level", "Global")
        if ($scopeChoice -eq 1) {
            $CursorInstallScope = "project"
        } else {
            $CursorInstallScope = "global"
        }
    }
} else {
    if (-not $JiraBaseUrl) { throw "Missing parameter: JiraBaseUrl" }
    if (-not $JiraUsername) { throw "Missing parameter: JiraUsername" }
    if (-not $JiraPassword) { throw "Missing parameter: JiraPassword" }
    if (-not $Agent) { throw "Missing parameter: Agent" }
    if ($Agent -eq "cursor" -and -not $CursorInstallScope) {
        throw "When Agent=cursor, CursorInstallScope is required."
    }
}

Set-JiraEnvVars -BaseUrl $JiraBaseUrl -Username $JiraUsername -Password $JiraPassword

switch ($Agent) {
    "codex" {
        Ensure-CodexConfig -ResolvedRepoRoot $resolvedRepoRoot
        if ($ImportSkills) {
            Install-CodexSkills -ResolvedRepoRoot $resolvedRepoRoot
        }
    }
    "cursor" {
        Ensure-CursorConfig -ResolvedRepoRoot $resolvedRepoRoot -Scope $CursorInstallScope
        if ($ImportSkills) {
            Write-WarnLine "Cursor does not read Codex skills directly. Skill import was skipped."
        }
    }
    "openclaw" {
        Ensure-OpenClawConfig -ResolvedRepoRoot $resolvedRepoRoot
        if ($ImportSkills) {
            Write-WarnLine "OpenClaw does not read Codex skills directly. Skill import was skipped."
        }
    }
    "hermes" {
        Ensure-HermesConfig -ResolvedRepoRoot $resolvedRepoRoot
        if ($ImportSkills) {
            Write-WarnLine "Hermes does not read Codex skills directly. Skill import was skipped."
        }
    }
}

Show-NextSteps -SelectedAgent $Agent -SkillsImported ([bool]$ImportSkills) -CursorScope $CursorInstallScope
