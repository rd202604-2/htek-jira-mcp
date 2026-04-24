"""
本模块用于对本地 Jira Server MCP 做自动化自测。

测试目标：
1. 验证 Jira 连接、项目可见性和用户检索能力。
2. 验证 issue 创建、更新、评论、流转、子任务创建等核心写操作。
3. 默认同时生成结构化 JSON 结果和 Markdown 报告，便于留档和团队查看。

执行方式：
- 默认对 **`PR`** 项目执行自测（仓库约定的**测试项目区**，用于新流程跑通验证）。
- 可以通过 `--project` 切换测试项目。
- 可以通过 `--mode` 选择检查模式：
  - `readonly`：只执行只读检查，不会创建或修改 Jira 数据。
  - `write`：只执行写入相关检查，前提是只读检查通过。
  - `all`：执行完整检查，默认值。
- 默认输出：
  - `test/Jira MCP自测结果.json`
  - `test/Jira MCP自测报告.md`
- 可以通过 `--json-out` / `--md-out` 覆盖默认输出路径。
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TOOLS = _REPO_ROOT / "tools"
_TEST_DIR = Path(__file__).resolve().parent
_DEFAULT_JSON_OUT = _TEST_DIR / "Jira MCP自测结果.json"
_DEFAULT_MD_OUT = _TEST_DIR / "Jira MCP自测报告.md"
_DEFAULT_MODE = "all"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

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


def build_markdown_report(report: dict[str, Any]) -> str:
    """
    将本次自测结果渲染成人类可读的 Markdown 报告。
    """
    checks = report.get("checks", [])
    passed = [c for c in checks if c.get("status") == "passed"]
    skipped = [c for c in checks if c.get("status") == "skipped"]
    failed = [c for c in checks if c.get("status") == "failed"]
    artifacts = report.get("artifacts", {})

    lines = [
        "# Jira MCP自测报告",
        "",
        f"- 执行时间：`{report.get('started_at', '')}`",
        f"- 完成时间：`{report.get('finished_at', '')}`",
        f"- 测试项目：`{report.get('project', '')}`",
        f"- 测试模式：`{report.get('mode', '')}`",
        f"- 总体结果：`{report.get('status', '')}`",
        "",
        "## 结果汇总",
        "",
        f"- 通过：`{len(passed)}` 项",
        f"- 跳过：`{len(skipped)}` 项",
        f"- 失败：`{len(failed)}` 项",
        "",
        "## 各项测试结果",
        "",
    ]

    for check in checks:
        name = check.get("name", "")
        status = check.get("status", "")
        details = json.dumps(check.get("details", {}), ensure_ascii=False, indent=2)
        lines.extend(
            [
                f"### {name}",
                "",
                f"- 状态：`{status}`",
                "- 详情：",
                "```json",
                details,
                "```",
                "",
            ]
        )

    if artifacts:
        lines.extend(["## 本次产生的测试单", ""])
        parent_issue = artifacts.get("parent_issue")
        subtask_issue = artifacts.get("subtask_issue")
        if parent_issue:
            lines.append(
                f"- 父任务：`{parent_issue.get('key', '')}`  {parent_issue.get('browse_url', '')}"
            )
        if subtask_issue:
            lines.append(
                f"- 子任务：`{subtask_issue.get('key', '')}`  {subtask_issue.get('browse_url', '')}"
            )
        lines.append("")

    lines.extend(
        [
            "## 输出文件",
            "",
            f"- JSON：`{_DEFAULT_JSON_OUT}`",
            f"- Markdown：`{_DEFAULT_MD_OUT}`",
            "",
        ]
    )

    return "\n".join(lines)


def write_outputs(report: dict[str, Any], json_out: Path, md_out: Path) -> str:
    """
    同时写出 JSON 结果和 Markdown 报告。
    """
    output = json.dumps(report, ensure_ascii=False, indent=2)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(output, encoding="utf-8")
    md_out.write_text(build_markdown_report(report), encoding="utf-8")
    return output


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


# create_jira_issue / create_jira_subtask 已在主参数里写入的字段 id，不应再出现在 additional_fields。
_ISSUE_CREATE_EXCLUDE_FIELD_IDS = frozenset({"project", "summary", "description", "issuetype", "priority", "assignee"})
_SUBTASK_CREATE_EXCLUDE_FIELD_IDS = _ISSUE_CREATE_EXCLUDE_FIELD_IDS | {"parent"}


def _rest_option_single_from_allowed_first(first: Any) -> tuple[dict[str, Any], str]:
    """
    从 `get_jira_issue_type_fields` 返回的 `allowed_values` 首项构造 Jira REST 单选占位。

    若首项带 `children`（级联），向下取第一个子项，以满足「在父母选择对象中有效」类校验。
    """
    if isinstance(first, dict):

        def walk(entry: dict[str, Any]) -> dict[str, Any]:
            children = entry.get("children") or []
            if isinstance(children, list) and children and isinstance(children[0], dict):
                return walk(children[0])
            if entry.get("id") is not None and str(entry["id"]).strip() != "":
                return {"id": entry["id"]}
            if entry.get("name") is not None:
                return {"name": entry["name"]}
            if entry.get("value") is not None:
                return {"value": entry["value"]}
            return {"name": str(entry)}

        payload = walk(first)
        name_hint = str(
            first.get("name")
            or first.get("value")
            or first.get("id")
            or payload.get("name")
            or payload.get("id")
            or ""
        )
        return payload, name_hint

    text = str(first)
    return {"name": text}, text


def _placeholder_for_jira_field(field: dict[str, Any], me_name: str, unique_tag: str) -> Any:
    """
    根据 createmeta 中的字段元数据，为「创建 issue」生成可提交的占位值。

    无法安全推断的必填字段会抛出 ValueError，由上层在只读阶段提前失败并提示维护者。
    """
    fid = field["id"]
    schema = (field.get("schema_type") or "").lower()
    allowed = field.get("allowed_values") or []
    safe_tag = unique_tag.replace(":", "-")[:80]

    if allowed:
        first = allowed[0]
        opt_payload, name_hint = _rest_option_single_from_allowed_first(first)
        if fid in ("components", "fixVersions", "versions"):
            if "name" in opt_payload and opt_payload["name"]:
                return [{"name": opt_payload["name"]}]
            if "id" in opt_payload:
                return [{"id": opt_payload["id"]}]
            return [{"name": name_hint or str(first)}]
        if fid == "labels":
            return [name_hint or str(opt_payload.get("name", first))]
        if schema == "array":
            return [opt_payload]
        return opt_payload

    if schema == "user" or fid == "reporter":
        return {"name": me_name}
    if schema in ("number", "float", "integer"):
        return 1
    if schema == "date":
        return date.today().isoformat()
    if schema == "datetime":
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000")
    if schema == "option":
        raise ValueError(f"必填字段 {fid}（{field.get('name')}）为单选且无 allowed_values，无法自动生成占位值。")
    if schema == "array":
        if fid == "labels":
            return [f"mcp-selftest-{safe_tag}"[:255]]
        raise ValueError(f"必填字段 {fid}（{field.get('name')}）为数组且无 allowed_values，无法自动生成占位值。")
    if fid in ("timetracking", "attachment"):
        raise ValueError(f"必填字段 {fid}（{field.get('name')}）类型较复杂，自测脚本暂未支持自动生成占位值。")
    return f"[MCP selftest {safe_tag}] {field.get('name') or fid}"


def _collect_required_additional_fields(
    fields: list[dict[str, Any]],
    me_name: str,
    unique_tag: str,
    exclude_field_ids: frozenset[str],
) -> tuple[dict[str, Any], list[str]]:
    """
    从 get_jira_issue_type_fields 返回的 fields 列表中，挑出创建时尚未写入且 required 的字段，生成占位字典。

    返回 (additional_fields, error_messages)。
    """
    out: dict[str, Any] = {}
    errors: list[str] = []
    for f in fields:
        if not f.get("required"):
            continue
        fid = f["id"]
        if fid in exclude_field_ids:
            continue
        try:
            out[fid] = _placeholder_for_jira_field(f, me_name, unique_tag)
        except ValueError as exc:
            errors.append(str(exc))
    return out, errors


def _parse_jira_400_errors(message: str) -> dict[str, str] | None:
    """从 `jira_server_mcp._request` 抛出的 RuntimeError 文案中解析 Jira `errors` 对象。"""
    marker = "）："
    idx = message.rfind(marker)
    if idx == -1:
        return None
    tail = message[idx + len(marker) :].strip()
    try:
        obj = json.loads(tail)
    except json.JSONDecodeError:
        return None
    errs = obj.get("errors")
    if isinstance(errs, dict):
        return {str(k): str(v) for k, v in errs.items()}
    return None


def _field_meta_by_id(fields_meta: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {f["id"]: f for f in fields_meta}


def _merge_server_error_fields_into_extra(
    current: dict[str, Any],
    server_errors: dict[str, str],
    fields_meta: list[dict[str, Any]],
    me_name: str,
    unique_tag: str,
    exclude_field_ids: frozenset[str],
) -> dict[str, Any]:
    """
    Jira createmeta 的 required 标记有时与创建校验不一致；按 400 响应里的字段 id 补占位。
    """
    by_id = _field_meta_by_id(fields_meta)
    merged = dict(current)
    safe_tag = unique_tag.replace(":", "-")[:80]
    for fid in server_errors:
        if fid in exclude_field_ids:
            continue
        meta = by_id.get(fid)
        if meta is None:
            meta = {"id": fid, "name": fid, "required": True, "schema_type": "string", "allowed_values": []}
        try:
            merged[fid] = _placeholder_for_jira_field(meta, me_name, unique_tag)
        except ValueError:
            merged[fid] = f"[MCP selftest {safe_tag}] {meta.get('name') or fid}"
    return merged


def _retry_create_with_400_field_backfill(
    initial_extra: dict[str, Any],
    fields_meta: list[dict[str, Any]],
    me_name: str,
    unique_tag: str,
    exclude_field_ids: frozenset[str],
    call_create: Callable[[dict[str, Any] | None], Any],
) -> tuple[Any, dict[str, Any]]:
    """
    调用 `call_create(additional_fields)`；若 Jira 返回 400 且 body 含 `errors`，
    则按字段 id 合并占位并重试。返回 (create 返回值, 最终 additional_fields 字典)。
    """
    extra: dict[str, Any] = dict(initial_extra)
    prev_snapshot: str | None = None
    last_exc: RuntimeError | None = None
    for _ in range(6):
        try:
            result = call_create(extra if extra else None)
            return result, extra
        except RuntimeError as exc:
            last_exc = exc
            parsed = _parse_jira_400_errors(str(exc))
            if not parsed:
                raise
            extra = _merge_server_error_fields_into_extra(
                extra,
                parsed,
                fields_meta,
                me_name,
                unique_tag,
                exclude_field_ids,
            )
            snapshot = json.dumps(extra, ensure_ascii=False, sort_keys=True)
            if snapshot == prev_snapshot:
                raise RuntimeError(
                    "创建 issue 仍返回字段错误，且无法通过占位消除（请检查 PR 字段或扩展 `_placeholder_for_jira_field`）。"
                ) from exc
            prev_snapshot = snapshot
    if last_exc:
        raise last_exc
    raise AssertionError("不可达分支")


def main():
    """
    自测主流程。

    命令行参数：
    - `--project`：目标 Jira 项目 key，默认 `PR`。
    - `--mode`：检查模式，取值为 `readonly` / `write` / `all`。
    - `--json-out`：可选，输出 JSON 结果的文件路径。
    - `--md-out`：可选，输出 Markdown 报告的文件路径。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="PR")
    parser.add_argument("--mode", choices=["readonly", "write", "all"], default=_DEFAULT_MODE)
    parser.add_argument("--json-out", default=str(_DEFAULT_JSON_OUT))
    parser.add_argument("--md-out", default=str(_DEFAULT_MD_OUT))
    args = parser.parse_args()
    json_out_path = Path(args.json_out)
    md_out_path = Path(args.md_out)

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
    required_task_field_ids = [field["id"] for field in type_fields["fields"] if field["required"]]
    task_extra, task_field_errors = _collect_required_additional_fields(
        type_fields["fields"],
        me["name"],
        unique_tag,
        _ISSUE_CREATE_EXCLUDE_FIELD_IDS,
    )
    require(
        not task_field_errors,
        "顶层问题类型存在无法自动生成占位的必填字段：" + "；".join(task_field_errors),
    )
    record(
        "get_jira_issue_type_fields",
        "passed",
        {
            "issue_type": type_fields.get("issue_type"),
            "required_field_ids": required_task_field_ids,
            "additional_placeholder_keys": sorted(task_extra.keys()),
        },
    )

    subtask_type_fields = get_jira_issue_type_fields(args.project, subtask_type_id)
    required_subtask_field_ids = [field["id"] for field in subtask_type_fields["fields"] if field["required"]]
    subtask_extra, subtask_field_errors = _collect_required_additional_fields(
        subtask_type_fields["fields"],
        me["name"],
        unique_tag,
        _SUBTASK_CREATE_EXCLUDE_FIELD_IDS,
    )
    require(
        not subtask_field_errors,
        "子任务问题类型存在无法自动生成占位的必填字段：" + "；".join(subtask_field_errors),
    )
    record(
        "get_jira_issue_type_fields_subtask",
        "passed",
        {
            "issue_type": subtask_type_fields.get("issue_type"),
            "required_field_ids": required_subtask_field_ids,
            "additional_placeholder_keys": sorted(subtask_extra.keys()),
        },
    )

    if args.mode == "readonly":
        report["finished_at"] = datetime.now().astimezone().isoformat()
        report["status"] = "passed"
        output = write_outputs(report, json_out_path, md_out_path)
        print(output)
        return

    # =========================================================================
    # 第二阶段：写入检查
    # =========================================================================
    parent_issue, task_extra = _retry_create_with_400_field_backfill(
        task_extra,
        type_fields["fields"],
        me["name"],
        unique_tag,
        _ISSUE_CREATE_EXCLUDE_FIELD_IDS,
        lambda additional: create_jira_issue(
            args.project,
            parent_summary,
            "Created by Codex self-test.",
            task_type_id,
            "P3",
            me["name"],
            additional,
        ),
    )
    parent_key = parent_issue["key"]
    report["artifacts"]["parent_issue"] = parent_issue
    record("create_jira_issue", "passed", parent_issue)

    # 顶层 labels 由下方 labels= 传入；勿在 additional_fields 里带 labels，否则会覆盖显式参数。
    update_additional = (
        {
            k: (v + " (updated)" if isinstance(v, str) else v)
            for k, v in task_extra.items()
            if isinstance(v, str) and k != "labels"
        }
        if task_extra
        else {}
    )
    update_result = update_jira_issue(
        parent_key,
        summary=updated_summary,
        description="Updated by Codex self-test.",
        labels=[unique_tag],
        additional_fields=update_additional if update_additional else None,
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
    if transitions_before["transitions"]:
        chosen_transition = transitions_before["transitions"][0]
        transition_result = transition_jira_issue(parent_key, transition_id=chosen_transition["id"])
        record("list_jira_transitions", "passed", transitions_before)
        record("transition_jira_issue", "passed", transition_result)
        parent_issue_after = get_jira_issue(parent_key)
        require(parent_issue_after["summary"] == updated_summary, "更新后的概要未持久化。")
        require(unique_tag in parent_issue_after["labels"], "更新后的标签未持久化。")
        require(parent_issue_after["status"] == chosen_transition["to_status"], "状态流转结果未持久化。")
    else:
        record(
            "list_jira_transitions",
            "skipped",
            {
                **transitions_before,
                "reason": "当前状态下无可用 outward 流转（测试项目起始状态常见）；已跳过 transition_jira_issue。",
            },
        )
        parent_issue_after = get_jira_issue(parent_key)
        require(parent_issue_after["summary"] == updated_summary, "更新后的概要未持久化。")
        require(unique_tag in parent_issue_after["labels"], "更新后的标签未持久化。")
    record("get_jira_issue", "passed", parent_issue_after)

    subtask_issue, subtask_extra = _retry_create_with_400_field_backfill(
        subtask_extra,
        subtask_type_fields["fields"],
        me["name"],
        unique_tag,
        _SUBTASK_CREATE_EXCLUDE_FIELD_IDS,
        lambda additional: create_jira_subtask(
            args.project,
            parent_key,
            subtask_summary,
            "Created by Codex self-test.",
            subtask_type_id,
            "P3",
            me["name"],
            additional,
        ),
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

    output = write_outputs(report, json_out_path, md_out_path)
    print(output)


if __name__ == "__main__":
    main()
