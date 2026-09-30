#!/usr/bin/env python3
"""Static casual-game gate for code, game data and store copy.

Exit 0 for clean files, 2 for violations. This catches common regressions; review
the actual mechanic and reference translation as well. Art/reference docs are
deliberately outside the scan, so decorative coins and casino source images remain valid.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from simulate_balance import forbidden_keys, split_key

MECHANIC_WORDS = {
    "bet", "bets", "betting", "wager", "wagers", "stake", "stakes", "jackpot",
    "payout", "payouts", "paytable", "rtp", "gacha", "roulette", "blackjack", "poker",
}
MECHANIC_JOINED = (
    "cashout", "houseedge", "lootbox", "freespin", "slotmachine", "coinbalance",
    "chipbalance", "gembalance", "creditbalance", "agegate", "responsiblegambling",
)
COPY = re.compile(
    r"\b(?:bet(?:s|ting)?|wager(?:s)?|jackpot|payout(?:s)?|paytable|cash[ -]?out|house[ -]?edge|"
    r"rtp|gacha|loot[ -]?box(?:es)?|free[ -]?spins?|roulette|blackjack|poker|"
    r"slot[ -]?machine|spin to win|max bet|double or nothing)\b", re.I)
CURRENCY = re.compile(
    r"\b(?:wallet|currency|coinBalance|chipBalance|gemBalance|creditBalance|"
    r"startingCoins|startingChips|startingCredits)\b|"
    r"\b(?:coins?|chips?|gems?|credits?|balance)\b.{0,100}\b"
    r"(?:spend|price|purchase|afford|deduct)\b", re.I)
MONEY_SCORE = re.compile(r"\$\{?(?:score|points)|(?:USD|EUR|€|₽)\s*\$?\{?(?:score|points)", re.I)
# Keep strings intact while removing comments, so URLs and // inside strings survive.
DART_PARTS = re.compile(
    r'''r?"""[\s\S]*?"""|r?''' + "'''[\\s\\S]*?'''" +
    r'''|r?"(?:\\.|[^"\\])*"|r?'(?:\\.|[^'\\])*'|//[^\n]*|/\*[\s\S]*?\*/''')


def without_comments(text: str) -> str:
    return DART_PARTS.sub(lambda m: re.sub(r"[^\n]", " ", m[0])
                         if m[0].startswith(("//", "/*")) else m[0], text)


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for directory, suffixes in (("lib", {".dart"}), ("assets/data", {".json"}),
                                ("design/balance", {".json"}), ("store", {".md", ".txt", ".json"})):
        for path in sorted((root / directory).rglob("*")):
            if not path.is_file() or path.suffix not in suffixes:
                continue
            rel = path.relative_to(root)
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                try:
                    data = json.loads(text)
                except ValueError:
                    findings.append(f"{rel}: invalid JSON")
                    continue
                findings.extend(f"{rel}: forbidden config field {key}" for key in forbidden_keys(data))
            if path.suffix == ".dart":
                text = without_comments(text)
            for num, line in enumerate(text.splitlines(), 1):
                bad = COPY.search(line) or CURRENCY.search(line) or MONEY_SCORE.search(line)
                if path.suffix == ".dart" and not bad:
                    for identifier in re.findall(r"\b[A-Za-z_]\w*\b", line):
                        words = split_key(identifier)
                        if MECHANIC_WORDS.intersection(words) or any(
                                term in "".join(words) for term in MECHANIC_JOINED):
                            bad = identifier
                            break
                if bad:
                    label = bad if isinstance(bad, str) else bad[0]
                    findings.append(f"{rel}:{num}: gambling/currency marker {label!r}")
                if path.suffix == ".dart" and re.search(r"\bRandom\s*(?:\.secure)?\s*\(", line):
                    if path.name not in {"game_rng.dart", "vfx_rng.dart"}:
                        findings.append(f"{rel}:{num}: RNG constructor outside GameRng/VfxRng")
                    elif path.name == "game_rng.dart" and re.search(
                            r"\bRandom\s*(?:\.secure\s*\([^)]*\)|\(\s*\))", line):
                        findings.append(f"{rel}:{num}: GameRng must use an explicit seed")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    findings = scan(args.root)
    if findings:
        print("FAIL — casual-game gate:")
        print("\n".join(findings))
        return 2
    print("PASS — static no-gambling/seeded-RNG checks; review actual gameplay as well.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
