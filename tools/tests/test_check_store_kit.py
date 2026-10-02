import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from check_store_kit import check


def png(size, mode="RGB"):
    output = BytesIO()
    Image.new(mode, size).save(output, format="PNG")
    return output.getvalue()


class StoreKitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = png((1320, 2868))
        cls.play = png((1080, 1920))
        cls.feature = png((1024, 500))
        cls.master = png((1024, 1024))
        cls.listing = png((512, 512))
        cls.emblem = png((32, 32), "RGBA")
        cls.banner = png((64, 32))
        cls.panorama = png((96, 64))

    @staticmethod
    def ledger(*records):
        return json.dumps({"schema_version": 1, "records": [
            {"sha256": hashlib.sha256(data).hexdigest(), "role": role, "made": made,
             "generation": generation} for data, role, made, generation in records]}).encode()

    def kit(self, count=2, play_set=True, changes=None, manifest_changes=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        archive = Path(tmp.name) / "kit.zip"
        manifest = {"schema_version": 1, "status": "COMPLETE", "screenshot_count": count,
                    "play_set": play_set, "visual_review": "PASS", "gameplay_review": "PASS",
                    "icon_master": "branding/app_icon.png", "listing_icon": "branding/store_icon_512.png",
                    "emblem": "branding/emblem.png"}
        manifest.update(manifest_changes or {})
        files = {"STORE_DELIVERY.json": json.dumps(manifest).encode(), "STORE_BRIEF.md": b"Brief",
                 "STORE_INFO.md": b"Reviewed", "feature-graphic-1024x500.png": self.feature,
                 "branding/app_icon.png": self.master, "branding/store_icon_512.png": self.listing,
                 "branding/emblem.png": self.emblem, "art/long-banner.png": self.banner,
                 "art/lineage.json": self.ledger((self.banner, "banner", "fresh", 1))}
        for i in range(1, count + 1):
            files[f"store/store-{i:02d}.png"] = self.app
            if play_set:
                files[f"store-play/store-{i:02d}.png"] = self.play
        for name, value in (changes or {}).items():
            if value is None:
                files.pop(name, None)
            else:
                files[name] = value
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as out:
            for name, value in files.items():
                out.writestr("kit/" + name, value)
        return archive

    def test_complete_custom_count_and_app_store_only_kits_pass(self):
        self.assertEqual(check(self.kit(), 2), [])
        self.assertEqual(check(self.kit(play_set=False), 2, False), [])

    def test_cli_validates_the_real_zip_with_requested_scope(self):
        archive = self.kit(play_set=False)
        result = subprocess.run([sys.executable, "-B", str(REPO / "tools/check_store_kit.py"),
                                 "--archive", str(archive), "--count", "2", "--no-play-set"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_missing_zip_reports_and_required_assets_fail(self):
        for name in ("STORE_DELIVERY.json", "STORE_INFO.md", "feature-graphic-1024x500.png",
                     "branding/app_icon.png", "branding/emblem.png", "store/store-02.png"):
            with self.subTest(name=name):
                self.assertTrue(check(self.kit(changes={name: None}), 2))

    def test_scope_mismatch_and_unreviewed_or_blocked_kits_fail(self):
        for change in ({"status": "BLOCKED"}, {"visual_review": "PENDING"},
                       {"gameplay_review": "FAIL"}, {"play_set": "true"}):
            with self.subTest(change=change):
                self.assertTrue(check(self.kit(manifest_changes=change), 2))
        self.assertTrue(check(self.kit(), 8))
        self.assertTrue(check(self.kit(play_set=False), 2, True))

    def test_bad_dimensions_transparency_numbering_and_image_corruption_fail(self):
        for changes in ({"store/store-01.png": self.play},
                        {"store/store-01.png": png((1320, 2868), "RGBA")},
                        {"store/store-03.png": self.app},
                        {"store/store-01.png": b"not a PNG"},
                        {"branding/app_icon.png": png((1024, 1024), "RGBA")}):
            with self.subTest(changes=list(changes)):
                self.assertTrue(check(self.kit(changes=changes), 2))

    def test_shipped_art_must_be_recorded_at_most_one_edit_from_fresh(self):
        edited_once = self.ledger((self.banner, "banner", "edit", 2),
                                  (self.panorama, "panorama", "fresh", 1))
        self.assertEqual(check(self.kit(changes={"art/panorama.png": self.panorama,
                                                 "art/lineage.json": edited_once}), 2), [])
        for changes in ({"art/lineage.json": None},
                        {"art/long-banner.png": None},
                        {"art/lineage.json": b"not json"},
                        {"art/lineage.json": self.ledger((self.banner, "banner", "edit", 3))},
                        {"art/panorama.png": self.panorama},
                        {"art/lineage.json": self.ledger((self.panorama, "panorama", "fresh", 1))}):
            with self.subTest(changes=list(changes)):
                self.assertTrue(check(self.kit(changes=changes), 2))

    def test_the_kit_exports_the_panorama_the_user_approved(self):
        approved, canvas, detailed, rerendered = (png((97, 64)), png((194, 128)),
                                                  png((194, 129)), png((97, 65)))
        sha = lambda data: hashlib.sha256(data).hexdigest()  # noqa: E731
        records = [
            {"sha256": sha(self.banner), "role": "banner", "made": "fresh", "generation": 1},
            {"sha256": sha(approved), "role": "panorama", "made": "fresh", "generation": 1},
            {"sha256": sha(canvas), "role": "panorama", "made": "derive", "generation": 1,
             "parent_sha256": sha(approved)},
            {"sha256": sha(detailed), "role": "panorama", "made": "detail", "generation": 1,
             "parent_sha256": sha(canvas)},
            {"sha256": sha(rerendered), "role": "panorama", "made": "edit", "generation": 2,
             "parent_sha256": sha(approved)},
        ]
        ledger = json.dumps({"schema_version": 1, "records": records}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            concept = Path(tmp) / "concept.json"
            concept.write_text(json.dumps({"status": "APPROVED",
                                           "panorama": {"sha256": sha(approved)}}))
            for shipped in (approved, detailed):
                with self.subTest(shipped="approved" if shipped is approved else "detailed"):
                    kit = self.kit(changes={"art/panorama.png": shipped, "art/lineage.json": ledger})
                    self.assertEqual(check(kit, 2, concept=concept), [])
            edited = self.kit(changes={"art/panorama.png": rerendered, "art/lineage.json": ledger})
            self.assertTrue(any("'edit' step after approval" in e
                                for e in check(edited, 2, concept=concept)))
            missing = self.kit(changes={"art/lineage.json": ledger})
            self.assertTrue(any("Missing art/panorama.png" in e
                                for e in check(missing, 2, concept=concept)))
            concept.write_text(json.dumps({"status": "PENDING",
                                           "panorama": {"sha256": sha(approved)}}))
            pending = self.kit(changes={"art/panorama.png": approved, "art/lineage.json": ledger})
            self.assertTrue(any("not APPROVED" in e for e in check(pending, 2, concept=concept)))
            # Without --concept (a game made before the gate) the kit is checked as before.
            self.assertEqual(check(edited, 2), [])

    def test_cli_returns_failure_for_invalid_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "bad.zip"
            archive.write_bytes(b"not a ZIP")
            result = subprocess.run([sys.executable, "-B", str(REPO / "tools/check_store_kit.py"),
                                     "--archive", str(archive)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("FAIL", result.stderr)


if __name__ == "__main__":
    unittest.main()
