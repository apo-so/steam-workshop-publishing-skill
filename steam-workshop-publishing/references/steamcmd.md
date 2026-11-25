# SteamCMD：仅适用于明确受支持的游戏

Valve 的 Workshop Implementation Guide 将 SteamCMD 创建/更新项作为开发测试集成途径介绍；不能据此声称所有游戏都提供该发布渠道。普通用户仅在对应游戏的官方创作说明明确支持其用于当前目的时考虑它；未找到支持即停在准备阶段。尤其不要假定 CK3 支持用 SteamCMD 替代 Launcher。

- 独立核对官方命令、SteamCMD 版本、游戏许可、在线连接、写权限和协议状态。SteamCMD 的登录与会话独立于桌面客户端，不设置必须打开 Steam 客户端的硬门槛。
- 若该游戏明确采用 Valve 示例式 VDF：核对 `appid`、`publishedfileid`、`contentfolder`、`previewfile`，以及确实要改的 `title`、`description`、`visibility`、`changenote` 等字段；实际必填/编码/转义以游戏工具文档为准。仅确认初发后才允许无 ID 或 0 的配置；更新必须保留已确认的非零 ID，未列字段是否保留需现场核对。VDF 可能要求本机绝对路径，作为临时本地配置保存于发布目录外，不把它或本机路径上传给公众。
- 只生成待审 VDF 与差异说明（不生成含密码或验证码的命令）。不执行自动登录、凭据注入、命令行传递密码、不记录会话。用户本人在官方客户端或 SteamCMD 的交互验证入口操作；不支持安全验证方式就停止。
- 创建/更新命令（Valve 文档称 `workshop_build_item`）是写操作，准备 VDF 不授权执行。经确认后才由支持的方式操作。成功时回读 VDF/回执的 ID 及真实页面；未知结果按通用流程先查 ID、不要重复创建。
