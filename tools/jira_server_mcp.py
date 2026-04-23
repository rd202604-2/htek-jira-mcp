"""
本模块提供公司本地 Jira Server 的 MCP 适配层。

设计目标：
1. 让 Codex 能以统一工具形式访问 Jira Server 常用能力。
2. 尽量兼容本地 Jira Server 的项目自定义字段、问题类型和工作流。
3. 将常见的 REST 请求、错误处理和字段映射集中到这一层，避免上层 workflow 重复实现。

当前覆盖的能力包括：
- 读取当前登录身份
- 列项目
- 用 JQL 搜索 issue
- 读取 issue 详情
- 读取项目可用 issue type 与字段元数据
- 创建顶层 issue 和子任务
- 查询/添加评论
- 查询/执行状态流转
- 更新负责人和常用字段
"""

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from mcp.server.fastmcp import FastMCP

# =============================================================================
# 函数索引
# =============================================================================
#
# 一、内部工具函数
# - _normalize_base_url(raw_url)
# - _request(method, path, data)
# - _issue_brief(issue)
# - _get_project_createmeta(project_key)
# - _pick_subtask_issue_type(project_key, preferred_issue_type)
# - _resolve_issue_type(project_key, issue_type)
#
# 二、只读类 MCP 工具
# - jira_whoami()
# - list_jira_projects(limit)
# - search_jira_issues(jql, max_results, fields)
# - get_jira_issue(issue_key)
# - get_jira_issue_types(project_key)
# - get_jira_issue_type_fields(project_key, issue_type)
# - search_jira_users(query, max_results)
# - get_jira_comments(issue_key, max_results)
# - list_jira_transitions(issue_key)
#
# 三、写入类 MCP 工具
# - create_jira_issue(project_key, summary, description, issue_type, ...)
# - create_jira_subtask(project_key, parent_key, summary, description, ...)
# - add_jira_comment(issue_key, comment)
# - transition_jira_issue(issue_key, transition_name, transition_id)
# - update_jira_assignee(issue_key, assignee_username)
# - update_jira_issue(issue_key, summary, description, priority, ...)
# =============================================================================


def _normalize_base_url(raw_url: str) -> str:
    """
    规范化 Jira 基础地址。

    参数：
    - `raw_url`：环境变量中配置的 Jira 地址，可能是站点首页，也可能是某个页面 URL。

    返回：
    - 仅保留 `协议 + 域名 + 端口` 的基础地址，供 REST API 拼接使用。

    说明：
    用户配置里可能给的是完整页面地址，例如：
    `http://oa.htek.com:8088/secure/Dashboard.jspa`
    这里统一裁剪成基础地址，避免后续拼 REST 路径时出错。
    """
    parsed = urllib.parse.urlsplit(raw_url.strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("HTEK_JIRA_BASE_URL 必须是完整 URL，例如 http://host:8080")
    return f"{parsed.scheme}://{parsed.netloc}"


# 从环境变量读取连接配置，避免把敏感信息硬编码到脚本中。
BASE_URL = _normalize_base_url(os.environ["HTEK_JIRA_BASE_URL"])
USERNAME = os.environ["HTEK_JIRA_USERNAME"]
PASSWORD = os.environ["HTEK_JIRA_PASSWORD"]
AUTH_TOKEN = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode("utf-8")).decode("ascii")

mcp = FastMCP(
    name="HTEK Jira Server",
    instructions=(
        "Use these tools to work with the company's on-prem Jira Server. "
        "Prefer search_jira_issues before creating new issues."
    ),
)


def _request(method: str, path: str, data: dict[str, Any] | None = None) -> Any:
    """
    Jira REST API 的统一请求封装。

    参数：
    - `method`：HTTP 方法，例如 `GET`、`POST`、`PUT`。
    - `path`：相对 Jira 基础地址的 REST 路径，例如 `/rest/api/2/myself`。
    - `data`：可选的 JSON 请求体，会自动编码为 UTF-8 JSON。

    返回：
    - 解析后的 JSON 对象；如果响应体为空，则返回空字典。

    说明：
    这里负责：
    - 自动补全基础 URL
    - 统一 Basic Auth
    - 统一 JSON 编码/解码
    - 统一错误处理
    """
    url = f"{BASE_URL}{path}"
    body = None
    headers = {
        "Authorization": f"Basic {AUTH_TOKEN}",
        "Accept": "application/json",
    }
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Jira 接口调用失败（HTTP {exc.code}，路径：{path}）：{payload}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"无法连接 Jira 服务（{BASE_URL}）：{exc}") from exc


def _issue_brief(issue: dict[str, Any]) -> dict[str, Any]:
    """
    把 Jira 搜索结果压缩成适合列表展示的简要结构。

    参数：
    - `issue`：Jira 搜索接口返回的单条 issue 原始数据。

    返回：
    - 仅保留列表页常用字段的简化结果。
    """
    fields = issue.get("fields", {})
    assignee = fields.get("assignee") or {}
    status = fields.get("status") or {}
    issuetype = fields.get("issuetype") or {}
    priority = fields.get("priority") or {}
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "status": status.get("name"),
        "issue_type": issuetype.get("name"),
        "priority": priority.get("name"),
        "assignee": assignee.get("displayName") or assignee.get("name"),
        "updated": fields.get("updated"),
    }


def _get_project_createmeta(project_key: str) -> dict[str, Any]:
    """
    读取项目创建元数据。

    参数：
    - `project_key`：Jira 项目 key。

    返回：
    - `createmeta` 中对应项目的元数据对象。

    说明：
    这是 Jira Server 里非常关键的一步，用于获取：
    - 可用 issue type
    - 后续字段定义
    - 项目级别的自定义配置
    """
    query = urllib.parse.urlencode({"projectKeys": project_key, "expand": "projects.issuetypes"})
    data = _request("GET", f"/rest/api/2/issue/createmeta?{query}")
    projects = data.get("projects", [])
    if not projects:
        raise RuntimeError(f"项目 {project_key} 没有返回可用的创建元数据，请检查项目 key 或权限。")
    return projects[0]


def _pick_subtask_issue_type(project_key: str, preferred_issue_type: str | None = None) -> dict[str, Any]:
    """
    为子任务创建流程挑选可用的子任务类型。

    参数：
    - `project_key`：目标项目 key。
    - `preferred_issue_type`：可选，优先使用的问题类型名称或 ID。

    返回：
    - 匹配到的 issue type 元数据。
    """
    project = _get_project_createmeta(project_key)
    issue_types = project.get("issuetypes", [])
    if preferred_issue_type:
        for issue_type in issue_types:
            if issue_type.get("name") == preferred_issue_type or issue_type.get("id") == preferred_issue_type:
                if not issue_type.get("subtask", False):
                    raise RuntimeError(f"项目 {project_key} 中的问题类型 {preferred_issue_type} 不是子任务类型。")
                return issue_type
        raise RuntimeError(f"项目 {project_key} 中未找到子任务类型 {preferred_issue_type}。")

    for issue_type in issue_types:
        if issue_type.get("subtask", False):
            return issue_type

    raise RuntimeError(f"项目 {project_key} 中没有可用的子任务类型。")


def _resolve_issue_type(project_key: str, issue_type: str) -> dict[str, Any]:
    """
    根据 issue type 名称或 ID 解析出 Jira 可接受的类型定义。

    参数：
    - `project_key`：目标项目 key。
    - `issue_type`：问题类型名称或 ID。

    返回：
    - 匹配到的 issue type 元数据。

    说明：
    在当前 Jira Server 环境里，创建 issue 时使用 issue type ID
    比直接使用中文名称更稳定，所以最终会统一转换为 ID。
    """
    project = _get_project_createmeta(project_key)
    issue_types = project.get("issuetypes", [])
    for candidate in issue_types:
        if candidate.get("id") == issue_type or candidate.get("name") == issue_type:
            return candidate
    raise RuntimeError(f"项目 {project_key} 中未找到问题类型 {issue_type}。")


@mcp.tool(description="Verify Jira Server connectivity and return the current authenticated user.")
def jira_whoami() -> dict[str, Any]:
    """
    验证当前连接和认证身份。

    入参：
    - 无

    返回：
    - 当前登录用户名、显示名、邮箱和基础地址。
    """
    data = _request("GET", "/rest/api/2/myself")
    return {
        "name": data.get("name"),
        "display_name": data.get("displayName"),
        "email": data.get("emailAddress"),
        "base_url": BASE_URL,
    }


@mcp.tool(description="List Jira projects visible to the current user.")
def list_jira_projects(limit: int = 50) -> dict[str, Any]:
    """
    列出当前账号可见的 Jira 项目。

    入参：
    - `limit`：最多返回多少个项目，默认 50。

    返回：
    - 项目总数和项目列表。
    """
    data = _request("GET", "/rest/api/2/project")
    projects = [
        {
            "key": p.get("key"),
            "name": p.get("name"),
            "project_type": p.get("projectTypeKey"),
        }
        for p in data[: max(limit, 0)]
    ]
    return {"count": len(projects), "projects": projects}


@mcp.tool(description="Search Jira issues with JQL. Use this before creating new issues whenever possible.")
def search_jira_issues(
    jql: str,
    max_results: int = 20,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    使用 JQL 搜索 issue。

    入参：
    - `jql`：JQL 查询语句。
    - `max_results`：最多返回多少条结果，范围会被限制在 1 到 100 之间。
    - `fields`：可选，指定需要返回的字段列表；不传则使用列表页常用字段。

    返回：
    - 命中的 issue 总数、本次返回条数，以及简化后的 issue 列表。
    """
    field_list = fields or ["summary", "status", "issuetype", "priority", "assignee", "updated"]
    query = urllib.parse.urlencode(
        {
            "jql": jql,
            "maxResults": max(1, min(max_results, 100)),
            "fields": ",".join(field_list),
        }
    )
    data = _request("GET", f"/rest/api/2/search?{query}")
    issues = [_issue_brief(issue) for issue in data.get("issues", [])]
    return {
        "total": data.get("total", len(issues)),
        "returned": len(issues),
        "issues": issues,
    }


@mcp.tool(description="Get a Jira issue by key, including core fields and description.")
def get_jira_issue(issue_key: str) -> dict[str, Any]:
    """
    按 issue key 拉取详情。

    入参：
    - `issue_key`：Jira issue key，例如 `TASK-138`。

    返回：
    - 常用详情字段，包括描述、状态、优先级、标签、父任务等。
    """
    query = urllib.parse.urlencode(
        {
            "fields": "summary,status,issuetype,priority,assignee,reporter,description,created,updated,resolution,labels,parent",
        }
    )
    issue = _request("GET", f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}?{query}")
    fields = issue.get("fields", {})
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "description": fields.get("description"),
        "status": (fields.get("status") or {}).get("name"),
        "issue_type": (fields.get("issuetype") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "labels": fields.get("labels") or [],
        "parent": (fields.get("parent") or {}).get("key"),
        "assignee": ((fields.get("assignee") or {}).get("displayName") or (fields.get("assignee") or {}).get("name")),
        "reporter": ((fields.get("reporter") or {}).get("displayName") or (fields.get("reporter") or {}).get("name")),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "resolution": (fields.get("resolution") or {}).get("name"),
        "browse_url": f"{BASE_URL}/browse/{issue.get('key')}",
    }


@mcp.tool(description="List available issue types for a project before creating issues.")
def get_jira_issue_types(project_key: str) -> dict[str, Any]:
    """
    查看某个项目可创建的问题类型。

    入参：
    - `project_key`：Jira 项目 key。

    返回：
    - 项目 key 和可用 issue type 列表。
    """
    try:
        project = _get_project_createmeta(project_key)
    except RuntimeError:
        return {"project_key": project_key, "issue_types": []}
    issue_types = [
        {"id": it.get("id"), "name": it.get("name"), "subtask": it.get("subtask", False)}
        for it in project.get("issuetypes", [])
    ]
    return {"project_key": project_key, "issue_types": issue_types}


@mcp.tool(description="Inspect create metadata fields for a project issue type, including required custom fields.")
def get_jira_issue_type_fields(project_key: str, issue_type: str) -> dict[str, Any]:
    """
    查看某个项目 + 问题类型下的字段元数据。

    入参：
    - `project_key`：Jira 项目 key。
    - `issue_type`：问题类型名称或 ID。

    返回：
    - 该类型下的字段定义，包括必填标记、类型和允许值。
    """
    query = urllib.parse.urlencode({"projectKeys": project_key, "expand": "projects.issuetypes.fields"})
    data = _request("GET", f"/rest/api/2/issue/createmeta?{query}")
    projects = data.get("projects", [])
    if not projects:
        return {"project_key": project_key, "issue_type": issue_type, "fields": []}

    for issue_type_meta in projects[0].get("issuetypes", []):
        if issue_type_meta.get("id") == issue_type or issue_type_meta.get("name") == issue_type:
            field_items = []
            for field_id, meta in (issue_type_meta.get("fields") or {}).items():
                field_items.append(
                    {
                        "id": field_id,
                        "name": meta.get("name"),
                        "required": meta.get("required", False),
                        "schema_type": (meta.get("schema") or {}).get("type"),
                        "allowed_values": [
                            value.get("name") if isinstance(value, dict) else value
                            for value in (meta.get("allowedValues") or [])
                        ],
                    }
                )
            field_items.sort(key=lambda item: (not item["required"], item["name"] or item["id"]))
            return {"project_key": project_key, "issue_type": issue_type_meta.get("name"), "fields": field_items}

    return {"project_key": project_key, "issue_type": issue_type, "fields": []}


@mcp.tool(description="Search Jira users by username, display name, or email fragment.")
def search_jira_users(query: str, max_results: int = 10) -> dict[str, Any]:
    """
    按用户名、显示名或邮箱片段搜索 Jira 用户。

    入参：
    - `query`：搜索关键词。
    - `max_results`：最多返回多少条结果，默认 10。

    返回：
    - 命中用户数量和用户列表。
    """
    params = urllib.parse.urlencode({"username": query, "maxResults": max(1, min(max_results, 50))})
    data = _request("GET", f"/rest/api/2/user/search?{params}")
    users = [
        {
            "name": user.get("name"),
            "display_name": user.get("displayName"),
            "email": user.get("emailAddress"),
            "active": user.get("active"),
        }
        for user in data[: max_results]
    ]
    return {"count": len(users), "users": users}


@mcp.tool(description="Create a new Jira issue in a project. Prefer running get_jira_issue_types first if unsure about issue_type.")
def create_jira_issue(
    project_key: str,
    summary: str,
    description: str = "",
    issue_type: str = "Task",
    priority: str | None = None,
    assignee_username: str | None = None,
    additional_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    创建顶层 issue。

    入参：
    - `project_key`：目标项目 key。
    - `summary`：问题概要。
    - `description`：问题描述。
    - `issue_type`：问题类型名称或 ID。
    - `priority`：可选，优先级名称，例如 `P3`。
    - `assignee_username`：可选，负责人用户名。
    - `additional_fields`：可选，额外字段字典，用于透传自定义字段。

    返回：
    - 新创建 issue 的 key、id、类型和浏览地址。
    """
    resolved_issue_type = _resolve_issue_type(project_key, issue_type)
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "summary": summary,
        "description": description,
        "issuetype": {"id": resolved_issue_type.get("id")},
    }
    if priority:
        fields["priority"] = {"name": priority}
    if assignee_username:
        fields["assignee"] = {"name": assignee_username}
    if additional_fields:
        fields.update(additional_fields)

    data = _request("POST", "/rest/api/2/issue", {"fields": fields})
    return {
        "key": data.get("key"),
        "id": data.get("id"),
        "issue_type": resolved_issue_type.get("name"),
        "browse_url": f"{BASE_URL}/browse/{data.get('key')}",
    }


@mcp.tool(description="Create a Jira subtask under an existing parent issue. If issue_type is omitted, the first available subtask type is used.")
def create_jira_subtask(
    project_key: str,
    parent_key: str,
    summary: str,
    description: str = "",
    issue_type: str | None = None,
    priority: str | None = None,
    assignee_username: str | None = None,
    additional_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    创建子任务。

    入参：
    - `project_key`：目标项目 key。
    - `parent_key`：父任务 key。
    - `summary`：子任务概要。
    - `description`：子任务描述。
    - `issue_type`：可选，子任务类型名称或 ID；不传则自动选择第一个可用子任务类型。
    - `priority`：可选，优先级名称。
    - `assignee_username`：可选，负责人用户名。
    - `additional_fields`：可选，透传的自定义字段。

    返回：
    - 新创建子任务的 key、id、类型和浏览地址。
    """
    chosen_issue_type = _pick_subtask_issue_type(project_key, issue_type)
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "parent": {"key": parent_key},
        "summary": summary,
        "description": description,
        "issuetype": {"id": chosen_issue_type.get("id")},
    }
    if priority:
        fields["priority"] = {"name": priority}
    if assignee_username:
        fields["assignee"] = {"name": assignee_username}
    if additional_fields:
        fields.update(additional_fields)

    data = _request("POST", "/rest/api/2/issue", {"fields": fields})
    return {
        "key": data.get("key"),
        "id": data.get("id"),
        "issue_type": chosen_issue_type.get("name"),
        "browse_url": f"{BASE_URL}/browse/{data.get('key')}",
    }


@mcp.tool(description="Add a comment to an existing Jira issue.")
def add_jira_comment(issue_key: str, comment: str) -> dict[str, Any]:
    """
    给 issue 添加评论。

    入参：
    - `issue_key`：目标 issue key。
    - `comment`：评论正文。

    返回：
    - 评论 ID、创建时间和浏览地址。
    """
    data = _request(
        "POST",
        f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}/comment",
        {"body": comment},
    )
    return {
        "issue_key": issue_key,
        "comment_id": data.get("id"),
        "created": data.get("created"),
        "browse_url": f"{BASE_URL}/browse/{issue_key}",
    }


@mcp.tool(description="List comments on a Jira issue.")
def get_jira_comments(issue_key: str, max_results: int = 50) -> dict[str, Any]:
    """
    读取 issue 评论列表。

    入参：
    - `issue_key`：目标 issue key。
    - `max_results`：最多返回多少条评论，默认 50。

    返回：
    - 评论总数和评论列表。
    """
    params = urllib.parse.urlencode({"maxResults": max(1, min(max_results, 200))})
    data = _request("GET", f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}/comment?{params}")
    comments = [
        {
            "id": comment.get("id"),
            "author": ((comment.get("author") or {}).get("displayName") or (comment.get("author") or {}).get("name")),
            "body": comment.get("body"),
            "created": comment.get("created"),
            "updated": comment.get("updated"),
        }
        for comment in data.get("comments", [])
    ]
    return {"issue_key": issue_key, "total": data.get("total", len(comments)), "comments": comments}


@mcp.tool(description="List available workflow transitions for a Jira issue.")
def list_jira_transitions(issue_key: str) -> dict[str, Any]:
    """
    查询某个 issue 当前可执行的状态流转。

    入参：
    - `issue_key`：目标 issue key。

    返回：
    - 当前可执行的 transition 列表。
    """
    data = _request("GET", f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}/transitions")
    transitions = [
        {
            "id": transition.get("id"),
            "name": transition.get("name"),
            "to_status": ((transition.get("to") or {}).get("name")),
        }
        for transition in data.get("transitions", [])
    ]
    return {"issue_key": issue_key, "transitions": transitions}


@mcp.tool(description="Transition a Jira issue to a new status. Provide either transition_name or transition_id.")
def transition_jira_issue(
    issue_key: str,
    transition_name: str | None = None,
    transition_id: str | None = None,
) -> dict[str, Any]:
    """
    执行 issue 状态流转。

    入参：
    - `issue_key`：目标 issue key。
    - `transition_name`：可选，transition 名称或目标状态名。
    - `transition_id`：可选，transition ID。

    返回：
    - 实际执行的 transition ID、名称和浏览地址。

    说明：
    必须至少提供 `transition_name` 或 `transition_id` 其中之一。
    """
    if not transition_name and not transition_id:
        raise RuntimeError("请提供 transition_name 或 transition_id 中的一个。")

    chosen_id = transition_id
    chosen_name = transition_name
    if not chosen_id:
        transitions = list_jira_transitions(issue_key).get("transitions", [])
        for transition in transitions:
            if transition.get("name") == transition_name or transition.get("to_status") == transition_name:
                chosen_id = transition.get("id")
                chosen_name = transition.get("name")
                break
        if not chosen_id:
            raise RuntimeError(f"Issue {issue_key} 当前没有可用的状态流转：{transition_name}。")
    elif not chosen_name:
        transitions = list_jira_transitions(issue_key).get("transitions", [])
        for transition in transitions:
            if transition.get("id") == chosen_id:
                chosen_name = transition.get("name")
                break

    _request(
        "POST",
        f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}/transitions",
        {"transition": {"id": chosen_id}},
    )
    return {
        "issue_key": issue_key,
        "transition_id": chosen_id,
        "transition_name": chosen_name,
        "browse_url": f"{BASE_URL}/browse/{issue_key}",
    }


@mcp.tool(description="Change the assignee of a Jira issue by username.")
def update_jira_assignee(issue_key: str, assignee_username: str) -> dict[str, Any]:
    """
    按用户名更新 issue 负责人。

    入参：
    - `issue_key`：目标 issue key。
    - `assignee_username`：负责人用户名。

    返回：
    - 更新后的负责人和浏览地址。
    """
    _request(
        "PUT",
        f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}/assignee",
        {"name": assignee_username},
    )
    return {
        "issue_key": issue_key,
        "assignee_username": assignee_username,
        "browse_url": f"{BASE_URL}/browse/{issue_key}",
    }


@mcp.tool(description="Update standard Jira issue fields. Use additional_fields for custom fields or advanced payloads.")
def update_jira_issue(
    issue_key: str,
    summary: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    assignee_username: str | None = None,
    additional_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    更新标准字段和自定义字段。

    入参：
    - `issue_key`：目标 issue key。
    - `summary`：可选，新概要。
    - `description`：可选，新描述。
    - `priority`：可选，新优先级。
    - `labels`：可选，新标签列表。
    - `assignee_username`：可选，新负责人用户名。
    - `additional_fields`：可选，额外字段字典，用于更新自定义字段。

    返回：
    - 被更新的字段名列表和浏览地址。
    """
    fields: dict[str, Any] = {}
    if summary is not None:
        fields["summary"] = summary
    if description is not None:
        fields["description"] = description
    if priority is not None:
        fields["priority"] = {"name": priority}
    if labels is not None:
        fields["labels"] = labels
    if assignee_username is not None:
        fields["assignee"] = {"name": assignee_username}
    if additional_fields:
        fields.update(additional_fields)
    if not fields:
        raise RuntimeError("未提供任何可更新字段，请至少传入一个字段。")

    _request("PUT", f"/rest/api/2/issue/{urllib.parse.quote(issue_key)}", {"fields": fields})
    return {
        "issue_key": issue_key,
        "updated_fields": sorted(fields.keys()),
        "browse_url": f"{BASE_URL}/browse/{issue_key}",
    }


if __name__ == "__main__":
    # 以 stdio 方式启动 MCP，供 Codex 客户端接入。
    mcp.run()
