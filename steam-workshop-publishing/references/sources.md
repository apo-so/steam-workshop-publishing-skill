# 来源与证据边界

文档核对日期：2026-11-24。以下为公开资料核查，不是平台实际发布测试。后续使用时重新打开适用来源并确认当前 UI，发现差异记入修订记录。技能中的保守预算、建议尺寸、审稿和安全门禁属于工作约定，不冒充 Valve 或游戏的统一强制政策。

| 规则 | 来源与定位 | 能证明的范围 / 不能证明的范围 |
|---|---|---|
| 8000 字节 | Valve [ISteamRemoteStorage — Constants](https://partner.steamgames.com/doc/api/ISteamRemoteStorage#k_cchPublishedDocumentDescriptionMax)，常量 `k_cchPublishedDocumentDescriptionMax`；[ISteamUGC — SetItemDescription](https://partner.steamgames.com/doc/api/ISteamUGC#SetItemDescription) 引用该常量 | Workshop API 描述长度以字节为单位。默认 7800 是本技能留余量的约定；UTF-8 BOM 和行尾处理是本地文件计数规则；不能承诺各编辑器边界行为或终止符细节。 |
| 主图 | Valve [ISteamUGC — SetItemPreview](https://partner.steamgames.com/doc/api/ISteamUGC#SetItemPreview)；[SubmitItemUpdateResult_t](https://partner.steamgames.com/doc/api/ISteamUGC#SubmitItemUpdateResult_t) 的 `k_EResultLimitExceeded` | 前者定义主预览图与建议格式（JPG/PNG/GIF）、Cloud 配额；该段未写 1MB 数值。后者明确预览图需小于 1 Megabyte，Cloud 空间不足也可导致同类错误。不能把接口建议格式视为某游戏入口的格式白名单。 |
| API 新增预览图 | Valve [ISteamUGC — AddItemPreviewFile](https://partner.steamgames.com/doc/api/ISteamUGC#AddItemPreviewFile) | 追加图片小于 1MB；不是网页画廊条款。 |
| API 替换预览图 | Valve [ISteamUGC — UpdateItemPreviewFile](https://partner.steamgames.com/doc/api/ISteamUGC#UpdateItemPreviewFile) | 替换额外图片也小于 1MB；不等同网页上传。 |
| 网页画廊 | 本次未找到适用于 Steam 网页 Workshop 画廊的一般官方文件大小上限 | 未知；现场核查。API 预算严格低于 1000000 字节，以避免单位解释与边界差异；网页可自愿参考但不作硬性限制。 |
| 创建、更新、回执、协议 | Valve [Workshop Implementation Guide](https://partner.steamgames.com/doc/features/workshop/implementation)，Creating a Workshop Item / Uploading a Workshop Item / Workshop Legal Agreement | 游戏 AppID、保存 PublishedFileId、提交回调和协议检查；未经同意的可见性不能推定。未确认的上传必须回读。 |
| SteamCMD | 同一 [Implementation Guide — SteamCmd Integration](https://partner.steamgames.com/doc/features/workshop/implementation#SteamCmd_Integration) | Valve 将其作为测试集成，说明 VDF 及初发/更新 ID 语义；不是所有游戏的通用用户上传承诺。 |
| 离线模式 | [Steam Support — Offline Mode](https://help.steampowered.com/en/faqs/view/0E18-319B-E34B-B2C8) | 本次直接页面正文仅返回图像占位，但公开搜索索引返回 FAQ 正文，明确需要连接的客户端功能在离线模式不可用。连通性必须现场检查。 |
| 受限账户与投稿 | [Steam 受限账户说明](https://help.steampowered.com/en/faqs/view/71d3-35c2-ad96-aa3a) | 受限账户不能投稿。Steam 按符合条件的支出判定，不以能否玩某款游戏判定；本指南不要求为检查而消费。 |
| 验证与审核 | [Steam 投稿审核说明](https://help.steampowered.com/en/wizard/HelpWithUGCSubmission) | 部分用户需验证邮箱；某些社区中心审核完成前作者仍可见，而订阅者可能保留上一核准版。不是对任意条目的当前状态或审核时长保证。 |
| BBCode | [Steam Community — Text Formatting](https://steamcommunity.com/comment/ForumTopic/formattinghelp) | 公共格式说明，包括标题、加粗、链接和列表等；不同 Workshop UI 的最终渲染仍需核对。 |
| CK3 AppID | [Steam 商店 — Crusader Kings III](https://store.steampowered.com/app/1158310/Crusader_Kings_III/) | AppID 1158310 及 Workshop 功能；不证明任意上传入口可用。 |
| CK3 启动器步骤 | 社区 Wiki [Modding](https://ck3.paradoxwikis.com/Modding) 原站 401；公开 [镜像：Modding](https://github.com/jesec/ck3-modding-wiki/blob/master/wiki_pages/Modding.md) 的 Uploading/updating a mod 章节可读 | 社区参考支持 Mod library / Upload Mod / 选择平台 / thumbnail.png / 初发私有的既有描述；非当前官方逐屏保证。不能实测确认按钮、自动覆盖、初发可见性。 |
| CK3 绑定与元数据 | 社区 Wiki [Mod structure](https://ck3.paradoxwikis.com/Mod_structure) 原站 401；[公开镜像](https://github.com/jesec/ck3-modding-wiki/blob/master/wiki_pages/Mod_structure.md) 的 Keys 表可读；[社区文档](https://github.com/CK3-Modding/Documentation/blob/master/docs/fundamentals/folder-structure.md) | 支持 `remote_file_id`、`thumbnail.png`、旁置 `.mod` 与内容目录的区分；具体版本的写回方式需现场确认。640×640 仅设计建议。 |
| Codex 技能 | OpenAI [Build skills](https://developers.openai.com/codex/skills)，当前重定向至 [ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills) | `SKILL.md` YAML、`name` / `description`、`.agents/skills` 发现路径及 `$` 显式调用；未在真实 Codex 会话加载测试。 |

## 无法由静态文档确认的现场事实

当前游戏/启动器版本和界面、当前账号权限及许可证、平台条款接受状态、服务可达性、网页画廊的即时限制、提交后页面/订阅副本、具体 Mod 的兼容性及依赖。所有这些须按实际目标获取证据，而非由示例推定。当前包没有任何真实账号或作品的数据。
