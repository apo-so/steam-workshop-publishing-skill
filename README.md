# Steam Workshop Publishing Skill

面向 Codex 的创意工坊发布辅助技能，为 Mod 作者提供可审阅的发布准备、离线预览、提交前检查和发布后核验流程。通用 Steam Workshop 工作流与 CK3（Crusader Kings III）启动器专项指引分离，避免将特定游戏的上传步骤误用到其他游戏。技能默认只准备和展示，不执行任何未获明确授权的外部操作。

## 使用方式

1. 克隆本仓库或下载并解压源码 ZIP 后，将完整 `steam-workshop-publishing/` 目录放进项目的 `.agents/skills/`，或放进个人的 `~/.agents/skills/`。保持 `SKILL.md`、`references/`、`scripts/` 和 `tests/` 的相对位置不变。如果当前 Codex 版本未发现技能，核对官方技能文档并重启 Codex。
2. 在 Codex 中用 `$steam-workshop-publishing` 显式调用，说明游戏、初发或更新、希望准备的文件与检查范围。不提供密码、Steam Guard、验证码或会话凭据。
3. 审阅生成的 BBCode、离线 HTML、图片清单、版本和发布差异；核对目标条目与权限。是否执行任何实际提交或公开操作由使用者单独决定。

示例提示词：

```text
$steam-workshop-publishing
为我的 CK3 Mod 准备创意工坊更新材料，仅生成离线稿和发布前检查报告。
核对正文实际 UTF-8 字节数、封面及画廊清单，并标明待核事项。
不登录、不上传、不修改线上条目；更新 ID 不确定时保持未决。
```

## 本地检查

技能正文与参考资料无需额外依赖。可选检查脚本使用 Python 3.10+；图片检查另需已安装的 Pillow，不自动安装或联网。参见 [工具说明](steam-workshop-publishing/references/local-tools.md) 及 [验收说明](steam-workshop-publishing/references/acceptance.md)。从 `steam-workshop-publishing/` 技能目录运行 `python -m unittest discover -s tests -v` 重跑离线测试。缺少 Pillow 时图像解码相关测试将跳过，应记为未测试。

## English summary

A Codex skill for preparing, previewing, and auditing Steam Workshop mod releases and updates, with a separate CK3 launcher guide. It checks UTF-8 description budgets, preview images, release targets, and post-release evidence. Offline-first and non-submitting by default; authentication, legal acceptance, and explicit authorization remain with the user.

本项目为独立的工作流程辅助资料，不代表 Steam、Valve、Paradox 或 OpenAI 的官方产品。外部平台规则与界面以其现行文档及实际入口为准。
