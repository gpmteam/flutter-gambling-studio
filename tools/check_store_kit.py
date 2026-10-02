#!/usr/bin/env python3
"""Check the actual store ZIP's scope, review declaration, and required images.

This is structural validation, not a replacement for visual or runtime review.
"""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile


# The kit's generated scenes, and the most generations each may be from a fresh render. A
# whole-frame image edit re-paints every pixel, so a banner edited for a pose, then a ball, then
# a new rule ships visibly degraded — and passes it on to everything that used it as a reference.
# tools/art_lineage.py keeps the ledger; this checks the files actually shipped against it.
LINEAGE_ART = ("art/long-banner.png", "art/panorama.png", "art/shared-background.png",
               "art/multiplier-showcase-bg.png")
MAX_ART_GENERATION = 2
# After the user approves the concept carousel (tools/concept_gate.py) the panorama is a
# contract: the store kit crops, grades and detail-passes it, and may repair an objective defect
# as a region, but never re-renders or whole-frame edits it.
APPROVED_PANORAMA_STEPS = ("derive", "detail", "repair")


def lineage_errors(kit: zipfile.ZipFile, names: list[str], member) -> list[str]:
    errors: list[str] = []
    banner = member("art/long-banner.png")
    if banner not in names:
        errors.append("Missing art/long-banner.png, the accepted banner the kit is built on.")
    present = [rel for rel in LINEAGE_ART if member(rel) in names]
    ledger_name = member("art/lineage.json")
    if ledger_name not in names:
        errors.append("Missing art/lineage.json: copy production/store-art/lineage.json "
                      "(tools/art_lineage.py) into the kit.")
        return errors
    try:
        ledger = json.loads(kit.read(ledger_name))
        records = {r["sha256"]: r for r in ledger["records"]}
    except (ValueError, KeyError, TypeError) as exc:
        return errors + [f"art/lineage.json is not a lineage ledger ({exc})."]
    for rel in present:
        digest = hashlib.sha256(kit.read(member(rel))).hexdigest()
        record = records.get(digest)
        if not isinstance(record, dict):
            errors.append(f"{rel}: not recorded in art/lineage.json; record how it was made "
                          "with tools/art_lineage.py.")
        elif not isinstance(record.get("generation"), int) \
                or not 1 <= record["generation"] <= MAX_ART_GENERATION:
            errors.append(f"{rel}: generation {record.get('generation')!r}; at most "
                          f"{MAX_ART_GENERATION} (one whole-frame edit of a fresh render). "
                          "Render it fresh or repair regions instead.")
    return errors


def concept_errors(kit: zipfile.ZipFile, names: list[str], member, concept: Path) -> list[str]:
    """`art/panorama.png` must be the approved concept panorama, or descend from it only by
    crops, grading, detail passes and region repairs recorded in `art/lineage.json`."""
    try:
        record = json.loads(concept.read_text(encoding="utf-8"))
        approved = record["panorama"]["sha256"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"{concept} is not a concept record ({exc})."]
    if record.get("status") != "APPROVED":
        return [f"The concept carousel is {record.get('status')!r}, not APPROVED; the store kit "
                "is built from the panorama the user approved."]
    name = member("art/panorama.png")
    if name not in names:
        return ["Missing art/panorama.png, the approved concept panorama the kit exports."]
    try:
        ledger = json.loads(kit.read(member("art/lineage.json")))
        records = {r["sha256"]: r for r in ledger["records"]}
    except (KeyError, ValueError, TypeError):
        return []  # lineage_errors() already reports a missing or broken ledger
    digest = hashlib.sha256(kit.read(name)).hexdigest()
    seen: set[str] = set()
    while digest != approved:
        step = records.get(digest)
        if digest in seen or not isinstance(step, dict):
            return ["art/panorama.png does not descend from the approved concept panorama "
                    f"({approved[:12]}…): record every crop, canvas and detail merge with "
                    "tools/art_lineage.py --parent, or export the approved file unchanged."]
        if step.get("made") not in APPROVED_PANORAMA_STEPS:
            return [f"art/panorama.png went through a {step.get('made')!r} step after approval; "
                    "the approved panorama is only cropped, graded, detail-passed or "
                    "region-repaired, never re-rendered or whole-frame edited."]
        seen.add(digest)
        digest = step.get("parent_sha256")
    return []


def check(archive: Path, count: int = 8, play_set: bool = True,
          concept: Path | None = None) -> list[str]:
    from PIL import Image

    if count < 1:
        return ["Screenshot count must be positive."]
    errors: list[str] = []
    with zipfile.ZipFile(archive) as kit:
        entries = [i for i in kit.infolist() if not i.is_dir()]
        names = [i.filename for i in entries]
        if len(names) != len(set(names)):
            return ["Duplicate ZIP members."]
        if any(PurePosixPath(n).is_absolute() or ".." in PurePosixPath(n).parts for n in names):
            return ["ZIP members must have relative paths without traversal."]
        manifests = [n for n in names if PurePosixPath(n).name == "STORE_DELIVERY.json"]
        if len(manifests) != 1:
            return ["Exactly one STORE_DELIVERY.json is required."]
        root = PurePosixPath(manifests[0]).parent
        manifest = json.loads(kit.read(manifests[0]))
        if not isinstance(manifest, dict):
            return ["STORE_DELIVERY.json must be an object."]
        expected = {"schema_version": 1, "status": "COMPLETE", "screenshot_count": count,
                    "play_set": play_set, "visual_review": "PASS", "gameplay_review": "PASS"}
        for key, value in expected.items():
            if manifest.get(key) != value or type(manifest.get(key)) is not type(value):
                errors.append(f"Delivery {key} must be {value!r}.")

        def member(relative: str) -> str:
            p = PurePosixPath(relative)
            if p.is_absolute() or ".." in p.parts or "\\" in relative:
                raise ValueError("Artifact paths must be relative to the kit root.")
            return str(root / p)

        def image(relative: str, size: tuple[int, int] | None, kind: str) -> None:
            name = member(relative)
            if name not in names:
                errors.append(f"Missing {relative}.")
                return
            payload = kit.read(name)
            try:
                with Image.open(BytesIO(payload)) as im:
                    im.verify()
                with Image.open(BytesIO(payload)) as im:
                    im.load()
                    if im.format != "PNG" or size is not None and im.size != size:
                        errors.append(f"{relative}: expected PNG {size}, got {im.format} {im.size}.")
                    if kind == "screenshot" and (im.mode != "RGB" or "transparency" in im.info):
                        errors.append(f"{relative}: screenshots must be opaque RGB PNGs.")
                    if kind == "icon" and im.convert("RGBA").getchannel("A").getextrema()[0] != 255:
                        errors.append(f"{relative}: icon must be opaque.")
                    if kind == "emblem" and im.convert("RGBA").getchannel("A").getextrema()[0] == 255:
                        errors.append(f"{relative}: emblem must have transparency.")
            except (OSError, SyntaxError, ValueError) as exc:
                errors.append(f"{relative}: invalid PNG ({exc}).")

        for directory, size in (("store", (1320, 2868)), ("store-play", (1080, 1920))):
            prefix = member(directory) + "/"
            images = sorted(n for n in names if n.startswith(prefix) and n.lower().endswith(".png"))
            if directory == "store-play" and not play_set:
                if images:
                    errors.append("Play screenshots present despite --no-play-set.")
                continue
            wanted = [f"{prefix}store-{i:02d}.png" for i in range(1, count + 1)]
            if images != wanted:
                errors.append(f"{directory}: expected {count} sequential store-NN.png files.")
            for name in images:
                image(str(PurePosixPath(name).relative_to(root)), size, "screenshot")
        image("feature-graphic-1024x500.png", (1024, 500), "icon")
        for key, size, kind in (("icon_master", (1024, 1024), "icon"),
                                ("listing_icon", (512, 512), "icon"), ("emblem", None, "emblem")):
            relative = manifest.get(key)
            if not isinstance(relative, str) or not relative:
                errors.append(f"Delivery must name the {key} artifact.")
            else:
                image(relative, size, kind)
        errors.extend(lineage_errors(kit, names, member))
        if concept is not None:
            errors.extend(concept_errors(kit, names, member, concept))
        for report in ("STORE_BRIEF.md", "STORE_INFO.md"):
            name = member(report)
            if name not in names or not kit.read(name).strip():
                errors.append(f"Missing or empty {report}.")
        bad_member = kit.testzip()
        if bad_member:
            errors.append(f"Corrupt ZIP member: {bad_member}.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--no-play-set", action="store_true")
    parser.add_argument("--concept", type=Path, default=None,
                        help="production/store-art/concept/concept.json: require the kit's "
                             "panorama to be the user-approved concept panorama")
    args = parser.parse_args()
    try:
        errors = check(args.archive, args.count, not args.no_play_set, args.concept)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ImportError) as exc:
        errors = [str(exc)]
    if errors:
        print("FAIL — store delivery:\n" + "\n".join(errors), file=sys.stderr)
        return 2
    print("PASS — store ZIP structure, required images, and recorded review declarations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
