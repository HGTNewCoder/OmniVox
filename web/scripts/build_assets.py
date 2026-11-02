"""
Build web-ready images for the OmniVox Next.js site.

The originals in ../../assets are multi-MB photos meant for the Pi's local
display. This writes resized WebP copies (plus alarm.wav) to ../public/assets.
The JSON content in ../../json_page is read directly at build time by
lib/data.ts, so it does not need copying.

Run:  python web/scripts/build_assets.py   (or: npm run assets, from web/)
Re-run whenever you change assets/.
"""
import shutil
from pathlib import Path

from PIL import Image

WEB = Path(__file__).resolve().parent.parent
ROOT = WEB.parent
SRC = ROOT / "assets"
OUT = WEB / "public" / "assets"

MAX_WIDE = 1400   # large "big screen" photos
MAX_ICON = 256    # small icons (mood faces, bell, yes/no, card art)
QUALITY = 78


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total_in = total_out = 0
    for src in sorted(SRC.glob("*.png")):
        dst = OUT / (src.stem + ".webp")
        total_in += src.stat().st_size
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            with Image.open(src) as im:
                im.load()
                limit = MAX_WIDE if (im.width > 900 or im.height > 900) else MAX_ICON
                im.thumbnail((limit, limit), Image.Resampling.LANCZOS)
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA")
                im.save(dst, "WEBP", quality=QUALITY, method=6)
            print(f"  {src.name:28s} -> {dst.name}")
        total_out += dst.stat().st_size
    wav = SRC / "alarm.wav"
    if wav.exists():
        shutil.copy2(wav, OUT / "alarm.wav")
    print(f"Images: {total_in / 1e6:.0f} MB -> {total_out / 1e6:.1f} MB in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
