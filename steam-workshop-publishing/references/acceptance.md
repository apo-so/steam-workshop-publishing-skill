# 离线验收与上线边界

从技能目录运行 `python -m unittest discover -s tests -v`。以下是可复跑的离线回归用例及期望，不是 Steam 或 CK3 运行实测。

| 用例 | 预期行为 | 自动测试 |
|---|---|---|
| 客户端离线但有网络 | 启动器提交阻断；离线准备继续 | `test_steam_offline` |
| 无网络 | 不阻断本地稿件；提交阻断 | `test_no_network_prepare` |
| 有网络且服务可达、未装加速器 | 不因加速器缺失而阻断；仍不实际提交 | `test_no_accelerator_required` |
| 更新 ID 未知、无效、超出 uint64 | 停止更新；不改初发 | `test_update_id_unknown` |
| 主图超 1000000、追加图预算、网页画廊 | 主图/API 图超预算；网页始终待现场确认，不推出硬性上限 | `test_main_budget_not_web_limit`, `test_real_decoding_and_mismatched_suffix` |
| 中文正文 2667 个三字节字符 | 8001 字节，超限（不能用字符数代替） | `test_chinese_over_bytes` |
| 只要求预览，即使形式上其他条件齐备 | 永远只准备；没有实际动作 | `test_preview_only` |
| BOM、标签、URL、CRLF、边界和错误编码 | 只扣起始 BOM；实际换行与标记计数；边界留余量；无效数据不放行 | `test_bom_crlf_and_markup`, `test_boundary`, `test_invalid_utf8_and_nul` |
| BBCode 与离线 HTML 同源、转义、未知标签 | 相同正文哈希；不执行 HTML 或链接；未知标签显示原文、标待核 | `test_preview_same_source_and_safe`, `test_unsupported_preview_visible` |
| PNG 扩展名但 JPEG 编码；无效 PNG | 实际解码识别，不靠扩展名；无效文件失败 | `test_real_decoding_and_mismatched_suffix`, `test_corrupt_png` |
| 提交结果未决、服务未知、AppID 错、初发已有 ID | 阻断并要求真实证据，不自动重试 | `test_uncertain_previous_submission`, `test_unknown_service_even_online`, `test_wrong_appid`, `test_create_with_id` |
| SteamCMD 仅官方支持且独立会话 | 未证支持阻断；桌面 Steam 未运行不独立构成该渠道阻断 | `test_steamcmd_independent` |
| 权限未知、协议未确认、预算未通过 | 阻断；协议由用户本人处理 | `test_permission_unknown`, `test_legal_by_user`, `test_budget_blocks_gate` |

本次运行记录见 [test-results.md](test-results.md)。

## 真实环境仍需验收

1. 将技能目录安装到目标 Codex 版本，确认发现和显式/隐式触发。验证只预览提示不会触发写操作；测试提示不得包含实际提交授权。
2. 在真实 CK3 启动器版本中由用户核实入口、绑定回写、初发可见性及格式限制；读取官方现行说明，记录版本和截图。其他游戏分别核对，网页画廊限制现场确认。
3. 在任何真正的发布中，依权限与明确授权逐动作确认，并独立保存三层证据。不在技能验收中创建测试条目或实际提交。

自动回归证明本地实现对合成输入的行为，不能证明模型在任意工具环境必然遵守指令，也不能证明平台连通、真实账号权限或服务接受。发布门禁必须人工复核。
