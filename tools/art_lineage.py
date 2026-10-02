#!/usr/bin/env python3
"""Keep generated art close to its first generation — across calls, retries and runs.

Every image-model edit re-paints the whole frame, and every reference image is copied at high
fidelity, artifacts included. Artifacts therefore compound along two paths:

  edit chains       a banner edited for a pose, then for a ball, then (next run) for a new rule;
                    a game background edited five times in one run.
  reference chains  a new background rendered from the old background, a new banner rendered
                    "in the world of" the old banner: each render is fresh, yet each inherits
                    the previous one's smear and adds its own.

This ledger (`production/store-art/lineage.json`, kept in the project so it survives into every
later run) records how each generated picture was made and refuses the two moves that compound:

  * a whole-frame `edit` of anything but a fresh render (at most one edit per lineage);
  * a reference that is an earlier generated version of the same picture, or any generated
    campaign/marketing picture other than the accepted banner used as world context.

Region repairs and detail merges (`tools/region_repair.py`) and deterministic derivations
(resize, export, grade, upscale canvas) keep their parent's generation: they do not re-paint the
picture. A file the ledger has never seen, edited or repaired, is treated as an edited one —
its history is unknown, so it gets no further whole-frame edit.

  record  --file F --role R --made fresh|edit|repair|detail|derive|adopt [--parent P] [--ref X]
  check   --file F --for edit|reference [--role R]
  show    [--file F]
  verify  --file F [--file G ...]          (every file recorded, generation <= 2)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_LEDGER = "production/store-art/lineage.json"
ROLES = ("banner", "background", "panorama", "icon", "emblem", "showcase", "asset")
MADE = ("fresh", "edit", "repair", "detail", "derive", "adopt")
# A fresh render is generation 1; one whole-frame edit makes it 2, and that is the ceiling.
MAX_GENERATION = 2
# Generated pictures that may never feed another generation as a reference. The accepted banner
# is the one exception (world context for the other campaign pictures); shipped game assets are
# the identity authority however they were made.
NO_REFERENCE_ROLES = {"background", "panorama", "icon", "emblem", "showcase"}


class LineageError(RuntimeError):
    """A move that would compound generation loss, or a broken ledger."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError as exc:
        raise LineageError(f"cannot read {path}: {exc}") from exc
    return digest.hexdigest()


def load(ledger: Path) -> dict:
    if not ledger.exists():
        return {"schema_version": SCHEMA_VERSION, "records": []}
    try:
        data = json.loads(ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LineageError(f"{ledger} is not readable JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise LineageError(f"{ledger} is not a lineage ledger")
    return data


def save(ledger: Path, data: dict) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    tmp = ledger.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(ledger)


def find(data: dict, digest: str) -> dict | None:
    for record in data["records"]:
        if record.get("sha256") == digest:
            return record
    return None


def reference_issue(ref: dict | None, role: str) -> str | None:
    """Why a recorded generated picture may not be a reference for a new `role` picture."""
    if ref is None:
        return None  # shipped asset, capture or user source: not a generated picture
    if ref["role"] == role:
        return (f"it is an earlier {role} — a new {role} renders from the original references, "
                "never from its previous version (that copies its artifacts forward)")
    if ref["role"] in NO_REFERENCE_ROLES:
        return (f"it is a generated {ref['role']}; only the accepted banner may be world context "
                "for another campaign picture")
    return None


def plan_record(data: dict, file: Path, role: str, made: str, parent: Path | None,
                refs: list[Path]) -> dict:
    """The record `record` would write, or LineageError for a compounding move."""
    if role not in ROLES:
        raise LineageError(f"unknown role {role!r}; choose one of {', '.join(ROLES)}")
    if made not in MADE:
        raise LineageError(f"unknown --made {made!r}; choose one of {', '.join(MADE)}")
    parent_record = None
    parent_digest = None
    if made in ("fresh", "adopt"):
        if parent is not None:
            raise LineageError(f"--made {made} has no parent; name a fresh render's inputs "
                               "with --ref")
        # An adopted picture predates the ledger: its history is unknown, so it is counted as
        # already edited — reusable and repairable, never edited whole-frame again.
        generation = 1 if made == "fresh" else MAX_GENERATION
    else:
        if parent is None:
            raise LineageError(f"--made {made} needs --parent (the picture it was made from)")
        parent_digest = sha256(parent)
        parent_record = find(data, parent_digest)
        if made == "edit":
            if parent_record is None:
                raise LineageError(
                    f"{parent} has no recorded lineage, so it may already be an edit. A "
                    "whole-frame edit of it could stack generation loss: render fresh from the "
                    "original references, or repair the defect as a region "
                    "(tools/region_repair.py)")
            if parent_record["generation"] >= MAX_GENERATION:
                raise LineageError(
                    f"{parent} is generation {parent_record['generation']} (already edited). "
                    "Another whole-frame edit re-paints every pixel again and compounds the "
                    "loss: render fresh from the original references, or repair the defect as "
                    "a region (tools/region_repair.py)")
            if parent_record["role"] != role:
                raise LineageError(f"an edit of a {parent_record['role']} is still a "
                                   f"{parent_record['role']}, not a {role}")
            generation = parent_record["generation"] + 1
        else:
            generation = parent_record["generation"] if parent_record else MAX_GENERATION
    ref_entries = []
    for ref in refs:
        digest = sha256(ref)
        ref_record = find(data, digest)
        issue = reference_issue(ref_record, role)
        if issue:
            raise LineageError(f"--ref {ref}: {issue}")
        ref_entries.append({"path": str(ref), "sha256": digest,
                            "role": ref_record["role"] if ref_record else None,
                            "generation": ref_record["generation"] if ref_record else None})
    return {
        "sha256": sha256(file),
        "path": str(file),
        "role": role,
        "made": made,
        "generation": generation,
        "parent_sha256": parent_digest,
        "parent_path": str(parent) if parent else None,
        "lineage_unknown": made == "adopt" or bool(parent is not None and parent_record is None),
        "refs": ref_entries,
    }


def cmd_record(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    data = load(ledger)
    existing = find(data, sha256(Path(args.file)))
    if existing:
        print(f"= {args.file} is already recorded as generation {existing['generation']} "
              f"{existing['role']} ({existing['made']}); keeping that record")
        return 0
    record = plan_record(data, Path(args.file), args.role, args.made,
                         Path(args.parent) if args.parent else None,
                         [Path(r) for r in args.ref])
    if args.prompt:
        record["prompt"] = args.prompt
        record["prompt_sha256"] = sha256(Path(args.prompt))
    if args.note:
        record["note"] = args.note
    record["recorded_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    data["records"].append(record)
    save(ledger, data)
    note = " (parent lineage unknown — counted as edited)" if record["lineage_unknown"] else ""
    print(f"✅ {args.file}: {record['role']}, {record['made']}, generation "
          f"{record['generation']}{note}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    data = load(Path(args.ledger))
    record = find(data, sha256(Path(args.file)))
    if args.use == "edit":
        if record is None:
            print(f"❌ {args.file} has no recorded lineage — no whole-frame edit. Render fresh "
                  "or repair a region", file=sys.stderr)
            return 1
        if record["generation"] >= MAX_GENERATION:
            print(f"❌ {args.file} is generation {record['generation']} — no further "
                  "whole-frame edit. Render fresh or repair a region", file=sys.stderr)
            return 1
        print(f"✅ {args.file} is a fresh render: one whole-frame edit allowed")
        return 0
    if not args.role:
        print("❌ --for reference needs --role (the picture being made)", file=sys.stderr)
        return 2
    issue = reference_issue(record, args.role)
    if issue:
        print(f"❌ {args.file} may not be a reference for a new {args.role}: {issue}",
              file=sys.stderr)
        return 1
    kind = (f"generated {record['role']}, generation {record['generation']}" if record
            else "not a recorded generated picture")
    print(f"✅ {args.file} may be a reference for a {args.role} ({kind})")
    return 0


def chain(data: dict, digest: str) -> list[dict]:
    out, seen = [], set()
    while digest and digest not in seen:
        seen.add(digest)
        record = find(data, digest)
        if record is None:
            break
        out.append(record)
        digest = record.get("parent_sha256")
    return out


def cmd_show(args: argparse.Namespace) -> int:
    data = load(Path(args.ledger))
    records = (chain(data, sha256(Path(args.file))) if args.file else data["records"])
    if not records:
        print("no recorded lineage")
        return 1 if args.file else 0
    for record in records:
        refs = ", ".join(Path(r["path"]).name for r in record.get("refs", [])) or "—"
        print(f"gen {record['generation']}  {record['role']:<10} {record['made']:<7} "
              f"{record['path']}  refs: {refs}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    data = load(Path(args.ledger))
    failed = False
    for name in args.file:
        record = find(data, sha256(Path(name)))
        if record is None:
            print(f"❌ {name}: not in the lineage ledger", file=sys.stderr)
            failed = True
        elif record["generation"] > MAX_GENERATION:  # pragma: no cover - record refuses it
            print(f"❌ {name}: generation {record['generation']}", file=sys.stderr)
            failed = True
        else:
            print(f"✅ {name}: generation {record['generation']} {record['role']} "
                  f"({record['made']})")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ledger", default=DEFAULT_LEDGER,
                        help=f"lineage ledger (default {DEFAULT_LEDGER})")
    sub = parser.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="record how a generated picture was made")
    rec.add_argument("--file", required=True)
    rec.add_argument("--role", required=True, choices=ROLES)
    rec.add_argument("--made", required=True, choices=MADE,
                     help="fresh: new render from original references; edit: whole-frame "
                          "image-model edit of --parent; repair/detail: region_repair merge "
                          "into --parent; derive: resize/export/grade/upscale of --parent; "
                          "adopt: a picture made before the ledger (counted as edited)")
    rec.add_argument("--parent", default=None)
    rec.add_argument("--ref", action="append", default=[],
                     help="every image attached to the call (repeatable)")
    rec.add_argument("--prompt", default=None, help="the prompt file sent with the call")
    rec.add_argument("--note", default=None)
    rec.set_defaults(handler=cmd_record)

    chk = sub.add_parser("check", help="may this file be edited / used as a reference?")
    chk.add_argument("--file", required=True)
    chk.add_argument("--for", dest="use", required=True, choices=("edit", "reference"))
    chk.add_argument("--role", choices=ROLES, help="the picture being made (for --for reference)")
    chk.set_defaults(handler=cmd_check)

    show = sub.add_parser("show", help="print the ledger, or one file's chain")
    show.add_argument("--file", default=None)
    show.set_defaults(handler=cmd_show)

    ver = sub.add_parser("verify", help="every file recorded at generation <= 2")
    ver.add_argument("--file", action="append", required=True)
    ver.set_defaults(handler=cmd_verify)

    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except LineageError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
