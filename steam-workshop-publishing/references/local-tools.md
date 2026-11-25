# 本地检查工具

`python` 指 Python 3.10+（某些系统命令为 `python3`）。从技能目录运行。所有命令只读取显式指定的本地输入，或新建离线 HTML；不访问网络、不登录、不上传、不执行游戏或平台命令。不要将真实发布材料或账号信息提交到技能仓库。图像解码需要已安装 Pillow；工具不自动安装依赖。源文件必须由用户授权读取。

## 正文字节与同源预览

```shell
python scripts/preflight.py description description.bbcode
python scripts/preflight.py preview description.bbcode review.html
```

`description` 报告 UTF-8 正文字节数、文件字节数、是否去除起始 BOM、真实行尾计数、正文 SHA-256。严格 UTF-8 解码，拒绝无效编码；NUL 字符视为无效。`within_budget` 表示不超过 7800；7801–8000 为 `revise_margin`；大于 8000 为 `over_limit`。预算不是平台实测。`preview` 使用同一正文、同一哈希，生成桌面/手机参考宽度的近似预览及转义后的原文，拒绝覆盖既有输出（包括源文件）。HTML 不加载任何外部图片、字体、脚本或链接；明确的 URL 仅显示为文字与提示，链接可达性需现场验证。

支持小范围 BBCode：配对 `h1/h2/h3`、`b/i/u/strike`、`list/olist`（`[*]` 项）、`hr`（空配对）、`url=https://...`（或 http）。遇不支持的标签、带方括号的未知语法、错配、嵌入媒体等时报告 `unsupported_or_malformed`，显示原文而非静默丢弃。并非完整 Steam 解析器，自动嵌入、复杂排版、裸 URL 与最终浏览器效果须人工检查。即使状态为 `approximate_subset` 也不表示 Steam 一定支持或显示一致；手机/桌面外观、图片和链接由人工确认。

## 预览图转换

```shell
python scripts/convert_preview.py cover.webp thumbnail.png --role ck3-thumbnail --max-edge 640
python scripts/convert_preview.py frame.png gallery.jpg --role web-gallery --max-edge 1600 --matte "#17212A"
```

工具离线读取静态图片，按需等比缩小（不放大），明确生成新的 PNG/JPEG，不通过改后缀冒充转换。PNG 可保留透明；JPEG 需要为透明背景显式选定底色。工具移除 EXIF 等源元数据，并拒绝多帧输入、过大的解码图片及覆盖已有文件；转换后应人工核对色彩、裁切与文字。CK3 主图和 API 图片使用本地低于 1,000,000 字节的保守预算；网页画廊仍需当场核对。不会上传。用下方命令复查输出后，再按所选渠道走已获授权的上传步骤。

## 图片

```shell
python scripts/preflight.py image thumbnail.png --role primary --ck3-thumbnail
python scripts/preflight.py image gallery.png --role api-additional
python scripts/preflight.py image gallery.png --role web-gallery
```

工具读取文件实际字节，使用 Pillow 校验并解码图像，报告 SHA-256、真实编码、尺寸、扩展名匹配情况（常用 API 建议格式 JPG/PNG/GIF）、体积状态。其他实际编码需要按渠道确认。`--ck3-thumbnail` 仅适用于 CK3 主图，另外检查 `thumbnail.png` 与 PNG 编码是否一致、是否符合可选 640×640 建议。所有图片仍需放大人工检查内容、文字可读性、权利与隐私；图像解码不保证平台兼容。

- `primary` 和 `api-additional`：小于 1000000 字节才在保守预算内；`api-additional` 同时适用于 API 追加与替换图片。
- `web-gallery`：总是返回 `check_live_web_rules`，无论大小；`above_reference` 仅指是否达到自愿参考预算。即使 1MB 以上也不是判定网页一定拒收。
- 缺少 Pillow、损坏文件、过大解码风险等返回未完成检查；不要自动安装或跳过。

## 门禁（仅评估声明，不是上传授权）

可创建一个本地 JSON（放在发布目录外），从保守的最小输入开始：

```json
{
  "intent": "preview",
  "game": "CK3",
  "appid": "1158310",
  "route": "ck3-launcher",
  "mode": "update",
  "item_id": null,
  "network_available": false,
  "explicit_current_action_authorization": false
}
```

```shell
python scripts/preflight.py gate review-facts.json
```

只有 `intent: "submit"` 会评估所有提交前的声明；其他意图总是 `offline_preparation_only`（允许继续离线准备，并非本地工作失败）。所有布尔前提都必须是真正的 JSON `true`；缺失、null、false、字符串等视为未核实。不要把下面字段复制为一整套 true 来冒充事实。

| 字段 | 填写规则 |
|---|---|
| `intent`, `game`, `title`, `version`, `action` | 当前意图、游戏、目标名称、待发布版本、明确具体动作；`action` 不代替人工核对动作范围 |
| `appid`, `mode`, `item_id` | AppID 与 item ID 用十进制字符串（防止大整数精度损失）；`create` 或 `update`；初发 ID 可缺失/空/字符串 0，更新须非零 |
| `item_identity_verified`, `no_existing_item_verified`, `previous_submission_resolved` | 更新身份交叉确认 / 初发没有对应条目已核 / 无未解决的上次提交；根据模式要求相应字段 |
| `observed_workshop_status` | 可选记录当场观察到的状态；`email_verification_pending` 或 `moderation_pending` 会阻止再次提交，先保留 ID 并处理原状态 |
| `route`, `route_supported`, `official_steamcmd_support` | `ck3-launcher`、`game-client`、`steamcmd` 或 `web-editor`（仅既有条目的编辑）；渠道经验证支持当前动作；SteamCMD 另要求游戏官方支持 |
| `steam_client_running`, `steam_online_mode` | 仅 CK3 / 游戏客户端路线检查；SteamCMD 不以运行桌面客户端为条件 |
| `network_available`, `community_reachable`, `required_service_reachable` | 网络、Steam 社区及该动作需要的服务实际可达；仅连通网络不能证明后两项 |
| `session_authenticated_by_user`, `account_permission_verified`, `ugc_submission_eligible`, `game_access_verified` | 用户本人已完成认证、对应写权限、账号无创意工坊投稿限制和适用游戏资格均已核；不传凭据 |
| `visibility`, `update_fields` | `private` / `friends-only` / `public` / `unlisted` / `unchanged`（以入口真实支持为准）；非空字段列表，由人工确认保留和改动差异 |
| `package_reviewed`, `description_reviewed`, `description_within_budget` | 内容白名单与哈希/路径/秘密已人工核查、正文已审、正文满足字节预算 |
| `media_reviewed`, `media_within_applicable_budget`, `current_route_limits_checked` | 图像与角色已核、符合对应渠道预算、当场核查入口限制；无媒体变更需确认旧媒体保留，不能用 API 限制替代网页上限 |
| `fields_reviewed`, `legal_status_confirmed_by_user` | 差异和保留项已确认；用户本人处理协议并确认当前状态 |
| `review_digest`, `current_review_shown`, `explicit_current_action_authorization` | 最终审核材料（含目标、动作、字段差异、内容/正文/媒体哈希、可见性）确定性序列化后计算 SHA-256；显示给用户并重新核对；用户明确授权当前动作和该版本。脚本仅检查摘要格式及声明，不计算或验证材料绑定，不代替授权。 |

结果 `hold_external_action` 表示至少一个声明缺失；`self_reported_checks_complete_human_review_required` 只表示输入条件形式上齐备，仍需独立证据与人工确认，**不是允许提交**。所有结果的 `external_action_performed` 均为 false。工具没有提交接口。加速器不属于门禁字段。

## 退出码与验收

- 0：本地检查未触发该命令的预算/格式/门禁警告；不表示 Steam 接受或可发布。
- 2：需要注意（如预算、未知网页规则、格式异常、仅预览意图或缺少提交前事实）；应按 JSON 状态处理，不影响继续离线准备。
- 1：运行/输入错误；结果未核查。命令行参数错误由 argparse 返回 2。

回归测试：`python -m unittest discover -s tests -v`。测试只使用合成正文、图像和声明，不存在真实 Mod、实际账号或在线条目。门禁输入与输出只能作为审阅辅助；内容包人工核查、实际平台权限和发布后证据不由脚本自动完成。
