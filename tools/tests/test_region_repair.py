from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover - host without the imaging stack
    raise unittest.SkipTest("Pillow and numpy are not installed in this host environment")


SCRIPT = Path(__file__).resolve().parents[1] / "region_repair.py"
SPEC = importlib.util.spec_from_file_location("region_repair", SCRIPT)
assert SPEC and SPEC.loader
region_repair = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(region_repair)


def scene(width: int = 640, height: int = 440, seed: int = 5) -> Image.Image:
    """A structured stand-in for generated art: gradients, shapes and edges to align on."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:height, 0:width]
    base = np.stack([60 + 120 * xx / width, 40 + 90 * yy / height,
                     150 - 60 * xx / width], axis=-1)
    img = Image.fromarray(base.astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)
    for _ in range(70):
        x, y = int(rng.integers(0, width)), int(rng.integers(0, height))
        r = int(rng.integers(6, 40))
        colour = tuple(int(c) for c in rng.integers(0, 255, 3))
        if rng.random() < 0.5:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=colour, outline=(10, 10, 10))
        else:
            draw.rectangle((x - r, y - r // 2, x + r, y + r // 2), fill=colour)
    return img


def model_render(window: Image.Image, *, zoom: float = 1.0, shift: tuple[int, int] = (0, 0),
                 gain: float = 1.0, offset: float = 0.0, noise: float = 0.0,
                 paint: tuple[int, int, int, int] | None = None,
                 size: tuple[int, int] | None = None, seed: int = 3) -> Image.Image:
    """What the image model plausibly returns: slightly reframed, re-toned, re-textured."""
    w, h = window.size
    zw, zh = round(w * zoom), round(h * zoom)
    big = window.resize((zw, zh), Image.LANCZOS)
    left, top = (zw - w) // 2 - shift[0], (zh - h) // 2 - shift[1]
    out = big.crop((left, top, left + w, top + h)).filter(ImageFilter.GaussianBlur(0.8))
    arr = np.asarray(out, dtype=np.float32) * gain + offset
    if noise:
        arr += np.random.default_rng(seed).normal(0, noise, arr.shape)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    if paint:
        ImageDraw.Draw(out).ellipse(paint, fill=(20, 220, 90))
    return out.resize(size, Image.LANCZOS) if size else out


class RegionRepairTests(unittest.TestCase):
    BOX = (250, 150, 330, 240)

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.src = self.dir / "candidate.png"
        scene().save(self.src)

    def run_cli(self, *argv: str) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            region_repair.main(list(argv))
        return out.getvalue()

    def assert_refused(self, *argv: str) -> None:
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            region_repair.main(list(argv))
        self.assertEqual(ctx.exception.code, 1)

    def cut(self, box=BOX, name: str = "r1", src: Path | None = None) -> tuple[Path, dict]:
        out = self.dir / name
        self.run_cli("cut", "--src", str(src or self.src), "--box", ",".join(map(str, box)),
                     "--out-dir", str(out))
        return out, json.loads((out / "plan.json").read_text(encoding="utf-8"))

    def test_cut_window_holds_the_box_and_renders_at_a_valid_larger_size(self) -> None:
        out, plan = self.cut()
        window, box = plan["window"], plan["box"]
        self.assertLessEqual(window[0], box[0])
        self.assertLessEqual(window[1], box[1])
        self.assertGreaterEqual(window[2], box[2])
        self.assertGreaterEqual(window[3], box[3])
        ww, wh = window[2] - window[0], window[3] - window[1]
        self.assertTrue(any(abs(ww / wh - a) < 0.02 for a in region_repair.WINDOW_ASPECTS))
        rw, rh = plan["render_size"]
        self.assertEqual((rw % 16, rh % 16), (0, 0))
        self.assertGreaterEqual(rw * rh, region_repair.API_MIN_PIXELS)
        self.assertGreater(rw, ww)
        with Image.open(out / "window.png") as target:
            self.assertEqual(target.size, (rw, rh))
        self.assertEqual(plan["src_sha256"], region_repair.sha256(self.src))

    def test_render_sizes_are_valid_for_the_images_api(self) -> None:
        for window in ((90, 90), (300, 200), (200, 300), (1400, 950), (2600, 1800)):
            with self.subTest(window=window):
                w, h = region_repair.render_size(*window)
                self.assertEqual((w % 16, h % 16), (0, 0))
                self.assertLessEqual(max(w, h), 3840)
                self.assertGreaterEqual(w * h, region_repair.API_MIN_PIXELS)
                self.assertLessEqual(w * h, region_repair.API_MAX_PIXELS)
                self.assertAlmostEqual(w / h, window[0] / window[1], delta=0.05)

    def test_merge_changes_only_the_box_and_its_feather(self) -> None:
        out, plan = self.cut()
        window = Image.open(out / "window.png").convert("RGB")
        bx = plan["box_in_render"]
        inner = (bx[0] + 40, bx[1] + 40, bx[2] - 40, bx[3] - 40)
        render = model_render(window, zoom=1.02, shift=(18, -12), gain=1.06, offset=-5,
                              noise=3, paint=inner, size=(1254, 1254) if
                              plan["render_size"][0] == plan["render_size"][1] else None)
        render.save(out / "render.png")
        result = self.dir / "candidate-r1.png"
        self.run_cli("merge", "--plan", str(out / "plan.json"),
                     "--render", str(out / "render.png"), "--out", str(result))

        before = np.asarray(Image.open(self.src).convert("RGB"))
        after = np.asarray(Image.open(result).convert("RGB"))
        changed = np.any(before != after, axis=-1)
        f = plan["feather"]
        x0, y0, x1, y1 = plan["box"]
        allowed = np.zeros_like(changed)
        allowed[max(0, y0 - f):y1 + f, max(0, x0 - f):x1 + f] = True
        self.assertTrue(changed.any(), "the repair did not land")
        self.assertFalse((changed & ~allowed).any(), "pixels outside box + feather changed")

        merged = json.loads((out / "plan.json").read_text(encoding="utf-8"))["merge"]
        self.assertTrue(merged["unchanged_outside_box"])
        self.assertAlmostEqual(merged["alignment"]["zoom"], 1 / 1.02, delta=0.008)
        self.assertGreater(merged["alignment"]["match"], 0.6)
        self.assertLess(merged["seam_difference"], region_repair.SEAM_WARN)
        self.assertTrue((out / "proof.png").is_file())

    def test_merge_refuses_a_render_that_is_not_this_window(self) -> None:
        out, plan = self.cut()
        rw, rh = plan["render_size"]
        reframed = self.dir / "reframed.png"
        Image.open(out / "window.png").resize((round(rh * 1.5), rh)).save(reframed)
        self.assert_refused("merge", "--plan", str(out / "plan.json"),
                            "--render", str(reframed), "--out", str(self.dir / "x.png"))

        unrelated = self.dir / "unrelated.png"
        scene(seed=99).crop((0, 0, 320, 320)).resize((rw, rh)).save(unrelated)
        self.assert_refused("merge", "--plan", str(out / "plan.json"),
                            "--render", str(unrelated), "--out", str(self.dir / "x.png"))
        self.assertFalse((self.dir / "x.png").exists())

    def test_merge_refuses_a_changed_candidate_and_overwriting_it(self) -> None:
        out, _ = self.cut()
        render = out / "window.png"
        self.assert_refused("merge", "--plan", str(out / "plan.json"),
                            "--render", str(render), "--out", str(self.src))
        scene(seed=6).save(self.src)
        self.assert_refused("merge", "--plan", str(out / "plan.json"),
                            "--render", str(render), "--out", str(self.dir / "x.png"))

    def test_detail_mode_takes_added_detail_and_refuses_changed_content(self) -> None:
        out, plan = self.cut()
        window = Image.open(out / "window.png").convert("RGB")
        model_render(window, zoom=1.01, shift=(6, 4), noise=4).save(out / "detail.png")
        self.run_cli("merge", "--plan", str(out / "plan.json"), "--mode", "detail",
                     "--render", str(out / "detail.png"), "--out", str(self.dir / "d.png"))
        self.assertTrue((self.dir / "d.png").is_file())

        bx = plan["box_in_render"]
        model_render(window, paint=(bx[0] + 10, bx[1] + 10, bx[2] - 10, bx[3] - 10)
                     ).save(out / "drifted.png")
        self.assert_refused("merge", "--plan", str(out / "plan.json"), "--mode", "detail",
                            "--render", str(out / "drifted.png"),
                            "--out", str(self.dir / "d2.png"))
        self.assertFalse((self.dir / "d2.png").exists())

    def test_two_boxes_cut_from_one_candidate_merge_in_turn(self) -> None:
        first, _ = self.cut((60, 60, 120, 120), "a")
        second, _ = self.cut((470, 300, 540, 370), "b")
        for out in (first, second):
            model_render(Image.open(out / "window.png").convert("RGB"), noise=2
                         ).save(out / "render.png")
        mid, final = self.dir / "r1.png", self.dir / "r2.png"
        self.run_cli("merge", "--plan", str(first / "plan.json"),
                     "--render", str(first / "render.png"), "--out", str(mid))
        self.run_cli("merge", "--plan", str(second / "plan.json"), "--base", str(mid),
                     "--render", str(second / "render.png"), "--out", str(final))
        a = np.asarray(Image.open(mid).convert("RGB"))
        b = np.asarray(Image.open(final).convert("RGB"))
        self.assertTrue(np.array_equal(a[:200, :200], b[:200, :200]),
                        "the second merge disturbed the first repair")

        overlapping, _ = self.cut((90, 90, 150, 150), "c")
        self.assert_refused("merge", "--plan", str(overlapping / "plan.json"), "--base",
                            str(mid), "--render", str(overlapping / "window.png"),
                            "--out", str(self.dir / "r3.png"))

    def test_upscale_makes_a_taller_canvas_and_refuses_a_smaller_one(self) -> None:
        canvas = self.dir / "canvas.png"
        self.run_cli("upscale", "--src", str(self.src), "--height", "1100", "--out", str(canvas))
        with Image.open(canvas) as img:
            self.assertEqual(img.size, (1600, 1100))
        self.assert_refused("upscale", "--src", str(self.src), "--height", "300",
                            "--out", str(self.dir / "small.png"))


class StoreComposeCropTests(unittest.TestCase):
    def setUp(self) -> None:
        script = Path(__file__).resolve().parents[1] / "store_compose.py"
        spec = importlib.util.spec_from_file_location("store_compose_crop", script)
        assert spec and spec.loader
        self.store_compose = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.store_compose)

    def test_vertical_bias_keeps_the_top_or_bottom_of_a_tall_picture(self) -> None:
        geometry = self.store_compose.cover_geometry
        _, nh, _, centre, _ = geometry(1508, 1043, 3404, 1920)
        self.assertEqual(centre, (nh - 1920) // 2)
        self.assertEqual(geometry(1508, 1043, 3404, 1920, bias_y=-1.0)[3], 0)
        self.assertEqual(geometry(1508, 1043, 3404, 1920, bias_y=1.0)[3], nh - 1920)

    def test_sharpening_grows_with_the_factor_and_skips_mild_ones(self) -> None:
        img = scene(120, 80)
        self.assertIs(self.store_compose.upscale_sharpen(img, 1.2), img)
        self.assertIsNot(self.store_compose.upscale_sharpen(img, 2.75), img)


if __name__ == "__main__":
    unittest.main()
