# HtekJira REST API与MCP能力映射

## 1. 当前 MCP 已开发的功能

当前仓库中 [jira_server_mcp.py](../../tools/jira_server_mcp.py) 已实现的 MCP tools 如下。

### 1.1 只读类工具

- `jira_whoami`
- `list_jira_projects`
- `search_jira_issues`
- `get_jira_issue`
- `get_jira_issue_types`
- `get_jira_issue_type_fields`
- `search_jira_users`
- `get_jira_comments`
- `list_jira_transitions`

### 1.2 写入类工具

- `create_jira_issue`
- `create_jira_subtask`
- `add_jira_comment`
- `transition_jira_issue`
- `update_jira_assignee`
- `update_jira_issue`

## 2. 当前已覆盖的 REST 能力

| REST 能力 | 说明 | 当前 MCP 状态 |
|---|---|---|
| 当前用户 | 查询当前登录身份 | 已接入 |
| 项目列表 | 查询当前可见项目 | 已接入 |
| JQL 搜索 | 搜索 issue | 已接入 |
| issue 详情 | 查询 issue 详情 | 已接入 |
| issue type | 查询项目 issue type | 已接入 |
| 字段元数据 | 查询必填字段、可选值 | 已接入 |
| 用户搜索 | 按用户名/邮箱搜索用户 | 已接入 |
| 创建父任务 | 创建 issue | 已接入 |
| 创建子任务 | 创建 subtask | 已接入 |
| 更新 issue | 改 `summary`、`description`、自定义字段等 | 已接入 |
| 评论查询 | 查评论 | 已接入 |
| 评论新增 | 加评论 | 已接入 |
| 流转查询 | 查可用状态流转 | 已接入 |
| 执行流转 | 改状态 | 已接入 |
| 改负责人 | 改 `assignee` | 已接入 |

## 3. 当前能力覆盖的项目管理场景

当前这套 MCP 已经覆盖的核心场景包括：

- 看项目
- 查任务
- 查 issue type 和必填字段
- 建父任务
- 建子任务
- 改任务内容
- 改负责人
- 加评论和查评论
- 查状态流转
- 执行状态流转

