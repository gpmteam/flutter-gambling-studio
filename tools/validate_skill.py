#!/usr/bin/env python3
"""Validate repository skill metadata using its Claude or Codex schema."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


def validate(path: Path, skill_format: str = "auto") -> list[str]:
    try:
        import yaml
    except ImportError:
        return ["PyYAML is missing from this interpreter. Use python3-yaml in the worker, "
                "or install PyYAML with this environment's python -m pip."]

    source = path / "SKILL.md" if path.is_dir() else path
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        return [str(exc)]
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        return ["SKILL.md requires YAML frontmatter delimited by ---."]

    class UniqueLoader(yaml.SafeLoader):
        pass

    def unique_mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError(f"Invalid or duplicate metadata key: {key!r}")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
    try:
        data = yaml.load(match[1], Loader=UniqueLoader)
    except (yaml.YAMLError, ValueError) as exc:
        return [f"Invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["Frontmatter must be a mapping."]
    if skill_format == "auto":
        parts = source.resolve().parts
        skill_format = "claude" if any(parts[i:i + 2] == (".claude", "skills")
                                       for i in range(len(parts) - 1)) else "codex"
    allowed = {"name", "description", "license", "allowed-tools", "metadata"}
    if skill_format == "claude":
        allowed |= {"argument-hint", "user-invocable", "disable-model-invocation",
                    "model", "context", "agent", "hooks"}
    errors = [f"Unsupported {skill_format} field: {key}" for key in sorted(set(data) - allowed)]
    name = data.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        errors.append("name must be lowercase letters/digits/hyphens, at most 64 characters.")
    description = data.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append("description must be nonempty text, at most 1024 characters.")
    for key in ("user-invocable", "disable-model-invocation"):
        if key in data and not isinstance(data[key], bool):
            errors.append(f"{key} must be a YAML boolean.")
    for key in ("argument-hint", "license", "model", "context", "agent"):
        if key in data and not isinstance(data[key], str):
            errors.append(f"{key} must be text.")
    for key in ("metadata", "hooks"):
        if key in data and not isinstance(data[key], dict):
            errors.append(f"{key} must be a mapping.")
    tools = data.get("allowed-tools")
    if tools is not None and not (isinstance(tools, str) or
                                  isinstance(tools, list) and all(isinstance(t, str) for t in tools)):
        errors.append("allowed-tools must be text or a list of tool names.")
    if not text[match.end():].strip():
        errors.append("Skill instructions must not be empty.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--format", choices=("auto", "claude", "codex"), default="auto")
    args = parser.parse_args()
    errors = validate(args.path, args.format)
    if errors:
        print("FAIL — skill validation:\n" + "\n".join(errors), file=sys.stderr)
        return 2
    print("PASS — skill metadata and instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
