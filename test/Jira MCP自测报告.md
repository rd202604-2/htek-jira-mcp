# Jira MCP 自测报告

日期：2026-04-22  
环境：Windows 上的 Codex Desktop，公司内网，Jira Server 地址为 `http://oa.htek.com:8088`  
目标项目：`TASK`  
结果：通过

## 范围

本轮工作覆盖两个交付项：

1. 为本地 Jira Server MCP 补充项目管理相关操作能力。
2. 新增 4 个适配 Jira Server 的 skill，用于状态汇报、需求拆解、问题分诊和会议纪要转任务。

## 已实现的 MCP 功能

保留的已有功能：
- `jira_whoami`
- `list_jira_projects`
- `search_jira_issues`
- `get_jira_issue`
- `get_jira_issue_types`
- `create_jira_issue`
- `add_jira_comment`

本次新增功能：
- `search_jira_users`
- `get_jira_issue_type_fields`
- `create_jira_subtask`
- `get_jira_comments`
- `list_jira_transitions`
- `transition_jira_issue`
- `update_jira_assignee`
- `update_jira_issue`

## 已实现的 Skills

已创建到 `C:\Users\admin\.codex\skills`：
- `jira-server-status-report`
- `jira-server-spec-to-backlog`
- `jira-server-triage-issue`
- `jira-server-meeting-to-tasks`

校验结果：
- 以上 4 个 skill 均通过 `quick_validate.py` 校验。

## 自测方法

自动化自测脚本：
- [Jira MCP自测脚本.py](Jira%20MCP%E8%87%AA%E6%B5%8B%E8%84%9A%E6%9C%AC.py)

JSON 结果文件：
- [Jira MCP自测结果.json](Jira%20MCP%E8%87%AA%E6%B5%8B%E7%BB%93%E6%9E%9C.json)

本次针对真实 Jira Server 执行的测试流程如下：

1. 验证当前认证用户
2. 列出可见项目
3. 搜索当前 Jira 用户
4. 读取 `TASK` 项目的 issue type
5. 读取 `TASK` 项目的必填字段元数据
6. 创建父任务
7. 更新任务字段
8. 添加评论并回读
9. 更新负责人
10. 查询状态流转并执行一次流转
11. 创建子任务
12. 回读父任务和子任务详情
13. 按标签搜索刚创建的任务

## 自测结果汇总

通过的检查项：
- `jira_whoami`
- `list_jira_projects`
- `search_jira_users`
- `get_jira_issue_types`
- `get_jira_issue_type_fields`
- `create_jira_issue`
- `update_jira_issue`
- `add_jira_comment`
- `get_jira_comments`
- `update_jira_assignee`
- `list_jira_transitions`
- `transition_jira_issue`
- `get_jira_issue`
- `create_jira_subtask`
- `get_jira_issue_subtask`
- `search_jira_issues`

自动化自测过程中创建的真实 Jira 测试单：
- 父任务：`TASK-138`
- 子任务：`TASK-139`

在调试 Jira Server 兼容性时额外创建的人工验证单：
- 父任务：`TASK-136`
- 子任务：`TASK-137`

## 重要发现

1. `TASK` 项目在创建父任务和子任务时，都要求必填自定义字段 `customfield_12800`（`验收标准`）。
2. 当前这套 Jira Server 在创建 issue 时，使用 issue type 的 `id` 比使用 issue type 的 `name` 更稳定。
3. 如果机器走了会影响公司内网访问的 VPN，Jira 会访问失败；直接走公司内网时访问正常。

## 已知限制

1. 当前 MCP 还不支持删除 issue，因此自测过程中创建的测试单仍保留在 Jira 中。
2. 不同项目、不同 issue type 的必填字段不一致。在新项目里创建 issue 前，应先调用 `get_jira_issue_type_fields` 检查字段要求。
3. 这些 skill 目前是工作流指导层，依赖当前 Codex 会话里已经可用的 MCP 工具。

## 变更文件

核心实现：
- [jira_server_mcp.py](../tools/jira_server_mcp.py)
- [Jira MCP自测脚本.py](Jira%20MCP%E8%87%AA%E6%B5%8B%E8%84%9A%E6%9C%AC.py)

Skills：
- [jira-server-status-report](../skills/jira-server-status-report/SKILL.md)
- [jira-server-spec-to-backlog](../skills/jira-server-spec-to-backlog/SKILL.md)
- [jira-server-triage-issue](../skills/jira-server-triage-issue/SKILL.md)
- [jira-server-meeting-to-tasks](../skills/jira-server-meeting-to-tasks/SKILL.md)
