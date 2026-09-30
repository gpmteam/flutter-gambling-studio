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
                self.assertEqual(result["families"][0]["default_mechanic"], "swap match-3")
                self.assertEqual(result["families"][0]["reference_gameplay"], "casino")

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

    def test_casino_references_keep_the_look_and_get_a_casual_mechanic(self) -> None:
        for prompt, family_id, mechanic in (("Joker", "joker", "tap blast"),
                                            ("Book of Ra", "book-of-ra", "triple tile"),
                                            ("Shining Crown", "shining-crown", "slide merge"),
                                            ("Plinko", "plinko", "peg clear")):
            with self.subTest(prompt=prompt):
                result = detect(prompt, new_game=True)
                self.assertEqual(family_ids(result), [family_id])
                self.assertEqual(result["families"][0]["reference_gameplay"], "casino")
                self.assertEqual(result["mechanic"], mechanic)
                self.assertEqual(result["topology_source"], "family")

    def test_zeus_reuses_its_own_casual_grid(self) -> None:
        result = detect("Zeus game", new_game=True)
        family = result["families"][0]
        self.assertEqual(family["reference_gameplay"], "casual")
        self.assertEqual(family["topology"], "7x6")
        self.assertEqual(result["mechanic"], "link chain")

    def test_family_builds_are_casual_mechanics_documented_in_the_examples_doc(self) -> None:
        doc = (REPO / ".claude/docs/game-concept-examples.md").read_text(encoding="utf-8")
        for family in reference_detect.FAMILIES:
            with self.subTest(family=family.id):
                self.assertIn(family.default_mechanic, reference_detect.CASUAL_BY_NAME)
                self.assertIn(f"**{family.classification}**", doc)
                self.assertTrue(reference_detect.CASUAL_BY_NAME[family.default_mechanic]
                                .startswith(family.classification.rsplit(" / ", 1)[0]))

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
    def test_a_gambling_mechanic_is_translated_and_the_family_keeps_identity(self) -> None:
        result = detect("Zeus Lightning Dice: a three-dice betting game played at Zeus's temple.")
        self.assertEqual(family_ids(result), ["zeus"])
        self.assertEqual(result["mechanic_override"], "slide merge")
        self.assertEqual(result["topology_source"], "translated")
        self.assertIn("dice", result["gambling_asks"])
        md = reference_detect.to_markdown(result)
        self.assertIn("identity", md)
        self.assertIn("never built", md)

    def test_hi_lo_joker_host_becomes_card_patience(self) -> None:
        result = detect("Joker's High Card: a fast high-or-low card game hosted by a mischievous joker.")
        self.assertEqual(family_ids(result), ["joker"])
        self.assertEqual(result["mechanic_override"], "card patience")

    def test_naming_the_familys_own_casino_mechanic_keeps_the_family_build(self) -> None:
        for prompt, mechanic in (("Joker slot with a prize wheel bonus", "tap blast"),
                                 ("Zeus slot", "link chain"),
                                 ("Сделай слот Джокер", "tap blast")):
            with self.subTest(prompt=prompt):
                result = detect(prompt)
                self.assertIsNone(result["mechanic_override"])
                self.assertEqual(result["mechanic"], mechanic)
                self.assertEqual(result["topology_source"], "family")

    def test_a_casual_mechanic_overrides_the_family_build(self) -> None:
        result = detect("Joker bubble shooter")
        self.assertEqual(result["mechanic_override"], "bubble shooter")
        self.assertEqual(result["topology_source"], "user mechanic")
        self.assertEqual(result["mechanic_archetype"], "G4 / M")

    def test_a_user_grid_is_recorded(self) -> None:
        result = detect("Joker slot 5x3")
        self.assertEqual(result["grid"], "5x3")
        self.assertEqual(result["topology_source"], "user grid")

    def test_a_pure_gambling_request_is_translated_without_a_reference(self) -> None:
        result = detect("make a roulette game with a pharaoh", new_game=True)
        self.assertFalse(result["reference"])
        self.assertEqual(result["mechanic"], "target throw")
        self.assertEqual(result["topology_source"], "translated")
        self.assertIn("Gambling asks", reference_detect.to_markdown(result))

    def test_a_bug_report_about_a_crash_is_not_a_crash_game(self) -> None:
        result = detect("the game crashes on start, fix the crash")
        self.assertEqual(result["gambling_asks"], [])
        self.assertIsNone(result["mechanic"])

    def test_collection_requests_have_a_playable_casual_core_and_balance_category(self) -> None:
        for prompt in ("create a gacha game", "loot box game", "card packs", "capsule game"):
            with self.subTest(prompt=prompt):
                result = detect(prompt, new_game=True)
                self.assertEqual(result["mechanic"], "memory match")
                self.assertEqual(result["mechanic_archetype"], "G6 / AA")


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
        result = detect("make me a fruit match-3", root=self.root,
                        attachments_dir="design/references/user", new_game=True)
        self.assertTrue(result["reference"])
        self.assertEqual(result["binding"], "exact")
        self.assertEqual([a["path"] for a in result["attachments"]],
                         ["design/references/user/a1b2c3d4-1.png"])

    def test_a_follow_up_screenshot_binds_only_when_the_message_asks_to_match_it(self) -> None:
        bug = detect("the play button overlaps the score, fix it", root=self.root,
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
        result = detect("match-3", root=self.root, new_game=True)
        self.assertIn("user_reference.jpg", [a["path"] for a in result["attachments"]])


class PhrasingTests(unittest.TestCase):
    def test_an_unmapped_title_to_copy_is_a_description_reference(self) -> None:
        result = detect("make a game exactly like Gates of Olympus", new_game=True)
        self.assertTrue(result["reference"])
        self.assertEqual(result["binding"], "description")

    def test_ordinary_words_are_not_reproduction_asks(self) -> None:
        for prompt in ("a pirate match-3 where the board looks like a treasure chest",
                       "keep the level copy short",
                       "I'd like a candy blast game",
                       "такой же баланс как раньше, кнопка повторить уровень"):
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
