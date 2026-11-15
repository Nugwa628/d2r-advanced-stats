"""D2R file helpers of the Stat Book tools: read and write D2R's .sprite files (version 31, RGBA), the
half-size .lowend copy, and D2R's layout JSON (// comments, trailing commas). Copied from the D2R-XL 2012
tools by its tools/export_statbook.py; edit them there."""
import json
import re
import struct
from pathlib import Path

from PIL import Image


# from tools/dc6.py

HEADER = 40


def sprite_bytes(frame_width: int, strip_width: int, height: int, frames: int, rgba: bytes) -> bytes:
    return b"SpA1" + struct.pack("<HHIIIIIIII", 31, frame_width, strip_width, height, 0, frames, 0, 0,
                                 len(rgba), 4) + rgba


def sprite_info(path: Path) -> dict:
    d = Path(path).read_bytes()
    if d[:4] != b"SpA1" or len(d) < HEADER:
        raise ValueError(f"{path}: not a sprite")
    ver, fw, sw, h, _z, frames = struct.unpack_from("<HHIIII", d, 4)
    size = struct.unpack_from("<I", d, 32)[0]
    return {"version": ver, "frame_width": fw, "strip_width": sw, "height": h, "frames": frames,
            "data_size": size, "file_size": len(d)}


# from tools/ui_art.py


def read_sprite(path: Path) -> list[Image.Image]:
    """Frames of a D2R .sprite (version 31, RGBA) as images (frame width from the header, stride = strip width / frames)."""
    info = sprite_info(path)
    d = Path(path).read_bytes()
    sw, h, n, fw = info["strip_width"], info["height"], info["frames"], info["frame_width"]
    if len(d) < HEADER + sw * h * 4:
        raise ValueError(f"{path}: truncated")
    strip = Image.frombytes("RGBA", (sw, h), d[HEADER:HEADER + sw * h * 4])
    stride = sw // n
    return [strip.crop((i * stride, 0, i * stride + fw, h)) for i in range(n)]


def write_sprite(path: Path, frames: list[Image.Image], stride: int | None = None) -> None:
    """Frames side by side in stride-wide cells. A single picture: frame width = its width; a strip: frame width
    stride - 2 (D2R's skill tree strip: 895 in 897)."""
    w, h = frames[0].size
    stride = stride or w
    strip = Image.new("RGBA", (stride * len(frames), h))
    for i, f in enumerate(frames):
        strip.paste(f, (i * stride, 0))
    fw = w if len(frames) == 1 else stride - 2
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(sprite_bytes(fw, strip.width, h, len(frames), strip.tobytes()))


# from tools/median_stash.py


def lowend(im: Image.Image) -> Image.Image:
    return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


# from tools/rotw_stash_legacy.py


def lenient_json(text: str):
    """D2R's layout json: // comments and trailing commas."""
    text = re.sub(r'^\s*//.*$', "", text, flags=re.M)
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", text))


# from tools/pad_ui.py


def load(text: str) -> dict:
    """D2R's layout json: lenient_json plus the comments after a value (`"x": 1, // ...`) the gamepad files have."""
    return lenient_json(re.sub(r'\s//[^\n"]*$', "", text, flags=re.M))
