# EXE 打包说明

## 1. 目的

本文档用于说明如何将 `install/build/` 目录下的源脚本打包为 Windows `exe` 安装器。

当前支持打包的源脚本：

- [setup-jira-agent.ps1](setup-jira-agent.ps1)
  命令行安装器
- [setup-jira-agent-gui.ps1](setup-jira-agent-gui.ps1)
  图形界面安装器

打包脚本：

- [build-jira-installer.ps1](build-jira-installer.ps1)

默认输出目录：

- `install/output/`

## 2. 前置条件

打包前需要具备：

1. 已安装 Windows PowerShell
2. 已安装 Python
3. 当前机器可访问 PowerShell Gallery
4. 当前用户有权限安装 `ps2exe`

## 3. 打包命令

### 3.1 打包命令行版安装器

执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install\build\build-jira-installer.ps1 -InstallPs2Exe
```

默认生成：

```text
install/output/JiraMCPInstaller.exe
```

### 3.2 打包图形界面版安装器

执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install\build\build-jira-installer.ps1 `
  -SourceScript .\install\build\setup-jira-agent-gui.ps1 `
  -OutputPath .\install\output\JiraMCPInstallerGUI.exe `
  -NoConsole
```

生成：

```text
install/output/JiraMCPInstallerGUI.exe
```

## 4. 产物说明

- [JiraMCPInstaller.exe](../output/JiraMCPInstaller.exe)
  控制台版安装器，适合命令行或脚本调用

- [JiraMCPInstallerGUI.exe](../output/JiraMCPInstallerGUI.exe)
  图形界面版安装器，适合同事直接双击使用

推荐分发方式：

1. 将两个 `exe` 放在同一个目录
2. 优先让同事双击 GUI 版
3. 如果需要排障，再使用命令行版查看输出

## 5. 常见问题

### 问题 1：找不到 `ps2exe`

处理方式：

```powershell
powershell -ExecutionPolicy Bypass -File .\install\build\build-jira-installer.ps1 -InstallPs2Exe
```

### 问题 2：打包后 GUI 安装器无法调用后端

检查：

1. `JiraMCPInstallerGUI.exe` 和 `JiraMCPInstaller.exe` 是否放在同一目录
2. 是否误删了控制台版安装器
3. 是否修改了产物文件名
