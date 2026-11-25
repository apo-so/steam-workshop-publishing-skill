#!/usr/bin/env python3
"""Offline-only Workshop review helpers. No platform calls or credentials."""
import argparse
import hashlib
import html
import json
import re
import sys
import warnings
from pathlib import Path
from urllib.parse import urlsplit

LIMIT = 8000
BUDGET = 7800
IMAGE_BUDGET = 1_000_000  # exclusive conservative budget, NOT a web gallery limit
BOM = b'\xef\xbb\xbf'


def description(raw):
    body = raw[len(BOM):] if raw.startswith(BOM) else raw
    text = body.decode('utf-8', errors='strict')  # never normalize newline/Unicode
    size = len(body)
    status = ('over_limit' if size > LIMIT else 'revise_margin' if size > BUDGET else 'within_budget')
    if '\x00' in text:
        status = 'invalid_nul'
    return text, {'bytes': size, 'file_bytes': len(raw), 'file_bom_removed': raw.startswith(BOM),
                  'sha256_body': hashlib.sha256(body).hexdigest(), 'limit_bytes': LIMIT,
                  'budget_bytes': BUDGET, 'status': status, 'crlf_count': text.count('\r\n'),
                  'lf_only_count': text.count('\n') - text.count('\r\n'),
                  'cr_only_count': text.count('\r') - text.count('\r\n')}


# Deliberately limited, strict BBCode parser. Never executes or fetches links.
TOKEN = re.compile(r'\[([^\[\]\r\n]+)\]')
TAGS = {'h1': 'h1', 'h2': 'h2', 'h3': 'h3', 'b': 'strong', 'i': 'em', 'u': 'u',
        'strike': 's', 'list': 'ul', 'olist': 'ol', 'hr': 'hr', 'url': 'span'}


def parse(text):
    root = ['root', None, []]
    stack = [root]
    links = []
    pos = 0
    for match in TOKEN.finditer(text):
        stack[-1][2].append(text[pos:match.start()])
        pos = match.end()
        spec = match.group(1)
        if spec == '*':
            if stack[-1][0] == 'li':
                stack.pop()
            if stack[-1][0] not in {'list', 'olist'}:
                raise ValueError('list marker outside list')
            node = ['li', None, []]
            stack[-1][2].append(node)
            stack.append(node)
            continue
        if spec.startswith('/'):
            name = spec[1:]
            if name in {'list', 'olist'} and stack[-1][0] == 'li':
                stack.pop()
            if len(stack) == 1 or stack[-1][0] != name:
                raise ValueError('mismatched closing tag: ' + name)
            stack.pop()
            continue
        name, sep, arg = spec.partition('=')
        if name not in TAGS or (sep and name != 'url') or (name == 'url' and not sep):
            raise ValueError('unsupported tag or bracket syntax: ' + spec)
        if stack[-1][0] in {'list', 'olist'}:
            raise ValueError('list needs [*] before content')
        if name == 'url':
            if any(ord(c) < 33 or ord(c) == 127 for c in arg):
                raise ValueError('invalid URL syntax')
            target = urlsplit(arg)
            if target.scheme not in {'http', 'https'} or not target.hostname or target.username or target.password:
                raise ValueError('URL must be an explicit HTTP(S) link without credentials')
            links.append(arg)
        node = [name, arg if sep else None, []]
        stack[-1][2].append(node)
        stack.append(node)
        if len(stack) > 64:
            raise ValueError('nesting too deep')
    stack[-1][2].append(text[pos:])
    if len(stack) != 1:
        raise ValueError('unclosed BBCode tag')
    return root, links


def render_node(node):
    if isinstance(node, str):
        return html.escape(node)
    name, arg, children = node
    if name in {'list', 'olist'} and any(isinstance(c, str) and c.strip() for c in children):
        raise ValueError('list text outside [*] item')
    content = ''.join(render_node(c) for c in children)
    if name == 'root':
        return content
    if name == 'hr':
        if content.strip():
            raise ValueError('hr must be empty')
        return '<hr>'
    if name == 'url':
        return '<span class="link" title="' + html.escape(arg, quote=True) + '">' + content + '</span>'
    tag = 'li' if name == 'li' else TAGS[name]
    return f'<{tag}>{content}</{tag}>'


def make_preview(raw):
    text, report = description(raw)
    links = []
    try:
        tree, links = parse(text)
        rendered = render_node(tree)
        report['preview_status'] = 'approximate_subset'
        notice = '离线近似预览；不等同 Steam 实际渲染。链接不可点击，需人工核对。'
    except ValueError as exc:
        rendered = html.escape(text)
        report['preview_status'] = 'unsupported_or_malformed'
        report['preview_error'] = str(exc)
        links = []
        notice = '含未支持或不匹配的语法，以下仅显示完整原文。必须人工核查后再定稿。'
    # No external links, scripts, fonts, or images. Both panes use the same source.
    report['explicit_link_targets'] = links
    targets = ''.join('<li>' + html.escape(u) + '</li>' for u in links)
    doc = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
           '<title>Workshop 离线审稿</title><style>body{background:#eef0f2;color:#20252b;font:16px/1.65 system-ui,sans-serif;margin:20px}'
           'article{box-sizing:border-box;max-width:100%;padding:20px;background:white;margin:12px 0 30px;border:1px solid #aaa;overflow-wrap:anywhere;white-space:pre-wrap}'
           'h1,h2,h3{line-height:1.25;margin:.3em 0}ul,ol{padding-left:1.6em;margin:0}.link{color:#14558a;text-decoration:underline}'
           'pre,li{overflow-wrap:anywhere;white-space:pre-wrap}</style></head><body><h1>Workshop 离线审稿</h1><p>'
           + html.escape(notice) + '</p><p>正文 UTF-8 字节：' + str(report['bytes']) + '；源 SHA-256：' + report['sha256_body']
           + '</p><h2>桌面参考（860 px）</h2><article style="width:860px">' + rendered
           + '</article><h2>手机参考（390 px）</h2><article style="width:390px">' + rendered
           + '</article><h2>显式 URL 目标（离线，未验证可达性）</h2><ul>' + targets
           + '</ul><h2>原始正文</h2><pre>' + html.escape(text) + '</pre></body></html>')
    return doc, report


def image_policy(role, size):
    if role == 'web-gallery':
        return {'size_status': 'check_live_web_rules', 'web_limit_known': False,
                'conservative_reference_bytes': IMAGE_BUDGET, 'above_reference': size >= IMAGE_BUDGET}
    if role not in {'primary', 'api-additional'}:
        raise ValueError('unsupported image role')
    return {'size_status': 'within_budget' if size < IMAGE_BUDGET else 'over_budget',
            'exclusive_budget_bytes': IMAGE_BUDGET}


def inspect_image(path, role, ck3_thumbnail=False):
    from PIL import Image  # optional, no auto-install
    if ck3_thumbnail and role != 'primary':
        raise ValueError('CK3 thumbnail flag only applies to primary')
    raw = path.read_bytes()
    import io
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(raw)) as im:
            fmt, dims = im.format, im.size
            im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            for frame in range(getattr(im, 'n_frames', 1)):
                im.seek(frame)
                im.load()
    extensions = {'PNG': {'.png'}, 'JPEG': {'.jpg', '.jpeg'}, 'GIF': {'.gif'}}
    suffix = path.suffix.lower()
    known = fmt in extensions
    report = {'role': role, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
              'decoded_format': fmt, 'width': dims[0], 'height': dims[1],
              'extension_matches': suffix in extensions[fmt] if known else None,
              'format_status': 'suggested_api_format' if known else 'check_channel_format',
              'visual_review': 'manual_required', **image_policy(role, len(raw))}
    if ck3_thumbnail:
        report['ck3_thumbnail_filename_and_format_match'] = path.name == 'thumbnail.png' and fmt == 'PNG'
        report['square_640_recommendation_met'] = dims == (640, 640)
    return report


def positive_id(value, bits):
    return isinstance(value, str) and re.fullmatch(r'[1-9][0-9]*', value) is not None and len(value) <= 20 and int(value) < 2**bits


def gate(d):
    """Evaluate self-reported facts ONLY. Never grants authority, never submits."""
    reasons = []
    def require(flag):
        if d.get(flag) is not True:
            reasons.append(flag)
    intent = d.get('intent')
    if intent != 'submit':
        return {'status': 'offline_preparation_only', 'blocking': ['no_submit_intent'], 'external_action_performed': False}
    for field in ('game', 'title', 'version', 'action'):
        if not isinstance(d.get(field), str) or not d[field].strip():
            reasons.append('missing_' + field)
    if not positive_id(d.get('appid'), 32):
        reasons.append('invalid_appid')
    if d.get('visibility') not in {'private', 'friends-only', 'public', 'unlisted', 'unchanged'}:
        reasons.append('visibility_unknown')
    if not isinstance(d.get('update_fields'), list) or not d['update_fields'] or not all(isinstance(x, str) and x.strip() for x in d['update_fields']):
        reasons.append('update_fields_unknown')
    if not isinstance(d.get('review_digest'), str) or not re.fullmatch(r'[0-9a-f]{64}', d['review_digest']):
        reasons.append('review_digest_missing')
    if d.get('mode') == 'update':
        if not positive_id(d.get('item_id'), 64):
            reasons.append('update_id_unknown')
        require('item_identity_verified')
    elif d.get('mode') == 'create':
        if d.get('item_id') not in (None, '', '0'):
            reasons.append('existing_id_on_create')
        require('no_existing_item_verified')
    else:
        reasons.append('mode_unknown')
    if d.get('previous_submission_resolved') is not True:
        reasons.append('previous_submission_unresolved')
    route = d.get('route')
    if route in {'ck3-launcher', 'game-client'}:
        for flag in ('steam_client_running', 'steam_online_mode'):
            require(flag)
    elif route == 'steamcmd':
        require('official_steamcmd_support')  # no desktop client requirement
    elif route == 'web-editor':
        if d.get('mode') != 'update':
            reasons.append('web_editor_requires_existing_item')
    else:
        reasons.append('route_unconfirmed')
    if route == 'ck3-launcher' and d.get('appid') != '1158310':
        reasons.append('ck3_appid_mismatch')
    for flag in ('network_available', 'community_reachable', 'required_service_reachable',
                 'session_authenticated_by_user', 'account_permission_verified', 'game_access_verified',
                 'route_supported', 'current_route_limits_checked', 'package_reviewed',
                 'description_reviewed', 'description_within_budget', 'media_reviewed',
                 'media_within_applicable_budget', 'fields_reviewed', 'legal_status_confirmed_by_user',
                 'current_review_shown', 'explicit_current_action_authorization'):
        require(flag)
    return {'status': 'hold_external_action' if reasons else 'self_reported_checks_complete_human_review_required',
            'blocking': reasons, 'external_action_performed': False,
            'note': 'Input assertions only; independently verify evidence, target and fresh authorization. Not permission to submit.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('description'); a.add_argument('source', type=Path)
    a = sub.add_parser('preview'); a.add_argument('source', type=Path); a.add_argument('output', type=Path)
    a = sub.add_parser('image'); a.add_argument('source', type=Path); a.add_argument('--role', required=True, choices=['primary', 'api-additional', 'web-gallery']); a.add_argument('--ck3-thumbnail', action='store_true')
    a = sub.add_parser('gate'); a.add_argument('facts', type=Path)
    args = p.parse_args()
    try:
        if args.command == 'description':
            _, result = description(args.source.read_bytes())
        elif args.command == 'preview':
            doc, result = make_preview(args.source.read_bytes())
            # Refuse overwrite of any existing file, including source.
            with args.output.open('x', encoding='utf-8', newline='') as out:
                out.write(doc)
        elif args.command == 'image':
            result = inspect_image(args.source, args.role, args.ck3_thumbnail)
        else:
            facts = json.loads(args.facts.read_text(encoding='utf-8-sig'))
            if not isinstance(facts, dict):
                raise ValueError('gate facts must be a JSON object')
            result = gate(facts)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        needs_attention = (result.get('status') in {'over_limit', 'revise_margin', 'invalid_nul', 'hold_external_action', 'offline_preparation_only'}
                           or result.get('preview_status') == 'unsupported_or_malformed'
                           or result.get('size_status') != 'within_budget' and args.command == 'image'
                           or result.get('extension_matches') is False or result.get('format_status') == 'check_channel_format'
                           or result.get('ck3_thumbnail_filename_and_format_match') is False)
        return 2 if needs_attention else 0
    except Exception as exc:
        # Do not print paths or potentially sensitive raw input in error messages.
        print(json.dumps({'error': type(exc).__name__, 'status': 'not_checked'}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
