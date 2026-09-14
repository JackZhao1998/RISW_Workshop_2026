#!/usr/bin/env python3
"""Pre-tool security hook to keep workshop source data immutable.

The hook protects the demo data folder from overwrite, deletion, patching,
moving, appending, truncation, and other mutations. It is intended to run before
any tool call that may touch local files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_PROTECTED_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

READ_ONLY_OPERATIONS = {
    "read",
    "list",
    "inspect",
    "stat",
    "hash",
    "summarize",
    "load",
    "validate",
}

MUTATING_OPERATIONS = {
    "write",
    "overwrite",
    "delete",
    "remove",
    "unlink",
    "move",
    "rename",
    "patch",
    "apply_patch",
    "append",
    "truncate",
    "replace",
    "create",
    "mkdir",
    "rmdir",
    "copy",
}

MUTATING_TOOL_NAMES = {
    "apply_patch",
    "write_file",
    "delete_file",
    "move_file",
    "rename_file",
    "shell_command",
}

MUTATING_COMMAND_PATTERNS = [
    r"\bRemove-Item\b",
    r"\brm\b",
    r"\bdel\b",
    r"\berase\b",
    r"\bMove-Item\b",
    r"\bmv\b",
    r"\bRename-Item\b",
    r"\bren\b",
    r"\bSet-Content\b",
    r"\bAdd-Content\b",
    r"\bOut-File\b",
    r"\bNew-Item\b",
    r"\bCopy-Item\b",
    r"\bcopy\b",
    r">>",
    r"(?<![<])>(?!>)",
]


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def norm(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=False)))


def is_inside_or_equal(path: Path, directory: Path) -> bool:
    path_norm = norm(path)
    dir_norm = norm(directory)
    return path_norm == dir_norm or path_norm.startswith(dir_norm + os.sep)


def looks_like_path(value: str) -> bool:
    return (
        "\\" in value
        or "/" in value
        or bool(re.search(r"\.[A-Za-z0-9]{1,8}$", value))
        or value.lower() == "data"
    )


def collect_path_candidates(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_lower = str(key).lower()
            if any(token in key_lower for token in ["path", "file", "dir", "cwd", "workdir"]):
                if isinstance(nested, (str, int, float)):
                    paths.append(str(nested))
                else:
                    paths.extend(collect_path_candidates(nested))
            else:
                paths.extend(collect_path_candidates(nested))
    elif isinstance(value, list):
        for item in value:
            paths.extend(collect_path_candidates(item))
    elif isinstance(value, str) and looks_like_path(value):
        paths.append(value)
    return paths


def resolve_candidate(candidate: str, base_dir: Path) -> Path:
    path = Path(candidate)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve(strict=False)


def command_has_mutating_pattern(command: str) -> bool:
    return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern in MUTATING_COMMAND_PATTERNS)


def command_mentions_data_dir(command: str, protected_data_dir: Path) -> bool:
    variants = {
        str(protected_data_dir),
        str(protected_data_dir).replace("\\", "/"),
        protected_data_dir.name,
    }
    lowered = command.lower()
    return any(variant.lower() in lowered for variant in variants)


def run_pre_tool_data_security_hook(
    *,
    tool_name: str,
    operation: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
    paths: list[str] | None = None,
    protected_data_dir: str | Path = DEFAULT_PROTECTED_DATA_DIR,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Return ALLOW or BLOCK before a tool can touch files.

    Any mutating operation targeting the protected data directory is blocked.
    Unknown operations touching the protected data directory are also blocked
    unless explicitly classified as read-only.
    """

    protected_dir = Path(protected_data_dir).resolve(strict=False)
    base = Path(base_dir).resolve(strict=False) if base_dir else protected_dir.parents[0]
    args = tool_arguments or {}
    tool_name_norm = tool_name.lower().strip()
    operation_norm = operation.lower().strip() if operation else "unknown"

    candidate_strings = list(paths or [])
    candidate_strings.extend(collect_path_candidates(args))
    resolved_paths = [
        resolve_candidate(candidate, base)
        for candidate in candidate_strings
        if candidate and not str(candidate).strip().startswith("-")
    ]
    protected_hits = [
        str(path)
        for path in resolved_paths
        if is_inside_or_equal(path, protected_dir)
    ]

    command = str(args.get("command", ""))
    shell_mutation = bool(command) and command_has_mutating_pattern(command)
    shell_mentions_data = bool(command) and command_mentions_data_dir(command, protected_dir)

    mutating_operation = operation_norm in MUTATING_OPERATIONS
    read_only_operation = operation_norm in READ_ONLY_OPERATIONS
    mutating_tool = tool_name_norm in MUTATING_TOOL_NAMES

    reasons: list[str] = []
    decision = "ALLOW"

    if protected_hits and mutating_operation:
        decision = "BLOCK"
        reasons.append("Mutating operation targets the protected data folder.")
    elif protected_hits and mutating_tool and not read_only_operation:
        decision = "BLOCK"
        reasons.append("Mutating-capable tool targets the protected data folder without a read-only operation.")
    elif protected_hits and operation_norm == "unknown":
        decision = "BLOCK"
        reasons.append("Unknown operation targets the protected data folder; require explicit read-only classification.")
    elif shell_mutation and shell_mentions_data:
        decision = "BLOCK"
        reasons.append("Shell command appears mutating and mentions the protected data folder.")
    else:
        reasons.append("No protected data mutation detected.")

    return {
        "schema_version": "pre-tool-data-security-hook-v1",
        "generated_at_utc": utc_now(),
        "hook_name": "pre_tool_data_security_hook",
        "decision": decision,
        "protected_data_dir": str(protected_dir),
        "tool_name": tool_name_norm,
        "operation": operation_norm,
        "protected_path_hits": protected_hits,
        "resolved_path_candidates": [str(path) for path in resolved_paths],
        "shell_command_detected": bool(command),
        "shell_mutation_detected": shell_mutation,
        "reasons": reasons,
        "policy": {
            "read_only_operations_allowed": sorted(READ_ONLY_OPERATIONS),
            "mutating_operations_blocked": sorted(MUTATING_OPERATIONS),
            "rule": "Source data are immutable. Read-only inspection is allowed; mutation in the data folder is blocked.",
        },
    }


def load_event(path: Path | None) -> dict[str, Any]:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            return json.loads(raw)
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Block tool calls that would mutate protected demo data.")
    parser.add_argument("--event-json", type=Path, default=None, help="Optional JSON event file.")
    parser.add_argument("--tool-name", default=None, help="Name of tool about to be called.")
    parser.add_argument("--operation", default=None, help="Operation classification, e.g. read/write/delete.")
    parser.add_argument("--path", action="append", default=[], help="Path targeted by the tool. Repeatable.")
    parser.add_argument("--protected-data-dir", type=Path, default=DEFAULT_PROTECTED_DATA_DIR)
    parser.add_argument("--base-dir", type=Path, default=None, help="Base directory for relative paths.")
    parser.add_argument("--output-json", type=Path, default=None, help="Optional path to write hook result JSON.")
    args = parser.parse_args()

    event = load_event(args.event_json)
    tool_name = args.tool_name or event.get("tool_name") or event.get("tool") or "unknown"
    operation = args.operation or event.get("operation")
    tool_arguments = event.get("tool_arguments") or event.get("arguments") or {}
    paths = list(args.path or [])
    paths.extend(event.get("paths") or [])

    result = run_pre_tool_data_security_hook(
        tool_name=tool_name,
        operation=operation,
        tool_arguments=tool_arguments,
        paths=paths,
        protected_data_dir=args.protected_data_dir,
        base_dir=args.base_dir,
    )

    payload = json.dumps(result, indent=2)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(payload, encoding="utf-8")
    print(payload)

    if result["decision"] == "BLOCK":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
