# tools 目录开发说明

本文档说明仓库内 **`tools/`** 与 **`test/`** 中与本地 Jira Server MCP 相关的脚本职责、运行方式及维护注意点。命令示例默认在**仓库根目录**下执行（与 `README.md` 中目录约定一致）。

## 1. 目录与文件

| 路径 | 说明 |
|------|------|
| [jira_server_mcp.py](jira_server_mcp.py) | 本地 Jira Server 的 **MCP 适配层**（`FastMCP`），供 **Codex / Cursor / OpenClaw / Hermes** 等通过 MCP 调 Jira REST API。 |
| [../test/Jira MCP自测脚本.py](../test/Jira%20MCP%E8%87%AA%E6%B5%8B%E8%84%9A%E6%9C%AC.py) | 自动化自测：只读 + 可选写入；默认目标项目 **`PR`**（仓库约定的测试项目区；可用 `--project` 覆盖）。 |

## 2. `jira_server_mcp.py` 说明

### 2.1 职责

- 将公司内网 **Jira Server** 的常用能力封装为 MCP **tools**（见文件头部设计目标，约第 1–18 行）。
- 统一 **Basic Auth**、JSON 编解码与错误信息（`_request`，约第 100–141 行）。

### 2.2 MCP 工具一览（与源码 `@mcp.tool` 一致）

**只读**

| 函数 | 作用摘要 |
|------|----------|
| `jira_whoami` | 当前认证用户 |
| `list_jira_projects` | 可见项目列表 |
| `search_jira_issues` | JQL 搜索 issue |
| `get_jira_issue` | 按 key 取详情 |
| `get_jira_issue_types` | 项目下 issue 类型 |
| `get_jira_issue_type_fields` | 某类型创建字段元数据（含必填自定义字段） |
| `search_jira_users` | 用户搜索 |
| `get_jira_comments` | 评论列表 |
| `list_jira_transitions` | 可用工作流流转 |

**写入**

| 函数 | 作用摘要 |
|------|----------|
| `create_jira_issue` | 创建顶层 issue |
| `create_jira_subtask` | 创建子任务 |
| `add_jira_comment` | 添加评论 |
| `transition_jira_issue` | 执行状态流转 |
| `update_jira_assignee` | 更新负责人 |
| `update_jira_issue` | 更新概要/描述/优先级/标签等，**`additional_fields` 传自定义字段** |

完整索引见 `jira_server_mcp.py` 第 31–60 行注释块。

### 2.3 配置来源

依赖用户环境变量（与安装器写入的 **用户级** 变量一致）：

- `HTEK_JIRA_BASE_URL`
- `HTEK_JIRA_USERNAME`
- `HTEK_JIRA_PASSWORD`

`HTEK_JIRA_BASE_URL` 可为 Jira 首页完整 URL，由 `_normalize_base_url`（约第 64–82 行）裁剪为 REST 基础地址。

### 2.4 开发建议

新增或修改 MCP tool 时建议：

1. 先确认对应 Jira REST 接口与权限。
2. 先只读、再写入；创建 issue 前先调 `get_jira_issue_type_fields`。
3. issue type 写入优先使用 **类型 id**（自测与生产经验：比仅用 `name` 更稳）。
4. 错误路径保留 Jira 返回体，便于排障。

---

## 3. `test/Jira MCP自测脚本.py` 说明

### 3.1 模式（`--mode`）

| 模式 | 行为 |
|------|------|
| `readonly` | 仅第一阶段只读检查，**不写** Jira。 |
| `write` | 在只读检查通过后，执行第二阶段写入检查（当前实现中 `write` 仍会先跑只读段）。 |
| `all` | 默认：只读 + 写入全流程。 |

### 3.2 参数

| 参数 | 说明 |
|------|------|
| `--project` | 目标 Jira 项目 key，**默认 `PR`**。 |
| `--mode` | 见上表，默认 `all`。 |
| `--json-out` | 可选，覆盖默认 JSON 输出路径；默认写入 `test/Jira MCP自测结果.json`。 |
| `--md-out` | 可选，覆盖默认 Markdown 输出路径；默认写入 `test/Jira MCP自测报告.md`。 |

### 3.3 只读阶段实际调用的 MCP 函数

只读检查的目标，是先确认当前账号、目标项目、问题类型和字段元数据都正常，再决定是否进入后续写入测试。

当前只读阶段会依次检查：

- 当前 Jira 登录身份是否可读
- 当前账号是否能看到目标项目
- 用户搜索能力是否正常
- 目标项目的顶层 issue type 是否可读
- 目标项目的子任务 issue type 是否可读
- 顶层任务和子任务的必填字段元数据是否可用于后续建单

实现上，脚本会根据字段元数据里的 `required` 信息，尝试为后续建单阶段自动补齐一部分必填字段占位。

如果项目里存在脚本暂时无法自动补齐的复杂必填字段，例如某些结构化时间字段、附件类字段，脚本会在只读阶段直接失败，而不会继续进入写入阶段。这样可以更早暴露项目字段配置问题，避免在 Jira 里产生半成功的测试数据。

### 3.4 写入阶段（`--mode` 为 `write` 或 `all` 时）

写入阶段只会在只读检查通过后执行，目的是验证 Jira MCP 的核心写操作是否真正可用。

当前写入阶段会覆盖这些场景：

- 创建父任务
- 更新任务字段
- 添加评论并回读评论列表
- 更新负责人
- 查询当前任务可用流转，并在存在可用流转时执行一次状态流转
- 回读父任务详情，确认更新结果已持久化
- 创建子任务
- 回读子任务详情，确认父子关系正确
- 按本次测试标签搜索任务，确认搜索能力可回收刚创建的数据

实现上，父任务和子任务在创建时都会复用只读阶段算出的动态必填字段占位；如果目标项目的字段要求发生变化，通常会先在只读阶段暴露出来。

需要注意：

- `list_jira_transitions` 在部分项目或状态下可能返回空列表，这种情况会被记录为跳过，不会直接判定整轮自测失败。
- 报告中的 `get_jira_issue_subtask`，本质上是对子任务 key 再执行一次 `get_jira_issue`，只是为了在报告里区分“父任务回读”和“子任务回读”。

### 3.5 常用命令（在仓库根目录）

默认完整自测（会真实创建、更新 Jira 测试单）：

```powershell
python .\test\Jira MCP自测脚本.py
```

只读（不写 Jira）：

```powershell
python .\test\Jira MCP自测脚本.py --mode readonly
```

默认会同时生成：

```text
test/Jira MCP自测结果.json
test/Jira MCP自测报告.md
```

等价于显式指定默认项目：

```powershell
python .\test\Jira MCP自测脚本.py --project PR --mode readonly
```

显式指定完整自测（与默认行为等价）：

```powershell
python .\test\Jira MCP自测脚本.py --mode all
```

显式指定输出路径：

```powershell
python .\test\Jira MCP自测脚本.py --mode all --json-out .\test\Jira MCP自测结果.json --md-out .\test\Jira MCP自测报告.md
```

更多安装与验收说明见 [HtekJira安装与使用说明.md](../install/HtekJira安装与使用说明.md)。

---

## 4. 维护建议

### 4.1 新项目接入前先看字段元数据

不同项目、不同 issue type 的必填字段不同。创建 issue 前优先：`get_jira_issue_types` → `get_jira_issue_type_fields`。

### 4.2 谨慎在真实项目里做写入测试

自测 `all` / `write` 会真实创建、更新 issue。建议：

- 日常用 `readonly`；
- 写入类测试放在**可接受的测试项目**（默认 **`PR`** 为仓库约定的测试项目区，可按需 `--project`）；
- 脚本使用唯一 `labels` 便于事后检索。

### 4.3 兼容性结论（与当前实现一致）

1. 创建 issue 时，**issue type 使用 id** 比仅用 name 更稳（自测里从 `get_jira_issue_types` 取 id 再创建）。
2. **`PR` 上必填项会随工作流配置变化**：自测已改为按 `get_jira_issue_type_fields` **动态生成** `create_jira_issue` / `create_jira_subtask` 的 `additional_fields`；若新增「无法占位」的必填类型，需扩展 `test/Jira MCP自测脚本.py` 中的 `_placeholder_for_jira_field`（或放宽项目配置）。

### 4.4 扩展新能力时的顺序

例如附件、issue 链接、批量更新、sprint 等：

1. 单接口验证 → 2. 封装 MCP tool → 3. 纳入自测 → 4. 再写入 `skills/` 或 `docs/`。
