# Jira 跨电脑安装与使用说明

## 1. 目的

本文档用于说明如何在另一台电脑上复用当前仓库中的：
- 本地 Jira Server MCP
- 4 个 Jira skills
- 测试脚本与测试文档

适用对象：
- 研发
- 测试
- 产品
- 市场
- 需要在 Codex Desktop 中接入公司 Jira Server 的同事

## 2. 仓库目录约定

当前仓库建议按以下职责使用：

- `docs/`
  面向团队和流程的文档、SOP、Prompt 模板、安装说明

- `tools/`
  实际功能脚本和安装脚本

- `skills/`
  可安装到 Codex 的 Jira skills

- `test/`
  测试脚本、测试结果、测试报告

## 3. 需要的前置条件

新电脑上需要具备：

1. 已安装 Codex Desktop
2. 已安装 Python，并且 `python` 可在终端直接执行
3. 可以访问公司内网 Jira Server
4. 拥有自己的 Jira 账号密码

## 4. 仓库中包含的关键内容

### 4.1 MCP 脚本

- [jira_server_mcp.py](/C:/Users/admin/Documents/AllinAi/tools/jira_server_mcp.py)

### 4.2 安装脚本

- [setup-jira-codex.ps1](/C:/Users/admin/Documents/AllinAi/tools/setup-jira-codex.ps1)

### 4.3 Skills

- `skills/jira-server-status-report`
- `skills/jira-server-spec-to-backlog`
- `skills/jira-server-triage-issue`
- `skills/jira-server-meeting-to-tasks`

### 4.4 测试文件

- [Jira MCP自测脚本.py](/C:/Users/admin/Documents/AllinAi/test/Jira%20MCP%E8%87%AA%E6%B5%8B%E8%84%9A%E6%9C%AC.py)
- [Jira MCP自测结果.json](/C:/Users/admin/Documents/AllinAi/test/Jira%20MCP%E8%87%AA%E6%B5%8B%E7%BB%93%E6%9E%9C.json)
- [Jira MCP自测报告.md](/C:/Users/admin/Documents/AllinAi/test/Jira%20MCP%E8%87%AA%E6%B5%8B%E6%8A%A5%E5%91%8A.md)

## 5. 在另一台电脑上的安装步骤

### 第一步：获取仓库代码

在新电脑上执行：

```powershell
git clone <你的仓库地址>
cd <仓库目录>
```

### 第二步：运行安装脚本

推荐命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\setup-jira-codex.ps1 `
  -InstallPythonDeps `
  -JiraBaseUrl "http://oa.htek.com:8088/secure/Dashboard.jspa" `
  -JiraUsername "<你的Jira用户名>" `
  -JiraPassword "<你的Jira密码>"
```

脚本会自动完成：

1. 检查 Python 是否可用
2. 安装 `mcp` 和 `PyYAML`
3. 将仓库中的 4 个 skill 复制到 `~/.codex/skills/`
4. 在 `~/.codex/config.toml` 中注册 `htek_jira_server`
5. 将 Jira 地址、用户名、密码写入当前 Windows 用户环境变量

### 第三步：重启 Codex Desktop

安装完成后，重启 Codex Desktop。

## 6. 安装后验证方法

重启 Codex 后，可以直接让 Codex 执行以下操作验证：

```text
列出我当前能访问的 Jira 项目
```

或者：

```text
查看 RDTASK 最近 7 天更新的任务
```

## 7. 常用使用方式

### 7.1 查看项目状态

使用：
- `$jira-server-status-report`

示例：

```text
请使用 $jira-server-status-report 生成研发周报。

项目 key：RDTASK
时间范围：最近 7 天
汇报对象：研发负责人
输出风格：简洁摘要
```

### 7.2 将需求拆成 Jira 任务

使用：
- `$jira-server-spec-to-backlog`

### 7.3 处理 bug / 问题反馈

使用：
- `$jira-server-triage-issue`

### 7.4 把会议纪要转成任务

使用：
- `$jira-server-meeting-to-tasks`

## 8. 推荐使用规范

建议团队统一遵循：

1. 先展示方案，再执行创建或修改
2. 创建 issue 前先检查 issue type 和必填字段
3. 分诊类任务默认不直接建单
4. 会议纪要默认先展示拟创建列表

## 9. 故障排查

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

### 问题 2：连接 Jira 失败

检查：

1. 是否在公司内网环境
2. 是否开启了会影响内网访问的 VPN
3. Jira 用户名密码是否正确

### 问题 3：创建 issue 报缺字段

说明：
- 不同项目的 issue type 有不同必填字段

处理建议：
1. 先查看 issue type
2. 再查看字段元数据
3. 补齐字段后再创建

## 10. 推荐阅读

- [Jira Server团队使用SOP.md](/C:/Users/admin/Documents/AllinAi/docs/Jira%20Server%E5%9B%A2%E9%98%9F%E4%BD%BF%E7%94%A8SOP.md)
- [Jira内部标准Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira%E5%86%85%E9%83%A8%E6%A0%87%E5%87%86Prompt%E6%A8%A1%E6%9D%BF.md)
- [Jira分部门Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira%E5%88%86%E9%83%A8%E9%97%A8Prompt%E6%A8%A1%E6%9D%BF.md)
- [Jira Skills中文Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira%20Skills%E4%B8%AD%E6%96%87Prompt%E6%A8%A1%E6%9D%BF.md)
