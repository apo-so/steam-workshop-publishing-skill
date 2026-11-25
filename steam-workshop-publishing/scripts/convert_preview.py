"""Convert a user-selected static preview image. Offline; never uploads."""
import argparse, io, re, sys, warnings
from pathlib import Path


def convert(source, output, *, role, max_edge=None, matte=None, quality=90):
    from PIL import Image, ImageOps
    source, output = Path(source), Path(output)
    ext = output.suffix.lower()
    if ext not in ('.png', '.jpg', '.jpeg'):
        raise ValueError('output extension must be .png, .jpg or .jpeg')
    if not 1 <= quality <= 95 or (max_edge is not None and not 1 <= max_edge <= 4096):
        raise ValueError('quality must be 1–95; max-edge must be 1–4096')
    if matte is not None and not re.fullmatch(r'#[0-9a-fA-F]{6}', matte):
        raise ValueError('matte must be an explicit #RRGGBB color')
    if output.exists() or source.resolve() == output.resolve():
        raise FileExistsError('refusing to overwrite existing image')
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(source) as opened:
            if getattr(opened, 'n_frames', 1) != 1:
                raise ValueError('animated or multi-page image: export a chosen frame separately')
            if opened.width * opened.height > 40_000_000:
                raise ValueError('source exceeds local safety limit of 40 megapixels')
            im = ImageOps.exif_transpose(opened).convert('RGBA')
            im.info.clear()
    if max_edge:
        im.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    opaque = im.getchannel('A').getextrema() == (255, 255)
    if ext == '.png':
        target = im.convert('RGB') if opaque else im
        target.info.clear()
        cfg = {'format': 'PNG', 'optimize': True}
    else:
        if not opaque and matte is None:
            raise ValueError('JPEG cannot preserve transparency; choose PNG or provide --matte')
        if opaque:
            target = im.convert('RGB')
        else:
            target = Image.new('RGB', im.size, matte)
            target.paste(im, mask=im.getchannel('A'))
        target.info.clear()
        cfg = {'format': 'JPEG', 'quality': quality, 'optimize': True}
    buf = io.BytesIO()
    target.save(buf, **cfg)
    data = buf.getvalue()
    if role in ('ugc-primary', 'ugc-additional', 'ck3-thumbnail') and len(data) >= 1_000_000:
        raise ValueError('preview reaches the local 1,000,000-byte budget; choose a smaller --max-edge or JPEG quality')
    if role == 'ck3-thumbnail' and (output.name != 'thumbnail.png' or ext != '.png'):
        raise ValueError('CK3 launcher preview must be prepared as thumbnail.png')
    with Image.open(io.BytesIO(data)) as check:
        check.load()
        if check.format != cfg['format'] or check.size != target.size:
            raise ValueError('encoded preview could not be validated')
    with output.open('xb') as f:
        f.write(data)
    return target.size, len(data), cfg['format']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source'); parser.add_argument('output')
    parser.add_argument('--role', choices=('ugc-primary','ugc-additional','ck3-thumbnail','web-gallery'), required=True)
    parser.add_argument('--max-edge', type=int)
    parser.add_argument('--matte')
    parser.add_argument('--quality', type=int, default=90)
    a=parser.parse_args()
    try:
        size, n, kind=convert(a.source,a.output,role=a.role,max_edge=a.max_edge,matte=a.matte,quality=a.quality)
    except (ValueError,OSError,ImportError,Warning) as exc:
        print(str(exc),file=sys.stderr);return 1
    print(f'{kind} {size[0]}×{size[1]} / {n} bytes; local conversion only, not uploaded.')
    if a.role=='web-gallery':
        print('Verify the actual Steam web editor limits before uploading.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
