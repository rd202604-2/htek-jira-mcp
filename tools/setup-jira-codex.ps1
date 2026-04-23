param(
    [string]$CodexHome = "$HOME\.codex",
    [string]$JiraBaseUrl,
    [string]$JiraUsername,
    [string]$JiraPassword,
    [switch]$InstallPythonDeps
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[Jira Codex Setup] $Message"
}

function Get-RepoRoot {
    return Split-Path -Parent $PSScriptRoot
}

function Assert-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "未检测到 Python。请先安装 Python，并确保 `python` 已加入 PATH。"
    }
    return $python.Source
}

function Escape-TomlString {
    param([string]$Value)
    return ($Value -replace '\\', '\\') -replace '"', '\"'
}

function Set-TomlBlock {
    param(
        [string]$ConfigPath,
        [string]$SectionName,
        [string[]]$BlockLines
    )

    $content = ""
    if (Test-Path $ConfigPath) {
        $content = Get-Content -LiteralPath $ConfigPath -Raw
    }

    $blockText = ($BlockLines -join "`r`n").TrimEnd() + "`r`n"
    $sectionHeader = "[$SectionName]"
    $regex = "(?ms)^\[$([regex]::Escape($SectionName))\]\r?\n.*?(?=^\[|\z)"

    if ($content -match $regex) {
        $content = [regex]::Replace($content, $regex, $blockText)
    } else {
        if ($content -and -not $content.EndsWith("`n")) {
            $content += "`r`n"
        }
        if ($content -and -not $content.EndsWith("`r`n`r`n")) {
            $content += "`r`n"
        }
        $content += $blockText
    }

    Set-Content -LiteralPath $ConfigPath -Value $content -Encoding UTF8
}

function Install-Skills {
    param(
        [string]$RepoRoot,
        [string]$TargetSkillsDir
    )

    $sourceSkillsDir = Join-Path $RepoRoot "skills"
    if (-not (Test-Path $sourceSkillsDir)) {
        throw "仓库中未找到 skills 目录：$sourceSkillsDir"
    }

    New-Item -ItemType Directory -Force -Path $TargetSkillsDir | Out-Null

    Get-ChildItem -LiteralPath $sourceSkillsDir -Directory | ForEach-Object {
        $target = Join-Path $TargetSkillsDir $_.Name
        if (Test-Path $target) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
        Copy-Item -LiteralPath $_.FullName -Destination $TargetSkillsDir -Recurse -Force
        Write-Step "已安装 skill：$($_.Name)"
    }
}

function Set-JiraEnvVars {
    param(
        [string]$BaseUrl,
        [string]$Username,
        [string]$Password
    )

    if ($BaseUrl) {
        [Environment]::SetEnvironmentVariable("HTEK_JIRA_BASE_URL", $BaseUrl, "User")
        Write-Step "已写入用户环境变量 HTEK_JIRA_BASE_URL"
    }
    if ($Username) {
        [Environment]::SetEnvironmentVariable("HTEK_JIRA_USERNAME", $Username, "User")
        Write-Step "已写入用户环境变量 HTEK_JIRA_USERNAME"
    }
    if ($Password) {
        [Environment]::SetEnvironmentVariable("HTEK_JIRA_PASSWORD", $Password, "User")
        Write-Step "已写入用户环境变量 HTEK_JIRA_PASSWORD"
    }
}

function Ensure-CodexConfig {
    param(
        [string]$CodexHomeDir,
        [string]$RepoRoot
    )

    New-Item -ItemType Directory -Force -Path $CodexHomeDir | Out-Null
    $configPath = Join-Path $CodexHomeDir "config.toml"
    if (-not (Test-Path $configPath)) {
        Set-Content -LiteralPath $configPath -Value "" -Encoding UTF8
    }

    $mcpScriptPath = Join-Path $RepoRoot "tools\jira_server_mcp.py"
    $escapedScriptPath = Escape-TomlString $mcpScriptPath

    Set-TomlBlock -ConfigPath $configPath -SectionName "mcp_servers.htek_jira_server" -BlockLines @(
        "[mcp_servers.htek_jira_server]",
        'command = "python"',
        "args = [""$escapedScriptPath""]",
        "enabled = true"
    )

    Write-Step "已更新 Codex MCP 配置：$configPath"
}

$repoRoot = Get-RepoRoot
$pythonPath = Assert-Python

Write-Step "仓库根目录：$repoRoot"
Write-Step "Python 路径：$pythonPath"

if ($InstallPythonDeps) {
    Write-Step "安装 Python 依赖：mcp, PyYAML"
    & python -m pip install mcp PyYAML
}

$targetSkillsDir = Join-Path $CodexHome "skills"
Install-Skills -RepoRoot $repoRoot -TargetSkillsDir $targetSkillsDir
Ensure-CodexConfig -CodexHomeDir $CodexHome -RepoRoot $repoRoot
Set-JiraEnvVars -BaseUrl $JiraBaseUrl -Username $JiraUsername -Password $JiraPassword

Write-Step "安装完成。请重启 Codex Desktop 后再使用 Jira MCP 和相关 skills。"
