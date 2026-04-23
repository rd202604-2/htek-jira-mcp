Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendScript = Join-Path $scriptDir "setup-jira-agent.ps1"
$backendExe = Join-Path $scriptDir "JiraMCPInstaller.exe"

if (-not (Test-Path $backendExe) -and -not (Test-Path $backendScript)) {
    [System.Windows.Forms.MessageBox]::Show(
        "Backend installer was not found.`r`nExpected one of:`r`n$backendExe`r`n$backendScript",
        "Jira MCP Installer",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
    exit 1
}

$form = New-Object System.Windows.Forms.Form
$form.Text = "Jira MCP Installer"
$form.StartPosition = "CenterScreen"
$form.Size = New-Object System.Drawing.Size(680, 520)
$form.MinimumSize = New-Object System.Drawing.Size(680, 520)

$font = New-Object System.Drawing.Font("Segoe UI", 10)
$form.Font = $font

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

$y = 20

$lblTitle = New-Label -Text "Install Jira MCP for agent" -Left 20 -Top $y -Width 500
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
$lblTitle.Height = 32
$form.Controls.Add($lblTitle)

$y += 50
$form.Controls.Add((New-Label -Text "Repository Root" -Left 20 -Top $y))
$txtRepoRoot = New-TextBox -Left 170 -Top $y -Width 380 -Text (Split-Path -Parent $scriptDir)
$btnBrowseRepo = New-Object System.Windows.Forms.Button
$btnBrowseRepo.Text = "Browse..."
$btnBrowseRepo.Left = 565
$btnBrowseRepo.Top = $y - 1
$btnBrowseRepo.Width = 80
$form.Controls.Add($txtRepoRoot)
$form.Controls.Add($btnBrowseRepo)

$y += 40
$form.Controls.Add((New-Label -Text "Jira Base URL" -Left 20 -Top $y))
$txtJiraBaseUrl = New-TextBox -Left 170 -Top $y -Width 475 -Text "http://oa.htek.com:8088/secure/Dashboard.jspa"
$form.Controls.Add($txtJiraBaseUrl)

$y += 40
$form.Controls.Add((New-Label -Text "Jira Username" -Left 20 -Top $y))
$txtJiraUsername = New-TextBox -Left 170 -Top $y -Width 475
$form.Controls.Add($txtJiraUsername)

$y += 40
$form.Controls.Add((New-Label -Text "Jira Password" -Left 20 -Top $y))
$txtJiraPassword = New-TextBox -Left 170 -Top $y -Width 475 -UsePasswordChar $true
$form.Controls.Add($txtJiraPassword)

$y += 40
$form.Controls.Add((New-Label -Text "Target Agent" -Left 20 -Top $y))
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
$form.Controls.Add($cmbAgent)

$y += 40
$chkInstallPythonDeps = New-Object System.Windows.Forms.CheckBox
$chkInstallPythonDeps.Text = "Install Python dependencies (mcp, PyYAML)"
$chkInstallPythonDeps.Left = 170
$chkInstallPythonDeps.Top = $y
$chkInstallPythonDeps.Width = 320
$form.Controls.Add($chkInstallPythonDeps)

$y += 35
$chkImportSkills = New-Object System.Windows.Forms.CheckBox
$chkImportSkills.Text = "Import Codex skills"
$chkImportSkills.Left = 170
$chkImportSkills.Top = $y
$chkImportSkills.Width = 240
$chkImportSkills.Checked = $true
$form.Controls.Add($chkImportSkills)

$y += 40
$lblCursorScope = New-Label -Text "Cursor Scope" -Left 20 -Top $y
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
$txtStatus.Height = 140
$txtStatus.Multiline = $true
$txtStatus.ScrollBars = "Vertical"
$txtStatus.ReadOnly = $true
$form.Controls.Add($txtStatus)

$btnInstall = New-Object System.Windows.Forms.Button
$btnInstall.Text = "Install"
$btnInstall.Left = 455
$btnInstall.Top = 420
$btnInstall.Width = 90
$btnInstall.Height = 32

$btnClose = New-Object System.Windows.Forms.Button
$btnClose.Text = "Close"
$btnClose.Left = 555
$btnClose.Top = 420
$btnClose.Width = 90
$btnClose.Height = 32

$form.Controls.Add($btnInstall)
$form.Controls.Add($btnClose)

$folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog

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
        [System.Windows.Forms.MessageBox]::Show("Please choose a valid repository root.", "Jira MCP Installer") | Out-Null
        return
    }
    if ([string]::IsNullOrWhiteSpace($jiraBaseUrl)) {
        [System.Windows.Forms.MessageBox]::Show("Jira base URL is required.", "Jira MCP Installer") | Out-Null
        return
    }
    if ([string]::IsNullOrWhiteSpace($jiraUsername)) {
        [System.Windows.Forms.MessageBox]::Show("Jira username is required.", "Jira MCP Installer") | Out-Null
        return
    }
    if ([string]::IsNullOrWhiteSpace($jiraPassword)) {
        [System.Windows.Forms.MessageBox]::Show("Jira password is required.", "Jira MCP Installer") | Out-Null
        return
    }

    $btnInstall.Enabled = $false
    $txtStatus.Clear()
    Append-Status "Running installer..."

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
        Append-Status "Installation completed successfully."
        [System.Windows.Forms.MessageBox]::Show("Installation completed.", "Jira MCP Installer") | Out-Null
    } else {
        Append-Status ""
        Append-Status ("Installation failed with exit code {0}." -f $proc.ExitCode)
        [System.Windows.Forms.MessageBox]::Show("Installation failed. See details in the status box.", "Jira MCP Installer") | Out-Null
    }

    $btnInstall.Enabled = $true
})

Refresh-UiState
[void]$form.ShowDialog()
