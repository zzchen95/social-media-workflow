# 新 agent 从这里接手

本仓库是一个总向导和四个专项技能。按需在当前聊天执行，不需要 API Key、后台服务或计划任务。安装不会获得电脑控制权限，也不会带来维护者的账号、素材或历史。

## 给新 agent 的启动提示

> 读取 AGENTS.md、START_HERE.md 和 .agents/skills/social-media-workflow/SKILL.md。先运行只读安装检查和 agent_start.py，核对真实档案、版本、演练标记及延期资料。按我的当前目标直接执行可做的一步；需要我选题或提供必要材料时再交接。没有历史就从空项目开始。第一步按需研究，不创建 scheduled task；制作优先适配我指定的剪映。没有实测不能称已剪辑、导出或完成复盘。

在仓库根目录，用当前 Python 3.11+：

```bash
python scripts/bootstrap.py --check
python scripts/agent_start.py
```

Windows 可用 `py -3`；已安装本地环境时用 `.venv\Scripts\python.exe`，macOS/Linux 用 `.venv/bin/python`。检查缺运行依赖时按 [INSTALL](docs/INSTALL.md)安装到本地环境，再检查；不自动安装剪辑器或改系统设置。

`agent_start.py`只读项目内已知档案，输出 JSON：可用研究及实际窗口、每个工作流的检查点/模式/延期项、引用失配和选择缺口。它不联网、不创建目录、不运行技能或启动剪映；结果是导航信息，不能证明真实批准或媒体质量。多个内容工作流并存时不替用户挑选，演练不会自动成为当前任务。损坏的新检查点可回退读取旧版，但明确标待复查。

## 把意图落到一次可执行交付

| 用户当前目标 | agent 继续做什么 | 缺资料时交什么 |
| --- | --- | --- |
| 这周趋势、刷新研究 | 读第一步技能，用当前搜索和网页读取采集，prepare → 真实来源/候选/报告 → check | 工具失败保留阻塞；prepared不算研究完成 |
| 选题、脚本 | 读第二步技能，固定研究/画像/学习简报，先给三个方向 | 无画像做探索；用户选中后展开一稿 |
| 剪映剪辑、字幕、成片修改 | 读第三步及剪映参考；核对脚本/素材，验证小样后做主平台粗剪 | 无素材/工具交剪辑方案和文字，不能填实测时间码 |
| D1/D7复盘 | 读第四步及留存到剪辑参考；登记实际用版、时间、真实快照 | 无表现只做分析准备，不新建虚构帖子或学习结论 |
| 继续、看进度 | 先核对检查点引用与最新消息，恢复当前对象 | 看进度只读；不顺便研究、渲染或改稿 |

没有检查点时从专项档案恢复，不要求重做历史。研究必须检查 `completed/partial`、校验及来源；旧研究只能按实际窗口引用。脚本、制作包、发布快照分别固定版本与摘要，不用“最新文件”静默替换。

## 剪映和复盘的交接

- 用户要求实施/跑通剪映能力时，直接执行[实际实施剪映 Computer Use 能力](docs/implementation/jianying-capability.md)：先验证当前电脑，再完成独立小样、一次修改及用户使用交接。不能只读完文档就称能力完成。
- 剪映：读 [Computer Use 操作参考](.agents/skills/social-content-production/references/jianying-computer-use.md)。先识别当前软件/版本/窗口，按“观察 → 单动作 → 复查”操作；不继承别人的坐标、句柄或工具验证结果。
- 复盘到下一次剪辑：读 [留存与剪辑交接](.agents/skills/social-performance-review/references/retention-to-edit.md)。先核对实际发布视频和时间轴，再将学习记录落到脚本镜头、片段和一个实验变量。
- D1/D7时间可用 `scripts/review_windows.py`复算。该工具不采集指标、不设置提醒，也不能诊断流失原因。
- 每轮保存专项成果和必要的版本检查点；结束时说明实际完成项、未验证项、文件链接和一个下一步。长期画像和发布批准仍由用户明确确认。

## 运行边界

搜索、文件、Computer Use和播放能力由当前客户端提供，仓库不能安装出这些权限。Computer Use可用时读取其当前技能与安全/确认规则；不登录、不处理密码或改隐私设置。遇到上传型识别/云同步、付费或发布入口，不能把普通剪辑授权扩大为这些动作的授权。GitHub 同步也不能从“使用技能”推断授权，不读取 Token。

第一步完整保留为 [.agents/skills/public-social-research/SKILL.md](.agents/skills/public-social-research/SKILL.md)。本仓库默认日程关闭，其他用户也不会继承任何 scheduled task。
