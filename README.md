# 三平台内容工作向导

用一个入口串联小红书、TikTok、Instagram的公开研究、选题脚本、素材制作和发布后复盘。复用ChatGPT已有的搜索、文件分析、写作与可用本地工具。

这是**5个项目技能及其依赖**，没有模型API服务、平台账号连接或自动发布程序；不附带维护者的账号、素材、表现数据、历史研究或试跑档案。

## 快速开始

### 复制给自己的 agent

将下面整段复制给支持本地文件和终端的 agent，即可从克隆、本地化和自检开始，再按仓库流程实施剪映能力。实际电脑操作还需要当前环境提供 Computer Use 工具，验证要求见[实际实施任务](docs/implementation/jianying-capability.md)。

```text
请获取并在本地使用这个仓库：
https://github.com/zzchen95/social-media-workflow

1. 在当前已授权工作区克隆完整仓库，保留隐藏目录 .agents。若已有克隆，先核对远端和工作区改动；仅在安全时更新，不覆盖个人修改或运行数据。

2. 读取 AGENTS.md、README.md、START_HERE.md 和 docs/INSTALL.md。根据当前操作系统配置仓库内的 Python 环境，不复制到全局技能目录，不安装无关软件。

3. 运行安装自检和 scripts/agent_start.py，核对五个技能、文件引用、已有进度和延期资料。没有历史资料就从空项目开始，不继承维护者的账号、素材或测试结果。

4. 使用 $social-media-workflow，继续执行仓库内的“实际实施剪映 Computer Use 能力”任务，并逐步指导我使用。操作细节、验证、恢复和交付要求以仓库文档为准。

请实际完成当前工具和权限允许的工作，不只返回计划。缺少必要资料或工具时，说明具体阻塞和我需要完成的一步，同时继续其他可做的部分。不要读取 Token、修改安全设置、创建定时任务或发布内容；未经我明确要求，不推送 GitHub 或创建 PR。
```

### 手动克隆和安装

```bash
git clone https://github.com/zzchen95/social-media-workflow.git
cd social-media-workflow
```

1. 克隆本仓库，或下载ZIP并完整解压，保留隐藏目录`.agents/`。
2. 在支持本地工作的ChatGPT桌面端或Codex中打开解压后的仓库文件夹。
3. 将上面的完整启动提示发给 agent；它会识别已有克隆并继续。

本地终端也可以先运行：

```bash
# macOS / Linux
python3 scripts/bootstrap.py
```

```powershell
# Windows
py -3 scripts/bootstrap.py
```

无需激活虚拟环境。安装器只创建/复用本仓库的`.venv`、安装必要的运行依赖、检查文件与时区；不安装剪辑器、启用计划任务或运行研究。纯检查可加`--check`，不创建虚拟环境。

详见[安装、检查和更新](docs/INSTALL.md)。首次使用没有研究档案是正常状态：可以让向导做首轮研究，或先准备常青探索方案。

## 只记一个入口

> 使用 $social-media-workflow，看看当前进度，带我完成下一步。

可以接着说“选第二个”“修改开场”“素材在这个目录”“这是七天数据”。向导按需读取专项技能，在选择和反馈节点承接用户，而不是每个操作都问一次。

| 技能 | 用途 |
| --- | --- |
| `$social-media-workflow` | 总向导、跨步骤交接、版本恢复及方法迭代 |
| `$public-social-research` | 不登录的三平台近期topic/style候选池，保留来源及缺口 |
| `$social-content-planning` | 账号适配、探索选题、完整拍摄脚本及反馈 |
| `$social-content-production` | 实际素材的剪辑方案/导出、字幕、封面及平台文案 |
| `$social-performance-review` | 真实发布后D1/D7复盘、实验及下一轮创作简报 |

[新 agent 接手并运行](START_HERE.md) · [总向导说明](docs/implementation/workflow-guide.md) · [独立教学案例](examples/README.md) · [贡献与PR流程](CONTRIBUTING.md)

## 剪映制作与复盘闭环

新 agent 需要实施剪映能力时，按[实际实施任务](docs/implementation/jianying-capability.md)在用户当前电脑逐项跑通小样、恢复和一次修改，并指导用户使用；没有实测的项保留未验证。

第三步增加[剪映 Computer Use 操作参考](.agents/skills/social-content-production/references/jianying-computer-use.md)：当前窗口识别、小样验证、工程保护、字幕、平台版本、本地导出、检查和断点恢复。第四步增加[留存到剪辑交接](.agents/skills/social-performance-review/references/retention-to-edit.md)：核对实际发布版与时间轴，把一个实验变量对应到脚本镜头、片段及剪映操作意图；执行验收与效果验证分开。

这些是可执行的方法，不能替代用户当前电脑的实机小样。新 agent 用 `python scripts/agent_start.py` 只读识别档案；D1/D7可用 `scripts/review_windows.py` 复算时间。第一步完整保留为按需研究，默认日程关闭。

## 运行条件和边界

- 推荐Python 3.11或更新版本。两个档案工具使用Python标准库；Windows通过tzdata提供时区信息。使用/阅读技能不需要模型API Key。
- 研究需要当前聊天可用的搜索与网页读取工具；档案脚本只准备、校验文件，不采集网页。无法访问就保留缺口，不生成“本周热榜”。
- 实际剪辑需要用户自己的软件/素材，并先验证读取、操作、导出和播放。Computer Use等工具按客户端和授权可用性使用，不能由安装技能自动获得。
- 只有网页版/手机端聊天时，克隆仓库不会自动安装本地技能，也不会获得电脑文件权限。可将文档作为上下文；要分发为跨界面可安装能力，需要另行打包和测试插件。
- 脚本可拍确认与最终平台内容包批准分开；修改后新版本重新审核。本仓库不执行发布。

官方能力范围：[项目技能与发现位置](https://learn.chatgpt.com/docs/build-skills)、[本地与云端工作](https://learn.chatgpt.com/docs/use-chatgpt)。客户端与组织设置可能影响可用工具；文件结构自检不代表端到端媒体能力已验证。

## 个人资料留在本地

`content/`、`media/`、`docs/reports/`、`config/local/`及凭据/数据库/日志/虚拟环境均默认忽略。自己的账号、素材、复盘和检查点放这些运行目录，不提交到共享仓库。通用模板和脱敏小例放`examples/`或专项技能参考资料。

默认配置为中文小红书、以美国英语为目标的TikTok/Instagram，时区America/Los_Angeles。按当前用户需要调整；使用本地配置时给研究工具传`--config config/local/public_research.json`。本仓库没有默认活动日程或历史报告。

## 改进第三步并贡献回来

> 我使用剪辑工具X、版本Y。结合本项目和真实使用反馈完善第三步，将验证过的可复用方法写入相关技能参考资料；未验证项保留，个人路径和素材不带入。我明确要求后再提交PR。

普通使用可直接克隆上游；准备贡献时先Fork，用自己的分支试用、校验，再向上游提PR。维护者合并后其他人更新仓库即可得到改进。[完整PR步骤](CONTRIBUTING.md)

许可证尚未指定；对外复用和再分发的许可条款由维护者另行明确。
