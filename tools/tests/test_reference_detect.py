from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools/reference_detect.py"
SPEC = importlib.util.spec_from_file_location("reference_detect", SCRIPT)
assert SPEC and SPEC.loader
reference_detect = importlib.util.module_from_spec(SPEC)
sys.modules["reference_detect"] = reference_detect
SPEC.loader.exec_module(reference_detect)


def detect(prompt: str, **kwargs) -> dict:
    kwargs.setdefault("root", REPO)
    return reference_detect.detect(prompt, **kwargs)


def family_ids(result: dict) -> list[str]:
    return [family["id"] for family in result["families"]]


class NamedFamilyTests(unittest.TestCase):
    def test_every_spelling_of_joker_jewels_maps_to_the_folder_not_plain_joker(self) -> None:
        for prompt in ("Make Joker Jewels", "make a Joker's Jewels slot", "jokers jewels please",
                       "build joker-jewels", "JokerJewels", "сделай джокер джуэлс",
                       "игра Джокер Джевелс"):
            with self.subTest(prompt=prompt):
                result = detect(prompt, new_game=True)
                self.assertEqual(family_ids(result), ["joker-jewels"])
                self.assertEqual(result["binding"], "exact")
                self.assertEqual(result["families"][0]["topology"], "5x3")

    def test_russian_and_possessive_names_resolve(self) -> None:
        cases = {
            "Сделай слот Джокер": "joker",
            "Zeus's thunder slot": "zeus",
            "слот про зевса": "zeus",
            "Book of Ra deluxe": "book-of-ra",
            "сделай книгу ра": "book-of-ra",
            "book-of-ra": "book-of-ra",
            "Shining Crown": "shining-crown",
            "шайнинг краун": "shining-crown",
            "Plinko": "plinko",
            "плинко с бонусами": "plinko",
        }
        for prompt, expected in cases.items():
            with self.subTest(prompt=prompt):
                self.assertEqual(family_ids(detect(prompt)), [expected])

    def test_a_crown_themed_original_is_not_shining_crown(self) -> None:
        result = detect("Crown Cascade: a classic 3x3 slot with three crowned symbols", new_game=True)
        self.assertFalse(result["reference"])
        self.assertEqual(result["families"], [])

    def test_every_mapped_file_exists_and_is_listed_in_the_examples_doc(self) -> None:
        doc = (REPO / ".claude/docs/game-concept-examples.md").read_text(encoding="utf-8")
        for family in reference_detect.FAMILIES:
            for ref in family.files:
                with self.subTest(path=ref.path):
                    self.assertTrue((REPO / ref.path).is_file(), ref.path)
                    name = Path(ref.path).name
                    self.assertTrue(ref.path in doc or name in doc,
                                    f"{ref.path} is not documented in game-concept-examples.md")


class MechanicOverrideTests(unittest.TestCase):
    def test_a_named_family_with_another_mechanic_keeps_identity_but_not_topology(self) -> None:
        result = detect("Zeus Lightning Dice: a three-dice betting game played at Zeus's temple.")
        self.assertEqual(family_ids(result), ["zeus"])
        self.assertEqual(result["mechanic_override"], "dice")
        self.assertEqual(result["topology_source"], "user mechanic")
        self.assertIn("identity", reference_detect.to_markdown(result))

    def test_hi_lo_joker_host_is_a_joker_reference_with_the_users_mechanic(self) -> None:
        result = detect("Joker's High Card: a fast high-or-low card game hosted by a mischievous joker.")
        self.assertEqual(family_ids(result), ["joker"])
        self.assertEqual(result["mechanic_override"], "hi-lo")

    def test_naming_the_familys_own_mechanic_keeps_the_family_topology(self) -> None:
        result = detect("Joker slot with a prize wheel bonus")
        self.assertIsNone(result["mechanic_override"])
        self.assertEqual(result["topology_source"], "family")

    def test_a_user_grid_overrides_the_family_grid(self) -> None:
        result = detect("Joker slot 5x3")
        self.assertEqual(result["grid"], "5x3")
        self.assertEqual(result["topology_source"], "user grid")


class AttachmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        folder = self.root / "design/references/user"
        folder.mkdir(parents=True)
        (folder / "a1b2c3d4-1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
        (folder / "notes.txt").write_text("not an image", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_attachments_always_bind_on_a_new_game(self) -> None:
        result = detect("make me a fruit slot", root=self.root,
                        attachments_dir="design/references/user", new_game=True)
        self.assertTrue(result["reference"])
        self.assertEqual(result["binding"], "exact")
        self.assertEqual([a["path"] for a in result["attachments"]],
                         ["design/references/user/a1b2c3d4-1.png"])

    def test_a_follow_up_screenshot_binds_only_when_the_message_asks_to_match_it(self) -> None:
        bug = detect("the spin button overlaps the balance, fix it", root=self.root,
                     attachments_dir="design/references/user")
        self.assertFalse(bug["reference"])
        match = detect("make the character exactly like the reference image", root=self.root,
                       attachments_dir="design/references/user")
        self.assertTrue(match["reference"])
        match_ru = detect("сделай символы как на картинке", root=self.root,
                          attachments_dir="design/references/user")
        self.assertTrue(match_ru["attachments_bind"])

    def test_legacy_root_attachments_are_found(self) -> None:
        (self.root / "user_reference.jpg").write_bytes(b"\xff\xd8\xff" + b"0" * 32)
        result = detect("slot", root=self.root, new_game=True)
        self.assertIn("user_reference.jpg", [a["path"] for a in result["attachments"]])


class PhrasingTests(unittest.TestCase):
    def test_an_unmapped_title_to_copy_is_a_description_reference(self) -> None:
        result = detect("make a game exactly like Gates of Olympus", new_game=True)
        self.assertTrue(result["reference"])
        self.assertEqual(result["binding"], "description")

    def test_ordinary_words_are_not_reproduction_asks(self) -> None:
        for prompt in ("a pirate slot where the board looks like a treasure chest",
                       "keep the compliance copy short",
                       "I'd like a candy crash game",
                       "такой же баланс как раньше, кнопка повторить ставку"):
            with self.subTest(prompt=prompt):
                self.assertFalse(detect(prompt, new_game=True)["reference"])


class CliTests(unittest.TestCase):
    def test_json_and_markdown_outputs(self) -> None:
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--prompt", "Joker Jewels", "--new-game", "--json",
             "--root", str(REPO)],
            capture_output=True, text=True, timeout=30, check=True)
        self.assertEqual(family_ids(json.loads(out.stdout)), ["joker-jewels"])
        md = subprocess.run(
            [sys.executable, str(SCRIPT), "--prompt", "Joker Jewels", "--new-game", "--markdown",
             "--root", str(REPO)],
            capture_output=True, text=True, timeout=30, check=True).stdout
        self.assertIn("# Reference contract", md)
        self.assertIn("jj_gameplay.jpeg", md)
        self.assertIn("## Identity ledger", md)


if __name__ == "__main__":
    unittest.main()
