#!/usr/bin/env python3
"""Balance verifier for the casual game studio.

One entry point for the six balance models declared in .claude/docs/balance-models.md:

    B1  board simulation   G1  swap match-3, link chain, tap blast            (built-in bot)
    B2  solvable deals     G2  sort puzzle (built-in solver); tile tray, pairs, patience → report
    B3  run length         G3  slide merge (built-in bot); drop merge, block place, merge grid → report
    B4  shot simulation    G4  bubble, peg, brick, knockdown, draw & guide         → report
    B5  reflex ramp        G5  runners, stackers, catchers, slicers, flyers, throwers (built-in model)
    B6  solver curve       G6  logic levels                                         → report

`--model report` grades a bot report written by the game's own headless simulation
(`test/balance/bot_sim_test.dart` writes `design/balance/bot-report.json`) against the same
thresholds. Use it for every mechanic without a built-in simulator: the game's rules engine is
then the simulator, which beats any approximation this file could make.

The built-in simulators are deliberately conservative: bots simplify special pieces and boosters, and use bounded look-ahead. Their curve is an
estimate; the game's own bot is needed for faithful custom-rule verification.

Usage
-----
    python3 tools/simulate_balance.py --model b1 --config design/balance/level-config.json
    python3 tools/simulate_balance.py --model b5 --config design/balance/endless-config.json
    python3 tools/simulate_balance.py --model report --config design/balance/bot-report.json
    python3 tools/simulate_balance.py --selftest

Every run writes `design/balance/simulation-report.md` (or `--report`) and stamps the config's
`simulation` block with the date and verdict (`--no-stamp` to skip). A `.json` report path
writes structured JSON; other paths and console output use Markdown. Use `--report`, rather
than redirecting console output, to save a JSON artifact.

Exit code is 0 on PASS, 1 on CONCERNS, 2 on FAIL — so CI and hooks can gate on it.
Stdlib only, no dependencies.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import sys
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

PASS, CONCERNS, FAIL = "PASS", "CONCERNS", "FAIL"
_VERDICT_EXIT = {PASS: 0, CONCERNS: 1, FAIL: 2}
_VERDICT_MARK = {PASS: "✅", CONCERNS: "⚠️", FAIL: "❌"}

PCT = "{:.1%}"
INT = "{:.0f}"
ONE = "{:.1f}"

# A balance config describes difficulty, never money or chance-for-reward.
# Keys are split on underscores/camelCase before matching, so "points_per_piece" passes and
# "house_edge", "betTiers" or "coin_price" do not. See .claude/rules/no-gambling.md.
FORBIDDEN_KEY_WORDS = {
    "bet", "bets", "wager", "wagers", "stake", "stakes", "rtp", "payout", "payouts", "paytable",
    "jackpot", "odds", "price", "prices", "currency", "coin", "coins", "chip", "chips", "credit",
    "credits", "wallet", "balance", "pity", "gacha", "shop",
}
# Two-word terms, matched on the key with its separators removed.
FORBIDDEN_KEY_JOINED = ("houseedge", "cashout", "lootbox", "freespin", "startingcoins")


class ConfigError(Exception):
    """The config cannot be simulated as written."""


# --------------------------------------------------------------------------------------
# result plumbing
# --------------------------------------------------------------------------------------


@dataclass
class Metric:
    """One checked number: what we wanted, what we got, and whether that is acceptable."""

    name: str
    value: float
    target: str
    verdict: str
    fmt: str = "{:.2f}"
    note: str = ""

    def rendered(self) -> str:
        return self.fmt.format(self.value)


@dataclass
class Report:
    model: str
    title: str
    config_path: str
    method: str
    trials: int
    seed: int | None = None
    metrics: list[Metric] = field(default_factory=list)
    tables: list[tuple[str, list[str], list[list[str]]]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, metric: Metric) -> Metric:
        self.metrics.append(metric)
        return metric

    def table(self, caption: str, header: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
        self.tables.append((caption, list(header), [[str(c) for c in r] for r in rows]))

    @property
    def verdict(self) -> str:
        if any(m.verdict == FAIL for m in self.metrics):
            return FAIL
        if any(m.verdict == CONCERNS for m in self.metrics):
            return CONCERNS
        return PASS

    def to_json(self) -> str:
        """Serialize the same evidence and verdict as the human-readable report."""
        data = asdict(self)
        data.update(schema_version=1, date=date.today().isoformat(), verdict=self.verdict)
        data["tables"] = [
            {"caption": caption, "header": header, "rows": rows}
            for caption, header, rows in self.tables
        ]
        return json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"

    def to_markdown(self) -> str:
        out: list[str] = [f"# Balance Report — {self.title}", ""]
        out.append(f"- **Model**: {self.model}")
        out.append(f"- **Config**: `{self.config_path}`")
        out.append(f"- **Method**: {self.method}")
        out.append(f"- **Trials**: {self.trials:,}")
        if self.seed is not None:
            out.append(f"- **Seed**: {self.seed}")
        out.append(f"- **Date**: {date.today().isoformat()}")
        out += ["", "## Result", "", "| Metric | Target | Measured | Verdict |",
                "|---------|---------|----------|---------|"]
        for m in self.metrics:
            note = f" ({m.note})" if m.note else ""
            out.append(f"| {m.name} | {m.target} | {m.rendered()}{note} | "
                       f"{_VERDICT_MARK[m.verdict]} {m.verdict} |")
        out.append("")
        for caption, header, rows in self.tables:
            out += [f"## {caption}", "", "| " + " | ".join(header) + " |",
                    "|" + "|".join("---" for _ in header) + "|"]
            out += ["| " + " | ".join(row) + " |" for row in rows]
            out.append("")
        out += ["## Verdict", ""]
        if self.verdict == PASS:
            out.append("✅ **PASS** — the difficulty curve is inside its windows; the pipeline can continue.")
        else:
            head = "⚠️ **CONCERNS**" if self.verdict == CONCERNS else "❌ **FAIL**"
            out += [f"{head} — needs `balance-designer`'s attention:", ""]
            for m in self.metrics:
                if m.verdict != PASS:
                    detail = f" — {m.note}" if m.note else ""
                    out.append(f"- **{m.name}**: measured {m.rendered()}, target {m.target}{detail}")
        if self.notes:
            out += ["", "## Notes", ""]
            out += [f"- {n}" for n in self.notes]
        out.append("")
        return "\n".join(out)


def at_least(value: float, good: float, ok: float) -> str:
    return PASS if value >= good else CONCERNS if value >= ok else FAIL


def at_most(value: float, good: float, ok: float) -> str:
    return PASS if value <= good else CONCERNS if value <= ok else FAIL


def within(value: float, lo: float, hi: float, lo_ok: float, hi_ok: float) -> str:
    if lo <= value <= hi:
        return PASS
    if lo_ok <= value <= hi_ok:
        return CONCERNS
    return FAIL


def require(cfg: dict, key: str, kind: type | tuple[type, ...], where: str = "config") -> Any:
    if key not in cfg:
        raise ConfigError(f"{where}: missing required field `{key}`")
    value = cfg[key]
    if not isinstance(value, kind) or isinstance(value, bool) and kind is not bool:
        raise ConfigError(f"{where}: `{key}` has the wrong type ({type(value).__name__})")
    return value


def split_key(key: str) -> list[str]:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", key)
    return [w for w in re.split(r"[^A-Za-z0-9]+", spaced.lower()) if w]


def forbidden_keys(node: Any, path: str = "") -> list[str]:
    """Every key path whose words include money, wager or chance-for-reward vocabulary."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            words = split_key(str(key))
            if FORBIDDEN_KEY_WORDS.intersection(words) or any(
                    term in "".join(words) for term in FORBIDDEN_KEY_JOINED):
                found.append(here)
            found += forbidden_keys(value, here)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            found += forbidden_keys(value, f"{path}[{i}]")
    return found


def check_no_gambling(cfg: dict, report: Report) -> None:
    bad = forbidden_keys(cfg)
    report.add(Metric(
        "Casual-only config fields", len(bad), "0", PASS if not bad else FAIL, INT,
        note=", ".join(bad[:5]) + (" …" if len(bad) > 5 else "") if bad else ""))


def median(values: Sequence[float]) -> float:
    return statistics.median(values) if values else 0.0


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return ordered[idx]


# --------------------------------------------------------------------------------------
# shared: the level curve (B1, B2 completion, B4, B6 and bot reports)
# --------------------------------------------------------------------------------------


def grade_level_curve(report: Report, levels: list[dict]) -> None:
    """Grade per-level pass rates of an average-player bot.

    Each entry: {"id", "pass_rate", optional "skilled_rate"}.
    The shape we want: an onboarding plateau, then a ramp with breathers, no walls, no spikes.
    """
    n = len(levels)
    report.add(Metric("Levels in the curve", n, "≥ 12 (≥ 3 minimum)",
                      PASS if n >= 12 else CONCERNS if n >= 3 else FAIL, INT))
    if not n:
        return
    onboarding = levels[: min(3, n)]
    worst_on = min(onboarding, key=lambda lv: lv["pass_rate"])
    report.add(Metric("Onboarding pass rate (L1–L3, worst)", worst_on["pass_rate"], "≥ 80%",
                      at_least(worst_on["pass_rate"], 0.80, 0.60), PCT,
                      note=f"level {worst_on['id']}"))
    hardest = min(levels, key=lambda lv: lv["pass_rate"])
    report.add(Metric("Hardest level pass rate (player bot)", hardest["pass_rate"],
                      "≥ 25% (a wall below 15%)", at_least(hardest["pass_rate"], 0.25, 0.15), PCT,
                      note=f"level {hardest['id']}"))
    skilled = [lv for lv in levels if lv.get("skilled_rate") is not None]
    if skilled:
        worst_sk = min(skilled, key=lambda lv: lv["skilled_rate"])
        report.add(Metric("Hardest level pass rate (skilled bot)", worst_sk["skilled_rate"],
                          "≥ 40% (unfair below 25%)", at_least(worst_sk["skilled_rate"], 0.40, 0.25),
                          PCT, note=f"level {worst_sk['id']}"))
    if n >= 8:
        q = max(1, n // 4)
        first = statistics.mean(lv["pass_rate"] for lv in levels[:q])
        last = statistics.mean(lv["pass_rate"] for lv in levels[-q:])
        report.add(Metric("Ramp: first-quarter minus last-quarter pass rate", first - last,
                          "≥ 15 pp (the curve actually gets harder)",
                          PASS if first - last >= 0.15 else CONCERNS, "{:+.1%}"))
    if n >= 2:
        drops = [(levels[i - 1]["pass_rate"] - levels[i]["pass_rate"], levels[i]["id"])
                 for i in range(1, n)]
        worst_drop, at_id = max(drops)
        report.add(Metric("Biggest level-to-level spike", max(0.0, worst_drop), "≤ 40 pp",
                          at_most(worst_drop, 0.40, 0.55), "{:.1%}", note=f"into level {at_id}"))


def grade_par_curve(report: Report, levels: list[dict], max_par: float) -> None:
    """Grade minimum-move counts (par) for solver-backed levels (B2, B6)."""
    pars = [(lv["par"], lv["id"]) for lv in levels if lv.get("par") is not None]
    if not pars:
        return
    first_par, first_id = pars[0]
    report.add(Metric("First level par (minimum moves)", first_par, "≤ 10",
                      at_most(first_par, 10, 16), ONE, note=f"level {first_id}"))
    worst_ratio, at_id = 0.0, pars[0][1]
    for (prev, _), (cur, cid) in zip(pars, pars[1:]):
        if prev > 0 and cur / prev > worst_ratio:
            worst_ratio, at_id = cur / prev, cid
    if len(pars) >= 2:
        report.add(Metric("Biggest par step", worst_ratio, "≤ 2.0×", at_most(worst_ratio, 2.0, 3.0),
                          "{:.2f}×", note=f"into level {at_id}"))
    top_par, top_id = max(pars)
    report.add(Metric("Largest par", top_par, f"≤ {max_par:g}", at_most(top_par, max_par, max_par * 1.5),
                      ONE, note=f"level {top_id}"))
    if len(pars) >= 8:
        q = max(1, len(pars) // 4)
        early = statistics.mean(p for p, _ in pars[:q])
        late = statistics.mean(p for p, _ in pars[-q:])
        report.add(Metric("Par grows through the levels", late / early if early else 0.0,
                          "late/early ≥ 1.5×", PASS if early and late / early >= 1.5 else CONCERNS,
                          "{:.2f}×"))


def grade_endless(report: Report, run_s: Sequence[float] | None, *, median_s: float | None = None,
                  p90_s: float | None = None, early_rate: float | None = None,
                  time_to_cap_s: float | None = None) -> None:
    """Grade an endless run distribution (B5, and endless sections of bot reports)."""
    if run_s:
        median_s = median(run_s)
        p90_s = quantile(run_s, 0.9)
        early_rate = sum(1 for s in run_s if s < 10.0) / len(run_s)
    if median_s is not None:
        report.add(Metric("Median first run", median_s, "30–180 s",
                          within(median_s, 30, 180, 20, 300), "{:.0f} s"))
    if early_rate is not None:
        report.add(Metric("Runs ending in the first 10 s", early_rate, "≤ 10% (a fair start)",
                          at_most(early_rate, 0.10, 0.20), PCT))
    if p90_s is not None:
        report.add(Metric("90th-percentile run", p90_s, "≤ 600 s (the ramp ends runs)",
                          at_most(p90_s, 600, 1200), "{:.0f} s"))
    if time_to_cap_s is not None:
        report.add(Metric("Time for the tempo to reach its cap", time_to_cap_s, "60–300 s",
                          within(time_to_cap_s, 60, 300, 30, 600), "{:.0f} s"))


# --------------------------------------------------------------------------------------
# B1 — board simulation (G1: swap match-3, link chain, tap blast)
# --------------------------------------------------------------------------------------

_NEIGH4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
_NEIGH8 = _NEIGH4 + ((-1, -1), (-1, 1), (1, -1), (1, 1))


class Board:
    """A flat grid of symbol kinds; row 0 is the top. -1 marks an empty cell mid-resolve."""

    def __init__(self, cols: int, rows: int, kinds: int, rng: random.Random, rule: str) -> None:
        self.cols, self.rows, self.kinds, self.rng, self.rule = cols, rows, kinds, rng, rule
        self.cells = [0] * (cols * rows)
        self.fill()

    def fill(self) -> None:
        cols, cells, rng = self.cols, self.cells, self.rng
        for i in range(len(cells)):
            r, c = divmod(i, cols)
            while True:
                k = rng.randrange(self.kinds)
                if self.rule == "swap" and self.kinds >= 3:
                    if c >= 2 and cells[i - 1] == k and cells[i - 2] == k:
                        continue
                    if r >= 2 and cells[i - cols] == k and cells[i - 2 * cols] == k:
                        continue
                break
            cells[i] = k

    # swap rule ------------------------------------------------------------------------

    def _line_gain(self, i: int, k: int) -> int:
        cols, rows, cells = self.cols, self.rows, self.cells
        r, c = divmod(i, cols)
        h = 1
        cc = c - 1
        while cc >= 0 and cells[r * cols + cc] == k:
            h += 1
            cc -= 1
        cc = c + 1
        while cc < cols and cells[r * cols + cc] == k:
            h += 1
            cc += 1
        v = 1
        rr = r - 1
        while rr >= 0 and cells[rr * cols + c] == k:
            v += 1
            rr -= 1
        rr = r + 1
        while rr < rows and cells[rr * cols + c] == k:
            v += 1
            rr += 1
        gain = (h if h >= 3 else 0) + (v if v >= 3 else 0)
        return gain - 1 if h >= 3 and v >= 3 else gain

    def swap_moves(self) -> list[tuple[int, int, int]]:
        cols, rows, cells = self.cols, self.rows, self.cells
        moves: list[tuple[int, int, int]] = []
        for i in range(len(cells)):
            r, c = divmod(i, cols)
            for j in ((i + 1) if c + 1 < cols else -1, (i + cols) if r + 1 < rows else -1):
                if j < 0:
                    continue
                a, b = cells[i], cells[j]
                if a == b:
                    continue
                cells[i], cells[j] = b, a
                gain = self._line_gain(i, b) + self._line_gain(j, a)
                cells[i], cells[j] = a, b
                if gain:
                    moves.append((gain, i, j))
        return moves

    def _runs(self) -> set[int]:
        cols, rows, cells = self.cols, self.rows, self.cells
        marked: set[int] = set()
        for r in range(rows):
            c = 0
            while c < cols:
                k, start = cells[r * cols + c], c
                while c < cols and cells[r * cols + c] == k:
                    c += 1
                if k >= 0 and c - start >= 3:
                    marked.update(r * cols + x for x in range(start, c))
        for c in range(cols):
            r = 0
            while r < rows:
                k, start = cells[r * cols + c], r
                while r < rows and cells[r * cols + c] == k:
                    r += 1
                if k >= 0 and r - start >= 3:
                    marked.update(x * cols + c for x in range(start, r))
        return marked

    # link / blast rule ----------------------------------------------------------------

    def groups(self, diagonal: bool) -> list[list[int]]:
        cols, rows, cells = self.cols, self.rows, self.cells
        neigh = _NEIGH8 if diagonal else _NEIGH4
        seen = bytearray(len(cells))
        out: list[list[int]] = []
        for i in range(len(cells)):
            if seen[i]:
                continue
            k = cells[i]
            seen[i] = 1
            stack, comp = [i], []
            while stack:
                p = stack.pop()
                comp.append(p)
                r, c = divmod(p, cols)
                for dr, dc in neigh:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        q = rr * cols + cc
                        if not seen[q] and cells[q] == k:
                            seen[q] = 1
                            stack.append(q)
            out.append(comp)
        return out

    # shared ---------------------------------------------------------------------------

    def collapse(self) -> None:
        cols, rows, cells, rng, kinds = self.cols, self.rows, self.cells, self.rng, self.kinds
        for c in range(cols):
            column = [cells[r * cols + c] for r in range(rows) if cells[r * cols + c] >= 0]
            fresh = [rng.randrange(kinds) for _ in range(rows - len(column))]
            for r, k in enumerate(fresh + column):
                cells[r * cols + c] = k

    def reshuffle(self) -> None:
        self.rng.shuffle(self.cells)


@dataclass
class BoardRules:
    rule: str
    min_group: int
    diagonal: bool
    combo_bonus: float
    group_bonus: float


def board_moves(board: Board, rules: BoardRules) -> list[tuple[int, Any]]:
    """(gain, move) pairs; gain is the immediate number of cleared cells."""
    if rules.rule == "swap":
        return [(gain, (i, j)) for gain, i, j in board.swap_moves()]
    return [(len(g), g) for g in board.groups(rules.diagonal) if len(g) >= rules.min_group]


def apply_move(board: Board, rules: BoardRules, move: Any, collect_kind: int | None
               ) -> tuple[float, int, int]:
    """Resolve one move completely. Returns (score units, collected, cascade steps)."""
    cells = board.cells
    score, collected, steps = 0.0, 0, 0
    if rules.rule == "swap":
        i, j = move
        cells[i], cells[j] = cells[j], cells[i]
        while steps < 60:
            runs = board._runs()
            if not runs:
                break
            if collect_kind is not None:
                collected += sum(1 for p in runs if cells[p] == collect_kind)
            score += len(runs) * (1.0 + rules.combo_bonus * steps)
            for p in runs:
                cells[p] = -1
            board.collapse()
            steps += 1
        return score, collected, steps
    group = move
    if collect_kind is not None and cells[group[0]] == collect_kind:
        collected = len(group)
    extra = max(0, len(group) - rules.min_group)
    score = len(group) * (1.0 + rules.group_bonus * extra)
    for p in group:
        cells[p] = -1
    board.collapse()
    return score, collected, 1


def clone_board(board: Board, rng: random.Random) -> Board:
    copy = Board.__new__(Board)
    copy.cols, copy.rows, copy.kinds, copy.rule = board.cols, board.rows, board.kinds, board.rule
    copy.rng = rng
    copy.cells = board.cells[:]
    return copy


def skilled_choice(board: Board, rules: BoardRules, moves: list[tuple[int, Any]],
                   look_rng: random.Random, collect_kind: int | None, top_k: int = 6) -> Any:
    """One-ply lookahead: resolve each of the best candidates on a copy (cascades included) and
    prefer the move that scores well AND leaves a strong next move — what a practised player does."""
    ranked = sorted(moves, key=lambda gm: gm[0], reverse=True)[:top_k]
    best_val, best_move = float("-inf"), ranked[0][1]
    for _, move in ranked:
        sim = clone_board(board, look_rng)
        units, got, _ = apply_move(sim, rules, move, collect_kind)
        potential = max((g for g, _ in board_moves(sim, rules)), default=0)
        value = units + 0.5 * potential + 2.0 * got
        if value > best_val:
            best_val, best_move = value, move
    return best_move


def play_board_level(level: dict, rules: BoardRules, points_per_piece: float, rng: random.Random,
                     skill: float, skilled: bool = False) -> dict:
    """Play one attempt. The player bot takes the best immediate move with probability `skill`
    and a random valid move otherwise; the skilled bot always looks one move ahead."""
    board = Board(level["cols"], level["rows"], level["kinds"], rng, rules.rule)
    target = level.get("target_score")
    collect = level.get("collect")
    collect_kind = collect["kind"] if collect else None
    need = collect["count"] if collect else 0
    score = 0.0
    collected = dead = 0
    for used in range(1, level["moves"] + 1):
        moves = board_moves(board, rules)
        tries = 0
        while not moves:
            dead += 1
            tries += 1
            board.reshuffle() if tries < 20 else board.fill()
            moves = board_moves(board, rules)
            if tries >= 100 and not moves:
                raise ConfigError("no playable board after 100 reshuffles; check dimensions/group size")
        if skilled:
            move = skilled_choice(board, rules, moves, random.Random(rng.random()), collect_kind)
        elif rng.random() < skill:
            best = max(g for g, _ in moves)
            move = rng.choice([m for g, m in moves if g == best])
        else:
            move = rng.choice(moves)[1]
        units, got, _ = apply_move(board, rules, move, collect_kind)
        score += units * points_per_piece
        collected += got
        if (target is None or score >= target) and collected >= need:
            return {"passed": True, "moves_used": used, "score": score, "dead": dead}
    return {"passed": False, "moves_used": level["moves"], "score": score, "dead": dead}


def model_b1(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    rule = require(cfg, "rule", str)
    if rule not in ("swap", "link", "blast"):
        raise ConfigError("B1 built-in rules are swap | link | blast; simulate other G1 mechanics "
                          "in the game's own Dart bot and grade it with --model report")
    rules = BoardRules(
        rule=rule,
        min_group=int(cfg.get("min_group", 2 if rule == "blast" else 3)),
        diagonal=bool(cfg.get("diagonals", False)),
        combo_bonus=float(cfg.get("combo_bonus", 0.5)),
        group_bonus=float(cfg.get("group_bonus", 0.1)),
    )
    ppp = float(cfg.get("points_per_piece", 10))
    levels = require(cfg, "levels", list)
    if cfg.get("dead_board") != "reshuffle":
        report.add(Metric("Dead-board policy declared", 0, '"dead_board": "reshuffle"', FAIL, INT,
                          note="a board with no move must reshuffle automatically"))
    skill = float(cfg.get("player_skill", 0.6))
    report.method = (f"{rule} board simulation — player bot (best immediate move with p={skill:g}, "
                     "otherwise a random valid move) and skilled bot (one-move lookahead with "
                     "cascades); simplified rules without specials or boosters; estimated player curve")
    rows_out, curve = [], []
    dead_total = moves_total = 0
    skilled_trials = max(1, args.trials // 2)
    for idx, level in enumerate(levels):
        where = f"levels[{idx}]"
        for key in ("cols", "rows", "kinds", "moves"):
            require(level, key, int, where)
            if level[key] <= 0:
                raise ConfigError(f"{where}: `{key}` must be positive")
        if rules.min_group < 2 or rules.min_group > level["cols"] * level["rows"]:
            raise ConfigError(f"{where}: min_group does not fit the board")
        if rule == "swap" and max(level["cols"], level["rows"]) < 3:
            raise ConfigError(f"{where}: swap boards need a row or column of at least 3")
        if level.get("target_score") is None and not level.get("collect"):
            raise ConfigError(f"{where}: needs `target_score` and/or `collect`")
        if level["kinds"] < 3:
            raise ConfigError(f"{where}: `kinds` must be at least 3")
        rng = random.Random((args.seed or 0) * 1_000_003 + idx)
        player = [play_board_level(level, rules, ppp, rng, skill) for _ in range(args.trials)]
        skilled = [play_board_level(level, rules, ppp, rng, 1.0, skilled=True)
                   for _ in range(skilled_trials)]
        p_rate = sum(r["passed"] for r in player) / len(player)
        s_rate = sum(r["passed"] for r in skilled) / len(skilled)
        dead_total += sum(r["dead"] for r in player)
        moves_total += sum(r["moves_used"] for r in player)
        lid = level.get("id", idx + 1)
        curve.append({"id": lid, "pass_rate": p_rate, "skilled_rate": s_rate})
        goal = []
        if level.get("target_score") is not None:
            goal.append(f"{level['target_score']:,} pts")
        if level.get("collect"):
            goal.append(f"collect {level['collect']['count']}×k{level['collect']['kind']}")
        rows_out.append([lid, f"{level['cols']}×{level['rows']}", level["kinds"], level["moves"],
                         " + ".join(goal), f"{p_rate:.0%}", f"{s_rate:.0%}",
                         f"{median([r['score'] for r in player]):,.0f}"])
    grade_level_curve(report, curve)
    dead_rate = dead_total / moves_total * 100 if moves_total else 0.0
    report.add(Metric("Dead boards per 100 moves", dead_rate, "reported (reshuffle handles them)",
                      PASS, "{:.2f}"))
    report.table("Levels", ["Level", "Board", "Kinds", "Moves", "Goal", "Player bot", "Skilled bot",
                            "Median score"], rows_out)


# --------------------------------------------------------------------------------------
# B2 — solvable deals (G2: sort puzzle built in; others via report)
# --------------------------------------------------------------------------------------


def sort_deal(level: dict, rng: random.Random) -> tuple[tuple[int, ...], ...]:
    kinds, cap, empty = level["kinds"], level["capacity"], level.get("empty", 2)
    pieces = [k for k in range(kinds) for _ in range(cap)]
    rng.shuffle(pieces)
    filled = [tuple(pieces[i * cap:(i + 1) * cap]) for i in range(kinds)]
    return tuple(filled + [()] * empty)


def sort_solved(state: tuple[tuple[int, ...], ...], cap: int) -> bool:
    return all(not t or (len(t) == cap and len(set(t)) == 1) for t in state)


def sort_next(state: tuple[tuple[int, ...], ...], cap: int, pour_all: bool
              ) -> Iterable[tuple[tuple[int, ...], ...]]:
    for a, src in enumerate(state):
        if not src or (len(src) == cap and len(set(src)) == 1):
            continue
        top = src[-1]
        run = 1
        if pour_all:
            while run < len(src) and src[-1 - run] == top:
                run += 1
        uniform = len(set(src)) == 1
        for b, dst in enumerate(state):
            if a == b or len(dst) >= cap or (dst and dst[-1] != top):
                continue
            if not dst and uniform:
                continue  # moving a single-kind stack into an empty container changes nothing
            k = min(run, cap - len(dst))
            nxt = list(state)
            nxt[a] = src[:-k]
            nxt[b] = dst + (top,) * k
            yield tuple(nxt)


def sort_solve(start: tuple[tuple[int, ...], ...], cap: int, pour_all: bool, node_cap: int
               ) -> int | None | str:
    """Minimum moves (BFS), None when provably unsolvable, "cap" when the search gave up."""
    if sort_solved(start, cap):
        return 0
    key = lambda s: tuple(sorted(s))  # noqa: E731 — containers are interchangeable
    seen = {key(start)}
    frontier = deque([(start, 0)])
    while frontier:
        state, depth = frontier.popleft()
        for nxt in sort_next(state, cap, pour_all):
            k = key(nxt)
            if k in seen:
                continue
            if sort_solved(nxt, cap):
                return depth + 1
            seen.add(k)
            if len(seen) > node_cap:
                return "cap"
            frontier.append((nxt, depth + 1))
    return None


def model_b2(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    rule = require(cfg, "rule", str)
    if rule != "sort":
        raise ConfigError("B2's built-in rule is `sort`; tile tray, pairs and patience deals are "
                          "solved by the game's own Dart solver — grade them with --model report")
    policy = cfg.get("generator", "verify")
    if policy not in ("verify", "reverse", "raw"):
        raise ConfigError('`generator` must be "verify", "reverse" or "raw"')
    pour_all = cfg.get("pour", "all") == "all"
    node_cap = int(cfg.get("search_cap", 150_000))
    max_par = float(cfg.get("max_par", 60))
    levels = require(cfg, "levels", list)
    report.method = (f"sort-puzzle breadth-first solver over {args.trials} sampled deals per level "
                     f"(pour={'all matching' if pour_all else 'one piece'}, generator={policy})")
    rows_out, par_curve = [], []
    worst_raw, worst_id, capped = 1.0, None, 0
    for idx, level in enumerate(levels):
        where = f"levels[{idx}]"
        for key in ("kinds", "capacity"):
            require(level, key, int, where)
        rng = random.Random((args.seed or 0) * 7919 + idx)
        results = [sort_solve(sort_deal(level, rng), level["capacity"], pour_all, node_cap)
                   for _ in range(args.trials)]
        solved = [r for r in results if isinstance(r, int)]
        capped += sum(1 for r in results if r == "cap")
        raw = len(solved) / len(results)
        lid = level.get("id", idx + 1)
        if raw < worst_raw:
            worst_raw, worst_id = raw, lid
        par = median(solved) if solved else None
        par_curve.append({"id": lid, "par": par})
        rows_out.append([lid, level["kinds"], level["capacity"], level.get("empty", 2),
                         f"{raw:.0%}", "—" if par is None else f"{par:.0f}"])
    if policy == "raw":
        report.add(Metric("Shipped deals solvable (raw generator)", worst_raw, "100%",
                          PASS if worst_raw >= 1.0 else FAIL, PCT,
                          note=f"level {worst_id}" if worst_id is not None else ""))
    else:
        report.add(Metric("Raw deals solvable (generator rejects the rest)", worst_raw,
                          "≥ 50% (0% means the level cannot be generated)",
                          PASS if worst_raw >= 0.5 else CONCERNS if worst_raw > 0 else FAIL, PCT,
                          note=f"level {worst_id}" if worst_id is not None else ""))
    report.add(Metric("Searches that hit the node cap", capped, "0 (undecided deals)",
                      PASS if not capped else CONCERNS, INT))
    report.add(Metric("Levels in the curve", len(levels), "≥ 12 (≥ 3 minimum)",
                      PASS if len(levels) >= 12 else CONCERNS if len(levels) >= 3 else FAIL, INT))
    grade_par_curve(report, par_curve, max_par)
    report.table("Levels", ["Level", "Kinds", "Capacity", "Empty", "Raw solvable", "Median par"],
                 rows_out)
    report.notes.append("Completion by a real player is not simulated here: with undo and a "
                        "solvable deal every attempt can finish; difficulty is carried by par.")


# --------------------------------------------------------------------------------------
# B3 — run length (G3: slide merge built in; others via report)
# --------------------------------------------------------------------------------------


def slide_line(line: list[int]) -> tuple[list[int], int]:
    tiles = [t for t in line if t]
    out: list[int] = []
    merges = 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] + 1)
            merges += 1
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (len(line) - len(out)), merges


def slide(grid: list[int], size: int, direction: int) -> tuple[list[int], int]:
    """direction: 0 left, 1 right, 2 up, 3 down."""
    out = grid[:]
    merges = 0
    for k in range(size):
        if direction in (0, 1):
            idx = [k * size + c for c in range(size)]
        else:
            idx = [r * size + k for r in range(size)]
        if direction in (1, 3):
            idx.reverse()
        line, m = slide_line([grid[i] for i in idx])
        merges += m
        for i, v in zip(idx, line):
            out[i] = v
    return out, merges


def spawn_tile(grid: list[int], rng: random.Random, tiers: list[int], weights: list[float]) -> None:
    empty = [i for i, v in enumerate(grid) if not v]
    if empty:
        grid[rng.choice(empty)] = rng.choices(tiers, weights)[0]


def slide_value(grid: list[int], size: int) -> float:
    """The usual corner strategy: open space, rows/columns that descend away from the top-left
    corner, and the highest tier kept in that corner."""
    mono = 0
    for k in range(size):
        row = grid[k * size:(k + 1) * size]
        col = grid[k::size]
        mono += sum(1 for a, b in zip(row, row[1:]) if a >= b)
        mono += sum(1 for a, b in zip(col, col[1:]) if a >= b)
    return grid.count(0) * 3 + mono + (6 if grid[0] == max(grid) else 0)


def play_slide_run(size: int, tiers: list[int], weights: list[float], rng: random.Random,
                   skill: float, max_moves: int) -> tuple[int, int]:
    grid = [0] * (size * size)
    spawn_tile(grid, rng, tiers, weights)
    spawn_tile(grid, rng, tiers, weights)
    moves = 0
    while moves < max_moves:
        options = []
        for d in range(4):
            nxt, merges = slide(grid, size, d)
            if nxt != grid:
                options.append((slide_value(nxt, size) + merges, nxt))
        if not options:
            break
        if rng.random() < skill:
            best = max(v for v, _ in options)
            grid = rng.choice([g for v, g in options if v == best])
        else:
            grid = rng.choice(options)[1]
        spawn_tile(grid, rng, tiers, weights)
        moves += 1
    return moves, max(grid)


def model_b3(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    rule = require(cfg, "rule", str)
    if rule != "slide":
        raise ConfigError("B3's built-in rule is `slide`; drop merge, block place and merge grid "
                          "runs come from the game's own Dart bot — grade them with --model report")
    size = int(require(cfg, "size", int))
    spawn = require(cfg, "spawn", list)
    tiers = [int(s["tier"]) for s in spawn]
    weights = [float(s["weight"]) for s in spawn]
    goal = int(require(cfg, "goal_tier", int))
    sec_per_move = float(cfg.get("seconds_per_move", 1.2))
    skill = float(cfg.get("player_skill", 0.6))
    max_moves = int(cfg.get("max_moves", 5000))
    report.method = (f"slide-merge runs on a {size}×{size} grid — player bot (corner-strategy move "
                     f"with p={skill:g}, otherwise random) and skilled bot (always the corner-strategy "
                     f"move); {sec_per_move:g} s per move")
    rng = random.Random(args.seed or 0)
    player = [play_slide_run(size, tiers, weights, rng, skill, max_moves) for _ in range(args.trials)]
    skilled = [play_slide_run(size, tiers, weights, rng, 1.0, max_moves)
               for _ in range(max(1, args.trials // 2))]
    session_min = median([m for m, _ in player]) * sec_per_move / 60
    report.add(Metric("Median session (player bot)", session_min, "2–12 min",
                      within(session_min, 2, 12, 1, 20), "{:.1f} min"))
    early = sum(1 for m, _ in player if m < 40) / len(player)
    report.add(Metric("Runs over within 40 moves", early, "≤ 10% (a fair start)",
                      at_most(early, 0.10, 0.25), PCT))
    reach = sum(1 for _, t in skilled if t >= goal) / len(skilled)
    report.add(Metric(f"Skilled bot reaches the goal tier {goal}", reach,
                      "2–70% (hard but possible)",
                      PASS if 0.02 <= reach <= 0.70 else FAIL if reach == 0 else CONCERNS, PCT))
    milestone = goal - 3
    feel = sum(1 for _, t in player if t >= milestone) / len(player)
    report.add(Metric(f"Player bot reaches tier {milestone} (goal − 3)", feel,
                      "≥ 50% (progress is felt)", at_least(feel, 0.50, 0.30), PCT))
    counts: dict[int, int] = {}
    for _, t in player:
        counts[t] = counts.get(t, 0) + 1
    report.table("Highest tier reached (player bot)", ["Tier", "Runs", "Share"],
                 [[t, n, f"{n / len(player):.0%}"] for t, n in sorted(counts.items())])


# --------------------------------------------------------------------------------------
# B5 — reflex ramp (G5)
# --------------------------------------------------------------------------------------


def ease(x: float, curve: str) -> float:
    x = min(1.0, max(0.0, x))
    if curve == "ease_in":
        return x * x
    if curve == "ease_out":
        return 1 - (1 - x) * (1 - x)
    return x


def play_reflex_run(tempo: dict, player: dict, lives: int, grace: float, rng: random.Random,
                    max_s: float) -> float:
    t = grace
    cap_t = float(tempo["time_to_cap_s"])
    curve = tempo.get("curve", "linear")
    mean, sd = float(player["reaction_ms_mean"]), float(player["reaction_ms_sd"])
    lapse = float(player.get("lapse_rate", 0.01))
    while t < max_s:
        p = ease(t / cap_t, curve)
        interval = tempo["interval_start_s"] + (tempo["interval_cap_s"] - tempo["interval_start_s"]) * p
        window = tempo["window_start_ms"] + (tempo["window_cap_ms"] - tempo["window_start_ms"]) * p
        t += interval
        reaction = max(120.0, rng.gauss(mean, sd))
        if rng.random() < lapse or reaction > window:
            lives -= 1
            if lives <= 0:
                return t
    return max_s


def model_b5(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    tempo = require(cfg, "tempo", dict)
    for key in ("interval_start_s", "interval_cap_s", "window_start_ms", "window_cap_ms",
                "time_to_cap_s"):
        require(tempo, key, (int, float), "tempo")
    player = cfg.get("player", {"reaction_ms_mean": 430, "reaction_ms_sd": 90, "lapse_rate": 0.01})
    lives = int(cfg.get("lives", 1))
    grace = float(cfg.get("grace_s", 3.0))
    report.method = (f"reaction-window model: an average player (reaction {player['reaction_ms_mean']}"
                     f"±{player['reaction_ms_sd']} ms, lapse {player.get('lapse_rate', 0.01):.0%}) "
                     f"against the configured tempo ramp; {lives} life/lives, {grace:g} s grace")
    rng = random.Random(args.seed or 0)
    runs = [play_reflex_run(tempo, player, lives, grace, rng, 3600.0) for _ in range(args.trials)]
    grade_endless(report, runs, time_to_cap_s=float(tempo["time_to_cap_s"]))
    rows_out = []
    for lo, hi in ((0, 10), (10, 30), (30, 60), (60, 120), (120, 300), (300, 3601)):
        n = sum(1 for s in runs if lo <= s < hi)
        rows_out.append([f"{lo}–{hi if hi < 3601 else '∞'}", n, f"{n / len(runs):.0%}"])
    report.table("Run length distribution", ["Seconds", "Runs", "Share"], rows_out)


# --------------------------------------------------------------------------------------
# report — grade a bot report from the game's own headless simulation (B1–B6)
# --------------------------------------------------------------------------------------


def model_report(cfg: dict, args: argparse.Namespace, report: Report) -> None:
    model = require(cfg, "model", str).lower()
    if model not in {"b1", "b2", "b3", "b4", "b5", "b6"}:
        raise ConfigError("bot report must declare its B1–B6 model")
    if args.model != "report" and args.model != model:
        raise ConfigError("bot report model differs from the selected model")
    require(cfg, "bot", str)
    report.method = f"bot report from the game's own simulation — {cfg.get('bot', 'bot not described')}"
    levels = cfg.get("levels") or []
    endless = cfg.get("endless")
    if not levels and not endless:
        raise ConfigError("a bot report needs `levels` and/or `endless`")
    if model in {"b1", "b2", "b4", "b6"} and not levels:
        raise ConfigError(f"{model} requires a level curve")
    if model in {"b3", "b5"} and not endless:
        raise ConfigError(f"{model} requires endless run evidence")
    if levels:
        curve, rows_out = [], []
        unsolvable = []
        for idx, lv in enumerate(levels):
            where = f"levels[{idx}]"
            runs = require(lv, "runs", int, where)
            passes = require(lv, "passes", int, where)
            if runs <= 0 or not 0 <= passes <= runs:
                raise ConfigError(f"{where}: needs 0 ≤ passes ≤ runs and runs > 0")
            entry = {"id": lv.get("id", idx + 1), "pass_rate": passes / runs, "par": lv.get("par")}
            skilled_runs = require(lv, "skilled_runs", int, where)
            skilled_passes = require(lv, "skilled_passes", int, where)
            if skilled_runs <= 0 or not 0 <= skilled_passes <= skilled_runs:
                raise ConfigError(f"{where}: needs 0 ≤ skilled_passes ≤ skilled_runs and skilled_runs > 0")
            entry["skilled_rate"] = skilled_passes / skilled_runs
            if model in {"b2", "b6"}:
                require(lv, "solvable", bool, where)
                par = require(lv, "par", (int, float), where)
                if par <= 0:
                    raise ConfigError(f"{where}: par must be positive")
            curve.append(entry)
            if lv.get("solvable") is False:
                unsolvable.append(entry["id"])
            rows_out.append([entry["id"], runs, f"{entry['pass_rate']:.0%}",
                             "—" if "skilled_rate" not in entry else f"{entry['skilled_rate']:.0%}",
                             "—" if lv.get("par") is None else lv["par"],
                             {True: "yes", False: "NO", None: "—"}[lv.get("solvable")]])
        if any("solvable" in lv for lv in levels):
            report.add(Metric("Levels proven solvable", len(levels) - len(unsolvable),
                              f"all {len(levels)}", PASS if not unsolvable else FAIL, INT,
                              note=("unsolvable: " + ", ".join(map(str, unsolvable))) if unsolvable else ""))
        grade_level_curve(report, curve)
        grade_par_curve(report, curve, float(cfg.get("max_par", 60)))
        report.table("Levels", ["Level", "Runs", "Player bot", "Skilled bot", "Par", "Solvable"],
                     rows_out)
    if endless:
        runs = require(endless, "runs", int, "endless")
        if runs <= 0:
            raise ConfigError("endless.runs must be positive")
        if model == "b3":
            sm = require(endless, "session_minutes", (int, float), "endless")
            report.add(Metric("Median session", sm, "2–12 min", within(sm, 2, 12, 1, 20), "{:.1f} min"))
            for key in ("early_move_rate", "skilled_goal_rate", "player_milestone_rate"):
                value = require(endless, key, (int, float), "endless")
                if not 0 <= value <= 1:
                    raise ConfigError(f"endless.{key} must be in [0, 1]")
            early, reach, feel = (endless[k] for k in
                                  ("early_move_rate", "skilled_goal_rate", "player_milestone_rate"))
            report.add(Metric("Runs over within 40 moves", early, "≤ 10%", at_most(early, .10, .25), PCT))
            report.add(Metric("Skilled bot reaches goal tier", reach, "2–70%",
                              PASS if .02 <= reach <= .70 else FAIL if reach == 0 else CONCERNS, PCT))
            report.add(Metric("Player bot reaches goal − 3", feel, "≥ 50%", at_least(feel, .50, .30), PCT))
        else:
            for key in ("median_run_s", "p90_run_s", "early_death_rate", "time_to_cap_s"):
                require(endless, key, (int, float), "endless")
            if not 0 <= endless["early_death_rate"] <= 1:
                raise ConfigError("endless.early_death_rate must be in [0, 1]")
            if endless["median_run_s"] < 0 or endless["p90_run_s"] < endless["median_run_s"]:
                raise ConfigError("endless run percentiles must be nonnegative and ordered")
            grade_endless(report, None, median_s=endless["median_run_s"],
                          p90_s=endless["p90_run_s"], early_rate=endless["early_death_rate"],
                          time_to_cap_s=endless["time_to_cap_s"])


# --------------------------------------------------------------------------------------
# entry points
# --------------------------------------------------------------------------------------


def _report_only(model: str, category: str) -> Callable[[dict, argparse.Namespace, Report], None]:
    def run_model(cfg: dict, args: argparse.Namespace, report: Report) -> None:
        levels = cfg.get("levels")
        if cfg.get("endless") or (levels and isinstance(levels[0], dict) and "runs" in levels[0]):
            model_report(cfg, args, report)
            return
        raise ConfigError(f"{model} ({category}) has no built-in simulator: run the game's own "
                          "headless bot (test/balance/bot_sim_test.dart) and grade its report with "
                          "--model report --config design/balance/bot-report.json")
    return run_model


MODELS: dict[str, tuple[str, Callable[[dict, argparse.Namespace, Report], None], int]] = {
    "b1": ("B1 — Board simulation (G1)", model_b1, 40),
    "b2": ("B2 — Solvable deals (G2)", model_b2, 20),
    "b3": ("B3 — Run length (G3)", model_b3, 200),
    "b4": ("B4 — Shot simulation (G4)", _report_only("B4", "G4"), 0),
    "b5": ("B5 — Reflex ramp (G5)", model_b5, 2000),
    "b6": ("B6 — Solver curve (G6)", _report_only("B6", "G6"), 0),
    "report": ("Bot report (B1–B6, graded)", model_report, 0),
}


def stamp(path: Path, cfg: dict, verdict: str, model: str) -> None:
    cfg = dict(cfg)
    sim = dict(cfg.get("simulation") or {})
    sim.update({"last_run_date": date.today().isoformat(), "last_verdict": verdict, "model": model})
    cfg["simulation"] = sim
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{cfg_path} is not valid JSON: {exc}") from exc
    if not isinstance(cfg, dict):
        raise ConfigError(f"{cfg_path} must hold a JSON object")
    label, fn, default_trials = MODELS[args.model]
    if args.model != "report" and cfg.get("model", args.model) != args.model:
        raise ConfigError("config model differs from --model")
    if args.trials is None:
        args.trials = default_trials
    if default_trials and args.trials <= 0:
        raise ConfigError("--trials must be positive")
    def finite_numbers(value: Any) -> None:
        if isinstance(value, float) and not math.isfinite(value):
            raise ConfigError("config numbers must be finite")
        if isinstance(value, dict):
            for child in value.values():
                finite_numbers(child)
        elif isinstance(value, list):
            for child in value:
                finite_numbers(child)
    finite_numbers(cfg)
    report = Report(model=label, title=cfg.get("game_name", cfg_path.stem), config_path=args.config,
                    method="", trials=args.trials, seed=args.seed)
    check_no_gambling(cfg, report)
    fn(cfg, args, report)

    md = report.to_markdown()
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.to_json() if out.suffix.lower() == ".json" else md, encoding="utf-8")
    if not args.no_stamp:
        stamp(cfg_path, cfg, report.verdict, args.model)
    print(md)
    print(f"Report saved: {out}")
    return _VERDICT_EXIT[report.verdict]


# --------------------------------------------------------------------------------------
# self-test — every built-in model on the reference configs in the studio templates
# --------------------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / ".claude/docs/templates/balance-configs"
SELFTEST: tuple[tuple[str, str, int], ...] = (
    ("b1", "board-levels-config.json", 30),
    ("b2", "sort-levels-config.json", 6),
    ("b3", "slide-merge-config.json", 40),
    ("b5", "reflex-ramp-config.json", 600),
    ("report", "bot-report-example.json", 0),
)


def selftest() -> int:
    import tempfile

    failures = 0
    for model, name, trials in SELFTEST:
        src = TEMPLATE_DIR / name
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / name
            cfg_path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            args = argparse.Namespace(model=model, config=str(cfg_path), trials=trials, seed=7,
                                      report=str(Path(tmp) / "report.md"), no_stamp=False)
            try:
                code = run(args)
            except Exception as exc:  # noqa: BLE001 — self-test reports, does not crash
                failures += 1
                print(f"\n!!! {model} ({name}) crashed: {type(exc).__name__}: {exc}\n{'=' * 78}")
                continue
            if code == 2:
                failures += 1
            print(f"\n>>> {MODELS[model][0]} on {name}: exit {code}\n{'=' * 78}")
    print(f"\nSelf-test: {len(SELFTEST)} reference configs, {failures} failures")
    return 1 if failures else 0


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Balance verifier for the casual game studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Models: " + "; ".join(f"{k} = {v[0]}" for k, v in MODELS.items()),
    )
    p.add_argument("--model", choices=sorted(MODELS), help="which balance model to verify")
    p.add_argument("--config", help="the model's JSON config (or the bot report for --model report)")
    p.add_argument("--trials", type=int, default=None, help="runs per level / per model (model default)")
    p.add_argument("--seed", type=int, default=7, help="seed for the simulations (default 7)")
    p.add_argument("--report", default="design/balance/simulation-report.md",
                   help="where to write the report (.json for structured JSON; otherwise Markdown)")
    p.add_argument("--no-stamp", action="store_true",
                   help="do not write the date/verdict into the config's `simulation` block")
    p.add_argument("--selftest", action="store_true", help="run every built-in model on the templates")
    args = p.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.model or not args.config:
        p.error("--model and --config are required (or --selftest)")
    try:
        return run(args)
    except ConfigError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"❌ file not found: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
