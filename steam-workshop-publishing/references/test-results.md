# 本地验收记录

核查日期：2026-11-24。测试环境：Python 3.13.5、Pillow 12.3.0；技能 YAML 使用 PyYAML 6.0.3 解析。回归测试 22 项全部通过，无跳过；另实际运行 7 次 CLI 合成用例并通过（字节检查、同源预览、拒绝覆盖输出和源文件、超字节检查、离线预览门禁、未知更新 ID 门禁）。技能名称与目录一致，描述长度符合常规 Agent Skills 约束，包内 Markdown 相对引用均存在。没有使用真实发布材料、登录、创建条目或上传。

重跑回归：

```shell
python -m unittest discover -s tests -v
```

回归输出：

```text
test_budget_blocks_gate (test_preflight.GateTests.test_budget_blocks_gate) ... ok
test_create_with_id (test_preflight.GateTests.test_create_with_id) ... ok
test_legal_by_user (test_preflight.GateTests.test_legal_by_user) ... ok
test_no_accelerator_required (test_preflight.GateTests.test_no_accelerator_required) ... ok
test_no_network_prepare (test_preflight.GateTests.test_no_network_prepare) ... ok
test_permission_unknown (test_preflight.GateTests.test_permission_unknown) ... ok
test_preview_only (test_preflight.GateTests.test_preview_only) ... ok
test_steam_offline (test_preflight.GateTests.test_steam_offline) ... ok
test_steamcmd_independent (test_preflight.GateTests.test_steamcmd_independent) ... ok
test_uncertain_previous_submission (test_preflight.GateTests.test_uncertain_previous_submission) ... ok
test_unknown_service_even_online (test_preflight.GateTests.test_unknown_service_even_online) ... ok
test_update_id_unknown (test_preflight.GateTests.test_update_id_unknown) ... ok
test_wrong_appid (test_preflight.GateTests.test_wrong_appid) ... ok
test_corrupt_png (test_preflight.ImageTests.test_corrupt_png) ... ok
test_main_budget_not_web_limit (test_preflight.ImageTests.test_main_budget_not_web_limit) ... ok
test_real_decoding_and_mismatched_suffix (test_preflight.ImageTests.test_real_decoding_and_mismatched_suffix) ... ok
test_bom_crlf_and_markup (test_preflight.TextTests.test_bom_crlf_and_markup) ... ok
test_boundary (test_preflight.TextTests.test_boundary) ... ok
test_chinese_over_bytes (test_preflight.TextTests.test_chinese_over_bytes) ... ok
test_invalid_utf8_and_nul (test_preflight.TextTests.test_invalid_utf8_and_nul) ... ok
test_preview_same_source_and_safe (test_preflight.TextTests.test_preview_same_source_and_safe) ... ok
test_unsupported_preview_visible (test_preflight.TextTests.test_unsupported_preview_visible) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.047s

OK

```

边界：上述为本地代码及合成输入的结果；尚未在真实 Codex 会话加载技能或实际运行游戏启动器、访问登录态页面、验证上传服务及订阅副本。网页画廊限制与当前 CK3 上传界面待现场确认。
