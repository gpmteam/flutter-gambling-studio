from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools/simulate_balance.py"
SPEC = importlib.util.spec_from_file_location("simulate_balance", SCRIPT)
assert SPEC and SPEC.loader
sb = importlib.util.module_from_spec(SPEC)
sys.modules["simulate_balance"] = sb
SPEC.loader.exec_module(sb)
TEMPLATES = REPO / ".claude/docs/templates/balance-configs"


def run_model(model: str, cfg: dict, trials: int | None = None) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.json"
        path.write_text(json.dumps(cfg), encoding="utf-8")
        report = Path(tmp) / "report.md"
        with contextlib.redirect_stdout(io.StringIO()):
            code = sb.main(["--model", model, "--config", str(path), "--report", str(report),
                            *(["--trials", str(trials)] if trials is not None else [])])
        return code, report.read_text(encoding="utf-8") if report.exists() else ""


class NoGamblingFieldTests(unittest.TestCase):
    def test_money_wager_and_odds_keys_are_flagged(self) -> None:
        cfg = {"bet_tiers": [1, 2], "houseEdge": 0.02, "starting_coins": 100,
               "shop": {"skin_price": 50}, "levels": [{"jackpot": 1}]}
        found = sb.forbidden_keys(cfg)
        for key in ("bet_tiers", "houseEdge", "starting_coins", "shop.skin_price", "levels[0].jackpot"):
            self.assertIn(key, found)

    def test_casual_vocabulary_is_not_flagged(self) -> None:
        cfg = {"points_per_piece": 10, "spin_speed": 1.4, "gem_kinds": 5, "combo_bonus": 0.5,
               "collect": {"kind": 2, "count": 20}, "tier_chain": ["cherry", "seven", "crown"]}
        self.assertEqual(sb.forbidden_keys(cfg), [])

    def test_a_config_with_a_wager_fails_the_run(self) -> None:
        cfg = json.loads((TEMPLATES / "reflex-ramp-config.json").read_text(encoding="utf-8"))
        cfg["bet"] = 5
        code, report = run_model("b5", cfg, trials=200)
        self.assertEqual(code, 2)
        self.assertIn("Casual-only config fields", report)


class BoardTests(unittest.TestCase):
    def test_swap_moves_find_a_known_three_in_a_row(self) -> None:
        board = sb.Board(3, 3, 4, random.Random(1), "swap")
        board.cells = [0, 1, 0,
                       2, 0, 3,
                       1, 2, 3]
        moves = {(i, j) for _, i, j in board.swap_moves()}
        self.assertIn((1, 4), moves)  # dropping the middle 0 into the top row makes 0-0-0

    def test_a_swap_resolves_its_run_and_refills(self) -> None:
        board = sb.Board(3, 3, 4, random.Random(1), "swap")
        board.cells = [0, 1, 0, 2, 0, 3, 1, 2, 3]
        rules = sb.BoardRules("swap", 3, False, 0.5, 0.1)
        units, _, steps = sb.apply_move(board, rules, (1, 4), None)
        self.assertGreaterEqual(units, 3)
        self.assertGreaterEqual(steps, 1)
        self.assertTrue(all(c >= 0 for c in board.cells))

    def test_blast_groups_are_four_connected(self) -> None:
        board = sb.Board(3, 2, 3, random.Random(1), "blast")
        board.cells = [0, 0, 1,
                       2, 0, 1]
        sizes = sorted(len(g) for g in board.groups(False))
        self.assertEqual(sizes, [1, 2, 3])

    def test_a_missing_reshuffle_policy_fails(self) -> None:
        cfg = json.loads((TEMPLATES / "board-levels-config.json").read_text(encoding="utf-8"))
        cfg.pop("dead_board")
        cfg["levels"] = cfg["levels"][:3]
        code, report = run_model("b1", cfg, trials=6)
        self.assertEqual(code, 2)
        self.assertIn("Dead-board policy declared", report)


class SortTests(unittest.TestCase):
    def test_solver_finds_minimum_moves(self) -> None:
        start = ((0, 1), (1, 0), ())
        self.assertEqual(sb.sort_solve(start, 2, True, 10_000), 3)

    def test_solver_proves_a_locked_deal_unsolvable(self) -> None:
        start = ((0, 1), (1, 0))
        self.assertIsNone(sb.sort_solve(start, 2, True, 10_000))


class SlideTests(unittest.TestCase):
    def test_equal_tiles_merge_once_per_move(self) -> None:
        self.assertEqual(sb.slide_line([1, 1, 1, 1]), ([2, 2, 0, 0], 2))
        self.assertEqual(sb.slide_line([2, 0, 2, 3]), ([3, 3, 0, 0], 1))


class ReportTests(unittest.TestCase):
    def test_solver_report_requires_solvability_evidence_for_every_level(self) -> None:
        rep = json.loads((TEMPLATES / "bot-report-example.json").read_text())
        rep["model"] = "b6"
        for level in rep["levels"]:
            level["solvable"], level["par"] = True, 5
        del rep["levels"][2]["solvable"]
        self.assertEqual(run_model("report", rep)[0], 2)

    def test_missing_and_impossible_trial_counts_cannot_pass(self) -> None:
        for value in (0, -1):
            rep = json.loads((TEMPLATES / "bot-report-example.json").read_text())
            rep["levels"][0]["skilled_runs"] = value
            self.assertEqual(run_model("report", rep)[0], 2)
        rep = json.loads((TEMPLATES / "bot-report-example.json").read_text())
        rep["levels"][0]["skilled_passes"] = 201
        self.assertEqual(run_model("report", rep)[0], 2)

    def test_empty_endless_evidence_cannot_pass(self) -> None:
        self.assertEqual(run_model("report", {"model": "b5", "bot": "reflex bot",
                                               "endless": {"runs": 200}})[0], 2)

    def test_merge_reports_use_merge_windows_rather_than_reflex_windows(self) -> None:
        rep = {"model": "b3", "bot": "drop-merge bot", "endless": {
            "runs": 200, "session_minutes": 8, "early_move_rate": 0.05,
            "skilled_goal_rate": 0.3, "player_milestone_rate": 0.8}}
        code, report = run_model("report", rep)
        self.assertEqual(code, 0)
        self.assertNotIn("Median first run", report)
        rep["endless"]["skilled_goal_rate"] = 0
        self.assertEqual(run_model("report", rep)[0], 2)

    def test_nonfinite_data_and_model_mismatch_fail(self) -> None:
        rep = json.loads((TEMPLATES / "bot-report-example.json").read_text())
        rep["max_par"] = float("nan")
        self.assertEqual(run_model("report", rep)[0], 2)
        rep["max_par"] = 60
        self.assertEqual(run_model("b6", rep)[0], 2)

    def test_zero_trials_and_impossible_board_fail_without_hanging(self) -> None:
        cfg = json.loads((TEMPLATES / "board-levels-config.json").read_text())
        self.assertEqual(run_model("b1", cfg, trials=0)[0], 2)
        cfg["levels"][0]["cols"] = cfg["levels"][0]["rows"] = 1
        self.assertEqual(run_model("b1", cfg, trials=1)[0], 2)

    def test_an_unsolvable_level_fails_the_report(self) -> None:
        rep = json.loads((TEMPLATES / "bot-report-example.json").read_text(encoding="utf-8"))
        rep["levels"][4]["solvable"] = False
        code, report = run_model("report", rep)
        self.assertEqual(code, 2)
        self.assertIn("unsolvable: 5", report)

    def test_a_wall_is_a_fail(self) -> None:
        rep = json.loads((TEMPLATES / "bot-report-example.json").read_text(encoding="utf-8"))
        rep["levels"][7]["passes"] = 10
        code, report = run_model("report", rep)
        self.assertEqual(code, 2)
        self.assertIn("Hardest level pass rate (player bot)", report)

    def test_models_without_a_simulator_require_a_bot_report(self) -> None:
        code, _ = run_model("b4", {"game_name": "No bot yet", "levels": [{"id": 1, "shots": 10}]})
        self.assertEqual(code, 2)

    def test_b4_accepts_a_bot_report(self) -> None:
        rep = json.loads((TEMPLATES / "bot-report-example.json").read_text(encoding="utf-8"))
        code, _ = run_model("b4", rep)
        self.assertEqual(code, 0)


class ReportOutputTests(unittest.TestCase):
    def test_json_artifacts_preserve_evidence_and_pass_the_casual_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "bot-report.json"
            source = (TEMPLATES / "bot-report-example.json").read_text(encoding="utf-8")
            config.write_text(source, encoding="utf-8")
            for name in ("simulation-500.json", "simulation-preproduction.json"):
                output = root / "design/balance" / name
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT), "--model", "report", "--config",
                     str(config), "--report", str(output), "--no-stamp"],
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(data["verdict"], "PASS")
                self.assertEqual(data["seed"], 7)
                self.assertTrue(data["metrics"])
                levels = next(table for table in data["tables"] if table["caption"] == "Levels")
                self.assertEqual(len(levels["rows"]), 15)
                self.assertEqual(levels["rows"][0][1:4], ["200", "97%", "100%"])
            self.assertEqual(config.read_text(encoding="utf-8"), source)
            gate = subprocess.run(
                [sys.executable, "-B", str(REPO / "tools/check_no_gambling.py"),
                 "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)

    def test_json_and_markdown_keep_the_same_nonpassing_verdicts(self) -> None:
        for rate, verdict, code in ((0.4, "CONCERNS", 1), (0.1, "FAIL", 2)):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                config = root / "config.json"
                config.write_text(json.dumps({"model": "b3", "bot": "merge bot", "endless": {
                    "runs": 200, "session_minutes": 8, "early_move_rate": 0.05,
                    "skilled_goal_rate": 0.3, "player_milestone_rate": rate}}), encoding="utf-8")
                for suffix in (".json", ".md"):
                    output = root / ("report" + suffix)
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = sb.main(["--model", "report", "--config", str(config),
                                          "--report", str(output), "--no-stamp"])
                    self.assertEqual(result, code)
                    body = output.read_text(encoding="utf-8")
                    if suffix == ".json":
                        data = json.loads(body)
                        self.assertEqual(data["verdict"], verdict)
                        metric = next(m for m in data["metrics"]
                                      if m["name"] == "Player bot reaches goal − 3")
                        self.assertEqual(metric["value"], rate)
                        self.assertEqual(metric["verdict"], verdict)
                    else:
                        self.assertTrue(body.startswith("# Balance Report"))
                        self.assertIn(f"**{verdict}**", body)

    def test_json_report_does_not_hide_forbidden_config_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "config.json"
            cfg = json.loads((TEMPLATES / "bot-report-example.json").read_text(encoding="utf-8"))
            cfg["bet"] = 5
            config.write_text(json.dumps(cfg), encoding="utf-8")
            output = root / "design/balance/report.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = sb.main(["--model", "report", "--config", str(config),
                                "--report", str(output), "--no-stamp"])
            self.assertEqual(code, 2)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["verdict"], "FAIL")
            self.assertIn("bet", data["metrics"][0]["note"])
            gate = subprocess.run(
                [sys.executable, "-B", str(REPO / "tools/check_no_gambling.py"),
                 "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(gate.returncode, 2)
            self.assertIn("bet", gate.stdout)


class TemplateTests(unittest.TestCase):
    def test_selftest_passes_on_every_template(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sb.selftest(), 0)


if __name__ == "__main__":
    unittest.main()
