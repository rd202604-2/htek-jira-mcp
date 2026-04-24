# HtekJira REST API基础说明

## 1. 什么是 REST API

REST API 可以理解成：

`一个系统对外提供的“程序调用接口网址”集合。`

对 Jira 来说：

- 浏览器访问的是给人看的网页
- 程序访问的是给代码调用的 REST API

例如：

- 浏览器页面：`http://oa.htek.com:8088/browse/PR-614`
- REST API：`http://oa.htek.com:8088/rest/api/2/issue/PR-614`

区别在于：

- 网页通常返回 HTML 页面
- REST API 通常返回 JSON 结构化数据

## 2. 为什么能接入公司本地 Jira Server

核心原因有 4 个：

1. 当前电脑在公司内网环境下可以访问本地 Jira Server。
2. Jira Server 本身提供标准 REST API。
3. 当前实现通过用户名密码认证，并通过环境变量传入连接信息。
4. MCP 只是工具接入协议，不限制后端必须是公网 SaaS，接本地系统同样可行。

当前实现使用的环境变量为：

- `HTEK_JIRA_BASE_URL`
- `HTEK_JIRA_USERNAME`
- `HTEK_JIRA_PASSWORD`

## 3. Jira Server 官方 REST API 大类

Jira Server / Data Center 官方 REST API 更适合按“资源分类”理解，而不是手工列出全部单条 endpoint。

### 3.1 Jira Platform / Core REST API

| 分类 | 说明 |
|---|---|
| `application-properties` | 应用属性 |
| `applicationrole` | 应用角色 |
| `attachment` | 附件 |
| `avatar` | 头像 |
| `cluster` | 集群信息 |
| `comment` | 评论 |
| `component` | 组件 |
| `configuration` | 系统配置 |
| `customFieldOption` | 自定义字段选项 |
| `customFields` | 自定义字段 |
| `dashboard` | 仪表盘 |
| `email-templates` | 邮件模板 |
| `field` | 字段定义 |
| `filter` | 过滤器 |
| `group` | 用户组 |
| `groups` | 用户组集合 |
| `groupuserpicker` | 组选人器 |
| `index-snapshot` | 索引快照 |
| `index` | 索引 |
| `issue` | issue 查询、创建、更新、流转等 |
| `issueLink` | issue 关联 |
| `issueLinkType` | issue 关联类型 |
| `issuesecurityschemes` | issue 安全方案 |
| `issuetype` | issue 类型 |
| `issuetypescheme` | issue 类型方案 |
| `jql` | JQL 相关 |
| `licenseValidator` | 许可证校验 |
| `monitoring` | 监控 |
| `mypermissions` | 当前用户权限 |
| `mypreferences` | 当前用户偏好 |
| `myself` | 当前登录用户 |
| `notificationscheme` | 通知方案 |
| `password` | 密码相关 |
| `permissions` | 权限 |
| `permissionscheme` | 权限方案 |
| `priority` | 优先级 |
| `priorityschemes` | 优先级方案 |
| `project` | 单个项目 |
| `projectCategory` | 项目分类 |
| `projects` | 项目集合 |
| `projectvalidate` | 项目校验 |
| `reindex` | 重建索引 |
| `resolution` | 解决结果 |
| `role` | 项目角色 |
| `screens` | Screen 配置 |
| `search` | 搜索 |
| `searchLimits` | 搜索限制 |
| `securitylevel` | 安全级别 |
| `serverInfo` | 服务器信息 |
| `settings` | 设置 |
| `status` | 状态 |
| `statuscategory` | 状态分类 |
| `terminology` | 术语 |
| `universal_avatar` | 通用头像 |
| `upgrade` | 升级相关 |
| `user` | 用户 |
| `version` | 版本 |
| `workflow` | 工作流 |
| `workflowscheme` | 工作流方案 |
| `worklog` | 工时日志 |
| `session` | 会话 |
| `websudo` | WebSudo |

### 3.2 Jira Software REST API

| 分类 | 说明 |
|---|---|
| `backlog` | Backlog |
| `board` | 看板 |
| `epic` | Epic |
| `sprint` | Sprint |

### 3.3 Jira Service Management / Service Desk REST API

| 分类 | 说明 |
|---|---|
| `request` / `customer request` | 客户请求 |
| `customer` | 客户 |
| `servicedesk` / `service desk` | 服务台 |
| `organization` | 组织 |
| `request type` | 请求类型 |
| `customer transition` | 客户侧状态流转 |
| `approval` | 审批 |

## 4. 官方参考链接

- [About the JIRA Server REST APIs](https://developer.atlassian.com/server/jira/platform/about-the-jira-server-rest-apis/)
- [Jira Data Center REST API Reference](https://developer.atlassian.com/server/jira/platform/rest/)

