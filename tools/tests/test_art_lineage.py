from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "art_lineage.py"
SPEC = importlib.util.spec_from_file_location("art_lineage", SCRIPT)
assert SPEC and SPEC.loader
art_lineage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(art_lineage)


class ArtLineageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.ledger = self.dir / "lineage.json"
        self._n = 0

    def picture(self, name: str) -> Path:
        """Distinct bytes per file: the ledger identifies pictures by content."""
        self._n += 1
        path = self.dir / name
        path.write_bytes(f"picture {self._n} {name}".encode())
        return path

    def run_cli(self, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = art_lineage.main(["--ledger", str(self.ledger), *argv])
        return code, out.getvalue() + err.getvalue()

    def record(self, path: Path, role: str, made: str, parent: Path | None = None,
               refs: tuple[Path, ...] = ()) -> tuple[int, str]:
        argv = ["record", "--file", str(path), "--role", role, "--made", made]
        if parent is not None:
            argv += ["--parent", str(parent)]
        for ref in refs:
            argv += ["--ref", str(ref)]
        return self.run_cli(*argv)

    def generation(self, path: Path) -> int:
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        record = art_lineage.find(data, art_lineage.sha256(path))
        assert record is not None
        return record["generation"]

    def test_one_whole_frame_edit_per_lineage(self) -> None:
        fresh = self.picture("banner.png")
        self.assertEqual(self.record(fresh, "banner", "fresh")[0], 0)
        edited = self.picture("banner-e1.png")
        self.assertEqual(self.record(edited, "banner", "edit", fresh)[0], 0)
        self.assertEqual((self.generation(fresh), self.generation(edited)), (1, 2))

        again = self.picture("banner-e2.png")
        code, message = self.record(again, "banner", "edit", edited)
        self.assertEqual(code, 1)
        self.assertIn("render fresh", message)
        self.assertEqual(self.run_cli("check", "--file", str(edited), "--for", "edit")[0], 1)
        self.assertEqual(self.run_cli("check", "--file", str(fresh), "--for", "edit")[0], 0)

    def test_region_repairs_and_derivations_keep_the_generation(self) -> None:
        fresh = self.picture("panorama.png")
        self.record(fresh, "panorama", "fresh")
        repaired = self.picture("panorama-r1.png")
        self.assertEqual(self.record(repaired, "panorama", "repair", fresh)[0], 0)
        canvas = self.picture("panorama-canvas.png")
        self.assertEqual(self.record(canvas, "panorama", "derive", repaired)[0], 0)
        detailed = self.picture("panorama-canvas-d1.png")
        self.assertEqual(self.record(detailed, "panorama", "detail", canvas)[0], 0)
        self.assertEqual(self.generation(detailed), 1)
        # A repaired fresh render may still take its one whole-frame edit.
        self.assertEqual(self.run_cli("check", "--file", str(repaired), "--for", "edit")[0], 0)
        self.assertEqual(self.run_cli("verify", "--file", str(detailed))[0], 0)

    def test_unknown_history_counts_as_edited(self) -> None:
        legacy = self.picture("old-banner.png")
        code, message = self.record(self.picture("b.png"), "banner", "edit", legacy)
        self.assertEqual(code, 1)
        self.assertIn("no recorded lineage", message)
        repaired = self.picture("old-banner-r1.png")
        self.assertEqual(self.record(repaired, "banner", "repair", legacy)[0], 0)
        self.assertEqual(self.generation(repaired), 2)
        self.assertEqual(self.run_cli("check", "--file", str(legacy), "--for", "edit")[0], 1)
        self.assertEqual(self.run_cli("verify", "--file", str(legacy))[0], 1)
        self.assertEqual(self.record(legacy, "banner", "adopt")[0], 0)
        self.assertEqual(self.generation(legacy), 2)
        self.assertEqual(self.run_cli("verify", "--file", str(legacy))[0], 0)
        self.assertEqual(self.run_cli("check", "--file", str(legacy), "--for", "edit")[0], 1)

    def test_a_picture_never_renders_from_its_previous_version(self) -> None:
        banner = self.picture("banner.png")
        self.record(banner, "banner", "fresh")
        background = self.picture("background.png")
        character = self.picture("hero.png")  # shipped asset: not in the ledger
        self.assertEqual(self.record(background, "background", "fresh",
                                     refs=(character, banner))[0], 0)

        code, message = self.record(self.picture("banner-v2.png"), "banner", "fresh",
                                    refs=(character, banner))
        self.assertEqual(code, 1)
        self.assertIn("earlier banner", message)
        code, _ = self.record(self.picture("background-v2.png"), "background", "fresh",
                              refs=(character, banner, background))
        self.assertEqual(code, 1)
        code, message = self.record(self.picture("panorama.png"), "panorama", "fresh",
                                    refs=(character, banner, background))
        self.assertEqual(code, 1)
        self.assertIn("only the accepted banner", message)
        self.assertEqual(self.record(self.picture("icon.png"), "icon", "fresh",
                                     refs=(character, banner))[0], 0)
        self.assertEqual(self.run_cli("check", "--file", str(banner), "--for", "reference",
                                      "--role", "panorama")[0], 0)
        self.assertEqual(self.run_cli("check", "--file", str(background), "--for", "reference",
                                      "--role", "background")[0], 1)

    def test_recording_the_same_picture_twice_keeps_the_first_record(self) -> None:
        banner = self.picture("banner.png")
        self.record(banner, "banner", "fresh")
        copy = self.dir / "art-long-banner.png"
        copy.write_bytes(banner.read_bytes())
        code, message = self.record(copy, "banner", "derive", banner)
        self.assertEqual(code, 0)
        self.assertIn("already recorded", message)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(data["records"]), 1)


if __name__ == "__main__":
    unittest.main()
