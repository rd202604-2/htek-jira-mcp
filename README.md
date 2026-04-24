# Htek Jira MCP 项目说明

## 1. 目的

本文档用于介绍当前仓库的整体结构和用途。

本项目主要包含：
- 公司本地 Jira Server MCP
- 4 个 Jira skills
- 安装脚本、图形界面安装器、打包脚本
- 测试脚本与测试文档

适用对象：
- 研发
- 测试
- 产品
- 市场
- 需要在 Codex Desktop、Cursor、OpenClaw 或 Hermes 中接入公司 Jira Server 的同事

## 2. 仓库目录约定

当前仓库建议按以下职责使用：

- `docs/`
  面向团队和流程的文档、SOP、Prompt 模板

- `tools/`
  实际功能脚本

- `install/`
  安装说明和安装相关目录

- `install/build/`
  安装脚本、图形界面安装器源码、打包脚本

- `install/output/`
  打包后的安装产物，例如控制台版和图形界面版安装器 `exe`

- `skills/`
  可安装到 Codex 的 Jira skills

- `test/`
  测试脚本、测试结果、测试报告

## 3. 需要的前置条件

使用本项目前，目标机器通常需要具备：

1. 已安装 Agent
   当前支持：`Codex`、`Cursor`、`OpenClaw`、`Hermes`
2. 已安装 Python，并且 `python` 可在终端直接执行
3. 可以访问公司内网 Jira Server
4. 拥有自己的 Jira 账号密码

## 4. 关键内容

### 4.1 功能脚本

- MCP 主脚本：
  [jira_server_mcp.py](tools/jira_server_mcp.py)

### 4.2 安装目录

- 统一命令行安装器：
  [setup-jira-agent.ps1](install/build/setup-jira-agent.ps1)
- 图形界面安装器源码：
  [setup-jira-agent-gui.ps1](install/build/setup-jira-agent-gui.ps1)
- EXE 打包脚本：
  [build-jira-installer.ps1](install/build/build-jira-installer.ps1)
- EXE 打包说明：
  [EXE打包说明.md](install/build/EXE%E6%89%93%E5%8C%85%E8%AF%B4%E6%98%8E.md)
- 安装说明：
  [HtekJira安装与使用说明.md](install/HtekJira安装与使用说明.md)

### 4.3 安装产物

- 控制台版安装器：
  [JiraMCPInstaller.exe](install/output/JiraMCPInstaller.exe)
- 图形界面版安装器：
  [JiraMCPInstallerGUI.exe](install/output/JiraMCPInstallerGUI.exe)

### 4.4 Skills

- `skills/jira-server-status-report`
- `skills/jira-server-spec-to-backlog`
- `skills/jira-server-triage-issue`
- `skills/jira-server-meeting-to-tasks`

### 4.5 测试文件

- [Jira MCP自测脚本.py](test/Jira%20MCP%E8%87%AA%E6%B5%8B%E8%84%9A%E6%9C%AC.py)
- [Jira MCP自测结果.json](test/Jira%20MCP%E8%87%AA%E6%B5%8B%E7%BB%93%E6%9E%9C.json)
- [Jira MCP自测报告.md](test/Jira%20MCP%E8%87%AA%E6%B5%8B%E6%8A%A5%E5%91%8A.md)

## 5. 相关文档

### 5.1 获取仓库代码

在新电脑上执行：

```powershell
git clone <你的仓库地址>
cd <仓库目录>
```

### 5.2 相关文档

- 安装使用：
  [HtekJira安装与使用说明.md](install/HtekJira安装与使用说明.md)
- EXE 打包：
  [EXE打包说明.md](install/build/EXE%E6%89%93%E5%8C%85%E8%AF%B4%E6%98%8E.md)
- 团队 SOP：
  [HtekJira MCP使用SOP.md](docs/HtekJira%20MCP%E4%BD%BF%E7%94%A8SOP.md)
