Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Resolve-ScriptDirectory {
    $candidates = @()

    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $candidates += $PSScriptRoot
    }
    if (-not [string]::IsNullOrWhiteSpace($PSCommandPath)) {
        $candidates += (Split-Path -Parent $PSCommandPath)
    }

    $baseDirectory = [System.AppDomain]::CurrentDomain.BaseDirectory
    if (-not [string]::IsNullOrWhiteSpace($baseDirectory)) {
        $candidates += $baseDirectory
    }

    foreach ($candidate in $candidates) {
        if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw "Unable to determine the installer directory."
}

function Find-RepoRoot {
    param([string]$StartDirectory)

    if ([string]::IsNullOrWhiteSpace($StartDirectory) -or -not (Test-Path -LiteralPath $StartDirectory)) {
        return $null
    }

    $current = (Resolve-Path -LiteralPath $StartDirectory).Path
    while (-not [string]::IsNullOrWhiteSpace($current)) {
        $readmePath = Join-Path $current "README.md"
        $mcpScriptPath = Join-Path $current "tools\jira_server_mcp.py"
        if ((Test-Path -LiteralPath $readmePath) -and (Test-Path -LiteralPath $mcpScriptPath)) {
            return $current
        }

        $parent = Split-Path -Parent $current
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            break
        }
        $current = $parent
    }

    return $null
}

$scriptDir = Resolve-ScriptDirectory
$defaultRepoRoot = Find-RepoRoot -StartDirectory $scriptDir
$backendScript = Join-Path $scriptDir "setup-jira-agent.ps1"
$backendExe = Join-Path $scriptDir "JiraMCPInstaller.exe"

$script:translations = @{
    "zh-CN" = @{
        windowTitle = "Jira MCP 安装器"
        backendMissing = "未找到后端安装程序。`r`n期望路径之一：`r`n{0}`r`n{1}"
        title = "为 Agent 安装 Jira MCP"
        language = "界面语言"
        repoRoot = "Jira MCP项目根目录"
        browse = "浏览..."
        jiraBaseUrl = "Jira 地址"
        jiraUsername = "Jira 用户名"
        jiraPassword = "Jira 密码"
        targetAgent = "目标 Agent"
        installPythonDeps = "安装 Python 依赖（mcp、PyYAML）"
        importSkills = "导入 Codex Skills"
        cursorScope = "Cursor 安装范围"
        install = "安装"
        close = "关闭"
        folderDialogDescription = "请选择 Jira MCP 项目的根目录"
        repoRootRequired = "请选择有效的 Jira MCP项目根目录。"
        jiraBaseUrlRequired = "请填写 Jira 地址。"
        jiraUsernameRequired = "请填写 Jira 用户名。"
        jiraPasswordRequired = "请填写 Jira 密码。"
        runningInstaller = "正在运行安装程序..."
        installCompleted = "安装已完成。"
        installCompletedStatus = "安装成功完成。"
        installFailed = "安装失败，请查看状态框中的详细信息。"
        installFailedStatus = "安装失败，退出码：{0}。"
        languageZh = "中文"
        languageEn = "English"
    }
    "en-US" = @{
        windowTitle = "Jira MCP Installer"
        backendMissing = "Backend installer was not found.`r`nExpected one of:`r`n{0}`r`n{1}"
        title = "Install Jira MCP for Agent"
        language = "Language"
        repoRoot = "Jira MCP Project Root"
        browse = "Browse..."
        jiraBaseUrl = "Jira Base URL"
        jiraUsername = "Jira Username"
        jiraPassword = "Jira Password"
        targetAgent = "Target Agent"
        installPythonDeps = "Install Python dependencies (mcp, PyYAML)"
        importSkills = "Import Codex Skills"
        cursorScope = "Cursor Scope"
        install = "Install"
        close = "Close"
        folderDialogDescription = "Choose the Jira MCP project root folder"
        repoRootRequired = "Please choose a valid Jira MCP project root."
        jiraBaseUrlRequired = "Jira base URL is required."
        jiraUsernameRequired = "Jira username is required."
        jiraPasswordRequired = "Jira password is required."
        runningInstaller = "Running installer..."
        installCompleted = "Installation completed."
        installCompletedStatus = "Installation completed successfully."
        installFailed = "Installation failed. See details in the status box."
        installFailedStatus = "Installation failed with exit code {0}."
        languageZh = "中文"
        languageEn = "English"
    }
}

$script:currentLang = "zh-CN"

function T {
    param(
        [string]$Key,
        [object[]]$Args = @()
    )

    $text = $script:translations[$script:currentLang][$Key]
    if ($null -eq $text) {
        return $Key
    }
    if ($Args.Count -gt 0) {
        return [string]::Format($text, $Args)
    }
    return [string]$text
}

if (-not (Test-Path $backendExe) -and -not (Test-Path $backendScript)) {
    [System.Windows.Forms.MessageBox]::Show(
        (T -Key "backendMissing" -Args @($backendExe, $backendScript)),
        (T -Key "windowTitle"),
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
    exit 1
}

function New-Label {
    param(
        [string]$Text,
        [int]$Left,
        [int]$Top,
        [int]$Width = 140
    )

    $label = New-Object System.Windows.Forms.Label
    $label.Text = $Text
    $label.Left = $Left
    $label.Top = $Top
    $label.Width = $Width
    $label.Height = 24
    return $label
}

function New-TextBox {
    param(
        [int]$Left,
        [int]$Top,
        [int]$Width = 430,
        [string]$Text = "",
        [bool]$UsePasswordChar = $false
    )

    $tb = New-Object System.Windows.Forms.TextBox
    $tb.Left = $Left
    $tb.Top = $Top
    $tb.Width = $Width
    $tb.Text = $Text
    $tb.UseSystemPasswordChar = $UsePasswordChar
    return $tb
}

$form = New-Object System.Windows.Forms.Form
$form.Text = T -Key "windowTitle"
$form.StartPosition = "CenterScreen"
$form.Size = New-Object System.Drawing.Size(680, 620)
$form.MinimumSize = New-Object System.Drawing.Size(680, 620)
$font = New-Object System.Drawing.Font("Segoe UI", 10)
$form.Font = $font

$y = 20

$lblTitle = New-Label -Text (T -Key "title") -Left 20 -Top $y -Width 420
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
$lblTitle.Height = 32
$form.Controls.Add($lblTitle)

$lblLanguage = New-Label -Text (T -Key "language") -Left 450 -Top ($y + 3) -Width 90
$cmbLanguage = New-Object System.Windows.Forms.ComboBox
$cmbLanguage.Left = 540
$cmbLanguage.Top = $y
$cmbLanguage.Width = 105
$cmbLanguage.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
[void]$cmbLanguage.Items.Add("中文")
[void]$cmbLanguage.Items.Add("English")
$cmbLanguage.SelectedIndex = 0
$form.Controls.Add($lblLanguage)
$form.Controls.Add($cmbLanguage)

$y += 50
$lblRepoRoot = New-Label -Text (T -Key "repoRoot") -Left 20 -Top $y -Width 140
$txtRepoRoot = New-TextBox -Left 170 -Top $y -Width 380 -Text $defaultRepoRoot
$btnBrowseRepo = New-Object System.Windows.Forms.Button
$btnBrowseRepo.Text = T -Key "browse"
$btnBrowseRepo.Left = 565
$btnBrowseRepo.Top = $y - 1
$btnBrowseRepo.Width = 80
$form.Controls.Add($lblRepoRoot)
$form.Controls.Add($txtRepoRoot)
$form.Controls.Add($btnBrowseRepo)

$y += 40
$lblJiraBaseUrl = New-Label -Text (T -Key "jiraBaseUrl") -Left 20 -Top $y -Width 140
$txtJiraBaseUrl = New-TextBox -Left 170 -Top $y -Width 475 -Text "http://oa.htek.com:8088/secure/Dashboard.jspa"
$form.Controls.Add($lblJiraBaseUrl)
$form.Controls.Add($txtJiraBaseUrl)

$y += 40
$lblJiraUsername = New-Label -Text (T -Key "jiraUsername") -Left 20 -Top $y -Width 140
$txtJiraUsername = New-TextBox -Left 170 -Top $y -Width 475
$form.Controls.Add($lblJiraUsername)
$form.Controls.Add($txtJiraUsername)

$y += 40
$lblJiraPassword = New-Label -Text (T -Key "jiraPassword") -Left 20 -Top $y -Width 140
$txtJiraPassword = New-TextBox -Left 170 -Top $y -Width 475 -UsePasswordChar $true
$form.Controls.Add($lblJiraPassword)
$form.Controls.Add($txtJiraPassword)

$y += 40
$lblAgent = New-Label -Text (T -Key "targetAgent") -Left 20 -Top $y -Width 140
$cmbAgent = New-Object System.Windows.Forms.ComboBox
$cmbAgent.Left = 170
$cmbAgent.Top = $y
$cmbAgent.Width = 200
$cmbAgent.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
[void]$cmbAgent.Items.Add("codex")
[void]$cmbAgent.Items.Add("cursor")
[void]$cmbAgent.Items.Add("openclaw")
[void]$cmbAgent.Items.Add("hermes")
$cmbAgent.SelectedIndex = 0
$form.Controls.Add($lblAgent)
$form.Controls.Add($cmbAgent)

$y += 40
$chkInstallPythonDeps = New-Object System.Windows.Forms.CheckBox
$chkInstallPythonDeps.Text = T -Key "installPythonDeps"
$chkInstallPythonDeps.Left = 170
$chkInstallPythonDeps.Top = $y
$chkInstallPythonDeps.Width = 360
$form.Controls.Add($chkInstallPythonDeps)

$y += 35
$chkImportSkills = New-Object System.Windows.Forms.CheckBox
$chkImportSkills.Text = T -Key "importSkills"
$chkImportSkills.Left = 170
$chkImportSkills.Top = $y
$chkImportSkills.Width = 240
$chkImportSkills.Checked = $true
$form.Controls.Add($chkImportSkills)

$y += 40
$lblCursorScope = New-Label -Text (T -Key "cursorScope") -Left 20 -Top $y -Width 140
$cmbCursorScope = New-Object System.Windows.Forms.ComboBox
$cmbCursorScope.Left = 170
$cmbCursorScope.Top = $y
$cmbCursorScope.Width = 200
$cmbCursorScope.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
[void]$cmbCursorScope.Items.Add("project")
[void]$cmbCursorScope.Items.Add("global")
$cmbCursorScope.SelectedIndex = 0
$form.Controls.Add($lblCursorScope)
$form.Controls.Add($cmbCursorScope)

$y += 50
$txtStatus = New-Object System.Windows.Forms.TextBox
$txtStatus.Left = 20
$txtStatus.Top = $y
$txtStatus.Width = 625
$txtStatus.Height = 120
$txtStatus.Multiline = $true
$txtStatus.ScrollBars = "Vertical"
$txtStatus.ReadOnly = $true
$txtStatus.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor `
    [System.Windows.Forms.AnchorStyles]::Left -bor `
    [System.Windows.Forms.AnchorStyles]::Right -bor `
    [System.Windows.Forms.AnchorStyles]::Bottom
$form.Controls.Add($txtStatus)

$buttonTop = $txtStatus.Top + $txtStatus.Height + 12

$btnInstall = New-Object System.Windows.Forms.Button
$btnInstall.Text = T -Key "install"
$btnInstall.Left = 455
$btnInstall.Top = $buttonTop
$btnInstall.Width = 90
$btnInstall.Height = 32
$btnInstall.Anchor = [System.Windows.Forms.AnchorStyles]::Right -bor [System.Windows.Forms.AnchorStyles]::Bottom

$btnClose = New-Object System.Windows.Forms.Button
$btnClose.Text = T -Key "close"
$btnClose.Left = 555
$btnClose.Top = $buttonTop
$btnClose.Width = 90
$btnClose.Height = 32
$btnClose.Anchor = [System.Windows.Forms.AnchorStyles]::Right -bor [System.Windows.Forms.AnchorStyles]::Bottom

$form.Controls.Add($btnInstall)
$form.Controls.Add($btnClose)

$folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog
$folderDialog.Description = T -Key "folderDialogDescription"

function Refresh-Language {
    $form.Text = T -Key "windowTitle"
    $lblTitle.Text = T -Key "title"
    $lblLanguage.Text = T -Key "language"
    $lblRepoRoot.Text = T -Key "repoRoot"
    $btnBrowseRepo.Text = T -Key "browse"
    $lblJiraBaseUrl.Text = T -Key "jiraBaseUrl"
    $lblJiraUsername.Text = T -Key "jiraUsername"
    $lblJiraPassword.Text = T -Key "jiraPassword"
    $lblAgent.Text = T -Key "targetAgent"
    $chkInstallPythonDeps.Text = T -Key "installPythonDeps"
    $chkImportSkills.Text = T -Key "importSkills"
    $lblCursorScope.Text = T -Key "cursorScope"
    $btnInstall.Text = T -Key "install"
    $btnClose.Text = T -Key "close"
    $folderDialog.Description = T -Key "folderDialogDescription"
}

function Refresh-UiState {
    $isCursor = ($cmbAgent.SelectedItem -eq "cursor")
    $lblCursorScope.Enabled = $isCursor
    $cmbCursorScope.Enabled = $isCursor

    $isCodex = ($cmbAgent.SelectedItem -eq "codex")
    if (-not $isCodex) {
        $chkImportSkills.Checked = $false
    }
    $chkImportSkills.Enabled = $isCodex
}

function Append-Status {
    param([string]$Line)

    $txtStatus.AppendText($Line + [Environment]::NewLine)
}

$btnBrowseRepo.Add_Click({
    $folderDialog.SelectedPath = $txtRepoRoot.Text
    if ($folderDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $txtRepoRoot.Text = $folderDialog.SelectedPath
    }
})

$cmbLanguage.Add_SelectedIndexChanged({
    if ($cmbLanguage.SelectedIndex -eq 1) {
        $script:currentLang = "en-US"
    } else {
        $script:currentLang = "zh-CN"
    }
    Refresh-Language
})

$cmbAgent.Add_SelectedIndexChanged({
    Refresh-UiState
})

$btnClose.Add_Click({
    $form.Close()
})

$btnInstall.Add_Click({
    $repoRoot = $txtRepoRoot.Text.Trim()
    $jiraBaseUrl = $txtJiraBaseUrl.Text.Trim()
    $jiraUsername = $txtJiraUsername.Text.Trim()
    $jiraPassword = $txtJiraPassword.Text
    $agent = [string]$cmbAgent.SelectedItem
    $cursorScope = [string]$cmbCursorScope.SelectedItem

    if ([string]::IsNullOrWhiteSpace($repoRoot) -or -not (Test-Path $repoRoot)) {
        [System.Windows.Forms.MessageBox]::Show((T -Key "repoRootRequired"), (T -Key "windowTitle")) | Out-Null
        return
    }
    if ([string]::IsNullOrWhiteSpace($jiraBaseUrl)) {
        [System.Windows.Forms.MessageBox]::Show((T -Key "jiraBaseUrlRequired"), (T -Key "windowTitle")) | Out-Null
        return
    }
    if ([string]::IsNullOrWhiteSpace($jiraUsername)) {
        [System.Windows.Forms.MessageBox]::Show((T -Key "jiraUsernameRequired"), (T -Key "windowTitle")) | Out-Null
        return
    }
    if ([string]::IsNullOrWhiteSpace($jiraPassword)) {
        [System.Windows.Forms.MessageBox]::Show((T -Key "jiraPasswordRequired"), (T -Key "windowTitle")) | Out-Null
        return
    }

    $btnInstall.Enabled = $false
    $txtStatus.Clear()
    Append-Status (T -Key "runningInstaller")

    $args = @(
        "-NonInteractive",
        "-RepoRoot", $repoRoot,
        "-JiraBaseUrl", $jiraBaseUrl,
        "-JiraUsername", $jiraUsername,
        "-JiraPassword", $jiraPassword,
        "-Agent", $agent
    )

    if ($agent -eq "cursor") {
        $args += @("-CursorInstallScope", $cursorScope)
    }
    if ($chkImportSkills.Checked) {
        $args += "-ImportSkills"
    }
    if ($chkInstallPythonDeps.Checked) {
        $args += "-InstallPythonDeps"
    }

    $escapedArgs = [string]::Join(" ", ($args | ForEach-Object {
        if ($_ -match '\s') { '"' + $_.Replace('"', '\"') + '"' } else { $_ }
    }))

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    if (Test-Path $backendExe) {
        $psi.FileName = $backendExe
        $psi.Arguments = $escapedArgs
    } else {
        $psi.FileName = "powershell.exe"
        $psi.Arguments = ('-NoProfile -ExecutionPolicy Bypass -File "{0}" {1}' -f $backendScript, $escapedArgs)
    }
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()

    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    if (-not [string]::IsNullOrWhiteSpace($stdout)) {
        Append-Status $stdout.Trim()
    }
    if (-not [string]::IsNullOrWhiteSpace($stderr)) {
        Append-Status $stderr.Trim()
    }

    if ($proc.ExitCode -eq 0) {
        Append-Status ""
        Append-Status (T -Key "installCompletedStatus")
        [System.Windows.Forms.MessageBox]::Show((T -Key "installCompleted"), (T -Key "windowTitle")) | Out-Null
    } else {
        Append-Status ""
        Append-Status (T -Key "installFailedStatus" -Args @($proc.ExitCode))
        [System.Windows.Forms.MessageBox]::Show((T -Key "installFailed"), (T -Key "windowTitle")) | Out-Null
    }

    $btnInstall.Enabled = $true
})

Refresh-Language
Refresh-UiState
[void]$form.ShowDialog()
