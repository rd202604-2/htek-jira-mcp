# Jira MCP自测报告

- 执行时间：`2026-04-24T15:23:13.477057+08:00`
- 完成时间：`2026-04-24T15:23:16.864969+08:00`
- 测试项目：`PR`
- 测试模式：`all`
- 总体结果：`passed`

## 结果汇总

- 通过：`15` 项
- 跳过：`1` 项
- 失败：`0` 项

## 各项测试结果

### jira_whoami

- 状态：`passed`
- 详情：
```json
{
  "name": "russell.zhang",
  "display_name": "张力山",
  "email": "russell@htek.com",
  "base_url": "http://oa.htek.com:8088"
}
```

### list_jira_projects

- 状态：`passed`
- 详情：
```json
{
  "visible_project_count": 48,
  "contains_target": true
}
```

### search_jira_users

- 状态：`passed`
- 详情：
```json
{
  "matches": [
    {
      "name": "russell.zhang",
      "display_name": "张力山",
      "email": "russell@htek.com",
      "active": true
    }
  ]
}
```

### get_jira_issue_types

- 状态：`passed`
- 详情：
```json
{
  "task_type": {
    "id": "10002",
    "name": "任务"
  },
  "subtask_type": {
    "id": "10003",
    "name": "子任务"
  }
}
```

### get_jira_issue_type_fields

- 状态：`passed`
- 详情：
```json
{
  "issue_type": "任务",
  "required_field_ids": [
    "summary",
    "issuetype",
    "project"
  ],
  "additional_placeholder_keys": []
}
```

### get_jira_issue_type_fields_subtask

- 状态：`passed`
- 详情：
```json
{
  "issue_type": "子任务",
  "required_field_ids": [
    "summary",
    "parent",
    "issuetype",
    "project"
  ],
  "additional_placeholder_keys": []
}
```

### create_jira_issue

- 状态：`passed`
- 详情：
```json
{
  "key": "PR-616",
  "id": "79864",
  "issue_type": "任务",
  "browse_url": "http://oa.htek.com:8088/browse/PR-616"
}
```

### update_jira_issue

- 状态：`passed`
- 详情：
```json
{
  "issue_key": "PR-616",
  "updated_fields": [
    "customfield_12800",
    "customfield_13700",
    "description",
    "duedate",
    "labels",
    "summary"
  ],
  "browse_url": "http://oa.htek.com:8088/browse/PR-616"
}
```

### add_jira_comment

- 状态：`passed`
- 详情：
```json
{
  "issue_key": "PR-616",
  "comment_id": "62233",
  "created": "2026-04-24T15:23:15.049+0800",
  "browse_url": "http://oa.htek.com:8088/browse/PR-616"
}
```

### get_jira_comments

- 状态：`passed`
- 详情：
```json
{
  "total": 1
}
```

### update_jira_assignee

- 状态：`passed`
- 详情：
```json
{
  "issue_key": "PR-616",
  "assignee_username": "russell.zhang",
  "browse_url": "http://oa.htek.com:8088/browse/PR-616"
}
```

### list_jira_transitions

- 状态：`skipped`
- 详情：
```json
{
  "issue_key": "PR-616",
  "transitions": [],
  "reason": "当前状态下无可用 outward 流转（测试项目起始状态常见）；已跳过 transition_jira_issue。"
}
```

### get_jira_issue

- 状态：`passed`
- 详情：
```json
{
  "key": "PR-616",
  "summary": "[Codex Selftest 20260424-152313] Parent task updated",
  "description": "Updated by Codex self-test.",
  "status": "任务规划",
  "issue_type": "任务",
  "priority": "P3",
  "labels": [
    "codex-selftest-20260424-152313"
  ],
  "parent": null,
  "assignee": "张力山",
  "reporter": "张力山",
  "created": "2026-04-24T15:23:14.000+0800",
  "updated": "2026-04-24T15:23:15.000+0800",
  "resolution": null,
  "browse_url": "http://oa.htek.com:8088/browse/PR-616"
}
```

### create_jira_subtask

- 状态：`passed`
- 详情：
```json
{
  "key": "PR-617",
  "id": "79865",
  "issue_type": "子任务",
  "browse_url": "http://oa.htek.com:8088/browse/PR-617"
}
```

### get_jira_issue_subtask

- 状态：`passed`
- 详情：
```json
{
  "key": "PR-617",
  "summary": "[Codex Selftest 20260424-152313] Subtask",
  "description": "Created by Codex self-test.",
  "status": "待办",
  "issue_type": "子任务",
  "priority": "P3",
  "labels": [],
  "parent": "PR-616",
  "assignee": "CCB Plan",
  "reporter": "张力山",
  "created": "2026-04-24T15:23:16.000+0800",
  "updated": "2026-04-24T15:23:16.000+0800",
  "resolution": null,
  "browse_url": "http://oa.htek.com:8088/browse/PR-617"
}
```

### search_jira_issues

- 状态：`passed`
- 详情：
```json
{
  "total": 1,
  "returned": 1,
  "issues": [
    {
      "key": "PR-616",
      "summary": "[Codex Selftest 20260424-152313] Parent task updated",
      "status": "任务规划",
      "issue_type": "任务",
      "priority": "P3",
      "assignee": "张力山",
      "updated": "2026-04-24T15:23:15.000+0800"
    }
  ]
}
```

## 本次产生的测试单

- 父任务：`PR-616`  http://oa.htek.com:8088/browse/PR-616
- 子任务：`PR-617`  http://oa.htek.com:8088/browse/PR-617

## 输出文件

- JSON：`C:\Users\admin\Documents\AllinAi\test\Jira MCP自测结果.json`
- Markdown：`C:\Users\admin\Documents\AllinAi\test\Jira MCP自测报告.md`
