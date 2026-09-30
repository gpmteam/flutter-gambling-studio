#!/usr/bin/env python3
"""Check the actual store ZIP's scope, review declaration, and required images.

This is structural validation, not a replacement for visual or runtime review.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile


def check(archive: Path, count: int = 8, play_set: bool = True) -> list[str]:
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
    args = parser.parse_args()
    try:
        errors = check(args.archive, args.count, not args.no_play_set)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ImportError) as exc:
        errors = [str(exc)]
    if errors:
        print("FAIL — store delivery:\n" + "\n".join(errors), file=sys.stderr)
        return 2
    print("PASS — store ZIP structure, required images, and recorded review declarations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
