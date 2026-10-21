# 工作流检查点

用于跨轮/跨聊天恢复当前对象、实际进度和下一步。在用户启动/推进内容任务，或明确授权端到端演练时创建；演练增加 purpose=workflow_trial，真实内容任务为 content_work，不因安装技能预建业务任务。研究、脚本、制作包和复盘文件保持各自原有结构。

## 文件与最低字段

content/workflows/<workflow-id>/checkpoint-v001.json；后续递增版本，保留 parent_checkpoint 路径与摘要。示例只演示结构，不是当前项目的实际状态：

```json
{
  "schema_version": 1,
  "purpose": "content_work",
  "workflow_id": "<safe-id>",
  "created_at": "<actual-offset-aware-time>",
  "parent_checkpoint": null,
  "mode": "exploratory",
  "focus": {
    "account_id": null,
    "content_id": null,
    "platforms": ["xiaohongshu", "tiktok", "instagram"]
  },
  "stage_records": [
    {
      "stage": "planning",
      "scope": {"content_id": null, "platform": null},
      "progress": "not_started",
      "artifacts": [],
      "gaps": ["profile_deferred"],
      "needs_recheck": false
    }
  ],
  "user_decisions": [],
  "deferred_inputs": [
    {"field": "profile", "basis": "user_deferred", "resume_when": "user_provides"}
  ],
  "next_action": {
    "stage": "planning",
    "description": "基于已核对的研究准备探索选题",
    "state": "proposed",
    "requires": [],
    "basis": "recommendation_only"
  },
  "needs_recheck": false
}
```

执行时用真实 ID/时间替换结构占位符；可将暂无事实的阶段留空，不机械创建所有记录。无真实用户决定时数组为空；示例中的推荐不代表已授权执行，暂无账号或内容时为 null，不制造 ID 冒充已建档。

stage 使用 research / planning / production / review；progress 可用 not_started / in_progress / delivered / waiting_user / waiting_input / blocked。状态与专项文件原值并存，不能用 delivered 推断已审核或下游就绪。用 deliverable_kind 区分 research_snapshot_reused / exploratory_script / production_plan / review_preparation 等实际交付，便于恢复时不把准备状态显示为成片或已复盘。mode 区分探索/正式；制作方案是否已渲染、发布是否真实等以引用档案为准，不用总mode抹去细节。

artifacts 的每项记录角色、项目相对路径（外部素材用核实可访问的实际路径）、SHA-256、所引用对象ID与版本；记录该专项文件的实际状态以及检查范围。具体字段可按当前任务补充，不为缺字段捏造值。用户上传截图也需关联对应帖子、来源与时间精度，未知保留 null。

## 关联而不混淆

- research 可是全项目共用快照，planning 是批次；同批次可能产生多个内容，不以文件夹日期强行认作同一对象。
- content_id 关联脚本与制作包，各自版本独立。平台与账号适配分别保存，批准引用具体内容版本而非检查点。
- 每个平台每个帖子有独立 publication_id，D1/D7各绑定真实快照及修订；复盘可以不依赖完整上游链，缺口照实记录。
- learning/brief引用范围及版本；第二步采用记录决定如何使用，不凭简报存在自动改稿。
- 用户原话摘要、适用对象、时间/消息依据属于 user_decisions。演练执行授权另记 authorization；它不等于选题、脚本或发布批准。模型推荐、合成演练选择和测试反馈单列演示依据，不写为真人选择；不复制或生成批准记录。
- next_action 表示推荐/已授权/等用户选择/等资料，已有授权需有依据；它不是下一条工具调用指令，也不授予外部操作许可。
- deferred_inputs 保留用户“之后补”的范围和依据，收到对应资料后记录解决，不重复要求已决定延期的资料。

## 更新与恢复

1. 优先使用用户给定workflow/content/版本；否则先用 rg --files 列已有检查点及相关manifest，不深读所有素材。
2. 判断候选检查点的对象、模式、父链和实际时间。多个工作流不能按文件名最大值决定“当前”；无足够上下文时只澄清当前对象。没有检查点时从专项文件恢复关联，未知状态留未知。
3. 对本轮将消费的引用核对文件存在、摘要和专项状态/确认/实际输出。记录失配与 needs_recheck；不自动用更新文件覆盖固定引用，跨入新版本须按专项规则处理。
4. 读取阶段交付、待决定与延后资料，结合最新用户消息更新下一步。确认尚缺选择/反馈/数据时交付对应成果，不循环重跑已完成步骤；新数据足以继续则完成当前授权工作。
5. 保存新版本，记录父路径/摘要与实际变更。创建前检查目标不存在，避免并发覆盖；并发父链冲突先核对对象与输入，不伪造一条成功合并的历史。
6. 检查点损坏/缺文件时保留问题，从能核实的档案继续；不借总进度将失败、待核验或演示提升为完成。文件无法写入时说明未保存的索引，不重复执行已完成媒体/研究来假装恢复。

总向导不改专项原档来适配这个索引，不引入额外数据库工作流，也不维护一个覆盖所有账号的全局“当前步骤”。用户查看进度只读这些真实依据；不因查看而启动新阶段。
