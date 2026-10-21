# 第一步：三平台公开研究

默认按需启动，无活动日程，无历史报告。用户明确需要定时研究时，另行配置其自己的计划任务；配置文件中的schedule不会创建应用任务。

## 输入和实际采集

读取[默认配置](../../config/public_research.json)，以其中时区的当天为截止、含当天回溯7个日历日。小红书研究中文市场；TikTok/Instagram以美国英语为目标，但无法证明地区代表性时必须说明。

使用当前ChatGPT实际可用的公开搜索与网页读取，不登录、不绕过访问限制。不需要平台密码或模型API Key。来源入口是候选，不保证当前可用；搜索后读取正文，记录真实访问时间、文章日期、实际数据窗口和限制。

每平台目标10个topic/style配对候选，证据不足可少给。独立主题聚类，不用同事件多个标签或转载充数。B只表示当前窗口资料明确提及，不能证明全站排名或周增长；C为较长周期/未定日期，只作背景，不填B缺口。原帖不可读时必须标未核验；截图、作者名、音频或主页不是完整原帖观察。

## 准备和校验

先按[安装说明](../INSTALL.md)选择当前Python解释器；下列python表示该解释器。

```bash
python scripts/public_research.py prepare
```

显式日期可使用--date YYYY-MM-DD，不能指定未来截止。默认输出docs/reports/public-research/日期/run-NNN，同日不覆盖旧目录。私有配置可传--config config/local/public_research.json。

脚本只创建空白档案，状态为prepared；不会检索网页。完成实际查阅、候选和报告后更新运行状态，再校验本轮目录：

```bash
python scripts/public_research.py check docs/reports/public-research/YYYY-MM-DD/run-001
```

| 文件 | 用途 |
| --- | --- |
| config.snapshot.json | 本轮配置的固定副本 |
| run.json | 状态、窗口、观察/结束时间、三平台覆盖说明和检索记录 |
| sources.json | 真实来源、日期与访问范围/阻塞 |
| candidates.json | 候选ID、平台、topic/style、复合来源引用和证据限制 |
| report.md | 中文报告，来源链接、覆盖表及最多三个通用制作建议 |
| validation.json | check产生的档案一致性校验 |

prepared=尚未采集；三平台本周候选均够目标为completed；有有效候选但存在缺口为partial；无任何可用候选且已记录原因时为blocked。执行结束不等于覆盖完整。

校验通过后，最终报告与回复的覆盖数字使用check结果的summary；核对总数、各平台数、B/C合计以及totals_match。候选改动后重新校验，不沿用旧数字。结构校验不能证明网页真假或模型语义判断正确。

## 来源与候选字段

sources.json为数组，每条包含id、url、title、observed_at（真实带时区时间）、published_on、coverage_start/end、access_status（read/limited/blocked）、notes。未知日期为null，不把访问时间当发布日期。

candidates.json为数组，每条包含id、platform、topic、style、source_ids、evidence_grade（B/C）、period_scope、original_post_verified、rank_type和limitations。B对应week_mentioned，C对应longer_window/undated；rank_type为unranked_candidate。原帖核验为true时还需original_post_url与original_observation。自己衍生的style标为制作建议。

按同一运行目录关联run、validation、sources、candidates和report，第二步固定这五份文件和摘要。没有旧报告时从零开始；旧报告只作比较，不能替代本轮查阅。

## 检索预算、重试与交付

默认各平台先3次检索、必要时追加2次。批量工具调用里的查询逐条计数，共享查询按覆盖平台计数；不用耗尽预算。来源核查、候选筛选、写入和校验按依赖顺序执行，不要求多个Agent或新增后台服务。

在run.json.search_log记录schema_version=1及events数组，每个事件有id、platform、action（search/open）、query或url、observed_at、result（success/limited/blocked/error）、reason、retry_of、source_ids。只写实际做过的动作，不凭计划补记录。

同一受阻URL合计最多重试一次，不能换平台重置次数；登录、robots、429或工具失败不记正文已读。预算用完或访问受阻就换公开来源/平台，保留缺口；工具不可用时报告真实阻塞，不复制旧内容假装本轮采集。

普通任务交付简短结果与报告链接。若用户另行授权计划运行，仅在新有效信号、重要变化、失败或需用户处理时通知，未变则按任务设置保持安静。是否有实际任务以客户端为准，仓库没有预装自动化。
