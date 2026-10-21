# 安装、检查和更新

## 1. 获取完整项目

克隆维护者提供的仓库URL，或下载ZIP后完整解压。不要只复制五个SKILL.md；技能通过项目相对路径读取文档和脚本。下载ZIP后，`.agents/skills/`应存在，即使文件管理器默认隐藏点开头的文件。

上游仓库为[zzchen95/social-media-workflow](https://github.com/zzchen95/social-media-workflow)：

```bash
git clone https://github.com/zzchen95/social-media-workflow.git
cd social-media-workflow
```

如果准备提交改进，先在GitHub Fork，再克隆自己的Fork。

## 2. 在支持本地工作的客户端打开目录

使用ChatGPT桌面端的本地项目或Codex，在仓库根目录工作。向当前聊天发送：

> 读取README和AGENTS.md，运行安装自检，再使用 $social-media-workflow 引导我开始。按当前资料和工具能做的范围推进，不启用日程或发布内容。

如果技能名未出现在当前会话，先要求读取`.agents/skills/social-media-workflow/SKILL.md`执行，必要时重新进入该项目会话。仓库存在只证明文件已获取，不证明客户端已启用对应技能或有媒体操作工具。

普通网页版/手机端不会因Git clone而获得本地技能或电脑文件访问。当前分发方式是本地项目包，不是已发布插件。

## 3. 配置本地Python（推荐3.11+）

macOS/Linux：

```bash
python3 scripts/bootstrap.py
.venv/bin/python scripts/bootstrap.py --check
```

Windows PowerShell：

```powershell
py -3 scripts/bootstrap.py
.venv\Scripts\python.exe scripts/bootstrap.py --check
```

脚本不会激活环境、改全局设置或安装剪辑器。已有`.venv`时复用；若该路径不是可识别虚拟环境则报错，不覆盖。必要依赖安装需要网络；失败会说明已完成步骤，可在恢复网络后重试。

仅检查已有文件与当前解释器、不创建环境：

```bash
python scripts/bootstrap.py --check
```

这里以及其他流程文档中的`python`表示当前环境的解释器；Windows可使用`py -3`或`.venv\Scripts\python.exe`。不必激活环境即可执行。

## 4. 首次使用与能力检查

新仓库没有账号、研究结果、原片、成片、发布记录或计划任务。让向导按目标启动公开研究或先做常青探索；没有研究就不声称基于“最新趋势”。

研究档案准备示例：

```bash
python scripts/public_research.py prepare
```

此命令只生成空白prepared目录，不会联网或产出研究；需要ChatGPT的真实搜索/读取。研究结束后运行check并核对summary，不能将prepared称完成。

实际制作前使用自己的软件/素材验证小样；转写、Computer Use、字体、编解码器和播放能力分别核实。安装包不提供或声称已验证这些能力。

默认时区与市场见`config/public_research.json`。若要私有覆盖，复制到被忽略的`config/local/public_research.json`并按需求编辑，给工具传`--config`，不要修改历史快照。日程默认关闭，只有用户明确请求才另行配置。

## 5. 更新与本地修改

普通克隆且没有待提交的共享文件改动：

```bash
git pull --ff-only
```

如有本地技能改动，先保存到个人分支，再按贡献说明同步上游；不要删除目录、重装覆盖或强制重置。运行数据目录默认不受Git管理，仍应自行备份。

## 6. 开发检查

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_share.py --full
python -m pytest -q
```

结构与测试通过不证明研究真实性、账号适配或媒体输出质量；实际工具方法需附实测范围。依赖详情见根目录requirements文件。
