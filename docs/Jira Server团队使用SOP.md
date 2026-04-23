# Jira Server 团队使用 SOP

## 1. 目的

本 SOP 用于统一团队在 Codex 中通过 Jira Server MCP 和 skill 进行项目管理的使用方式。

适用范围：
- 研发
- 测试
- 产品
- 市场

适用系统：
- 公司本地 Jira Server
- Codex Desktop 中已接入的本地 Jira MCP

## 2. 使用目标

通过统一模板和流程，达到以下目标：

1. 统一团队创建、查询、更新 Jira 的表达方式
2. 降低误建单、错建类型、漏填字段的风险
3. 让不同岗位都能复用同一套 Jira AI 工作流
4. 让汇报、提单、需求拆解、会议任务沉淀更规范

## 3. 当前已接入能力

### 3.1 MCP 能力

当前 Jira MCP 支持：
- 查看当前登录身份
- 列出项目
- JQL 搜索 issue
- 查看 issue 详情
- 查看 issue type
- 查看 issue type 字段定义
- 搜索 Jira 用户
- 创建顶层任务
- 创建子任务
- 添加评论
- 查看评论
- 查看状态流转
- 执行状态流转
- 修改负责人
- 修改 issue 字段

### 3.2 Skills 能力

当前已沉淀 4 个 Jira skill：

- `jira-server-status-report`
  用于状态汇报、周报、日报、进度总结

- `jira-server-spec-to-backlog`
  用于把需求说明、PRD、方案文档拆成 Jira backlog

- `jira-server-triage-issue`
  用于 bug 分诊、查重、判断是否新建问题

- `jira-server-meeting-to-tasks`
  用于把会议纪要中的行动项转成 Jira 任务

## 4. 标准使用原则

### 4.1 默认两阶段流程

推荐统一使用：

1. 先分析和展示
2. 再确认和执行

标准表达建议：

```text
先展示方案，不要直接创建 / 修改 Jira。
等我确认后再执行。
```

### 4.2 创建前先检查项目规则

创建 issue 前，优先检查：
- 项目可用 issue type
- 必填字段
- 是否需要自定义字段

特别注意：
- `TASK` 项目已验证存在必填字段 `customfield_12800`，含义为“验收标准”

### 4.3 分诊默认不直接建单

对问题分诊类任务，统一建议：

```text
先展示分诊结果，不要直接创建 Jira。
```

### 4.4 会议纪要默认先展示拟建列表

对会议纪要转任务类任务，统一建议：

```text
先展示拟创建任务列表，等我确认后再执行。
```

## 5. 按项目的使用建议

### 5.1 `TASK`

适用场景：
- 公司内部综合任务
- 协同事项
- 行政、市场、跨部门推进任务

特点：
- 常用类型：`任务`、`子任务`
- 需要特别关注“验收标准”字段

建议：
- 创建前先检查必填字段
- 需求类工作也可拆成父任务 + 子任务

### 5.2 `HTEK`

适用场景：
- 主线版本项目
- 产品需求推进
- 故障跟踪和修复

特点：
- 常用类型：`需求`、`故障`、`任务`、`子任务`

建议：
- 功能工作优先用 `需求`
- 缺陷修复优先用 `故障`
- 协调和实现支撑工作用 `任务`

### 5.3 `RDTASK`

适用场景：
- 研发日常任务
- 技术调研
- 文档输出
- 测试用例设计

特点：
- 常用类型：`任务`、`子任务`、`文档撰写任务`、`用例撰写任务`

建议：
- 开发实现类工作用 `任务`
- 文档整理类工作用 `文档撰写任务`
- 测试设计类工作用 `用例撰写任务`

## 6. 推荐使用场景

### 6.1 做周报 / 日报 / 汇报

使用：
- `$jira-server-status-report`

典型场景：
- 项目周报
- 日会同步
- 管理层状态汇总

### 6.2 把 PRD / 方案变成 Jira

使用：
- `$jira-server-spec-to-backlog`

典型场景：
- 产品需求拆解
- 技术方案任务化
- 活动计划任务化

### 6.3 处理 bug / 问题反馈

使用：
- `$jira-server-triage-issue`

典型场景：
- 测试提 bug
- 线上报错查重
- 回归问题判断

### 6.4 会议后补任务

使用：
- `$jira-server-meeting-to-tasks`

典型场景：
- 需求会
- 例会
- 复盘会
- 跨部门协调会

## 7. 推荐 Prompt 入口

推荐先从以下文档复制模板：

- [Jira内部标准Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira内部标准Prompt模板.md)
- [Jira分部门Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira分部门Prompt模板.md)

## 8. 团队推荐话术

### 8.1 通用话术

```text
请使用 $skill-name 完成以下任务。
项目 key：
任务目标：
输入材料：
输出要求：
执行方式：先展示方案，等我确认后再执行
```

### 8.2 分诊类话术

```text
先展示分诊结果，不要直接创建 Jira。
```

### 8.3 创建类话术

```text
如果项目存在必填字段，请先提醒我。
先展示拟创建结果，确认后再执行。
```

## 9. 常见错误与处理建议

### 错误 1：项目里创建失败

常见原因：
- 缺少必填字段
- 选错 issue type
- 当前账号权限不足

处理建议：
1. 先查看 issue type
2. 再查看 issue type 字段元数据
3. 补充必填字段后重试

### 错误 2：问题分诊直接建了重复单

处理建议：
1. 默认先执行分诊，不直接建单
2. 先展示相似 issue，再决定是评论旧单还是建新单

### 错误 3：会议纪要里负责人不明确

处理建议：
1. 优先展示拟建列表
2. 不明确时保持未分配
3. 避免猜测负责人

## 10. 推荐团队落地方式

建议团队内部这样推广：

1. 固定用这套 SOP 作为 Jira AI 使用标准
2. 所有人默认采用“两阶段流程”
3. 先从 `TASK / HTEK / RDTASK` 三个常用项目开始
4. 每个部门优先使用自己的分部门模板
5. 逐步沉淀更多项目专用模板

## 11. 相关文档

- [Jira Skills中文Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira%20Skills%E4%B8%AD%E6%96%87Prompt%E6%A8%A1%E6%9D%BF.md)
- [Jira内部标准Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira内部标准Prompt模板.md)
- [Jira分部门Prompt模板.md](/C:/Users/admin/Documents/AllinAi/docs/Jira分部门Prompt模板.md)
- [Jira MCP自测报告.md](/C:/Users/admin/Documents/AllinAi/test/Jira%20MCP%E8%87%AA%E6%B5%8B%E6%8A%A5%E5%91%8A.md)
