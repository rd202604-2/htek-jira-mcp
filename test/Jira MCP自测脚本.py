"""
本模块用于对本地 Jira Server MCP 做自动化自测。

测试目标：
1. 验证 Jira 连接、项目可见性和用户检索能力。
2. 验证 issue 创建、更新、评论、流转、子任务创建等核心写操作。
3. 生成结构化 JSON 报告，便于留档和测试报告引用。

执行方式：
- 默认对 `TASK` 项目执行自测。
- 可以通过 `--project` 切换测试项目。
- 可以通过 `--mode` 选择检查模式：
  - `readonly`：只执行只读检查，不会创建或修改 Jira 数据。
  - `write`：只执行写入相关检查，前提是只读检查通过。
  - `all`：执行完整检查，默认值。
- 可以通过 `--json-out` 将测试结果落盘为 JSON 文件。
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from jira_server_mcp import (
    add_jira_comment,
    create_jira_issue,
    create_jira_subtask,
    get_jira_comments,
    get_jira_issue,
    get_jira_issue_type_fields,
    get_jira_issue_types,
    jira_whoami,
    list_jira_projects,
    list_jira_transitions,
    search_jira_issues,
    search_jira_users,
    transition_jira_issue,
    update_jira_assignee,
    update_jira_issue,
)


def require(condition, message):
    """
    统一断言出口，便于在自测失败时抛出可读错误。

    参数：
    - `condition`：断言条件。
    - `message`：条件不成立时抛出的错误信息。
    """
    if not condition:
        raise AssertionError(message)


def find_issue_type_id(issue_types, preferred_names, subtask):
    """
    按优先名称匹配问题类型。

    参数：
    - `issue_types`：项目返回的 issue type 列表。
    - `preferred_names`：优先尝试匹配的名称列表。
    - `subtask`：是否需要子任务类型。

    返回：
    - 匹配到的 `(issue_type_id, issue_type_name)`。
    """
    for preferred_name in preferred_names:
        for issue_type in issue_types:
            if issue_type["name"] == preferred_name and issue_type["subtask"] == subtask:
                return issue_type["id"], issue_type["name"]
    for issue_type in issue_types:
        if issue_type["subtask"] == subtask:
            return issue_type["id"], issue_type["name"]
    raise AssertionError(f"未找到{'子任务' if subtask else '顶层'}问题类型。")


def main():
    """
    自测主流程。

    命令行参数：
    - `--project`：目标 Jira 项目 key，默认 `TASK`。
    - `--mode`：检查模式，取值为 `readonly` / `write` / `all`。
    - `--json-out`：可选，输出 JSON 报告的文件路径。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="TASK")
    parser.add_argument("--mode", choices=["readonly", "write", "all"], default="all")
    parser.add_argument("--json-out")
    args = parser.parse_args()

    started_at = datetime.now().astimezone()
    stamp = started_at.strftime("%Y%m%d-%H%M%S")

    # 为每次自测生成唯一标签和概要，避免和已有 Jira 数据混淆。
    unique_tag = f"codex-selftest-{stamp}"
    parent_summary = f"[Codex Selftest {stamp}] Parent task"
    updated_summary = f"[Codex Selftest {stamp}] Parent task updated"
    subtask_summary = f"[Codex Selftest {stamp}] Subtask"
    comment_body = f"Codex self-test comment {stamp}."

    report = {
        "started_at": started_at.isoformat(),
        "project": args.project,
        "mode": args.mode,
        "checks": [],
        "artifacts": {},
    }

    def record(name, status, details):
        """
        记录每一步测试结果，最终统一输出为 JSON 报告。

        参数：
        - `name`：测试项名称。
        - `status`：测试状态，通常为 `passed`。
        - `details`：该步骤的结果详情。
        """
        report["checks"].append({"name": name, "status": status, "details": details})

    # =========================================================================
    # 第一阶段：只读检查
    # =========================================================================
    me = jira_whoami()
    require(me["name"], "jira_whoami 未返回用户名。")
    record("jira_whoami", "passed", me)

    projects = list_jira_projects(200)
    require(any(project["key"] == args.project for project in projects["projects"]), f"当前账号不可见项目 {args.project}。")
    record("list_jira_projects", "passed", {"visible_project_count": projects["count"], "contains_target": True})

    user_hits = search_jira_users(me["name"], 5)
    require(any(user["name"] == me["name"] for user in user_hits["users"]), "search_jira_users 未检索到当前用户。")
    record("search_jira_users", "passed", {"matches": user_hits["users"]})

    issue_types_payload = get_jira_issue_types(args.project)
    issue_types = issue_types_payload["issue_types"]
    require(issue_types, f"项目 {args.project} 未返回任何问题类型。")
    task_type_id, task_type_name = find_issue_type_id(issue_types, ["任务", "Task", "需求"], subtask=False)
    subtask_type_id, subtask_type_name = find_issue_type_id(issue_types, ["子任务", "Sub-task"], subtask=True)
    record(
        "get_jira_issue_types",
        "passed",
        {
            "task_type": {"id": task_type_id, "name": task_type_name},
            "subtask_type": {"id": subtask_type_id, "name": subtask_type_name},
        },
    )

    type_fields = get_jira_issue_type_fields(args.project, task_type_id)
    required_field_ids = [field["id"] for field in type_fields["fields"] if field["required"]]
    require("customfield_12800" in required_field_ids, "未找到预期的必填字段 customfield_12800。")
    record("get_jira_issue_type_fields", "passed", {"required_fields": required_field_ids})

    if args.mode == "readonly":
        report["finished_at"] = datetime.now().astimezone().isoformat()
        report["status"] = "passed"
        output = json.dumps(report, ensure_ascii=False, indent=2)
        print(output)
        if args.json_out:
            Path(args.json_out).write_text(output, encoding="utf-8")
        return

    # =========================================================================
    # 第二阶段：写入检查
    # =========================================================================
    parent_issue = create_jira_issue(
        args.project,
        parent_summary,
        "Created by Codex self-test.",
        task_type_id,
        "P3",
        me["name"],
        {"customfield_12800": f"Acceptance criteria for {unique_tag}"},
    )
    parent_key = parent_issue["key"]
    report["artifacts"]["parent_issue"] = parent_issue
    record("create_jira_issue", "passed", parent_issue)

    update_result = update_jira_issue(
        parent_key,
        summary=updated_summary,
        description="Updated by Codex self-test.",
        labels=[unique_tag],
        additional_fields={"customfield_12800": f"Updated acceptance criteria for {unique_tag}"},
    )
    record("update_jira_issue", "passed", update_result)

    comment_result = add_jira_comment(parent_key, comment_body)
    record("add_jira_comment", "passed", comment_result)

    comments = get_jira_comments(parent_key)
    require(any(comment["id"] == comment_result["comment_id"] for comment in comments["comments"]), "评论创建后未能在评论列表中读回。")
    record("get_jira_comments", "passed", {"total": comments["total"]})

    assignee_result = update_jira_assignee(parent_key, me["name"])
    record("update_jira_assignee", "passed", assignee_result)

    transitions_before = list_jira_transitions(parent_key)
    require(transitions_before["transitions"], "新创建的 issue 当前没有可用状态流转。")
    chosen_transition = transitions_before["transitions"][0]
    transition_result = transition_jira_issue(parent_key, transition_id=chosen_transition["id"])
    record("list_jira_transitions", "passed", transitions_before)
    record("transition_jira_issue", "passed", transition_result)

    parent_issue_after = get_jira_issue(parent_key)
    require(parent_issue_after["summary"] == updated_summary, "更新后的概要未持久化。")
    require(unique_tag in parent_issue_after["labels"], "更新后的标签未持久化。")
    require(parent_issue_after["status"] == chosen_transition["to_status"], "状态流转结果未持久化。")
    record("get_jira_issue", "passed", parent_issue_after)

    subtask_issue = create_jira_subtask(
        args.project,
        parent_key,
        subtask_summary,
        "Created by Codex self-test.",
        subtask_type_id,
        "P3",
        me["name"],
        {"customfield_12800": f"Subtask acceptance criteria for {unique_tag}"},
    )
    report["artifacts"]["subtask_issue"] = subtask_issue
    record("create_jira_subtask", "passed", subtask_issue)

    subtask_issue_after = get_jira_issue(subtask_issue["key"])
    require(subtask_issue_after["parent"] == parent_key, "子任务的父任务关联不正确。")
    record("get_jira_issue_subtask", "passed", subtask_issue_after)

    search_result = search_jira_issues(f'project = {args.project} AND labels = "{unique_tag}" ORDER BY updated DESC', 10)
    require(any(issue["key"] == parent_key for issue in search_result["issues"]), "未能通过标签搜索到刚创建的 issue。")
    record("search_jira_issues", "passed", search_result)

    report["finished_at"] = datetime.now().astimezone().isoformat()
    report["status"] = "passed"

    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.json_out:
        Path(args.json_out).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
