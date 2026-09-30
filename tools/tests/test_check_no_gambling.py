from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from check_no_gambling import scan


class CasualGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, path: str, body: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)

    def test_points_stars_seeded_board_and_decorative_reference_art_pass(self) -> None:
        self.write("lib/systems/game_rng.dart", "final random = Random(seed);\n")
        self.write("lib/systems/vfx_rng.dart", "final random = Random();\n")
        self.write("lib/game/game.dart", "score += cleared * pointsPerTile;\nfinal sprite = 'gold_coin.png';\n")
        self.write("assets/data/levels.json", '{"levels": [{"moves": 20, "stars": [100, 200, 300]}]}')
        self.write("design/reference-contract.md", "Casino source has bets and payouts; art only.")
        self.write("store/age-rating.md", "Simulated gambling: no. Casual skill game.")
        self.assertEqual(scan(self.root), [])

    def test_point_wagers_and_camel_case_currency_systems_fail(self) -> None:
        self.write("lib/game/game.dart", "points -= betSize;\ncoinBalance += payoutMultiplier;\n")
        self.assertGreaterEqual(len(scan(self.root)), 2)

    def test_nested_currency_data_fails_with_a_field_location(self) -> None:
        self.write("assets/data/modes.json", '{"modes": [{"startingCoins": 1000}]}')
        self.assertTrue(any("modes[0].startingCoins" in hit for hit in scan(self.root)))

    def test_comments_do_not_fail_but_strings_with_urls_are_still_scanned(self) -> None:
        self.write("lib/main.dart", '// Never add a jackpot or wallet.\n'
                   'final helpUrl = "https://example.test"; final label = "spin to win";\n')
        hits = scan(self.root)
        self.assertEqual(len(hits), 1)
        self.assertIn("lib/main.dart:2", hits[0])

    def test_gameplay_rng_requires_a_seed_and_one_owner(self) -> None:
        self.write("lib/systems/game_rng.dart", "final rng = Random();")
        self.write("lib/components/board.dart", "final rng = Random(42);")
        hits = scan(self.root)
        self.assertTrue(any("explicit seed" in h for h in hits))
        self.assertTrue(any("outside GameRng/VfxRng" in h for h in hits))

    def test_cli_rejects_gambling_copy_and_malformed_data(self) -> None:
        self.write("store/en/short_description.txt", "Hit the jackpot")
        self.write("assets/data/levels.json", "{broken")
        result = subprocess.run([sys.executable, "-B", str(REPO / "tools/check_no_gambling.py"),
                                 "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("store/en/short_description.txt:1", result.stdout)
        self.assertIn("invalid JSON", result.stdout)


if __name__ == "__main__":
    unittest.main()
