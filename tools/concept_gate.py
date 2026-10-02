#!/usr/bin/env python3
"""The concept carousel and its approval gate.

`/autocreate` no longer rushes from assets into code. Once the concept, assets and data exist it
renders the store panorama — the same picture `/store-screenshots` would make, sliced into the
same three carousel panels — and stops. The user looks at it and approves it (the web service's
Approve button) or asks for changes. Only an approved carousel unlocks implementation, and that
same panorama then drives everything after it: the game's field is built to look like its
gameplay sample, the game background is rendered in its world, and the store kit exports it
unchanged and makes the banner from it.

This tool keeps that state in `production/store-art/concept/concept.json`, beside the files it
describes, so it survives in every project snapshot:

  publish   record a reviewed panorama + its sliced panels as the PENDING concept (and write
            the small web previews the service shows), with `--known-issue` for anything the
            render budget left unfixed; archives a previous revision first
  budget    fresh renders and region repairs left in the revision being made (3 and 5): the
            user reviews the picture next, so its own review loop is bounded
  revise    archive the PENDING concept before a revision render (status DRAFTING)
  approve   PENDING -> APPROVED, pinned to the panorama's SHA-256 (idempotent when approved)
  status    print the record (`--json` for the service)
  check     `--for implement`: exit 0 only when implementation may start

Statuses: NONE (no record), DRAFTING (a revision is being rendered), PENDING (awaiting the user),
APPROVED. A project made before this gate existed has no record and no `Concept gate: required`
line in its Session 1 handoff; `check --for implement` reports it as LEGACY and lets it through.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_DIR = "production/store-art/concept"
HANDOFF_1 = "production/session-state/autocreate-handoff-1.md"
GATE_MARKER = "Concept gate: required"
STATUSES = ("DRAFTING", "PENDING", "APPROVED")
# The web previews the service copies into the chat. Small on purpose: the chat shows three
# phone-shaped slides and one wide panorama, and the full-size panels stay in the project.
PANEL_PREVIEW_HEIGHT = 1200
PANORAMA_PREVIEW_WIDTH = 2400
PREVIEW_QUALITY = 86
PANEL_SIZE = (1320, 2868)
DEFAULT_LEDGER = "production/store-art/lineage.json"
# The concept panorama's own review is bounded, because the user reviews it the moment it is
# published. Unbounded, one panorama took ten fresh renders and 42 minutes, every one of them
# re-rolling the grid count and the cut placement together. Per revision: fresh renders (each a
# new composition), and region repairs (each one local defect). `tools/art_lineage.py` refuses
# to record the next one once these are spent; crops and re-exports are always free.
FRESH_RENDER_BUDGET = 3
REPAIR_BUDGET = 5
# What a publish may tell the user about the picture it shows, so the card says it, not a log.
MAX_KNOWN_ISSUES = 8
MAX_KNOWN_ISSUE_CHARS = 300


class GateError(RuntimeError):
    """A concept that cannot be published, approved or built from."""


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def record_path(root: Path) -> Path:
    return root / "concept.json"


def load(root: Path) -> dict | None:
    path = record_path(root)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"{path} is not readable JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("status") not in STATUSES:
        raise GateError(f"{path} is not a concept record")
    return data


def save(root: Path, data: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    path = record_path(root)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def rel(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)


def panorama_of(root: Path, data: dict) -> Path:
    return root / data["panorama"]["file"]


def current_panorama_matches(root: Path, data: dict) -> bool:
    path = panorama_of(root, data)
    return path.exists() and sha256(path) == data["panorama"]["sha256"]


def _instant(stamp: str | None) -> _dt.datetime | None:
    try:
        return _dt.datetime.fromisoformat(stamp) if stamp else None
    except ValueError:
        return None


def render_counts(root: Path, records: list[dict]) -> dict:
    """Fresh renders and region repairs of the concept panorama in the revision being made.

    A revision starts when `revise` archives the shown one (`drafting_since`); a first revision
    counts every concept panorama the ledger holds, so a run that resumes an interrupted Session 1
    inherits what the interrupted one already spent.
    """
    data = load(root)
    if data is None:
        revision, since = 1, None
    elif data["status"] == "DRAFTING":
        revision, since = int(data.get("revision", 0)) + 1, _instant(data.get("drafting_since"))
    else:
        revision, since = int(data.get("revision", 1)), _instant(data.get("published_at"))
    concept = root.resolve()
    fresh = repairs = 0
    for record in records:
        if record.get("role") != "panorama" or record.get("made") not in ("fresh", "repair"):
            continue
        path = Path(record.get("path") or "")
        if concept not in (path if path.is_absolute() else Path.cwd() / path).resolve().parents:
            continue
        at = _instant(record.get("recorded_at"))
        if since is not None and (at is None or at < since):
            continue
        if record["made"] == "fresh":
            fresh += 1
        else:
            repairs += 1
    return {"revision": revision, "fresh": fresh, "fresh_budget": FRESH_RENDER_BUDGET,
            "repairs": repairs, "repair_budget": REPAIR_BUDGET}


def budget_refusal(root: Path, records: list[dict], made: str) -> str | None:
    """Why another `made` (fresh|repair) concept panorama may not be recorded, or None."""
    counts = render_counts(root, records)
    spent = {"fresh": (counts["fresh"], FRESH_RENDER_BUDGET, "fresh renders"),
             "repair": (counts["repairs"], REPAIR_BUDGET, "region repairs")}.get(made)
    if spent is None or spent[0] < spent[1]:
        return None
    return (f"the concept panorama's {spent[2]} are spent ({spent[0]} of {spent[1]} in revision "
            f"{counts['revision']}). Choose the best candidate, fix what a crop or re-export can, "
            "and publish it with `concept_gate.py publish --known-issue \"…\"` for anything still "
            "off — the user reviews it next and can ask for a revision")


def archive(root: Path, data: dict) -> Path:
    """Move the recorded revision's files under revisions/rN/ so a new render starts clean."""
    target = root / "revisions" / f"r{data.get('revision', 0)}"
    target.mkdir(parents=True, exist_ok=True)
    for entry in sorted(root.iterdir()):
        if entry.name in ("revisions", "concept.json") or entry.name.endswith(".tmp"):
            continue
        destination = target / entry.name
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        shutil.move(str(entry), str(destination))
    (target / "concept.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return target


def make_previews(root: Path, panorama: Path, panels: list[Path],
                  carousel: Path | None) -> list[dict]:
    from PIL import Image  # only publishing needs Pillow; status/approve/check never do

    out_dir = root / "preview"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    written: list[dict] = []

    def jpeg(src: Path, name: str, *, height: int | None = None, width: int | None = None) -> None:
        with Image.open(src) as image:
            image = image.convert("RGB")
            if height and image.height > height:
                image = image.resize((round(image.width * height / image.height), height),
                                     Image.LANCZOS)
            if width and image.width > width:
                image = image.resize((width, round(image.height * width / image.width)),
                                     Image.LANCZOS)
            target = out_dir / name
            image.save(target, "JPEG", quality=PREVIEW_QUALITY, optimize=True, progressive=True)
            written.append({"file": f"preview/{name}", "width": image.width,
                            "height": image.height, "sha256": sha256(target)})

    for index, panel in enumerate(panels, start=1):
        jpeg(panel, f"panel-{index}.jpg", height=PANEL_PREVIEW_HEIGHT)
    jpeg(panorama, "panorama.jpg", width=PANORAMA_PREVIEW_WIDTH)
    if carousel is not None:
        jpeg(carousel, "carousel.jpg", width=PANORAMA_PREVIEW_WIDTH)
    return written


def cmd_publish(args: argparse.Namespace) -> int:
    from PIL import Image

    root = Path(args.dir)
    project = Path.cwd()
    panorama = Path(args.panorama)
    prompt = Path(args.prompt)
    panels_dir = Path(args.panels)
    sample = Path(args.sample)
    sample_spec = Path(args.sample_spec)
    issues = known_issues(args.known_issue)
    for path, what in ((panorama, "panorama"), (prompt, "panorama prompt"),
                       (sample, "gameplay-sample crop"), (sample_spec, "gameplay-sample spec")):
        if not path.is_file():
            raise GateError(f"missing {what}: {path}")
    for path in (panorama, prompt, sample, sample_spec):
        if root.resolve() not in path.resolve().parents:
            raise GateError(f"{path} must live under {root}/ so it is archived with its revision")
    panels = [panels_dir / f"store-{i:02d}.png" for i in range(1, args.count + 1)]
    for panel in panels:
        if not panel.is_file():
            raise GateError(f"missing carousel panel {panel} — export the panorama with "
                            f"`store_compose.py triptych --panels {args.count}` first")
        with Image.open(panel) as image:
            if image.size != PANEL_SIZE:
                raise GateError(f"{panel} is {image.size[0]}x{image.size[1]}; the carousel is "
                                f"exported at the App Store size {PANEL_SIZE[0]}x{PANEL_SIZE[1]}")
    if not sample_spec.read_text(encoding="utf-8").strip():
        raise GateError(f"{sample_spec} is empty — describe the gameplay sample the game must match")

    ledger = Path(args.ledger)
    if ledger.exists():
        records = json.loads(ledger.read_text(encoding="utf-8")).get("records", [])
        digest = sha256(panorama)
        record = next((r for r in records if r.get("sha256") == digest), None)
        if record is None:
            raise GateError(f"{panorama} is not in {ledger}; record it with "
                            "`tools/art_lineage.py record --role panorama` before publishing")
        if record.get("role") != "panorama" or not 1 <= int(record.get("generation", 99)) <= 2:
            raise GateError(f"{panorama} is recorded as {record.get('role')} generation "
                            f"{record.get('generation')}; a concept panorama is a panorama at "
                            "generation 2 or less")
    else:
        raise GateError(f"no lineage ledger at {ledger}; record the panorama with "
                        "tools/art_lineage.py before publishing")

    previous = load(root)
    revision = 1
    if previous is not None:
        if previous["status"] == "APPROVED":
            raise GateError("the concept is already APPROVED; an approved carousel is not "
                            "replaced — the game, background and store kit are built from it")
        revision = int(previous.get("revision", 0)) + 1
        if previous["status"] == "PENDING" and previous["panorama"]["sha256"] != sha256(panorama):
            raise GateError("a different panorama is still PENDING; run `concept_gate.py revise` "
                            "before rendering a revision so the shown one is archived")
        if previous["status"] == "PENDING":
            revision = int(previous.get("revision", 1))

    carousel = panels_dir / "_carousel-preview.png"
    previews = make_previews(root, panorama, panels, carousel if carousel.is_file() else None)
    with Image.open(panorama) as image:
        pano_size = list(image.size)
    data = {
        "schema_version": SCHEMA_VERSION,
        "status": "PENDING",
        "revision": revision,
        "lead_kind": args.lead_kind,
        "panorama": {"file": rel(panorama, root), "sha256": sha256(panorama),
                     "size": pano_size},
        "prompt": {"file": rel(prompt, root), "sha256": sha256(prompt)},
        "panels": [{"file": rel(p, root), "sha256": sha256(p)} for p in panels],
        "gameplay_sample": {"file": rel(sample, root), "sha256": sha256(sample),
                            "spec": rel(sample_spec, root)},
        "previews": previews,
        "feedback": (previous or {}).get("feedback", []),
        "published_at": now(),
        "approved_at": None,
        "approved_by": None,
        "approved_run": None,
    }
    if args.note:
        data["note"] = args.note
    data["known_issues"] = issues
    save(root, data)
    print(f"✅ concept revision {revision} is PENDING approval — {rel(panorama, project)} "
          f"({len(panels)} panels, sha256 {data['panorama']['sha256'][:12]}…)")
    for issue in data["known_issues"]:
        print(f"   known issue: {issue}")
    return 0


def known_issues(values: list[str] | None) -> list[str]:
    """What is still off in the published picture, one plain sentence each, for the user."""
    issues = [" ".join(v.split()) for v in values or [] if v and v.strip()]
    if len(issues) > MAX_KNOWN_ISSUES:
        raise GateError(f"{len(issues)} known issues; name at most {MAX_KNOWN_ISSUES} — a picture "
                        "with more is not ready to show")
    long = [i for i in issues if len(i) > MAX_KNOWN_ISSUE_CHARS]
    if long:
        raise GateError(f"a known issue is one sentence of at most {MAX_KNOWN_ISSUE_CHARS} "
                        f"characters: {long[0][:60]}…")
    return issues


def cmd_revise(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    data = load(root)
    if data is None:
        print("= no concept recorded yet; nothing to archive")
        return 0
    if data["status"] == "APPROVED":
        raise GateError("the concept is APPROVED and the game is built from it; a revision now "
                        "would orphan the game, the background and the store kit")
    feedback = list(data.get("feedback", []))
    if args.feedback_file:
        text = Path(args.feedback_file).read_text(encoding="utf-8").strip()
        if text:
            feedback.append({"revision": data.get("revision"), "text": text, "at": now()})
    if data["status"] == "PENDING":
        target = archive(root, data)
        print(f"📦 revision {data.get('revision')} archived to {target}")
    data.update({"status": "DRAFTING", "feedback": feedback, "drafting_since": now()})
    save(root, data)
    print("✏️  concept is DRAFTING — render the revision fresh from the original references, "
          "then publish it")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    data = load(root)
    if data is None:
        raise GateError(f"no concept carousel at {record_path(root)} to approve")
    if args.expect_sha and data["panorama"]["sha256"] != args.expect_sha:
        raise GateError("the concept changed since the user saw it: the shown panorama was "
                        f"{args.expect_sha[:12]}…, the recorded one is "
                        f"{data['panorama']['sha256'][:12]}…")
    if not current_panorama_matches(root, data):
        raise GateError(f"{panorama_of(root, data)} no longer matches the panorama the user saw")
    if data["status"] == "APPROVED":
        print(f"= concept revision {data['revision']} was already approved "
              f"({data['approved_at']}, by {data['approved_by']})")
        return 0
    if data["status"] != "PENDING":
        raise GateError(f"the concept is {data['status']}, not PENDING — there is no published "
                        "carousel to approve")
    data.update({"status": "APPROVED", "approved_at": now(), "approved_by": args.by,
                 "approved_run": args.run})
    save(root, data)
    print(f"✅ concept revision {data['revision']} APPROVED — implementation may start")
    return 0


def legacy_project() -> bool:
    handoff = Path(HANDOFF_1)
    return not handoff.exists() or GATE_MARKER not in handoff.read_text(encoding="utf-8")


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    data = load(root)
    if args.json:
        if data is None:
            print(json.dumps({"status": "NONE", "legacy": legacy_project()}))
            return 0
        print(json.dumps({
            "status": data["status"],
            "revision": data.get("revision"),
            "lead_kind": data.get("lead_kind"),
            "panorama_sha256": data["panorama"]["sha256"],
            "panorama_intact": current_panorama_matches(root, data),
            "previews": [p["file"] for p in data.get("previews", [])],
            "approved_at": data.get("approved_at"),
            "known_issues": data.get("known_issues", []),
        }))
        return 0
    if data is None:
        print("NONE — no concept carousel recorded"
              + (" (legacy project: made before the approval gate)" if legacy_project() else ""))
        return 0
    intact = "intact" if current_panorama_matches(root, data) else "CHANGED SINCE PUBLISH"
    print(f"{data['status']} — revision {data.get('revision')}, panorama "
          f"{data['panorama']['file']} ({intact})")
    for issue in data.get("known_issues", []):
        print(f"known issue: {issue}")
    if data.get("approved_at"):
        print(f"approved {data['approved_at']} by {data['approved_by']}")
    return 0


def cmd_budget(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    records: list[dict] = []
    if ledger.exists():
        try:
            records = json.loads(ledger.read_text(encoding="utf-8")).get("records", [])
        except (OSError, json.JSONDecodeError) as exc:
            raise GateError(f"{ledger} is not readable JSON: {exc}") from exc
    counts = render_counts(Path(args.dir), records)
    if args.json:
        print(json.dumps(counts))
        return 0
    fresh_left = counts["fresh_budget"] - counts["fresh"]
    repairs_left = counts["repair_budget"] - counts["repairs"]
    print(f"concept panorama, revision {counts['revision']}: fresh renders "
          f"{counts['fresh']}/{counts['fresh_budget']}, region repairs "
          f"{counts['repairs']}/{counts['repair_budget']}")
    if fresh_left > 0:
        print(f"→ {fresh_left} fresh render(s) left: spend one only on a composition defect that a "
              "crop, a re-export or a region repair cannot fix")
    else:
        print("→ no fresh renders left: choose the best candidate, fix what a crop, a re-export"
              + (f" or a region repair ({repairs_left} left)" if repairs_left > 0 else "")
              + " can, and publish it with --known-issue for anything still off")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    data = load(root)
    if data is None:
        if legacy_project():
            print("LEGACY — this project predates the concept gate; continuing without one")
            return 0
        print("❌ no concept carousel: Session 1 must publish one (autocreate Phase 3.9) and the "
              "user must approve it before implementation", file=sys.stderr)
        return 1
    if data["status"] != "APPROVED":
        print(f"❌ the concept carousel is {data['status']}, not APPROVED — implementation waits "
              "for the user's approval", file=sys.stderr)
        return 1
    if not current_panorama_matches(root, data):
        print(f"❌ {panorama_of(root, data)} changed after approval; the approved panorama is the "
              "contract and may not be altered", file=sys.stderr)
        return 1
    print(f"✅ concept revision {data['revision']} APPROVED — panorama "
          f"{panorama_of(root, data)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", default=DEFAULT_DIR, help=f"concept directory ({DEFAULT_DIR})")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pub = sub.add_parser("publish", help="record the reviewed carousel as PENDING approval")
    pub.add_argument("--panorama", required=True)
    pub.add_argument("--prompt", required=True, help="the rendered panorama prompt file")
    pub.add_argument("--panels", required=True,
                     help="the triptych output directory (store-01.png …, _carousel-preview.png)")
    pub.add_argument("--count", type=int, default=3, help="carousel panel count (default 3)")
    pub.add_argument("--sample", required=True, help="crop of the panorama's gameplay sample")
    pub.add_argument("--sample-spec", required=True, help="gameplay-sample.md")
    pub.add_argument("--lead-kind", required=True, choices=("character", "object", "mechanic"))
    pub.add_argument("--ledger", default=DEFAULT_LEDGER)
    pub.add_argument("--note", default=None)
    pub.add_argument("--known-issue", action="append", default=[],
                     help="one thing still off in this picture, in a plain sentence the user "
                          f"reads on the card (repeatable, at most {MAX_KNOWN_ISSUES})")
    pub.set_defaults(handler=cmd_publish)

    bud = sub.add_parser("budget", help="fresh renders and region repairs left in this revision")
    bud.add_argument("--ledger", default=DEFAULT_LEDGER)
    bud.add_argument("--json", action="store_true")
    bud.set_defaults(handler=cmd_budget)

    rev = sub.add_parser("revise", help="archive the PENDING concept before a revision render")
    rev.add_argument("--feedback-file", default=None)
    rev.set_defaults(handler=cmd_revise)

    app = sub.add_parser("approve", help="PENDING -> APPROVED")
    app.add_argument("--expect-sha", default=None,
                     help="the panorama SHA-256 the user approved; refuses any other")
    app.add_argument("--by", default="user", choices=("user", "service"))
    app.add_argument("--run", default=None, help="the service run that recorded the approval")
    app.set_defaults(handler=cmd_approve)

    st = sub.add_parser("status", help="print the concept record")
    st.add_argument("--json", action="store_true")
    st.set_defaults(handler=cmd_status)

    chk = sub.add_parser("check", help="may implementation start?")
    chk.add_argument("--for", dest="use", required=True, choices=("implement",))
    chk.set_defaults(handler=cmd_check)

    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except GateError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
