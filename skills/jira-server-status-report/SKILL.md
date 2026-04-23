---
name: jira-server-status-report
description: 基于公司本地 Jira Server 生成周报、日报、迭代报告或临时项目状态汇报。适用于用户希望查看项目进展、阻塞项、团队更新、管理层摘要，或基于 Jira issue 评估 backlog 健康度的场景。
---

# Jira Server 状态报告

## 概述

通过查询本地 Jira Server 中的项目 issue，按状态和优先级进行归类，生成适合管理者、项目负责人或团队同步使用的状态报告。

## 工作流程

1. 先明确汇报范围。  
确认或推断以下信息：
- Jira 项目 key
- 时间范围
- 汇报对象
- 用户希望要简版摘要还是 issue 级明细

2. 构造聚焦的 JQL 查询。  
优先使用多条窄查询，而不是一条过宽的查询：
- 最近完成的工作
- 当前进行中的工作
- 当前阻塞项
- 高优先级未完成工作

每类查询都使用 `search_jira_issues`。

3. 只在必要时补充细节。  
对于阻塞项、疑似回归问题、或特别重要的完成项，再使用 `get_jira_issue` 或 `get_jira_comments` 拉取详情。

4. 将结果整理为以下部分：
- 总体状态
- 已完成事项
- 进行中事项
- 阻塞与风险
- 下一步优先事项

5. 根据受众调整表达方式。  
- 管理层：突出状态、风险、依赖关系、需要决策的事项
- 团队负责人：包含 issue key、责任人和下一步动作
- 日常站会：保持简短，聚焦行动项

## 查询模式

可参考以下模式，并根据项目 key 和时间范围调整：

```text
project = TASK AND updated >= -7d ORDER BY priority DESC, updated DESC
project = TASK AND status in ("处理中","任务审核") ORDER BY priority DESC, updated DESC
project = TASK AND status = "完成" AND updated >= -7d ORDER BY updated DESC
project = TASK AND priority in (P0, P1, P2) AND status != "完成" ORDER BY priority DESC, updated DESC
```

## 输出结构

除非用户另有要求，优先使用以下结构：

```text
项目：
周期：
总体状态：

已完成：
- ISSUE-1 概要

进行中：
- ISSUE-2 概要

阻塞 / 风险：
- ISSUE-3 概要 - 为什么重要

下一步：
- 优先事项 1
- 优先事项 2
```

## 注意事项

- 项目 key 不明确时先确认。
- 不要自行脑补状态含义，应以 Jira 中实际返回的状态名为准。
- 若流程、优先级、标签使用不一致，要明确指出数据存在缺口。
- 优先引用 issue key，不要只做模糊转述。
