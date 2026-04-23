# Htek Jira 安装与使用说明

## 1. 说明

本文档只聚焦安装与接入步骤。

如果你想先了解项目结构、目录约定、关键文件和整体说明，请先阅读：

- [README.md](/C:/Users/admin/Documents/AllinAi/README.md)

## 2. 通用安装步骤

推荐优先级如下：

- 方式 A：直接使用 [JiraMCPInstaller.exe](/C:/Users/admin/Documents/AllinAi/install/output/JiraMCPInstaller.exe)
- 方式 B：使用 [JiraMCPInstallerGUI.exe](/C:/Users/admin/Documents/AllinAi/install/output/JiraMCPInstallerGUI.exe)
- 方式 C：使用 [setup-jira-agent.ps1](/C:/Users/admin/Documents/AllinAi/install/build/setup-jira-agent.ps1)

### 方式 A：使用 JiraMCPInstaller.exe 安装

适用场景：

- 需要最稳妥的安装方式
- 希望直接看到控制台输出，便于排障
- 适合技术同事自行安装

使用方法：

1. 打开目录：
   `install/output/`
2. 双击运行：
   [JiraMCPInstaller.exe](/C:/Users/admin/Documents/AllinAi/install/output/JiraMCPInstaller.exe)
3. 按提示输入：
   Jira 地址、用户名、密码
4. 选择目标 agent：
   `Codex`、`Cursor`、`OpenClaw`、`Hermes`
5. 选择是否导入 skill
6. 如果目标是 `Cursor`，继续选择：
   `项目级配置` 或 `全局配置`

说明：

- 这是控制台版安装器
- 安装过程中的详细输出会直接显示出来
- 如果安装失败，优先建议先用这个版本排障

### 方式 B：使用 JiraMCPInstallerGUI.exe 安装

适用场景：

- 希望同事直接双击安装
- 希望使用图形界面表单输入配置
- 适合非技术同事或批量分发使用

使用方法：

1. 打开目录：
   `install/output/`
2. 确保以下两个文件在同一目录下：
   [JiraMCPInstaller.exe](/C:/Users/admin/Documents/AllinAi/install/output/JiraMCPInstaller.exe)
   [JiraMCPInstallerGUI.exe](/C:/Users/admin/Documents/AllinAi/install/output/JiraMCPInstallerGUI.exe)
3. 双击运行：
   [JiraMCPInstallerGUI.exe](/C:/Users/admin/Documents/AllinAi/install/output/JiraMCPInstallerGUI.exe)
4. 在界面中填写：
   仓库路径、Jira 地址、用户名、密码
5. 选择目标 agent、是否导入 skill，以及 Cursor 安装范围
6. 点击 `Install`

说明：

- GUI 版会优先调用同目录下的控制台版安装器
- 所以分发时最好把两个 `exe` 一起发给同事
- 如果图形界面安装失败，建议回退到 `JiraMCPInstaller.exe`

### 方式 C：使用 setup-jira-agent.ps1 安装

推荐命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\install\build\setup-jira-agent.ps1
```

安装器会依次提示你：

1. 输入 Jira 地址
2. 输入 Jira 用户名
3. 输入 Jira 密码
4. 选择当前 agent
   支持：`Codex`、`Cursor`、`OpenClaw`、`Hermes`
5. 选择是否导入 skill
6. 如果选择 `Cursor`，继续选择：
   `项目级配置` 或 `全局配置`

说明：

- `skill` 目前只会真正导入到 `Codex`
- `Cursor`、`OpenClaw`、`Hermes` 会安装同一个 Jira MCP，但不会直接读取 Codex skill

适用场景：

- 需要通过脚本参数做自动化安装
- 需要开发、调试或扩展安装逻辑
- 需要查看或修改安装源码

如果你想重新打包 `exe`，请查看：

- [EXE打包说明.md](/C:/Users/admin/Documents/AllinAi/install/build/EXE%E6%89%93%E5%8C%85%E8%AF%B4%E6%98%8E.md)

## 3. 在 Codex Desktop 中接入 Jira MCP

### 第一步：确认 Codex 配置已写入

检查 `~/.codex/config.toml` 中是否已有：

```toml
[mcp_servers.htek_jira_server]
command = "python"
args = ["<仓库路径>\\tools\\jira_server_mcp.py"]
enabled = true
```

### 第二步：重启 Codex Desktop

安装完成后，重启 Codex Desktop。

### 第三步：验证 Codex 是否已接入成功

可以直接让 Codex 执行：

```text
列出我当前能访问的 Jira 项目
```

或者：

```text
查看 RDTASK 最近 7 天更新的任务
```

## 4. 在 Cursor 中接入 Jira MCP

根据 Cursor 官方 MCP 文档，Cursor 支持项目级配置和全局配置。

推荐两种方式：

- 只想当前仓库可用：在仓库根目录创建 `.cursor/mcp.json`
- 想让本机所有项目都可用：在 `%USERPROFILE%\\.cursor\\mcp.json` 中配置

### 方式 A：项目级配置

在当前仓库根目录新建文件 `.cursor/mcp.json`，内容示例：

```json
{
  "mcpServers": {
    "htek_jira_server": {
      "command": "python",
      "args": [
        "${workspaceFolder}/tools/jira_server_mcp.py"
      ],
      "env": {
        "HTEK_JIRA_BASE_URL": "${env:HTEK_JIRA_BASE_URL}",
        "HTEK_JIRA_USERNAME": "${env:HTEK_JIRA_USERNAME}",
        "HTEK_JIRA_PASSWORD": "${env:HTEK_JIRA_PASSWORD}"
      }
    }
  }
}
```

说明：

- `${workspaceFolder}` 表示当前 Cursor 打开的项目根目录
- 这里直接复用安装脚本已经写入的 3 个环境变量
- 如果仓库路径变了，只要还是在该项目里打开，通常不需要手动改路径

### 方式 B：全局配置

如果你希望任何项目里都能使用这个 Jira MCP，可以在 `%USERPROFILE%\\.cursor\\mcp.json` 中写入：

```json
{
  "mcpServers": {
    "htek_jira_server": {
      "command": "python",
      "args": [
        "C:/你的仓库路径/tools/jira_server_mcp.py"
      ],
      "env": {
        "HTEK_JIRA_BASE_URL": "${env:HTEK_JIRA_BASE_URL}",
        "HTEK_JIRA_USERNAME": "${env:HTEK_JIRA_USERNAME}",
        "HTEK_JIRA_PASSWORD": "${env:HTEK_JIRA_PASSWORD}"
      }
    }
  }
}
```

说明：

- 全局配置里的脚本路径建议写绝对路径
- 如果换了仓库位置，需要同步更新这里的路径

### 第三步：重启 Cursor

保存配置后，重启 Cursor。

### 第四步：验证 Cursor 是否已接入成功

可以在 Cursor Agent / Chat 中直接尝试：

```text
列出我当前能访问的 Jira 项目
```

或者：

```text
查看 RDTASK 最近 7 天更新的任务
```

如果你本机装了 Cursor CLI，也可以用官方命令检查 MCP 状态：

```powershell
cursor-agent mcp list
```

以及查看该服务器提供的工具：

```powershell
cursor-agent mcp list-tools htek_jira_server
```

## 5. Codex 与 Cursor 的差异说明

- `jira_server_mcp.py` 这一套 MCP，Codex 和 Cursor 都可以复用
- `skills/` 目录下的 4 个 Jira skill 目前是给 Codex 使用的
- Cursor 侧这次主要接入的是 Jira MCP，不会直接读取 `~/.codex/skills/`
- 如果后续要给 Cursor 做统一模板，建议另行整理成 Cursor Prompt 模板或 Rules

## 6. 故障排查

### 问题 1：Codex 看不到 Jira MCP

检查：

1. `~/.codex/config.toml` 中是否已有：

```toml
[mcp_servers.htek_jira_server]
command = "python"
args = ["<仓库路径>\\tools\\jira_server_mcp.py"]
enabled = true
```

2. 是否已经重启 Codex Desktop

### 问题 2：Cursor 看不到 Jira MCP

检查：

1. `.cursor/mcp.json` 或 `%USERPROFILE%\\.cursor\\mcp.json` 是否已正确配置
2. `command` 是否可直接执行 `python`
3. `args` 中的 `jira_server_mcp.py` 路径是否正确
4. 当前终端里是否能读取到以下环境变量：

```powershell
echo $env:HTEK_JIRA_BASE_URL
echo $env:HTEK_JIRA_USERNAME
echo $env:HTEK_JIRA_PASSWORD
```

5. 是否已经重启 Cursor

### 问题 3：连接 Jira 失败

检查：

1. 是否在公司内网环境
2. 是否开启了会影响内网访问的 VPN
3. Jira 用户名密码是否正确

### 问题 4：创建 issue 报缺字段

说明：

- 不同项目的 issue type 有不同必填字段

处理建议：

1. 先查看 issue type
2. 再查看字段元数据
3. 补齐字段后再创建

## 7. 推荐阅读

- [README.md](/C:/Users/admin/Documents/AllinAi/README.md)
- [EXE打包说明.md](/C:/Users/admin/Documents/AllinAi/install/build/EXE%E6%89%93%E5%8C%85%E8%AF%B4%E6%98%8E.md)
- [HtekJira MCP使用SOP.md](/C:/Users/admin/Documents/AllinAi/docs/HtekJira%20MCP%E4%BD%BF%E7%94%A8SOP.md)
- [HtekJira内部标准Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/HtekJira%E5%86%85%E9%83%A8%E6%A0%87%E5%87%86Prompt%E6%A8%A1%E6%9D%BF.md)
- [HtekJira分部门Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/HtekJira%E5%88%86%E9%83%A8%E9%97%A8Prompt%E6%A8%A1%E6%9D%BF.md)
- [HtekJira Skills中文Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/HtekJira%20Skills%E4%B8%AD%E6%96%87Prompt%E6%A8%A1%E6%9D%BF.md)
