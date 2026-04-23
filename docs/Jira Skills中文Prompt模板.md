# Jira Skills 中文 Prompt 模板

本文档提供 4 个本地 Jira Server skill 的中文调用模板，可直接复制后按实际项目内容替换变量。

## 1. `jira-server-status-report`

### 模板 1：生成项目周报

```text
使用 $jira-server-status-report 帮我生成一份 Jira Server 项目周报。

项目 key：TASK
时间范围：最近 7 天
汇报对象：项目经理和部门负责人
输出风格：简洁摘要

请重点关注：
1. 已完成事项
2. 当前进行中事项
3. 阻塞项和风险
4. 下周优先事项

如果某些 issue 需要补充上下文，请继续读取 issue 详情和评论后再总结。
```

### 模板 2：生成团队日会同步

```text
使用 $jira-server-status-report 基于 Jira Server 生成一份团队日会同步内容。

项目 key：RDTASK
时间范围：最近 1 天
汇报对象：研发团队
输出风格：简短，适合日会口头同步

请按以下结构输出：
1. 昨天完成
2. 今天进行中
3. 当前阻塞
```

### 模板 3：查看高优先级 backlog 健康度

```text
使用 $jira-server-status-report 帮我评估 Jira Server 项目 backlog 健康度。

项目 key：HTEK
时间范围：最近 30 天
汇报对象：团队负责人
输出风格：详细一点

请重点分析：
1. 高优先级未关闭 issue
2. 长时间未更新 issue
3. 当前阻塞和潜在风险
4. 是否有积压过久的问题
```

## 2. `jira-server-spec-to-backlog`

### 模板 1：把需求描述拆成任务

```text
使用 $jira-server-spec-to-backlog 将下面这段需求拆成 Jira Server backlog。

目标项目 key：HTEK
希望优先使用：需求 / 任务 / 子任务

需求内容：
我们计划新增一个设备日志导出功能，支持用户在 Web 页面选择时间范围并导出日志文件。
要求：
1. 前端支持时间筛选
2. 后端提供导出接口
3. 导出文件需要支持下载
4. 需要补充测试验证

请先输出拆解方案，不要直接创建 issue。
```

### 模板 2：从 PRD 摘要生成 backlog

```text
使用 $jira-server-spec-to-backlog 把这份 PRD 摘要转成 Jira Server backlog。

目标项目 key：RDTASK
请先检查该项目有哪些 issue type 和必填字段，再给出建议拆解。

PRD 摘要：
1. 增加会议录音转写入口
2. 支持上传音频文件
3. 展示转写进度和结果
4. 失败时给出错误提示
5. 需要补齐测试项和验收标准

请先展示：
1. 父项建议
2. 子项清单
3. 每项建议使用的问题类型
```

### 模板 3：直接创建 backlog

```text
使用 $jira-server-spec-to-backlog 根据下面需求直接创建 Jira Server backlog。

目标项目 key：TASK
如果该项目有必填字段，请自动检查并告诉我需要补什么。
如果可以创建，请优先创建一个父任务，再创建对应子任务。

需求内容：
市场部需要整理 2026 新品宣传资料，包括：
1. 官网文案更新
2. 宣传页设计稿确认
3. PPT 内容更新
4. 最终材料审核

先给我展示拆解结果，等我确认后再创建。
```

## 3. `jira-server-triage-issue`

### 模板 1：检查 bug 是否重复

```text
使用 $jira-server-triage-issue 帮我判断这个问题在 Jira Server 里是否已经存在。

目标项目 key：HTEK
错误描述：
用户在升级固件后，设备重启时偶发卡在启动页，必须断电重启才能恢复。

请你：
1. 提取关键词
2. 搜索相似 issue
3. 判断是重复问题、相关问题，还是新问题
4. 给出建议动作

不要直接创建 issue，先把判断结果发给我。
```

### 模板 2：基于报错信息做问题分诊

```text
使用 $jira-server-triage-issue 对下面这个报错做分诊。

目标项目 key：RDTASK
错误信息：
Whisper 转写任务提交成功，但结果页一直为空，没有报错弹窗。

补充背景：
1. 发生在测试环境
2. 上传的是 30 分钟 wav 文件
3. 多次重试可复现

请优先搜索 Jira 中是否已有相同或相似问题，并告诉我是：
- 重复问题
- 疑似回归
- 还是建议新建 issue
```

### 模板 3：分诊后新建问题

```text
使用 $jira-server-triage-issue 帮我处理下面这个问题。

目标项目 key：HTEK
错误描述：
设备在启用蓝牙耳机后，来电时没有铃声，但通话连接后声音正常。

如果 Jira 中已经有高度相似的问题，请优先建议给已有 issue 加评论。
如果没有，请帮我准备一个适合创建 Jira issue 的标题和描述结构。
创建前先让我确认。
```

## 4. `jira-server-meeting-to-tasks`

### 模板 1：从会议纪要提取行动项

```text
使用 $jira-server-meeting-to-tasks 把下面的会议纪要转成 Jira Server 任务。

目标项目 key：TASK

会议纪要：
1. 张三本周内整理新品发布文案
2. 李四负责确认官网图片素材
3. 王五下周二前输出宣传 PPT 初稿
4. 需要再安排一个人审核最终材料

请先提取行动项、建议负责人和任务概要，先不要直接创建。
```

### 模板 2：将纪要挂到已有父任务下

```text
使用 $jira-server-meeting-to-tasks 将下面这些会议后续事项挂到已有父任务下面。

目标项目 key：TASK
父任务 key：TASK-138

会议纪要：
- Russell 更新验收标准说明
- 张力山补充测试验证步骤
- 产品同事确认最终提测时间

请优先判断哪些适合创建成子任务，先给我展示结果后再执行。
```

### 模板 3：解析负责人并创建任务

```text
使用 $jira-server-meeting-to-tasks 帮我把下面纪要整理成 Jira Server 任务。

目标项目 key：RDTASK

会议纪要：
- @russell.zhang 完成语音模型调研结论整理
- 张力山 输出 whisper 和 sherpa-onnx 对比结果
- 产品经理补齐场景清单

请你：
1. 解析行动项
2. 尝试匹配 Jira 用户
3. 展示拟创建任务列表
4. 等我确认后再创建
```

## 使用建议

- 第一次在某个项目里创建 issue 前，先让 skill 检查 issue type 和必填字段。
- 如果项目流程比较严格，建议统一采用“先展示方案，再执行创建”的模式。
- 对 `TASK` 这类有自定义必填字段的项目，创建前要特别注意验收标准等字段是否需要补齐。
