import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
try:
    from PIL import Image
except ImportError:
    Image=None
spec=importlib.util.spec_from_file_location('convert_preview',Path(__file__).resolve().parents[1]/'scripts'/'convert_preview.py')
cp=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


@unittest.skipIf(Image is None,'Pillow missing')
class PreviewConversionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/'source.webp'
        Image.new('RGBA',(96,64),(20,80,120,110)).save(self.source,format='PNG')

    def test_convert_and_preserve_ratio_alpha(self):
        dst=self.root/'thumbnail.png'
        dims, size, fmt=cp.convert(self.source,dst,role='ck3-thumbnail',max_edge=48)
        self.assertEqual(dims,(48,32))
        self.assertEqual(fmt,'PNG')
        self.assertLess(size,1_000_000)
        with Image.open(dst) as im:self.assertEqual(im.mode,'RGBA')

    def test_jpeg_requires_explicit_matte_and_preserves_source(self):
        dst=self.root/'gallery.jpg'
        digest=self.source.read_bytes()
        with self.assertRaises(ValueError):cp.convert(self.source,dst,role='web-gallery')
        self.assertFalse(dst.exists())
        _, _, fmt=cp.convert(self.source,dst,role='web-gallery',matte='#17212A')
        self.assertEqual(fmt,'JPEG')
        self.assertEqual(self.source.read_bytes(),digest)

    def test_does_not_overwrite(self):
        dst=self.root/'gallery.png';dst.write_bytes(b'original')
        with self.assertRaises(FileExistsError):cp.convert(self.source,dst,role='web-gallery')
        self.assertEqual(dst.read_bytes(),b'original')

    def test_animated_input_rejected(self):
        src=self.root/'anim.gif';out=self.root/'preview.png'
        a=Image.new('RGB',(10,10),'red');b=Image.new('RGB',(10,10),'blue')
        a.save(src,save_all=True,append_images=[b],duration=100)
        with self.assertRaises(ValueError):cp.convert(src,out,role='ugc-primary')
        self.assertFalse(out.exists())
