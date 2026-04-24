# HtekJira MCP开发规划

## 1. 当前还能继续开发哪些功能

如果按 Jira Server REST API 的完整能力来说，当前还远未“接全”。

### 1.1 推荐优先开发的高频功能

| 建议功能 | 说明 |
|---|---|
| 查询 issue 变更历史 | 用于排查谁改过什么字段 |
| 查询 issue 关联关系 | 看阻塞、依赖、重复等关系 |
| 创建 issue link | 建立任务依赖/阻塞/重复关系 |
| 查询子任务列表 | 快速看父任务下的拆解情况 |
| 更新优先级 | 单独改 `priority` |
| 更新标签 | 单独改 `labels` |
| 更新截止日期 | 单独改 `due date` |
| 查询版本列表 | 对接 `fixVersion` / release 管理 |
| 查询 sprint 列表 | 对接迭代管理 |
| 上传附件 | 把截图、日志、文档附到 issue |

### 1.2 偏项目管理统计的能力

| 建议功能 | 说明 |
|---|---|
| 查询某人某月完成的任务 | 做个人工作量统计 |
| 查询某人某月 Actual Story Points | 做绩效/产能统计 |
| 统计团队 Actual Story Points | 做部门月度统计 |
| 查询阻塞任务 | 做周报和管理汇报 |
| 查询超期任务 | 做跟踪和催办 |
| 查询未分配任务 | 做 backlog 清理 |
| 查询长期未更新任务 | 做项目健康度巡检 |
| 查询某版本任务 | 版本发布跟踪 |
| 查询某 sprint 任务 | 迭代跟踪 |
| 批量更新状态/负责人 | 管理性高频操作 |

### 1.3 偏自动化和治理的能力

| 建议功能 | 说明 |
|---|---|
| 批量创建 backlog | 适合需求拆解结果批量落库 |
| 批量创建子任务模板 | 适合标准实施流程 |
| 批量分配负责人 | 减少手工操作 |
| 自动查重 bug | 配合 triage 场景 |
| 自动补齐模板字段 | 降低建单失败率 |
| 自动扫描超期任务 | 做自动巡检 |
| 自动提醒阻塞项 | 做项目例会支撑 |
| 自动从会议纪要建单 | 已有 skill，可继续增强 |
| 自动从需求文档拆任务 | 已有 skill，可继续增强 |
| 自动生成周报/月报/迭代报告 | 已有 skill，可继续增强 |

## 2. 最值得优先补的下一批 MCP tools

如果按投入产出比排序，建议优先补这 10 个：

1. `get_jira_issue_changelog`
2. `list_jira_issue_links`
3. `create_jira_issue_link`
4. `list_jira_subtasks`
5. `update_jira_priority`
6. `update_jira_labels`
7. `update_jira_due_date`
8. `list_jira_versions`
9. `list_jira_sprints`
10. `upload_jira_attachment`

## 3. 面向公司项目管理的优先方向

如果更偏你们公司当前管理需求，建议优先考虑这几类：

- 个人月度任务与 Actual Story Points 统计
- 团队月度 Actual Story Points 汇总
- 阻塞项、逾期项、长期未更新项巡检
- Sprint / 版本维度任务查询
- 批量更新状态和负责人

