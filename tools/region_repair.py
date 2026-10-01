#!/usr/bin/env python3
"""Repair a generated picture one region at a time, without re-painting the rest of it.

Every image-model edit re-renders the WHOLE frame. "Change only the x25 label" still re-paints
the face, the board and the water, and the next correction re-paints that re-paint. Each pass
softens detail, smears texture and shifts colour a little more — generation loss. A store
panorama that went through a fresh render and three such edits (move the hero, lower the board,
re-letter one ball) came out visibly mushier than the banner it was rendered beside.

This tool keeps every repair local, so ten repairs cost no more picture quality than one:

  cut      Cuts a window around the defect from the current candidate and scales it up to the
           size the image model renders. Send window.png to the image model as the edit target
           (after the identity references, which keep their place first). The repair is drawn at
           more detail than the candidate has in that spot.
  merge    Scales the model's render back to the window, aligns it (models reframe by a few
           pixels and a percent or two of zoom), matches its tone on the untouched ring around
           the defect and lays back ONLY the defect box, with a feathered edge. Every pixel
           outside box + feather is byte-identical to the candidate, and the command proves it.
  upscale  Makes a store-resolution canvas from a low-resolution render (Lanczos plus a gentle
           sharpen scaled to the factor). It is the base for an optional DETAIL pass: cut the
           regions the eye goes to (the lead's head and shoulders, the ball labels), let the
           model re-render them at its full resolution, and `merge --mode detail`, which refuses
           a render whose content drifted from the region it replaces.

The merged pixels are the image model's own render of the same region of the same scene. No
shipped asset, capture crop, script-drawn label or compositor layer enters the art, which is why
this is the one blend the store-screenshots runbook permits inside generated art.

Examples:
  python3 tools/region_repair.py cut --src art/panorama.png --box 40,380,180,560 \
      --out-dir art/repairs/01-x25-label
  # image model: identity refs first, then art/repairs/01-x25-label/window.png as the edit
  # target; save its output as art/repairs/01-x25-label/render.png
  python3 tools/region_repair.py merge --plan art/repairs/01-x25-label/plan.json \
      --render art/repairs/01-x25-label/render.png --out art/panorama-r1.png
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
except ImportError as exc:  # pragma: no cover - environment problem, not logic
    sys.stderr.write(f"region_repair.py requires Pillow + numpy ({exc}).\n")
    sys.exit(2)

RES = getattr(Image, "Resampling", Image).LANCZOS
SCHEMA_VERSION = 1

# The window is grown to one of these shapes. The built-in image tool picks its own output
# size, and it keeps these aspects faithfully; an odd aspect comes back reframed.
WINDOW_ASPECTS = (1.0, 1.5, 2.0 / 3.0)
# Context kept around the defect box, as a fraction of the box's longer side. It is what the
# model reads the scene from, and the ring that alignment and tone matching measure.
DEFAULT_CONTEXT = 0.6
MIN_CONTEXT_PX = 48
# Render size limits, chosen to be valid for `tools/gpt_image.py edit --size`.
RENDER_MIN_LONG = 1024
RENDER_MAX_LONG = 2048
RENDER_UPSCALE = 2.0
API_MIN_PIXELS = 655_360
API_MAX_PIXELS = 8_294_400
# A render whose aspect differs more than this is a reframed picture, not this window.
MAX_ASPECT_ERROR = 0.04
# Alignment search: zoom and shift the model is allowed to have introduced.
MAX_ZOOM = 0.04
DEFAULT_MAX_SHIFT = 0.04
MIN_MATCH = 0.25
# Feedback thresholds, on a 0..255 scale.
SEAM_WARN = 14.0
DEFAULT_MAX_DRIFT = 9.0


def die(message: str) -> "None":
    print(f"❌ {message}", file=sys.stderr)
    sys.exit(1)


def warn(message: str) -> None:
    print(f"⚠️  {message}", file=sys.stderr)


def ok(message: str) -> None:
    print(f"✅ {message}")


def info(message: str) -> None:
    print(f"   {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rgb(path: Path, label: str) -> Image.Image:
    try:
        img = Image.open(path)
        img.load()
    except Exception as exc:  # noqa: BLE001 - any decoder error means the same thing here
        die(f"{label} is not a readable image ({path}): {exc}")
    return img


def parse_box(spec: str, width: int, height: int) -> tuple[int, int, int, int]:
    """`X0,Y0,X1,Y1` in pixels, or in fractions of the image when every value is <= 1."""
    try:
        values = [float(part) for part in spec.split(",")]
    except ValueError:
        die(f"--box {spec!r}: expected X0,Y0,X1,Y1")
    if len(values) != 4:
        die(f"--box {spec!r}: expected X0,Y0,X1,Y1")
    if all(0.0 <= v <= 1.0 for v in values) and any(v % 1 for v in values):
        values = [values[0] * width, values[1] * height, values[2] * width, values[3] * height]
    x0, y0, x1, y1 = (int(round(v)) for v in values)
    x0, x1 = max(0, min(x0, x1)), min(width, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(height, max(y0, y1))
    if x1 - x0 < 8 or y1 - y0 < 8:
        die(f"--box {spec!r} is under 8px on a side inside the {width}x{height} image")
    return x0, y0, x1, y1


def default_feather(box: tuple[int, int, int, int]) -> int:
    short = min(box[2] - box[0], box[3] - box[1])
    return max(8, min(64, round(short * 0.08)))


def plan_window(box: tuple[int, int, int, int], size: tuple[int, int], context: float,
                feather: int) -> tuple[int, int, int, int]:
    """Box plus context, grown to a window aspect, slid inside the image."""
    width, height = size
    bw, bh = box[2] - box[0], box[3] - box[1]
    pad = max(MIN_CONTEXT_PX, 3 * feather, round(context * max(bw, bh)))
    ww, wh = bw + 2 * pad, bh + 2 * pad
    aspect = min(WINDOW_ASPECTS, key=lambda a: abs(math.log((ww / wh) / a)))
    if ww / wh < aspect:
        ww = round(wh * aspect)
    else:
        wh = round(ww / aspect)
    ww, wh = min(ww, width), min(wh, height)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    x0 = int(round(min(max(cx - ww / 2, 0), width - ww)))
    y0 = int(round(min(max(cy - wh / 2, 0), height - wh)))
    return x0, y0, x0 + ww, y0 + wh


def render_size(window_w: int, window_h: int) -> tuple[int, int]:
    """A size `gpt_image.py edit` accepts, with the window's aspect and more pixels than it."""
    aspect = max(1 / 3, min(3.0, window_w / window_h))
    long_edge = max(RENDER_MIN_LONG,
                    min(RENDER_MAX_LONG, RENDER_UPSCALE * max(window_w, window_h)))
    while True:
        if aspect >= 1:
            w, h = long_edge, long_edge / aspect
        else:
            w, h = long_edge * aspect, long_edge
        w, h = max(16, round(w / 16) * 16), max(16, round(h / 16) * 16)
        if w * h >= API_MIN_PIXELS or long_edge >= 3840:
            break
        long_edge += 64
    while w * h > API_MAX_PIXELS:
        w, h = w - 16 * (w >= h), h - 16 * (h > w)
    return int(w), int(h)


def scaled_box(box, window, render) -> tuple[int, int, int, int]:
    sx = render[0] / (window[2] - window[0])
    sy = render[1] / (window[3] - window[1])
    return (round((box[0] - window[0]) * sx), round((box[1] - window[1]) * sy),
            round((box[2] - window[0]) * sx), round((box[3] - window[1]) * sy))


def cmd_cut(args: argparse.Namespace) -> None:
    src_path = Path(args.src)
    src = load_rgb(src_path, "--src")
    box = parse_box(args.box, *src.size)
    feather = args.feather if args.feather is not None else default_feather(box)
    if feather < 1:
        die("--feather must be at least 1px")
    window = plan_window(box, src.size, args.context, feather)
    rw, rh = render_size(window[2] - window[0], window[3] - window[1])

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    crop = src.convert("RGB").crop(window)
    target = crop.resize((rw, rh), RES)
    target.save(out_dir / "window.png", "PNG")
    inner = scaled_box(box, window, (rw, rh))
    marked = target.copy()
    ImageDraw.Draw(marked).rectangle(inner, outline=(255, 0, 160), width=max(3, rw // 300))
    marked.save(out_dir / "window-marked.png", "PNG")

    plan = {
        "schema_version": SCHEMA_VERSION,
        "tool": "region_repair",
        "src": str(src_path),
        "src_sha256": sha256(src_path),
        "src_size": list(src.size),
        "box": list(box),
        "window": list(window),
        "feather": feather,
        "render_size": [rw, rh],
        "box_in_render": list(inner),
        "window_png": "window.png",
    }
    (out_dir / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    ww, wh = window[2] - window[0], window[3] - window[1]
    ok(f"window {ww}x{wh} at ({window[0]},{window[1]}) around box "
       f"{box[2] - box[0]}x{box[3] - box[1]} → {out_dir / 'window.png'} ({rw}x{rh}, "
       f"{rw / ww:.2f}x the candidate's pixels)")
    info(f"edit target: window.png. In the prompt, the defect sits at x={inner[0]}..{inner[2]}, "
         f"y={inner[1]}..{inner[3]} of that {rw}x{rh} image; everything else in it stays as is")
    info(f"headless: tools/gpt_image.py edit ... --image {out_dir / 'window.png'} --size {rw}x{rh}")
    info("window-marked.png outlines the box for review only — never attach it to the model")


def _luma(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


def _highpass(gray: np.ndarray, radius: float) -> np.ndarray:
    img = Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8), "L")
    low = np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32)
    return gray - low


def _zoomed(img: Image.Image, size: tuple[int, int], zoom: float) -> Image.Image:
    """`img` scaled by `zoom` about its centre, cropped/padded back to `size` (edge padded)."""
    w, h = size
    zw, zh = max(1, round(w * zoom)), max(1, round(h * zoom))
    scaled = img.resize((zw, zh), RES)
    left, top = (zw - w) // 2, (zh - h) // 2
    if left >= 0 and top >= 0:
        return scaled.crop((left, top, left + w, top + h))
    canvas = img.resize((w, h), RES)
    canvas.paste(scaled, (-left, -top))
    return canvas


def _shift_score(a: np.ndarray, b: np.ndarray, weight: np.ndarray, dx: int, dy: int) -> float:
    """Weighted normalised correlation of base `a` with render `b` moved by (dx, dy)."""
    h, w = a.shape
    ax0, ax1 = max(0, dx), min(w, w + dx)
    ay0, ay1 = max(0, dy), min(h, h + dy)
    if ax1 - ax0 < 8 or ay1 - ay0 < 8:
        return -1.0
    pa = a[ay0:ay1, ax0:ax1]
    pb = b[ay0 - dy:ay1 - dy, ax0 - dx:ax1 - dx]
    pw = weight[ay0:ay1, ax0:ax1]
    den = math.sqrt(float((pw * pa * pa).sum()) * float((pw * pb * pb).sum()))
    return float((pw * pa * pb).sum()) / den if den > 1e-6 else -1.0


def _ring_weight(size: tuple[int, int], box: tuple[int, int, int, int], guard: int) -> np.ndarray:
    """1 on the untouched context, 0 on the box (plus a guard band), tapered at the borders."""
    w, h = size
    weight = np.ones((h, w), dtype=np.float32)
    weight[max(0, box[1] - guard):box[3] + guard, max(0, box[0] - guard):box[2] + guard] = 0.0
    taper = max(2, min(w, h) // 16)
    ramp_x = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / taper, 0, 1)
    ramp_y = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / taper, 0, 1)
    return weight * ramp_y[:, None].astype(np.float32) * ramp_x[None, :].astype(np.float32)


def align(base: Image.Image, render: Image.Image, box: tuple[int, int, int, int],
          feather: int, max_shift: float) -> tuple[float, int, int, float]:
    """Zoom and shift that put `render` back on `base`, judged on the untouched ring only.

    Coarse to fine: zoom and shift are found on a ~256px copy and refined at full size. Both are
    scored by normalised correlation of high-passed luma, so a global tone change in the render
    does not move the answer.
    """
    w, h = base.size
    base_l = _luma(np.asarray(base.convert("RGB"), dtype=np.float32))

    def level(scale: float):
        sw, sh = max(16, round(w * scale)), max(16, round(h * scale))
        small_base = np.asarray(Image.fromarray(base_l.astype(np.uint8), "L")
                                .resize((sw, sh), RES), dtype=np.float32)
        sbox = tuple(round(v * scale) for v in box)
        weight = _ring_weight((sw, sh), sbox, max(1, round(feather * scale)))
        return sw, sh, _highpass(small_base, max(1.0, 8.0 * scale)), weight

    def render_level(zoom: float, sw: int, sh: int) -> np.ndarray:
        z = _zoomed(render.convert("RGB"), (w, h), zoom).resize((sw, sh), RES)
        return _highpass(_luma(np.asarray(z, dtype=np.float32)), max(1.0, 8.0 * sw / w))

    coarse = min(1.0, 256 / max(w, h))
    sw, sh, cb, cw = level(coarse)
    reach = max(1, math.ceil(max_shift * max(sw, sh)))
    best = (-2.0, 1.0, 0, 0)
    steps = 9
    for i in range(steps):
        zoom = 1.0 - MAX_ZOOM + 2 * MAX_ZOOM * i / (steps - 1)
        cr = render_level(zoom, sw, sh)
        for dy in range(-reach, reach + 1):
            for dx in range(-reach, reach + 1):
                score = _shift_score(cb, cr, cw, dx, dy)
                if score > best[0]:
                    best = (score, zoom, dx, dy)

    _, zoom, dx, dy = best
    fb_w, fb_h, fb, fw = level(1.0)
    dx, dy = round(dx / coarse), round(dy / coarse)
    fine = (-2.0, zoom, dx, dy)
    radius = max(2, math.ceil(1 / coarse))
    zoom_step = 2 * MAX_ZOOM / (steps - 1)
    for _ in range(2):  # halve the zoom step twice: ~0.25% is under a pixel on any window
        zoom_step /= 2
        for z in (fine[1] - zoom_step, fine[1], fine[1] + zoom_step):
            fr = render_level(z, fb_w, fb_h)
            for ddy in range(-radius, radius + 1):
                for ddx in range(-radius, radius + 1):
                    score = _shift_score(fb, fr, fw, fine[2] + ddx, fine[3] + ddy)
                    if score > fine[0]:
                        fine = (score, z, fine[2] + ddx, fine[3] + ddy)
        radius = 1
    score, zoom, dx, dy = fine
    return zoom, dx, dy, score


def feather_alpha(size: tuple[int, int], box: tuple[int, int, int, int], feather: int) -> np.ndarray:
    """1 inside the box, a cosine fall to 0 over `feather` px outside it."""
    w, h = size
    xs, ys = np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32)
    dx = np.maximum(np.maximum(box[0] - xs, 0), xs - (box[2] - 1))[None, :]
    dy = np.maximum(np.maximum(box[1] - ys, 0), ys - (box[3] - 1))[:, None]
    dist = np.sqrt(dx * dx + dy * dy)
    t = np.clip(dist / float(feather), 0.0, 1.0)
    return (0.5 * (1.0 + np.cos(np.pi * t))).astype(np.float32)


def place(render: Image.Image, size: tuple[int, int], zoom: float, dx: int, dy: int
          ) -> tuple[np.ndarray, np.ndarray]:
    """The render zoomed and shifted onto the window grid, plus where it has pixels."""
    w, h = size
    zw, zh = max(1, round(w * zoom)), max(1, round(h * zoom))
    scaled = np.asarray(render.convert("RGB").resize((zw, zh), RES), dtype=np.float32)
    out = np.zeros((h, w, 3), dtype=np.float32)
    have = np.zeros((h, w), dtype=bool)
    # Same centring as _zoomed, so the alignment found there lands here unchanged.
    ox = -((zw - w) // 2) + dx
    oy = -((zh - h) // 2) + dy
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(w, ox + zw), min(h, oy + zh)
    if x1 > x0 and y1 > y0:
        out[y0:y1, x0:x1] = scaled[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
        have[y0:y1, x0:x1] = True
    return out, have


def tone_match(render: np.ndarray, base: np.ndarray, ring: np.ndarray
               ) -> tuple[np.ndarray, list[list[float]]]:
    """Per-channel gain/offset that makes the render's ring agree with the candidate's."""
    out = render.copy()
    params: list[list[float]] = []
    for c in range(3):
        r, b = render[..., c][ring], base[..., c][ring]
        if r.size < 64:
            params.append([1.0, 0.0])
            continue
        gain = float(np.clip(b.std() / max(r.std(), 1e-3), 0.85, 1.18))
        offset = float(np.clip(b.mean() - gain * r.mean(), -24.0, 24.0))
        out[..., c] = render[..., c] * gain + offset
        params.append([round(gain, 4), round(offset, 2)])
    return np.clip(out, 0.0, 255.0), params


def drift(render: np.ndarray, base: np.ndarray, box: tuple[int, int, int, int]) -> float:
    """Low-frequency difference inside the box: changed content, not added detail."""
    radius = max(2.0, 0.012 * min(box[2] - box[0], box[3] - box[1]))
    crop = (slice(box[1], box[3]), slice(box[0], box[2]))

    def low(a: np.ndarray) -> np.ndarray:
        img = Image.fromarray(np.clip(_luma(a[crop]), 0, 255).astype(np.uint8), "L")
        return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32)

    return float(np.abs(low(render) - low(base)).mean())


def proof_sheet(before: np.ndarray, after: np.ndarray, box: tuple[int, int, int, int],
                feather: int, path: Path) -> None:
    diff = np.clip(np.abs(after - before).max(axis=-1) * 4.0, 0, 255).astype(np.uint8)
    heat = np.stack([diff, (diff * 0.35).astype(np.uint8), np.zeros_like(diff)], axis=-1)
    tiles = [Image.fromarray(a.astype(np.uint8), "RGB") for a in (before, after, heat)]
    for tile in tiles[1:]:
        draw = ImageDraw.Draw(tile)
        draw.rectangle(box, outline=(255, 0, 160), width=2)
        draw.rectangle((box[0] - feather, box[1] - feather, box[2] + feather, box[3] + feather),
                       outline=(0, 200, 255), width=1)
    w, h = tiles[0].size
    sheet = Image.new("RGB", (w * 3 + 24, h), (18, 18, 22))
    for i, tile in enumerate(tiles):
        sheet.paste(tile, (i * (w + 12), 0))
    if sheet.height > 900:
        scale = 900 / sheet.height
        sheet = sheet.resize((max(1, round(sheet.width * scale)), 900), RES)
    sheet.save(path, "PNG")


def cmd_merge(args: argparse.Namespace) -> None:
    plan_path = Path(args.plan)
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        die(f"cannot read --plan {plan_path}: {exc}")
    if plan.get("tool") != "region_repair":
        die(f"{plan_path} is not a region_repair plan")
    src_path = Path(plan["src"])
    base_path = Path(args.base) if args.base else src_path
    out_path = Path(args.out)
    if out_path.resolve() in {src_path.resolve(), base_path.resolve()}:
        die("--out must be a new file: keep the candidate this repair starts from")

    src = load_rgb(src_path, "the plan's --src")
    if list(src.size) != plan["src_size"] or sha256(src_path) != plan["src_sha256"]:
        die(f"{src_path} changed after `cut`; cut the window again from the current candidate")
    window = tuple(plan["window"])
    box_abs = tuple(plan["box"])
    feather = int(plan["feather"])
    same_base = base_path.resolve() == src_path.resolve()
    base = src if same_base else load_rgb(base_path, "--base")
    if base.size != src.size:
        die(f"--base {base_path} is {base.size[0]}x{base.size[1]}, the plan was cut from "
            f"{src.size[0]}x{src.size[1]}")
    base_rgb = np.asarray(base.convert("RGB"), dtype=np.uint8)
    if not same_base:
        cut_rgb = np.asarray(src.convert("RGB"), dtype=np.uint8)
        if not np.array_equal(base_rgb[window[1]:window[3], window[0]:window[2]],
                              cut_rgb[window[1]:window[3], window[0]:window[2]]):
            die("an earlier merge changed this window in --base; cut it again from --base")

    render = load_rgb(Path(args.render), "--render").convert("RGB")
    render_native = list(render.size)
    ww, wh = window[2] - window[0], window[3] - window[1]
    aspect_error = abs(math.log((render.width / render.height) / (ww / wh)))
    if aspect_error > math.log(1 + MAX_ASPECT_ERROR):
        die(f"--render is {render.width}x{render.height} ({render.width / render.height:.3f}:1) "
            f"but the window is {ww / wh:.3f}:1 — the model reframed the picture. Re-render "
            "with window.png as the edit target and the same aspect")
    render = render.resize((ww, wh), RES)

    box = (box_abs[0] - window[0], box_abs[1] - window[1],
           box_abs[2] - window[0], box_abs[3] - window[1])
    before_img = Image.fromarray(base_rgb[window[1]:window[3], window[0]:window[2]], "RGB")
    zoom, dx, dy, match = align(before_img, render, box, feather, args.max_shift)
    if match < MIN_MATCH:
        die(f"the render does not line up with the window (match {match:.2f} < {MIN_MATCH}) — "
            "it is not a re-render of this region. Re-render from window.png")
    placed, have = place(render, (ww, wh), zoom, dx, dy)
    alpha = feather_alpha((ww, wh), box, feather)
    touched = alpha > 0
    if not have[touched].all():
        die("after alignment the render does not cover the box and its feather; cut a wider "
            "window (--context) and re-render")

    before = base_rgb[window[1]:window[3], window[0]:window[2]].astype(np.float32)
    ring = have & ~touched & (_ring_weight((ww, wh), box, feather) > 0.5)
    toned, tone = tone_match(placed, before, ring)
    band = touched & (alpha < 1.0)
    seam = float(np.abs(toned[band] - before[band]).mean()) if band.any() else 0.0
    inside = alpha >= 1.0
    changed = float(np.abs(toned[inside] - before[inside]).mean()) if inside.any() else 0.0
    content_drift = drift(toned, before, box)
    if args.mode == "detail" and content_drift > args.max_drift:
        die(f"detail render drifted: low-frequency difference {content_drift:.1f} > "
            f"{args.max_drift:.1f} inside the box — the model changed what is there, not just "
            "its detail. Re-render with stricter invariants; the candidate is unchanged")

    blended = toned * alpha[..., None] + before * (1.0 - alpha[..., None])
    after = before.copy()
    after[touched] = blended[touched]
    after_u8 = np.clip(np.rint(after), 0, 255).astype(np.uint8)
    after_u8[~touched] = base_rgb[window[1]:window[3], window[0]:window[2]][~touched]

    out_rgb = base_rgb.copy()
    out_rgb[window[1]:window[3], window[0]:window[2]] = after_u8
    diff_mask = np.any(out_rgb != base_rgb, axis=-1)
    allowed = np.zeros_like(diff_mask)
    allowed[window[1]:window[3], window[0]:window[2]] = touched
    if np.any(diff_mask & ~allowed):  # pragma: no cover - guards the construction above
        die("internal error: pixels outside the box and its feather changed")

    out = Image.fromarray(out_rgb, "RGB")
    if base.mode == "RGBA":
        out.putalpha(base.getchannel("A"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_path, "PNG")
    proof = plan_path.parent / "proof.png"
    proof_sheet(before, after_u8.astype(np.float32), box, feather, proof)

    ys, xs = np.nonzero(diff_mask)
    bbox = ([int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
            if xs.size else None)
    plan["merge"] = {
        "mode": args.mode,
        "base": str(base_path),
        "base_sha256": sha256(base_path),
        "render": str(args.render),
        "render_sha256": sha256(Path(args.render)),
        "render_size": render_native,
        "out": str(out_path),
        "out_sha256": sha256(out_path),
        "alignment": {"zoom": round(zoom, 4), "shift_px": [dx, dy], "match": round(match, 3)},
        "tone": tone,
        "seam_difference": round(seam, 2),
        "inside_change": round(changed, 2),
        "content_drift": round(content_drift, 2),
        "changed_bbox": bbox,
        "changed_pixels": int(diff_mask.sum()),
        "unchanged_outside_box": True,
        "proof": str(proof),
    }
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    ok(f"{out_path}: merged {int(diff_mask.sum())} px inside box + {feather}px feather; every "
       "other pixel is byte-identical to the candidate")
    info(f"alignment zoom {zoom:.3f}, shift {dx:+d},{dy:+d}px, match {match:.2f}; "
         f"tone gains {', '.join(f'{g:.2f}' for g, _ in tone)}")
    info(f"inside change {changed:.1f}, content drift {content_drift:.1f}, "
         f"seam difference {seam:.1f} (0-255)")
    if seam > SEAM_WARN:
        warn(f"seam difference {seam:.1f} > {SEAM_WARN:.0f}: the render also changed the area "
             f"around the box. Look at {proof} — a visible edge means cut a wider box or "
             "re-render with the surroundings named as invariants")
    info(f"review {proof} (before | after | difference; box magenta, feather cyan), then the "
         "affected export crops")


def upscale_sharpen(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Lanczos to `size`, then an unsharp mask scaled to the factor (store_compose.cover's curve).

    A fixed small radius at a large factor sharpens the interpolation ringing rather than the
    picture, which is what drew crunchy dark outlines around soft upscaled art.
    """
    scale = max(size[0] / img.width, size[1] / img.height)
    out = img.resize(size, RES)
    if scale > 1.25:
        out = out.filter(ImageFilter.UnsharpMask(
            radius=round(0.8 * scale, 2), percent=int(min(60, 24 * scale)), threshold=2))
    return out


def cmd_upscale(args: argparse.Namespace) -> None:
    src_path = Path(args.src)
    src = load_rgb(src_path, "--src").convert("RGB")
    out_path = Path(args.out)
    if out_path.resolve() == src_path.resolve():
        die("--out must be a new file")
    height = args.height
    if height <= src.height:
        die(f"--height {height} is not larger than the source's {src.height}px; "
            "nothing to upscale")
    width = round(src.width * height / src.height)
    out = upscale_sharpen(src, (width, height))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_path, "PNG")
    ok(f"{out_path}: {src.width}x{src.height} → {width}x{height} "
       f"({height / src.height:.2f}x) canvas for a detail pass")
    info("cut the regions the eye goes to from THIS canvas, re-render each, and merge with "
         "--mode detail; export the store panels from the merged canvas")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Repair a generated picture region by region, leaving the rest untouched")
    sub = parser.add_subparsers(dest="cmd", required=True)

    cut = sub.add_parser("cut", help="cut a window around a defect for the image model")
    cut.add_argument("--src", required=True, help="the current candidate PNG")
    cut.add_argument("--box", required=True, metavar="X0,Y0,X1,Y1",
                     help="the defect, in pixels of --src (or fractions when every value <= 1)")
    cut.add_argument("--out-dir", required=True, help="where window.png and plan.json go")
    cut.add_argument("--context", type=float, default=DEFAULT_CONTEXT,
                     help="context around the box, as a fraction of its longer side "
                          f"(default {DEFAULT_CONTEXT})")
    cut.add_argument("--feather", type=int, default=None,
                     help="blend width outside the box in px (default 8%% of its short side)")
    cut.set_defaults(handler=cmd_cut)

    merge = sub.add_parser("merge", help="lay the model's render back inside the box only")
    merge.add_argument("--plan", required=True, help="plan.json written by cut")
    merge.add_argument("--render", required=True, help="the image model's output for window.png")
    merge.add_argument("--out", required=True, help="the new candidate PNG (never the input)")
    merge.add_argument("--base", default=None,
                       help="merge into this candidate instead of the plan's --src (same size; "
                            "the window must be unchanged there) — for several boxes cut from "
                            "one candidate")
    merge.add_argument("--mode", choices=("repair", "detail"), default="repair",
                       help="repair: the box is meant to change. detail: the render only adds "
                            "detail, and content drift refuses the merge")
    merge.add_argument("--max-drift", type=float, default=DEFAULT_MAX_DRIFT,
                       help=f"detail mode's drift limit, 0-255 (default {DEFAULT_MAX_DRIFT})")
    merge.add_argument("--max-shift", type=float, default=DEFAULT_MAX_SHIFT,
                       help="largest reframing shift searched, as a fraction of the window "
                            f"(default {DEFAULT_MAX_SHIFT})")
    merge.set_defaults(handler=cmd_merge)

    up = sub.add_parser("upscale", help="store-resolution canvas for a detail pass")
    up.add_argument("--src", required=True)
    up.add_argument("--height", type=int, required=True,
                    help="canvas height in px, e.g. the 2868px App Store panel height")
    up.add_argument("--out", required=True)
    up.set_defaults(handler=cmd_upscale)

    args = parser.parse_args(argv)
    args.handler(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
