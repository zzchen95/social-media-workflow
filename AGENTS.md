# 项目协作约定

本仓库只包含内容工作技能、模板、工具和独立教学案例，不含应用服务、平台凭据、历史报告或用户数据。

## 使用与引导

- 开始/继续全流程、查看进度或跨步骤交接时，使用`.agents/skills/social-media-workflow/SKILL.md`；明确单步任务优先对应专项技能。
- 依当前用户目标逐步获取必要资料。用户选择延期时保留该约定，缺画像可做探索，缺素材可做方案，缺表现可做分析计划；不默认继承维护者的账号、偏好或日程。
- 技能安装不代表真实研究、剪辑或复盘完成。演示选择与合成反馈和真实用户决定分开；实例不是本周事实。
- 研究、脚本、制作包、发布记录、快照与简报分别绑定版本和摘要。新资料只触发影响核对，不静默覆盖定稿或转移批准。
- 所有发布须按具体账号、平台和内容包版本人工批准；本仓库自身不执行发布，不创建平台账号、付费操作或默认自动化。

## 五步入口（总向导加四个专项）

- 总向导：`.agents/skills/social-media-workflow/SKILL.md`。
- 公开研究：`.agents/skills/public-social-research/SKILL.md`，默认配置`config/public_research.json`；候选附来源与限制，不称全站周榜。脚本只准备和校验档案，不是采集器。
- 选题脚本：`.agents/skills/social-content-planning/SKILL.md`；默认三个方向，用户选择后展开一个主稿和适用平台改编。
- 素材制作：`.agents/skills/social-content-production/SKILL.md`；先验证工具小样，真实导出且检查后才称成片。原片和旧版本保留。
- 表现复盘：`.agents/skills/social-performance-review/SKILL.md`；D1/D7按实际发布后24/168小时，保留来源、实际年龄和指标口径，缺失不当零，相关性不作因果。

## 自我迭代与贡献

- 上下文来自当前项目和用户真实反馈，优先解决实际问题，再提炼适用范围明确的方法。
- 工具特有说明放对应技能references，主技能保留必要路由，不堆按钮和坐标细节。没有实测就保留待验证。
- 用户个人偏好和数据留本地；长期画像修改沿内容流程确认。共享技能修改不能扩大对发布、付费、安装或账号的授权。
- 按`CONTRIBUTING.md`做分支修改与验证，不因一次自我迭代自动提交PR。

## 文件与检查

- 不提交`content/`、`media/`、`docs/reports/`、`config/local/`、凭据、数据库、日志或虚拟环境；新示例必须独立、脱敏、标注教学性质。
- 按`docs/INSTALL.md`选择当前解释器；文档中的`python`表示当前环境的解释器，不假定Unix路径或全局包。
- 安装检查：`python scripts/bootstrap.py --check`。
- 贡献检查：`python scripts/validate_share.py --full`与`python -m pytest -q`（先安装requirements-dev.txt）。
- 不要求安装FastAPI、前端工具、模型API或额外服务。
