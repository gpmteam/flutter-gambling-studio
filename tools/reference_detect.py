#!/usr/bin/env python3
"""
reference_detect.py — is this game request a request to rebuild a reference, and
which mechanic governs play?

A reference request is the one case where the studio must NOT invent a look: the
user wants *that* game's character, sprites and symbols, frame and background.
Leaving this decision to a model reading a docs table was fuzzy in exactly the
cases that matter: a name typed in Russian ("джокер", "плинко"), a possessive
("Joker's Jewels"), a hyphenated folder name, or images attached to the chat
with no name at all. Every miss produced a re-themed game the user rejected.

The studio builds casual games only (.claude/rules/no-gambling.md). Most
references are casino slot art: their LOOK is reproduced exactly, their
GAMEPLAY never is. This tool therefore also decides the mechanic:

  1. NAMED FAMILY  — the local `examples-games/` families from
                     `.claude/docs/game-concept-examples.md`, matched on
                     English and Russian spellings, possessives, hyphens and
                     run-together names. Joker Jewels is tested before Joker.
                     Each family names the casual mechanic it is built as,
                     whether its own gameplay is a casino game (look only) or
                     already casual (reused), and its fidelity: `exact`
                     families are recreated, `loose` ones (Royal Joker) are a
                     common reference for the game's world, not a recreation.
  2. ATTACHMENTS   — images the user attached to the request (the web service
                     stores them under `design/references/user/`).
  3. PHRASING      — an explicit "same as / copy / recreate / по референсу /
                     один в один" ask, which binds attachments on follow-up
                     requests and flags an unmapped title on a new one.
  4. MECHANIC      — a casual mechanic the user named ("Book of Ra match-3")
                     governs play; a gambling mechanic the user named ("Book of
                     Ra dice", "a roulette game") is translated to its casual
                     equivalent (`.claude/docs/game-categories.md` →
                     "Translating a gambling ask"). The reference still governs
                     identity.

Detection only ever adds obligations. An agent may add a reference this tool
missed; it may not drop one this tool found, and it may not build the casino
mechanic a reference shows.

Usage:
  python3 tools/reference_detect.py --prompt "Make Joker Jewels" --new-game --json
  python3 tools/reference_detect.py --prompt-file request.txt \\
      --attachments-dir design/references/user --new-game --markdown \\
      > design/reference-contract.md

`binding` is `exact` when an exact family or binding attachments are present, `loose` when
only loose families matched, `description` for an unmapped title to copy, else `none`.

Exit codes: 0 = ran (read `reference` and `mechanic` in the output), 2 = bad invocation.
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
    # "casino": the preview shows a gambling game — only its look is reproduced.
    # "casual": the preview's own gameplay is casual and is reused with its topology.
    reference_gameplay: str
    # The mechanic the preview itself shows ("slot", "plinko", "link chain").
    reference_mechanic: str
    aliases: tuple[str, ...]
    # Families whose match makes this one redundant (Joker inside Joker Jewels).
    shadowed_by: tuple[str, ...] = ()
    # "exact": recreate the sources. "loose": a common reference — the game shares the sources'
    # world and background treatment, with its own character, symbols and composition.
    fidelity: str = "exact"
    # Family-specific direction carried into the contract and the worker's directive.
    guidance: str = ""
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
                    "symbol family, purple reel-strip colour for the board columns, frame"),
            RefFile("examples-games/joker-jewels/jj_character-reference.jpeg",
                    "jester lead: striped costume, three-point belled cap, painted face"),
            RefFile("examples-games/joker-jewels/jj_character-reference2.jpeg",
                    "jester lead: second pose, juggling gesture"),
        ),
        classification="G1 / A / B1",
        topology="7x8",
        lead_kind="character",
        default_mechanic="swap match-3",
        reference_gameplay="casino",
        reference_mechanic="slot",
        aliases=(
            r"jokers? jewels?",
            r"jokersjewels?",
            r"jokerjewels?",
            r"джокер\w* (?:джуэл|джевел|джувел|джуел)\w*",
            r"драгоценност\w* джокер\w*",
        ),
    ),
    Family(
        id="royal-joker",
        name="Royal Joker",
        files=(
            RefFile("examples-games/royal-joker/rj_key-art.jpeg",
                    "jester lead and backdrop: grinning jester in a purple-and-gold belled cap "
                    "over a warm red diamond-pattern glow with flames and gold light"),
            RefFile("examples-games/royal-joker/rj_store-set-1.jpeg",
                    "symbol family and mood: plums, oranges, cherries, stars, crowns, jester "
                    "medallions and a gold frame under lightning on a red-to-violet glow"),
            RefFile("examples-games/royal-joker/rj_store-set-2.jpeg",
                    "second jester pose; cherries, sevens and card suits in gold light streaks"),
        ),
        classification="G1 / C / B1",
        topology="7x8",
        lead_kind="character",
        default_mechanic="tap blast",
        reference_gameplay="casino",
        reference_mechanic="slot",
        # A plain "Joker" resolves here too; Joker Jewels keeps its own folder.
        aliases=(r"royal ?jokers?", r"(?:роял|ройал) джокер\w*", r"королевск\w* джокер\w*",
                 r"jokers?", r"джокер\w*"),
        shadowed_by=("joker-jewels",),
        fidelity="loose",
        guidance=("A common reference, not a recreation: keep its world — a grinning, mischievous "
                  "jester lead, fruit, seven, crown, star and gem symbols, gold trim and glow — "
                  "and design the character, symbols and composition fresh. The background is "
                  "the reference's own: a warm red-orange-to-magenta glow with a diamond pattern, "
                  "flames, gold light streaks and lightning. Never a palace, castle, ballroom, "
                  "throne room or curtained stage."),
    ),
    Family(
        id="book-of-ra",
        name="Book of Ra",
        files=(RefFile("examples-games/book-of-ra.png",
                       "explorer lead, relic symbol cast, sunset temple, gold-and-lapis frame"),),
        classification="G2 / E / B2",
        topology="layered tile pile + 7-slot tray",
        lead_kind="character",
        default_mechanic="triple tile",
        reference_gameplay="casino",
        reference_mechanic="slot",
        aliases=(r"book of ra", r"bookofra", r"книг\w* ра", r"бук оф ра"),
    ),
    Family(
        id="shining-crown",
        name="Shining Crown",
        files=(RefFile("examples-games/shining-crown.jpeg",
                       "crown, jewel star, clover gem, ruby, royal gold frame; no character"),),
        classification="G3 / I / B3",
        topology="4x4",
        lead_kind="object",
        default_mechanic="slide merge",
        reference_gameplay="casino",
        reference_mechanic="slot",
        aliases=(r"shining crown", r"shiningcrown", r"шайнинг краун", r"сияющ\w* корон\w*"),
    ),
    Family(
        id="plinko",
        name="Plinko",
        files=(RefFile("examples-games/plinko.jpeg",
                       "tilted peg field, glossy balls, glowing trails; no character"),),
        classification="G4 / N / B4",
        topology="peg field",
        lead_kind="mechanic",
        default_mechanic="peg clear",
        reference_gameplay="casino",
        reference_mechanic="plinko",
        aliases=(r"plinko\w*", r"плинко"),
    ),
)

# A casual mechanic the user named governs play and topology; the reference still
# governs the look. Order matters: specific names come before generic words.
CASUAL_MECHANICS: tuple[tuple[str, str, re.Pattern[str]], ...] = tuple(
    (name, archetype, re.compile(pattern)) for name, archetype, pattern in (
        ("swap match-3", "G1 / A", r"(?<!\w)(?:match ?3|match three|swap match\w*|bejeweled|"
                                   r"candy crush|три в ряд|3 в ряд)(?!\w)"),
        ("link chain", "G1 / B", r"(?<!\w)(?:link chain|chain link|link (?:the )?symbols|two dots|"
                                 r"connect (?:the )?(?:symbols|dots)|соедин\w* (?:символ|фишк)\w*|"
                                 r"цепочк\w*)(?!\w)"),
        ("tap blast", "G1 / C", r"(?<!\w)(?:tap ?blast|toon blast|tap (?:the )?groups?|same ?game|"
                                r"collapse)(?!\w)"),
        ("rotate match", "G1 / D", r"(?<!\w)(?:hexic|rotate match\w*)(?!\w)"),
        ("triple tile", "G2 / E", r"(?<!\w)(?:triple tile|tile (?:match|master|tray)|zen match|"
                                  r"три плитки)(?!\w)"),
        ("pair tiles", "G2 / F", r"(?<!\w)(?:mahjong|маджонг|маджонг\w*|pair tiles)(?!\w)"),
        ("sort puzzle", "G2 / G", r"(?<!\w)(?:(?:ball|water|color|colour) sort|sort puzzle|"
                                  r"sorting|сортировк\w*)(?!\w)"),
        ("card patience", "G2 / H", r"(?<!\w)(?:solitaire|patience|tri ?peaks|пасьянс\w*|"
                                    r"косынк\w*)(?!\w)"),
        ("slide merge", "G3 / I", r"(?<!\w)(?:2048|slide merge)(?!\w)"),
        ("drop merge", "G3 / J", r"(?<!\w)(?:suika|drop merge|watermelon game|арбуз\w*)(?!\w)"),
        ("block place", "G3 / K", r"(?<!\w)(?:block (?:blast|puzzle|place\w*)|1010|tetris|"
                                  r"тетрис\w*|блок пазл\w*)(?!\w)"),
        ("merge grid", "G3 / L", r"(?<!\w)(?:merge|мерж\w*|слиян\w*)(?!\w)"),
        ("bubble shooter", "G4 / M", r"(?<!\w)(?:bubble\w*|пузыр\w*|бабл\w*)(?!\w)"),
        ("peg clear", "G4 / N", r"(?<!\w)(?:peggle|peg clear)(?!\w)"),
        ("brick breaker", "G4 / O", r"(?<!\w)(?:brick breaker|breakout|arkanoid|арканоид\w*)(?!\w)"),
        ("knockdown", "G4 / P", r"(?<!\w)(?:angry birds|slingshot|knock ?down|рогатк\w*)(?!\w)"),
        ("draw & guide", "G4 / Q", r"(?<!\w)(?:cut the rope|draw (?:a )?(?:line|path)s?)(?!\w)"),
        ("lane runner", "G5 / R", r"(?<!\w)(?:runner|endless run\w*|crossy|road cross\w*|subway|"
                                  r"раннер\w*|бегалк\w*)(?!\w)"),
        ("stacker", "G5 / S", r"(?<!\w)(?:stacker|stack game|stacking|стакер\w*)(?!\w)"),
        ("catcher", "G5 / T", r"(?<!\w)(?:catcher|catch (?:the )?falling|ловилк\w*)(?!\w)"),
        ("slicer", "G5 / U", r"(?<!\w)(?:slicer|slice|fruit ninja|нарезк\w*)(?!\w)"),
        ("one-tap flyer", "G5 / V", r"(?<!\w)(?:flappy|one ?tap fly\w*|флаппи)(?!\w)"),
        ("target throw", "G5 / W", r"(?<!\w)(?:knife hit|knife throw\w*|darts?|метани\w* нож\w*|"
                                   r"дротик\w*)(?!\w)"),
        ("connect paths", "G6 / X", r"(?<!\w)(?:flow free|connect (?:the )?pairs|соедини пары)(?!\w)"),
        ("rotate pipes", "G6 / Y", r"(?<!\w)(?:pipes?|infinity loop|трубы|трубопровод\w*)(?!\w)"),
        ("unblock", "G6 / Z", r"(?<!\w)(?:unblock|rush hour|sliding block\w*)(?!\w)"),
        ("memory match", "G6 / AA", r"(?<!\w)(?:memory|мемори|найди пар\w*)(?!\w)"),
        ("logic grid", "G6 / AB", r"(?<!\w)(?:minesweeper|nonogram\w*|sudoku|судоку|"
                                  r"японск\w* кроссворд\w*)(?!\w)"),
    )
)

# A gambling mechanic the user named. It is never built: it is translated to the casual mechanic
# on the right (.claude/docs/game-categories.md → "Translating a gambling ask"). When the request
# also names a family whose built mechanic sits in the translation's category — "Joker slot",
# "Joker Jewels slot" — the family's own casual mechanic is kept.
GAMBLING_MECHANICS: tuple[tuple[str, str, str, re.Pattern[str]], ...] = tuple(
    (name, translation, category, re.compile(pattern)) for name, translation, category, pattern in (
        ("dice", "slide merge", "G3", r"(?<!\w)(?:dice|die roll\w*|кост(?:и|ей|ях|ями)|кубик\w*)(?!\w)"),
        # "crash" alone is usually a bug report ("fix the crash"); the game is "a crash game".
        ("crash", "one-tap flyer", "G5", r"(?<!\w)(?:crash (?:game|gambl\w*|multiplier)|краш\w*)(?!\w)"),
        ("mines", "logic grid", "G6", r"(?<!\w)(?:mines|minefield|мины)(?!\w)"),
        ("hi-lo", "card patience", "G2", r"(?<!\w)(?:hi ?lo|higher or lower|high or low|high card|"
                                         r"выше (?:или )?ниже|больше (?:или )?меньше)(?!\w)"),
        ("tower", "stacker", "G5", r"(?<!\w)(?:tower climb|tower|башн\w*)(?!\w)"),
        ("keno", "logic grid", "G6", r"(?<!\w)(?:keno|кено)(?!\w)"),
        ("scratch", "memory match", "G6", r"(?<!\w)(?:scratch\w*|скретч\w*|стиралк\w*)(?!\w)"),
        ("roulette", "target throw", "G5", r"(?<!\w)(?:roulette|рулетк\w*)(?!\w)"),
        ("blackjack", "card patience", "G2", r"(?<!\w)(?:black ?jack|блэк ?джек\w*|блекджек\w*)(?!\w)"),
        ("poker", "card patience", "G2", r"(?<!\w)(?:video poker|poker|покер\w*)(?!\w)"),
        ("bingo", "logic grid", "G6", r"(?<!\w)(?:bingo|бинго)(?!\w)"),
        ("wheel", "target throw", "G5", r"(?<!\w)(?:(?:prize |fortune )?wheel|колес\w*)(?!\w)"),
        ("plinko", "peg clear", "G4", r"(?<!\w)(?:plinko|плинко)(?!\w)"),
        ("coin pusher", "knockdown", "G4", r"(?<!\w)(?:coin ?pusher|coin dozer|пушер\w*)(?!\w)"),
        ("pachinko", "peg clear", "G4", r"(?<!\w)(?:pachinko|пачинко)(?!\w)"),
        ("gacha", "memory match", "G6", r"(?<!\w)(?:gacha|loot ?box\w*|card packs?|capsules?|case open\w*|гач\w*|"
                                           r"лутбокс\w*)(?!\w)"),
        ("slot", "swap match-3", "G1", r"(?<!\w)(?:slots?|slot machine|reels?|pokies|слот\w*|"
                                       r"барабан\w*|игров\w* автомат\w*)(?!\w)"),
        ("betting", "", "", r"(?<!\w)(?:bet|bets|betting|wager\w*|stake|jackpot|casino|"
                             r"ставк\w*|казино|джекпот\w*)(?!\w)"),
    )
)
CASUAL_BY_NAME = {name: archetype for name, archetype, _ in CASUAL_MECHANICS}
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


def match_casual(norm: str) -> list[str]:
    return [name for name, _, pattern in CASUAL_MECHANICS if pattern.search(norm)]


def match_gambling(norm: str) -> list[tuple[str, str, str]]:
    return [(name, translation, category)
            for name, translation, category, pattern in GAMBLING_MECHANICS if pattern.search(norm)]


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
    casual = match_casual(norm)
    gambling = match_gambling(norm)
    grid = match_grid(norm)
    phrasing = match_phrasing(norm)
    images = list_images(root, attachments or [], attachments_dir)

    # Attached images are the reference on a new game: a user who attaches a
    # picture to "make me a match-3" is showing the game they want. On a follow-up
    # an image may just be a bug screenshot, so it binds only when the message
    # asks to match it.
    images_bind = bool(images) and (new_game or bool(phrasing))

    # Which mechanic governs play. A casual mechanic the user named wins. A gambling
    # mechanic is translated — unless it is only the family's own casino gameplay or
    # its translation lands in the category the family is already built in ("Joker
    # slot" stays Joker's tap blast). Otherwise the family's casual mechanic governs.
    family = families[0][0] if families else None
    family_category = family.classification.split("/")[0].strip() if family else ""
    asks = [(name, tr, cat) for name, tr, cat in gambling if tr]
    mechanic: str | None = None
    override: str | None = None
    topology_source = "concept"
    if casual:
        mechanic = casual[0]
        if not family or mechanic != family.default_mechanic:
            override = mechanic
            topology_source = "user mechanic"
        else:
            topology_source = "family"
    else:
        # "Joker slot with a prize wheel bonus" is still the Joker game: once the user names the
        # family's own mechanic, the other gambling words describe features, not a new core.
        names_own = bool(family) and any(name == family.reference_mechanic for name, _, _ in gambling)
        foreign = [] if names_own else [
            (name, tr, cat) for name, tr, cat in asks
            if not family or (name != family.reference_mechanic and cat != family_category)]
        if foreign:
            mechanic = override = foreign[0][1]
            topology_source = "translated"
        elif family:
            mechanic = family.default_mechanic
            topology_source = "family"
        elif asks:
            mechanic = asks[0][1]
            topology_source = "translated"
    if topology_source in ("family", "concept") and grid:
        if not family or grid != family.topology:
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
        "binding": "exact" if (images_bind or any(f.fidelity == "exact" for f, _ in families))
                   else "loose" if families
                   else "description" if unmapped_title else "none",
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
                "reference_gameplay": family.reference_gameplay,
                "reference_mechanic": family.reference_mechanic,
                "fidelity": family.fidelity,
                "guidance": family.guidance,
                "files": [{"path": f.path, "role": f.role} for f in family.files],
                "missing_files": [f.path for f in family.files if not (root / f.path).is_file()],
            }
            for family, matched in families
        ],
        "attachments": [{"path": rel(root, p), "bytes": p.stat().st_size} for p in images],
        "attachments_bind": images_bind,
        "phrasing": phrasing,
        "mechanics": casual,
        "gambling_asks": [name for name, _, _ in gambling],
        "mechanic": mechanic,
        "mechanic_archetype": CASUAL_BY_NAME.get(mechanic or ""),
        "mechanic_override": override,
        "grid": grid,
        "topology_source": topology_source,
    }


def mechanic_lines(result: dict) -> list[str]:
    lines = ["## Mechanic and topology", ""]
    if result["families"]:
        family = result["families"][0]
        look = ("its look is a common reference" if family.get("fidelity") == "loose"
                else "its look is reproduced")
        own = (f"casino game — {look}, its gameplay is not"
               if family["reference_gameplay"] == "casino" else
               "casual — its gameplay and topology are reused")
        lines.append(f"- Reference gameplay: {family['reference_mechanic']} ({own})")
        lines.append(f"- Family build: {family['default_mechanic']} — {family['classification']}, "
                     f"{family['topology']}, lead `{family['lead_kind']}`")
    lines.append(f"- User-named casual mechanics: {', '.join(result['mechanics']) or 'none'}"
                 + (f"; grid {result['grid']}" if result["grid"] else ""))
    if result["gambling_asks"]:
        lines.append(f"- Gambling asks (never built — `.claude/rules/no-gambling.md`): "
                     f"{', '.join(result['gambling_asks'])}")
    source = result["topology_source"]
    mechanic = result["mechanic"]
    archetype = f" ({result['mechanic_archetype']})" if result.get("mechanic_archetype") else ""
    if source == "user mechanic":
        lines.append(f"- Governs play: the user's `{mechanic}`{archetype} mechanic. The reference "
                     "governs identity only: character, symbols/sprites, board and frame "
                     "materials, background, palette and finish.")
    elif source == "translated":
        lines.append(f"- Governs play: `{mechanic}`{archetype}, the casual translation of the "
                     "gambling ask (`.claude/docs/game-categories.md` → \"Translating a gambling "
                     "ask\"). Say so in the concept and the final report.")
    elif source == "user grid":
        lines.append(f"- Governs play: {mechanic or 'the concept'}{archetype} on the user's "
                     f"{result['grid']} grid when the mechanic can be played on it; record any "
                     "adjustment and why.")
    elif source == "family":
        lines.append(f"- Governs play: the family build above — `{mechanic}`{archetype}.")
    else:
        lines.append("- Governs play: the concept (no family, no named mechanic).")
    return lines


def to_markdown(result: dict) -> str:
    lines = ["# Reference contract", ""]
    if not result["reference"]:
        lines += ["- Detected: no — no named family, binding attachment or reproduction ask.",
                  "- The concept and Design DNA govern the look.", ""]
        if result["gambling_asks"] or result["mechanics"]:
            lines += mechanic_lines(result) + [""]
        return "\n".join(lines)
    binding = {
        "exact": "EXACT — the finished game's art must read as the same world as these sources",
        "loose": "LOOSE — a common reference, not a recreation: the game shares these sources' "
                 "world, mood, palette, light and background treatment; its character, symbols "
                 "and composition are designed fresh within that world",
    }.get(result["binding"], "DESCRIPTION — the user named a game with no local image; match "
                             "every described visual trait and record that no pixels were "
                             "available")
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
    for family in result["families"]:
        if family.get("guidance"):
            lines += ["", f"**{family['name']} direction:** {family['guidance']}"]
    lines += [""] + mechanic_lines(result)
    if result["binding"] == "loose":
        return "\n".join(lines + loose_contract_lines())
    lines += [
        "", "## Identity ledger (fill in at full size before Phase 3)", "",
        "- Character: costume colours and pattern, headwear shape and bell count, face paint, "
        "build, pose, expression — source:",
        "- Symbol / sprite cast, object for object (they become tiles, pieces, balls or targets):",
        "",
        "| Reference object | Source image | Game asset path | Role in the casual mechanic | Match verdict |",
        "|---|---|---|---|---|",
        "", "- Frame and board materials (a slot's reel frame becomes the board frame; reel strips "
        "become the column backing):",
        "- Background and environment:",
        "- Palette and light:",
        "- Finish (2D/2.5D, linework, shading, texture):",
        "- UI materials (buttons, panels, frame ornament):",
        "", "## Not carried over (production limits)", "",
        "- Title, wordmark, logo and operator branding",
        "- The casino mechanic and interface: spinning reels, paylines, bet/credit panels, "
        "SPIN/AUTOPLAY, paytables and payout figures",
        "", "## Gates", "",
        "- [ ] Phase 3: every identity asset generated from its source image "
        "(`tools/gpt_image.py edit --image <source> --fidelity high` or the built-in edit path)",
        "- [ ] Phase 3.6 AR11 side-by-side with the sources: PASS",
        "- [ ] Runtime V21 side-by-side (menu, idle, active): PASS",
        "- [ ] `.claude/rules/no-gambling.md`: no wager, currency or chance-based reward",
        "- [ ] Campaign art: sources attached to the banner and background calls",
        "",
    ]
    return "\n".join(lines)


def loose_contract_lines() -> list[str]:
    """The rest of the contract for a common reference: shared traits instead of a copy ledger."""
    return [
        "", "## Shared world (fill in at full size before Phase 3)", "",
        "- Character: the lead's archetype, attitude and signature colours kept from the sources; "
        "what is designed fresh (face, pose, costume details):",
        "- Symbol family: the kinds of objects kept (they become tiles, pieces, balls or targets); "
        "the game's own set and how it differs:",
        "- Background and environment: the sources' own treatment, followed closely:",
        "- Palette and light:",
        "- Finish (2D/2.5D, linework, shading, texture):",
        "", "## Not carried over (production limits)", "",
        "- Title, wordmark, logo and operator branding",
        "- The casino mechanic and interface: spinning reels, paylines, bet/credit panels, "
        "SPIN/AUTOPLAY, paytables, prize wheels and payout figures",
        "- Object-for-object copies: a loose reference is not recreated asset by asset",
        "", "## Gates", "",
        "- [ ] Phase 3: the sources are attached to generation as style references (editing a "
        "source is allowed, not required); assets are designed for this game",
        "- [ ] Phase 3.6 AR11 (loose): the set reads as the sources' world — character archetype, "
        "symbol family, palette, light, background — without one-for-one copies: PASS",
        "- [ ] Runtime V21 (loose): the menu and gameplay share that world and its background "
        "treatment: PASS",
        "- [ ] `.claude/rules/no-gambling.md`: no wager, currency or chance-based reward",
        "- [ ] Campaign art: sources attached to the banner and background calls; the background "
        "follows the sources' treatment",
        "",
    ]


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
