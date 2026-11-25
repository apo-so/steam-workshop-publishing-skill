import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('preflight', Path(__file__).resolve().parents[1] / 'scripts' / 'preflight.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
try:
    from PIL import Image
except ImportError:
    Image = None


def ready():
    d = {k: True for k in ('item_identity_verified', 'previous_submission_resolved',
        'steam_client_running', 'steam_online_mode', 'network_available', 'community_reachable',
        'required_service_reachable', 'session_authenticated_by_user', 'account_permission_verified', 'ugc_submission_eligible',
        'game_access_verified', 'route_supported', 'current_route_limits_checked', 'package_reviewed',
        'description_reviewed', 'description_within_budget', 'media_reviewed',
        'media_within_applicable_budget', 'fields_reviewed', 'legal_status_confirmed_by_user',
        'current_review_shown', 'explicit_current_action_authorization')}
    # Fictional ID and digest; do not use as real target or actual approval.
    d.update(intent='submit', mode='update', route='ck3-launcher', appid='1158310', item_id='1',
             game='CK3', title='Synthetic fixture', version='0.0-test', action='update content',
             visibility='unchanged', update_fields=['content'], review_digest='a'*64)
    return d


class GateTests(unittest.TestCase):
    def test_steam_offline(self):
        d = ready(); d['steam_online_mode'] = False
        self.assertIn('steam_online_mode', p.gate(d)['blocking'])

    def test_no_network_prepare(self):
        self.assertEqual(p.gate({'intent':'prepare', 'network_available':False})['status'], 'offline_preparation_only')
        d = ready(); d['network_available'] = False
        self.assertIn('network_available', p.gate(d)['blocking'])

    def test_no_accelerator_required(self):
        d = ready(); d['accelerator_installed'] = False
        r = p.gate(d)
        self.assertEqual(r['blocking'], [])
        self.assertFalse(r['external_action_performed'])
        self.assertIn('human_review_required', r['status'])

    def test_update_id_unknown(self):
        for value in (None, '', '0', 1, '-1', '0001', str(2**64)):
            d = ready(); d['item_id'] = value
            self.assertIn('update_id_unknown', p.gate(d)['blocking'])

    def test_preview_only(self):
        d = ready(); d['intent'] = 'preview'
        self.assertEqual(p.gate(d)['status'], 'offline_preparation_only')
        d = ready(); d['explicit_current_action_authorization'] = False
        self.assertIn('explicit_current_action_authorization', p.gate(d)['blocking'])

    def test_unknown_service_even_online(self):
        d = ready(); d.pop('required_service_reachable')
        self.assertIn('required_service_reachable', p.gate(d)['blocking'])

    def test_uncertain_previous_submission(self):
        d = ready(); d['previous_submission_resolved'] = False
        self.assertIn('previous_submission_unresolved', p.gate(d)['blocking'])

    def test_limited_account_cannot_submit_online(self):
        d = ready(); d['ugc_submission_eligible'] = False
        self.assertIn('ugc_submission_eligible', p.gate(d)['blocking'])
        d['intent'] = 'preview'
        self.assertEqual('offline_preparation_only', p.gate(d)['status'])

    def test_existing_visible_to_owner_pending_is_not_a_new_item(self):
        d = ready(); d.update(mode='create', observed_workshop_status='moderation_pending')
        r = p.gate(d)
        self.assertIn('existing_id_on_create', r['blocking'])
        self.assertIn('existing_submission_pending', r['blocking'])
        self.assertFalse(r['external_action_performed'])
        d['observed_workshop_status'] = 'email_verification_pending'
        self.assertIn('existing_submission_pending', p.gate(d)['blocking'])

    def test_wrong_appid(self):
        d = ready(); d['appid'] = '1'
        self.assertIn('ck3_appid_mismatch', p.gate(d)['blocking'])

    def test_create_with_id(self):
        d = ready(); d['mode'] = 'create'; d['no_existing_item_verified'] = True
        self.assertIn('existing_id_on_create', p.gate(d)['blocking'])

    def test_steamcmd_independent(self):
        d = ready(); d.update(route='steamcmd', steam_client_running=False, steam_online_mode=False)
        self.assertIn('official_steamcmd_support', p.gate(d)['blocking'])
        d['official_steamcmd_support'] = True
        self.assertEqual(p.gate(d)['blocking'], [])

    def test_legal_by_user(self):
        d = ready(); d['legal_status_confirmed_by_user'] = False
        self.assertIn('legal_status_confirmed_by_user', p.gate(d)['blocking'])

    def test_budget_blocks_gate(self):
        d = ready(); d.update(description_within_budget=False, media_within_applicable_budget=False)
        r = p.gate(d)
        self.assertIn('description_within_budget', r['blocking'])
        self.assertIn('media_within_applicable_budget', r['blocking'])

    def test_permission_unknown(self):
        d = ready(); d['account_permission_verified'] = 'yes'
        self.assertIn('account_permission_verified', p.gate(d)['blocking'])


class TextTests(unittest.TestCase):
    def test_chinese_over_bytes(self):
        text, r = p.description(('中'*2667).encode())
        self.assertEqual(len(text), 2667)
        self.assertEqual(r['bytes'], 8001)
        self.assertEqual(r['status'], 'over_limit')

    def test_bom_crlf_and_markup(self):
        body = '[b]中[/b]\r\n[url=https://example.org]链接[/url]\r\n'.encode()
        text, r = p.description(p.BOM + body)
        self.assertEqual(text.encode(), body)
        self.assertEqual(r['bytes'], len(body))
        self.assertEqual(r['file_bytes'], len(body)+3)
        self.assertEqual(r['crlf_count'], 2)
        self.assertTrue(r['file_bom_removed'])

    def test_boundary(self):
        for n, status in [(7800,'within_budget'), (7801,'revise_margin'), (7999,'revise_margin'), (8000,'revise_margin'), (8001,'over_limit')]:
            self.assertEqual(p.description(b'a'*n)[1]['status'], status)

    def test_invalid_utf8_and_nul(self):
        with self.assertRaises(UnicodeDecodeError): p.description(b'\xff')
        self.assertEqual(p.description(b'a\0b')[1]['status'], 'invalid_nul')

    def test_preview_same_source_and_safe(self):
        raw = '[h1]标题[/h1]\r\n[b]<script>测试</script>[/b]\n[list][*]一[*]二[/list]\n[url=https://example.org]示例[/url]'.encode()
        doc, r = p.make_preview(raw)
        self.assertEqual(r['sha256_body'], p.description(raw)[1]['sha256_body'])
        self.assertEqual(r['preview_status'], 'approximate_subset')
        self.assertEqual(doc.count('<h1>标题</h1>'), 2)
        self.assertIn('<li>一</li>', doc)
        self.assertNotIn('<script>', doc)
        self.assertNotIn('href=', doc)
        self.assertEqual(r['explicit_link_targets'], ['https://example.org'])

    def test_unsupported_preview_visible(self):
        for s in ('[img]https://example.org/x.png[/img]', '[b]x[/i]', '[url=javascript:alert(1)]x[/url]'):
            doc, r = p.make_preview(s.encode())
            self.assertEqual(r['preview_status'], 'unsupported_or_malformed')
            self.assertIn(s, doc)


class ImageTests(unittest.TestCase):
    def test_main_budget_not_web_limit(self):
        for n in (1_000_000, 1_000_001):
            self.assertEqual(p.image_policy('primary', n)['size_status'], 'over_budget')
            self.assertEqual(p.image_policy('api-additional', n)['size_status'], 'over_budget')
            r = p.image_policy('web-gallery', n)
            self.assertEqual(r['size_status'], 'check_live_web_rules')
            self.assertFalse(r['web_limit_known'])
        self.assertEqual(p.image_policy('primary',999_999)['size_status'], 'within_budget')

    @unittest.skipIf(Image is None, 'Pillow not installed')
    def test_real_decoding_and_mismatched_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'thumbnail.png'
            Image.new('RGB', (30, 20)).save(path, format='JPEG')
            r = p.inspect_image(path, 'primary', True)
            self.assertEqual(r['decoded_format'], 'JPEG')
            self.assertEqual((r['width'], r['height']), (30, 20))
            self.assertFalse(r['extension_matches'])
            self.assertFalse(r['ck3_thumbnail_filename_and_format_match'])
            Image.new('RGB', (640, 640)).save(path, format='PNG', compress_level=0)
            r = p.inspect_image(path, 'primary', True)
            self.assertTrue(r['ck3_thumbnail_filename_and_format_match'])
            self.assertTrue(r['square_640_recommendation_met'])
            self.assertGreater(r['bytes'], 1_000_000)
            self.assertEqual(r['size_status'], 'over_budget')
            self.assertEqual(p.inspect_image(path, 'web-gallery')['size_status'], 'check_live_web_rules')

    @unittest.skipIf(Image is None, 'Pillow not installed')
    def test_corrupt_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'thumbnail.png'
            path.write_bytes(b'not a png')
            with self.assertRaises(Exception): p.inspect_image(path, 'primary', True)


if __name__ == '__main__':
    unittest.main()
