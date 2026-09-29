#!/usr/bin/env python3
"""
reference_detect.py — is this game request a request to rebuild a reference?

A reference request is the one case where the studio must NOT invent: the user
wants *that* game — its character, its sprites and symbols, its reel strips and
board, its background and finish. Leaving this decision to a model reading a
docs table was fuzzy in exactly the cases that matter: a name typed in Russian
("джокер", "зевс"), a possessive ("Joker's Jewels"), a hyphenated folder name,
or images attached to the chat with no name at all. Every miss produced a
re-themed game that the user then had to reject.

This tool makes the detection deterministic and prints what the pipeline must
do with it:

  1. NAMED FAMILY  — the local `examples-games/` families from
                     `.claude/docs/game-concept-examples.md`, matched on
                     English and Russian spellings, possessives, hyphens and
                     run-together names. Joker Jewels is tested before Joker.
  2. ATTACHMENTS   — images the user attached to the request (the web service
                     stores them under `design/references/user/`).
  3. PHRASING      — an explicit "same as / copy / recreate / по референсу /
                     один в один" ask, which binds attachments on follow-up
                     requests and flags an unmapped title on a new one.
  4. MECHANIC      — a mechanic or grid the user named that differs from the
                     family's default ("Zeus Lightning Dice", "Joker hi-lo",
                     "Joker slot 5x3"). The user's mechanic then governs play
                     and topology; the reference still governs identity.

Detection only ever adds obligations. An agent may add a reference this tool
missed; it may not drop one this tool found.

Usage:
  python3 tools/reference_detect.py --prompt "Make Joker Jewels" --new-game --json
  python3 tools/reference_detect.py --prompt-file request.txt \\
      --attachments-dir design/references/user --new-game --markdown \\
      > design/reference-contract.md

Exit codes: 0 = ran (read `reference` in the output), 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
USER_REFERENCE_DIR = "design/references/user"
# Written by older web-service releases straight into the repository root.
LEGACY_ATTACHMENT_GLOB = "user_reference*"


@dataclass(frozen=True)
class RefFile:
    path: str
    role: str


@dataclass(frozen=True)
class Family:
    id: str
    name: str
    files: tuple[RefFile, ...]
    classification: str
    topology: str
    lead_kind: str
    default_mechanic: str
    aliases: tuple[str, ...]
    # Families whose match makes this one redundant (Joker inside Joker Jewels).
    shadowed_by: tuple[str, ...] = ()
    patterns: tuple[re.Pattern[str], ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        compiled = tuple(re.compile(rf"(?<!\w){alias}(?!\w)") for alias in self.aliases)
        object.__setattr__(self, "patterns", compiled)


# Order matters: the first family whose alias matches wins over the families it
# shadows. Aliases run against `normalize()`d text: lower case, ё→е, no
# apostrophes, hyphens/underscores/dots as spaces, single spaces.
FAMILIES: tuple[Family, ...] = (
    Family(
        id="joker-jewels",
        name="Joker Jewels",
        files=(
            RefFile("examples-games/joker-jewels/jj_reference.jpeg",
                    "key-art staging: festive purple stage, bunting, confetti, mask with gems"),
            RefFile("examples-games/joker-jewels/jj_gameplay.jpeg",
                    "5x3 board, purple reel strips and the complete symbol family"),
            RefFile("examples-games/joker-jewels/jj_character-reference.jpeg",
                    "jester lead: striped costume, three-point belled cap, painted face"),
            RefFile("examples-games/joker-jewels/jj_character-reference2.jpeg",
                    "jester lead: second pose, juggling gesture"),
        ),
        classification="C1 / B / M1",
        topology="5x3",
        lead_kind="character",
        default_mechanic="slot",
        aliases=(
            r"jokers? jewels?",
            r"jokersjewels?",
            r"jokerjewels?",
            r"джокер\w* (?:джуэл|джевел|джувел|джуел)\w*",
            r"драгоценност\w* джокер\w*",
        ),
    ),
    Family(
        id="joker",
        name="Joker",
        files=(
            RefFile("examples-games/joker2.png", "primary: the Joker character, symbols and board"),
            RefFile("examples-games/joker.jpeg", "secondary: supporting palette and symbols"),
        ),
        classification="C1 / A / M1",
        topology="3x3",
        lead_kind="character",
        default_mechanic="slot",
        aliases=(r"jokers?", r"джокер\w*"),
        shadowed_by=("joker-jewels",),
    ),
    Family(
        id="book-of-ra",
        name="Book of Ra",
        files=(RefFile("examples-games/book-of-ra.png",
                       "explorer lead, relic symbol cast, sunset temple, 5x3 board"),),
        classification="C1 / B / M1",
        topology="5x3",
        lead_kind="character",
        default_mechanic="slot",
        aliases=(r"book of ra", r"bookofra", r"книг\w* ра", r"бук оф ра"),
    ),
    Family(
        id="shining-crown",
        name="Shining Crown",
        files=(RefFile("examples-games/shining-crown.jpeg",
                       "crown, jewel star, clover gem, ruby; reels; no character"),),
        classification="C1 / A / M1",
        topology="3x3",
        lead_kind="object",
        default_mechanic="slot",
        aliases=(r"shining crown", r"shiningcrown", r"шайнинг краун", r"сияющ\w* корон\w*"),
    ),
    Family(
        id="zeus",
        name="Zeus Game",
        files=(RefFile("examples-games/zeus.jpeg",
                       "thunder-god lead, eagle/bolt/laurel symbols, Olympus sky, 7x6 board"),),
        classification="C1 / C / M1",
        topology="7x6",
        lead_kind="character",
        default_mechanic="slot",
        aliases=(r"zeus\w*", r"зевс\w*"),
    ),
    Family(
        id="plinko",
        name="Plinko",
        files=(RefFile("examples-games/plinko.jpeg",
                       "tilted peg field, glossy balls, buckets, charged coins; no character"),),
        classification="C6 / AE / M6",
        topology="peg field",
        lead_kind="mechanic",
        default_mechanic="plinko",
        aliases=(r"plinko\w*", r"плинко"),
    ),
)

# A mechanic the user named. When it differs from the family's default, the
# user's mechanic governs play and topology; the reference still governs look.
MECHANICS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern)) for name, pattern in (
        ("dice", r"(?<!\w)(?:dice|die roll\w*|кост(?:и|ей|ях|ями)|кубик\w*)(?!\w)"),
        ("crash", r"(?<!\w)(?:crash|краш\w*)(?!\w)"),
        ("mines", r"(?<!\w)(?:mines?|minefield|мины|сапер\w*)(?!\w)"),
        ("hi-lo", r"(?<!\w)(?:hi ?lo|higher or lower|high or low|high card|"
                  r"выше (?:или )?ниже|больше (?:или )?меньше)(?!\w)"),
        ("tower", r"(?<!\w)(?:tower climb|tower|башн\w*)(?!\w)"),
        ("keno", r"(?<!\w)(?:keno|кено)(?!\w)"),
        ("scratch", r"(?<!\w)(?:scratch\w*|скретч\w*|стиралк\w*)(?!\w)"),
        ("roulette", r"(?<!\w)(?:roulette|рулетк\w*)(?!\w)"),
        ("blackjack", r"(?<!\w)(?:black ?jack|блэк ?джек\w*|блекджек\w*)(?!\w)"),
        ("poker", r"(?<!\w)(?:video poker|poker|покер\w*)(?!\w)"),
        ("bingo", r"(?<!\w)(?:bingo|бинго)(?!\w)"),
        ("wheel", r"(?<!\w)(?:(?:prize |fortune )?wheel|колес\w*)(?!\w)"),
        ("plinko", r"(?<!\w)(?:plinko|плинко)(?!\w)"),
        ("coin pusher", r"(?<!\w)(?:coin ?pusher|coin dozer|пушер\w*)(?!\w)"),
        ("pachinko", r"(?<!\w)(?:pachinko|пачинко)(?!\w)"),
        ("gacha", r"(?<!\w)(?:gacha|loot ?box\w*|case open\w*|гач\w*|лутбокс\w*)(?!\w)"),
        ("slot", r"(?<!\w)(?:slots?|reels?|слот\w*|барабан\w*)(?!\w)"),
    )
)
GRID_RE = re.compile(r"(?<!\d)(\d{1,2}) ?[x×х*] ?(\d{1,2})(?!\d)")

# An explicit ask to reproduce something. Deliberately specific: "like", "copy"
# and "такой же" are everywhere in ordinary requests ("I'd like", "compliance
# copy", "такой же баланс"), so they only count inside fixed phrases.
PHRASING: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(pattern)) for label, pattern in (
        ("same as", r"(?<!\w)(?:exactly like|identical to|the same as (?:the|this|that|in)|"
                    r"exactly the same as|just like (?:the|this|that|in))(?!\w)"),
        ("copy/clone", r"(?<!\w)(?:copy (?:the|this|that|these|it)|copy of|clone of|clone|"
                       r"replica of|recreate|reproduce|remake of|one to one|1 ?: ?1|"
                       r"pixel perfect)(?!\w)"),
        ("from references", r"(?<!\w)(?:references?|reference images?|from (?:the|these|this|my) "
                            r"(?:images?|pictures?|screenshots?|photos?|examples?)|based on (?:the|these|this|my) "
                            r"(?:images?|pictures?|screenshots?|photos?|game))(?!\w)"),
        ("по референсу", r"(?<!\w)(?:референс\w*|по (?:образц|пример|картинк|скрин|фото)\w*)(?!\w)"),
        ("как на картинке", r"(?<!\w)как (?:на|в) (?:картинк|скрин|фото|изображени|пример|референс)\w*"),
        ("один в один", r"(?<!\w)(?:один в один|точь в точь|точно так(?:ой|ая|ое|ие|ую)? же|"
                        r"скопиру\w*|копи(?:я|ю|ей) (?:игр|слот)\w*|клон\w*|воссозда\w*)(?!\w)"),
    )
)


def normalize(text: str) -> str:
    """Lower-case, fold ё, drop apostrophes, treat -_./ as spaces, squeeze spaces."""
    text = text.lower().replace("ё", "е")
    text = re.sub(r"['‘’ʼ´`]", "", text)
    text = re.sub(r"[-_./\\]+", " ", text)
    text = re.sub(r"[^\w\s:×*]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def match_families(norm: str) -> list[tuple[Family, str]]:
    found: list[tuple[Family, str]] = []
    for family in FAMILIES:
        for pattern in family.patterns:
            hit = pattern.search(norm)
            if hit:
                found.append((family, hit.group(0)))
                break
    ids = {family.id for family, _ in found}
    return [(f, m) for f, m in found if not any(s in ids for s in f.shadowed_by)]


def match_mechanics(norm: str) -> list[str]:
    return [name for name, pattern in MECHANICS if pattern.search(norm)]


def match_grid(norm: str) -> str | None:
    hit = GRID_RE.search(norm)
    return f"{int(hit.group(1))}x{int(hit.group(2))}" if hit else None


def match_phrasing(norm: str) -> list[str]:
    return [label for label, pattern in PHRASING if pattern.search(norm)]


def list_images(root: Path, attachments: list[str], attachments_dir: str | None) -> list[Path]:
    seen: list[Path] = []
    for raw in attachments:
        path = (root / raw) if not Path(raw).is_absolute() else Path(raw)
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and path not in seen:
            seen.append(path)
    if attachments_dir:
        folder = root / attachments_dir
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and path not in seen:
                    seen.append(path)
    for path in sorted(root.glob(LEGACY_ATTACHMENT_GLOB)):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES and path not in seen:
            seen.append(path)
    return seen


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def detect(prompt: str, *, root: Path, attachments: list[str] | None = None,
           attachments_dir: str | None = None, new_game: bool = False) -> dict:
    norm = normalize(prompt)
    families = match_families(norm)
    mechanics = match_mechanics(norm)
    grid = match_grid(norm)
    phrasing = match_phrasing(norm)
    images = list_images(root, attachments or [], attachments_dir)

    # Attached images are the reference on a new game: a user who attaches a
    # picture to "make me a slot" is showing the game they want. On a follow-up
    # an image may just be a bug screenshot, so it binds only when the message
    # asks to match it.
    images_bind = bool(images) and (new_game or bool(phrasing))

    # "Joker slot with a wheel bonus" is still the Joker slot: once the user
    # names the family's own mechanic, other mechanic words are features.
    override = None
    if families:
        defaults = {family.default_mechanic for family, _ in families}
        if not defaults.intersection(mechanics):
            named = [m for m in mechanics if m not in defaults]
            override = named[0] if named else None
    topology_source = "concept"
    if families:
        family_topology = families[0][0].topology
        if override:
            topology_source = "user mechanic"
        elif grid and grid != family_topology:
            topology_source = "user grid"
        else:
            topology_source = "family"
    elif grid:
        topology_source = "user grid"

    sources = []
    if families:
        sources.append("named family")
    if images_bind:
        sources.append("attached images")
    unmapped_title = bool(phrasing) and not families and not images
    if unmapped_title:
        sources.append("description only")

    return {
        "reference": bool(families or images_bind or unmapped_title),
        "binding": "exact" if (families or images_bind) else
                   ("description" if unmapped_title else "none"),
        "sources": sources,
        "families": [
            {
                "id": family.id,
                "name": family.name,
                "matched": matched,
                "classification": family.classification,
                "topology": family.topology,
                "lead_kind": family.lead_kind,
                "default_mechanic": family.default_mechanic,
                "files": [{"path": f.path, "role": f.role} for f in family.files],
                "missing_files": [f.path for f in family.files if not (root / f.path).is_file()],
            }
            for family, matched in families
        ],
        "attachments": [{"path": rel(root, p), "bytes": p.stat().st_size} for p in images],
        "attachments_bind": images_bind,
        "phrasing": phrasing,
        "mechanics": mechanics,
        "mechanic_override": override,
        "grid": grid,
        "topology_source": topology_source,
    }


def to_markdown(result: dict) -> str:
    lines = ["# Reference contract", ""]
    if not result["reference"]:
        lines += ["- Detected: no — no named family, binding attachment or reproduction ask.",
                  "- The concept and Design DNA govern the look.", ""]
        return "\n".join(lines)
    binding = ("EXACT — the finished game must read as the same game as these sources"
               if result["binding"] == "exact" else
               "DESCRIPTION — the user named a game with no local image; match every "
               "described trait and record that no pixels were available")
    lines += [f"- Detected: yes — {', '.join(result['sources'])}",
              f"- Binding: {binding}",
              f"- Detection: `tools/reference_detect.py` "
              f"(phrasing: {', '.join(result['phrasing']) or 'none'})", ""]
    lines += ["## Sources", "", "| Path | Kind | Role |", "|---|---|---|"]
    for family in result["families"]:
        for ref in family["files"]:
            lines.append(f"| `{ref['path']}` | {family['name']} preview "
                         f"(matched “{family['matched']}”) | {ref['role']} |")
    for att in result["attachments"]:
        kind = "user attachment" if result["attachments_bind"] else "user attachment (context)"
        lines.append(f"| `{att['path']}` | {kind} | [fill in from full-size inspection] |")
    missing = [p for f in result["families"] for p in f["missing_files"]]
    if missing:
        lines += ["", "**Missing mapped files (blocker until restored):** "
                  + ", ".join(f"`{p}`" for p in missing)]
    lines += ["", "## Mechanic and topology", ""]
    if result["families"]:
        family = result["families"][0]
        lines.append(f"- Family default: {family['classification']}, {family['topology']}, "
                     f"lead `{family['lead_kind']}`")
    lines.append(f"- User-named mechanics: {', '.join(result['mechanics']) or 'none'}"
                 + (f"; grid {result['grid']}" if result["grid"] else ""))
    source = result["topology_source"]
    if source == "user mechanic":
        lines.append(f"- Governs play: the user's `{result['mechanic_override']}` mechanic. The "
                     "reference governs identity only: character, symbols/sprites, board and "
                     "frame materials, background, palette and finish.")
    elif source == "user grid":
        lines.append(f"- Governs play: the user's {result['grid']} grid; everything else matches "
                     "the reference.")
    elif source == "family":
        lines.append("- Governs play: the family classification and topology above.")
    else:
        lines.append("- Governs play: the concept (no family topology applies).")
    lines += [
        "", "## Identity ledger (fill in at full size before Phase 3)", "",
        "- Character: costume colours and pattern, headwear shape and bell count, face paint, "
        "build, pose, expression — source:",
        "- Symbol / sprite cast, object for object:", "",
        "| Reference object | Source image | Game asset path | Match verdict |",
        "|---|---|---|---|",
        "", "- Reel strips, board frame and field ornament:",
        "- Background and environment:",
        "- Palette and light:",
        "- Finish (2D/2.5D, linework, shading, texture):",
        "- UI materials (buttons, panels, frame ornament):",
        "", "## Not carried over (production limits)", "",
        "- Title, wordmark, logo and operator branding",
        "- Reference UI copy and paytable figures (the math model sets the numbers)",
        "", "## Gates", "",
        "- [ ] Phase 3: every identity asset generated from its source image "
        "(`tools/gpt_image.py edit --image <source> --fidelity high` or the built-in edit path)",
        "- [ ] Phase 3.6 AR11 side-by-side with the sources: PASS",
        "- [ ] Runtime V21 side-by-side (menu, idle, active): PASS",
        "- [ ] Campaign art: sources attached to the banner and background calls",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    text = parser.add_mutually_exclusive_group(required=True)
    text.add_argument("--prompt", help="the user's request text")
    text.add_argument("--prompt-file", help="a file holding the user's request text")
    parser.add_argument("--attachment", action="append", default=[], metavar="PATH",
                        help="an image attached to THIS request (repeatable)")
    parser.add_argument("--attachments-dir", default=None, metavar="DIR",
                        help=f"also list images saved there (normally {USER_REFERENCE_DIR})")
    parser.add_argument("--new-game", action="store_true",
                        help="a first request for a new game: attached images always bind")
    parser.add_argument("--root", default=".", help="studio/project root (default: cwd)")
    out = parser.add_mutually_exclusive_group()
    out.add_argument("--json", action="store_true", help="print JSON (default)")
    out.add_argument("--markdown", action="store_true",
                     help="print a design/reference-contract.md skeleton")
    args = parser.parse_args(argv)

    if args.prompt_file:
        try:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"reference_detect: cannot read {args.prompt_file}: {exc}", file=sys.stderr)
            return 2
    else:
        prompt = args.prompt

    result = detect(prompt, root=Path(args.root), attachments=args.attachment,
                    attachments_dir=args.attachments_dir, new_game=args.new_game)
    if args.markdown:
        print(to_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
