from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


concept_gate = load("concept_gate")
art_lineage = load("art_lineage")


class ConceptGateTests(unittest.TestCase):
    """The carousel the user approves is the one the game, background and store kit use."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.project = Path(tmp.name)
        self._cwd = os.getcwd()
        os.chdir(self.project)
        self.addCleanup(os.chdir, self._cwd)
        self.root = Path("production/store-art/concept")
        self.ledger = Path("production/store-art/lineage.json")
        self._shade = 0
        handoff = Path(concept_gate.HANDOFF_1)
        handoff.parent.mkdir(parents=True)
        handoff.write_text(f"# Handoff 1\n- {concept_gate.GATE_MARKER}\n", encoding="utf-8")

    def run_cli(self, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = concept_gate.main(list(argv))
        return code, out.getvalue() + err.getvalue()

    def render(self) -> Path:
        """A fresh panorama and its export, the way autocreate Phase 3.9 leaves them."""
        self._shade += 40
        self.root.mkdir(parents=True, exist_ok=True)
        panorama = self.root / "panorama.png"
        Image.new("RGB", (300, 207), (self._shade, 90, 140)).save(panorama)
        with contextlib.redirect_stdout(io.StringIO()):
            art_lineage.main(["--ledger", str(self.ledger), "record", "--file", str(panorama),
                              "--role", "panorama", "--made", "fresh"])
        (self.root / "panorama-prompt.txt").write_text("One continuous panorama…", "utf-8")
        panels = self.root / "panels"
        panels.mkdir(exist_ok=True)
        for i in range(1, 4):
            Image.new("RGB", (1320, 2868), (self._shade, 20 * i, 60)).save(
                panels / f"store-{i:02d}.png")
        Image.new("RGB", (900, 650), (10, 10, 10)).save(panels / "_carousel-preview.png")
        Image.new("RGB", (120, 90), (self._shade, 200, 40)).save(
            self.root / "gameplay-sample.png")
        (self.root / "gameplay-sample.md").write_text("7x8 board of gem tiles", "utf-8")
        return panorama

    def publish(self) -> tuple[int, str]:
        root = self.root
        return self.run_cli("publish", "--panorama", str(root / "panorama.png"),
                            "--prompt", str(root / "panorama-prompt.txt"),
                            "--panels", str(root / "panels"),
                            "--sample", str(root / "gameplay-sample.png"),
                            "--sample-spec", str(root / "gameplay-sample.md"),
                            "--lead-kind", "character")

    def record(self) -> dict:
        return json.loads((self.root / "concept.json").read_text(encoding="utf-8"))

    def test_implementation_waits_for_an_approved_carousel(self) -> None:
        self.assertEqual(self.run_cli("check", "--for", "implement")[0], 1)
        self.render()
        code, message = self.publish()
        self.assertEqual(code, 0, message)
        self.assertEqual(self.record()["status"], "PENDING")
        code, message = self.run_cli("check", "--for", "implement")
        self.assertEqual(code, 1)
        self.assertIn("not APPROVED", message)

        sha = self.record()["panorama"]["sha256"]
        self.assertEqual(self.run_cli("approve", "--expect-sha", sha, "--by", "service")[0], 0)
        self.assertEqual(self.run_cli("check", "--for", "implement")[0], 0)
        # Approving again is a no-op, not an error: a retried build run re-sends it.
        self.assertEqual(self.run_cli("approve", "--expect-sha", sha)[0], 0)

    def test_publish_writes_the_small_previews_the_service_shows(self) -> None:
        self.render()
        self.assertEqual(self.publish()[0], 0)
        previews = {p["file"] for p in self.record()["previews"]}
        self.assertEqual(previews, {"preview/panel-1.jpg", "preview/panel-2.jpg",
                                    "preview/panel-3.jpg", "preview/panorama.jpg",
                                    "preview/carousel.jpg"})
        with Image.open(self.root / "preview/panel-1.jpg") as panel:
            self.assertEqual(panel.height, concept_gate.PANEL_PREVIEW_HEIGHT)
        code, out = self.run_cli("status", "--json")
        status = json.loads(out)
        self.assertEqual((code, status["status"], status["panorama_intact"]), (0, "PENDING", True))

    def test_an_approval_is_pinned_to_the_panorama_the_user_saw(self) -> None:
        self.render()
        self.publish()
        code, message = self.run_cli("approve", "--expect-sha", "0" * 64)
        self.assertEqual(code, 1)
        self.assertIn("changed since the user saw it", message)
        # A panorama touched after publishing is not the one on the card either.
        Image.new("RGB", (300, 207), (1, 2, 3)).save(self.root / "panorama.png")
        code, message = self.run_cli("approve")
        self.assertEqual(code, 1)
        self.assertIn("no longer matches", message)

    def test_a_revision_archives_the_shown_carousel_and_bumps_the_revision(self) -> None:
        self.render()
        self.publish()
        feedback = self.project / "feedback.txt"
        feedback.write_text("Make the board bigger", "utf-8")
        self.assertEqual(self.run_cli("revise", "--feedback-file", str(feedback))[0], 0)
        self.assertEqual(self.record()["status"], "DRAFTING")
        self.assertTrue((self.root / "revisions/r1/panorama.png").is_file())
        self.assertTrue((self.root / "revisions/r1/concept.json").is_file())
        self.assertFalse((self.root / "panorama.png").exists())

        self.render()
        self.assertEqual(self.publish()[0], 0)
        record = self.record()
        self.assertEqual((record["status"], record["revision"]), ("PENDING", 2))
        self.assertEqual(record["feedback"][0]["text"], "Make the board bigger")

    def test_a_new_render_cannot_silently_replace_the_pending_one(self) -> None:
        self.render()
        self.publish()
        self.render()
        code, message = self.publish()
        self.assertEqual(code, 1)
        self.assertIn("concept_gate.py revise", message)

    def test_an_approved_concept_is_never_replaced(self) -> None:
        self.render()
        self.publish()
        self.run_cli("approve")
        self.assertEqual(self.run_cli("revise")[0], 1)
        code, message = self.publish()
        self.assertEqual(code, 1)
        self.assertIn("already APPROVED", message)

    def test_publish_requires_a_recorded_panorama_and_store_sized_panels(self) -> None:
        self.render()
        Image.new("RGB", (1080, 1920)).save(self.root / "panels/store-02.png")
        code, message = self.publish()
        self.assertEqual(code, 1)
        self.assertIn("1320x2868", message)

        self.render()
        Image.new("RGB", (300, 207), (9, 9, 9)).save(self.root / "panorama.png")  # unrecorded
        code, message = self.publish()
        self.assertEqual(code, 1)
        self.assertIn("art_lineage.py record", message)

    def lineage(self, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = art_lineage.main(["--ledger", str(self.ledger), *argv])
        return code, out.getvalue() + err.getvalue()

    def candidate(self, name: str, folder: Path | None = None) -> Path:
        self._shade += 7
        path = (folder or self.root) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (60, 40), (self._shade % 256, 30, self._shade // 256)).save(path)
        return path

    def test_the_concept_panorama_has_a_render_budget_per_revision(self) -> None:
        for i in range(concept_gate.FRESH_RENDER_BUDGET):
            path = self.candidate(f"panorama-candidate-{i + 1}.png")
            code, out = self.lineage("record", "--file", str(path), "--role", "panorama",
                                     "--made", "fresh")
            self.assertEqual(code, 0, out)
        code, out = self.lineage("record", "--file", str(self.candidate("one-more.png")),
                                 "--role", "panorama", "--made", "fresh")
        self.assertEqual(code, 1)
        self.assertIn("fresh renders are spent", out)
        self.assertIn("--known-issue", out)
        status = json.loads(self.run_cli("budget", "--json")[1])
        self.assertEqual((status["revision"], status["fresh"]), (1, concept_gate.FRESH_RENDER_BUDGET))
        self.assertIn("no fresh renders left", self.run_cli("budget")[1])

        # Region repairs are budgeted separately; a store run's panorama is not a concept render.
        parent = self.root / "panorama-candidate-1.png"
        for i in range(concept_gate.REPAIR_BUDGET):
            code, out = self.lineage("record", "--file", str(self.candidate(f"repaired-{i}.png")),
                                     "--role", "panorama", "--made", "repair",
                                     "--parent", str(parent))
            self.assertEqual(code, 0, out)
        code, out = self.lineage("record", "--file", str(self.candidate("repaired-x.png")),
                                 "--role", "panorama", "--made", "repair", "--parent", str(parent))
        self.assertEqual(code, 1)
        self.assertIn("region repairs are spent", out)
        store = self.candidate("panorama.png", Path("production/store-art/art"))
        self.assertEqual(self.lineage("record", "--file", str(store), "--role", "panorama",
                                      "--made", "fresh")[0], 0)

    def test_a_revision_gets_a_fresh_budget(self) -> None:
        self.render()
        self.assertEqual(self.publish()[0], 0)
        for i in range(concept_gate.FRESH_RENDER_BUDGET - 1):
            self.lineage("record", "--file", str(self.candidate(f"late-{i}.png")),
                         "--role", "panorama", "--made", "fresh")
        self.run_cli("revise")
        # Earlier renders in the same second as `revise` would still count; step past it.
        record = self.record()
        record["drafting_since"] = "2999-01-01T00:00:00+00:00"
        (self.root / "concept.json").write_text(json.dumps(record), "utf-8")
        status = json.loads(self.run_cli("budget", "--json")[1])
        self.assertEqual((status["revision"], status["fresh"]), (2, 0))

    def test_known_issues_reach_the_record_and_the_status(self) -> None:
        self.render()
        code, out = self.run_cli("publish", "--panorama", str(self.root / "panorama.png"),
                                 "--prompt", str(self.root / "panorama-prompt.txt"),
                                 "--panels", str(self.root / "panels"),
                                 "--sample", str(self.root / "gameplay-sample.png"),
                                 "--sample-spec", str(self.root / "gameplay-sample.md"),
                                 "--lead-kind", "character",
                                 "--known-issue", "The painted board is 6x8;  the game is 7x8.",
                                 "--known-issue", "The x25 label is soft at full size.")
        self.assertEqual(code, 0, out)
        self.assertIn("known issue: The painted board is 6x8; the game is 7x8.", out)
        issues = ["The painted board is 6x8; the game is 7x8.", "The x25 label is soft at full size."]
        self.assertEqual(self.record()["known_issues"], issues)
        self.assertEqual(json.loads(self.run_cli("status", "--json")[1])["known_issues"], issues)

    def test_known_issues_are_short_and_few(self) -> None:
        self.render()
        base = ["publish", "--panorama", str(self.root / "panorama.png"),
                "--prompt", str(self.root / "panorama-prompt.txt"),
                "--panels", str(self.root / "panels"),
                "--sample", str(self.root / "gameplay-sample.png"),
                "--sample-spec", str(self.root / "gameplay-sample.md"), "--lead-kind", "character"]
        many = [arg for i in range(concept_gate.MAX_KNOWN_ISSUES + 1)
                for arg in ("--known-issue", f"issue {i}")]
        code, out = self.run_cli(*base, *many)
        self.assertEqual(code, 1)
        self.assertIn("at most", out)
        code, out = self.run_cli(*base, "--known-issue", "x" * (concept_gate.MAX_KNOWN_ISSUE_CHARS + 1))
        self.assertEqual(code, 1)
        self.assertFalse((self.root / "concept.json").exists())
        self.assertFalse((self.root / "preview").exists())

    def test_a_project_made_before_the_gate_is_legacy(self) -> None:
        Path(concept_gate.HANDOFF_1).write_text("# Handoff 1\n", encoding="utf-8")
        code, message = self.run_cli("check", "--for", "implement")
        self.assertEqual(code, 0)
        self.assertIn("LEGACY", message)
        self.assertTrue(json.loads(self.run_cli("status", "--json")[1])["legacy"])


if __name__ == "__main__":
    unittest.main()
