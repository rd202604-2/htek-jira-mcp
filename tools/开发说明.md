# tools 目录开发说明

本文档用于说明 `tools/` 目录下本地 Jira 相关脚本的职责、使用方式和维护建议。

## 目录说明

当前目录下的主要文件有：

- `jira_server_mcp.py`
  本地 Jira Server 的 MCP 适配层。
  负责把 Jira REST API 封装成 Codex 可调用的 MCP 工具。

- `test/Jira MCP自测脚本.py`
  Jira MCP 的自动化自测脚本。
  用于验证只读能力、写入能力以及实际 Jira 项目中的字段兼容性。

## jira_server_mcp.py 说明

### 功能分层

脚本大致分为三层：

1. 内部基础函数
- URL 规范化
- 统一请求封装
- issue type 解析
- 子任务类型挑选

2. 只读工具
- 当前身份
- 项目列表
- issue 搜索
- issue 详情
- issue type 和字段元数据
- 用户搜索
- 评论列表
- 状态流转列表

3. 写入工具
- 创建 issue
- 创建子任务
- 添加评论
- 状态流转
- 更新负责人
- 更新字段

### 配置来源

脚本依赖以下用户环境变量：

- `HTEK_JIRA_BASE_URL`
- `HTEK_JIRA_USERNAME`
- `HTEK_JIRA_PASSWORD`

说明：
- 建议继续通过环境变量提供账号信息，不要把账号密码写死到代码里。
- `HTEK_JIRA_BASE_URL` 可以配置为 Jira 首页地址，脚本会自动裁剪成基础地址。

### 开发建议

新增 MCP tool 时，建议按这个顺序处理：

1. 先确认 Jira REST API 是否可用
2. 先做只读验证，再做写入逻辑
3. 如果涉及创建 issue，优先查 `get_jira_issue_type_fields`
4. 如果涉及 issue type，优先转成 issue type ID 再写入
5. 出错时尽量保留 Jira 返回的原始 payload，便于排查

## test/Jira MCP自测脚本.py 说明

### 支持模式

当前脚本支持三种模式：

- `readonly`
  只执行只读检查，不创建或修改 Jira 数据

- `write`
  执行完整检查中的写入部分
  说明：当前实现里默认前面会先跑一遍只读校验，保证写入前的上下文已准备好

- `all`
  执行完整检查，默认模式

### 常用命令

只读检查：

```powershell
python .\test\Jira MCP自测脚本.py --project TASK --mode readonly
```

完整检查：

```powershell
python .\test\Jira MCP自测脚本.py --project TASK --mode all
```

输出 JSON 报告：

```powershell
python .\test\Jira MCP自测脚本.py --project TASK --mode all --json-out .\test\Jira MCP自测结果.json
```

## 维护建议

### 1. 新项目接入前先看字段元数据

不同项目、不同问题类型的必填字段不一样。  
在新项目里创建 issue 前，优先执行：

- `get_jira_issue_types`
- `get_jira_issue_type_fields`

### 2. 谨慎在真实项目里做写入测试

当前自测脚本会真实创建 issue 和子任务。  
如果需要减少干扰，建议：

- 优先用 `readonly` 模式
- 在专门测试项目里跑 `write` 或 `all`
- 使用唯一标签，方便后续筛选测试单

### 3. 优先保留兼容性逻辑

当前 Jira Server 有两个已验证的兼容性点：

1. 创建 issue 时，使用 issue type `id` 比使用 `name` 更稳定
2. `TASK` 项目创建任务和子任务时要求 `customfield_12800`（验收标准）

后续修改代码时，建议不要去掉这两类兼容处理。

### 4. 先做最小闭环，再做扩展

如果要新增功能，例如：
- 上传附件
- 链接 issue
- 批量更新
- 查询 sprint / board

建议先做一个最小闭环：

1. 单接口验证
2. 封装成 MCP tool
3. 加入自测
4. 再写到技能或文档里
