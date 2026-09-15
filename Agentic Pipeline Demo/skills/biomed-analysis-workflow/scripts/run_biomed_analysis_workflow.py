#!/usr/bin/env python3
"""Run the complete governed biomedical analysis workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def find_demo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "SAP.md").exists() and (candidate / "data").exists():
            return candidate
    raise FileNotFoundError("Could not find biomedical_agent_workshop_demo root.")


def run_command(command: list[str], *, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def require_success(step: dict[str, Any]) -> None:
    if step["returncode"] != 0:
        raise RuntimeError(
            "Workflow step failed\n"
            f"Command: {' '.join(step['command'])}\n"
            f"Return code: {step['returncode']}\n"
            f"STDOUT:\n{step['stdout']}\n"
            f"STDERR:\n{step['stderr']}"
        )


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def artifact(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "exists": path.exists(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SAP extraction, data QC, gated ANCOVA, and final review.")
    parser.add_argument("--sap", required=True, type=Path, help="Path to SAP markdown/text file.")
    parser.add_argument("--subject-data", required=True, type=Path, help="Path to subject-level CSV.")
    parser.add_argument("--efficacy-data", required=True, type=Path, help="Path to efficacy CSV.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for workflow artifacts.")
    parser.add_argument("--final-report", type=Path, default=None, help="Optional final report text to scan.")
    parser.add_argument("--python", default=sys.executable, help="Python executable.")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    demo_root = find_demo_root(script_path)
    hooks_dir = demo_root / "hooks"
    skills_dir = demo_root / "skills"
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    sap_path = args.sap.resolve()
    subject_path = args.subject_data.resolve()
    efficacy_path = args.efficacy_data.resolve()

    paths = {
        "sap_contract": output_dir / "sap_analysis_contract.json",
        "data_checker_table_csv": output_dir / "data_checker_table.csv",
        "data_checker_table_json": output_dir / "data_checker_table.json",
        "data_checker_summary": output_dir / "data_checker_summary.json",
        "ancova_result": output_dir / "ancova_result.json",
        "final_review": output_dir / "final_result_review.json",
        "manifest": output_dir / "workflow_manifest.json",
    }

    step_results: list[dict[str, Any]] = []

    security_hook = hooks_dir / "pre_tool_data_security_hook.py"
    for label, path in [("subject-data", subject_path), ("efficacy-data", efficacy_path)]:
        step = run_command(
            [
                args.python,
                str(security_hook),
                "--tool-name",
                "pandas.read_csv",
                "--operation",
                "read",
                "--path",
                str(path),
                "--base-dir",
                str(demo_root),
            ],
            cwd=demo_root,
        )
        step["step"] = f"pre_tool_data_security_{label}"
        step_results.append(step)
        require_success(step)

    sap_extractor = skills_dir / "sap-extractor" / "scripts" / "extract_sap_contract.py"
    step = run_command(
        [
            args.python,
            str(sap_extractor),
            "--sap",
            str(sap_path),
            "--output",
            str(paths["sap_contract"]),
        ],
        cwd=demo_root,
    )
    step["step"] = "sap_extraction"
    step_results.append(step)
    require_success(step)

    data_checker = skills_dir / "data-checker" / "scripts" / "run_data_checker.py"
    step = run_command(
        [
            args.python,
            str(data_checker),
            "--contract",
            str(paths["sap_contract"]),
            "--subject-data",
            str(subject_path),
            "--efficacy-data",
            str(efficacy_path),
            "--output-dir",
            str(output_dir),
        ],
        cwd=demo_root,
    )
    step["step"] = "data_checker"
    step_results.append(step)
    require_success(step)

    ancova_test = skills_dir / "ancova-test" / "scripts" / "run_ancova_test.py"
    step = run_command(
        [
            args.python,
            str(ancova_test),
            "--contract",
            str(paths["sap_contract"]),
            "--qc-summary",
            str(paths["data_checker_summary"]),
            "--subject-data",
            str(subject_path),
            "--efficacy-data",
            str(efficacy_path),
            "--output-json",
            str(paths["ancova_result"]),
        ],
        cwd=demo_root,
    )
    step["step"] = "ancova_test"
    step_results.append(step)
    require_success(step)

    final_review = hooks_dir / "final_result_review_hook.py"
    final_review_command = [
        args.python,
        str(final_review),
        "--ancova-result",
        str(paths["ancova_result"]),
        "--output-json",
        str(paths["final_review"]),
    ]
    if args.final_report:
        final_review_command.extend(["--final-report", str(args.final_report.resolve())])
    step = run_command(final_review_command, cwd=demo_root)
    step["step"] = "final_result_review"
    step_results.append(step)
    require_success(step)

    qc_summary = load_json(paths["data_checker_summary"])
    ancova_result = load_json(paths["ancova_result"])
    review = load_json(paths["final_review"])

    manifest = {
        "schema_version": "biomed-analysis-workflow-manifest-v1",
        "generated_at_utc": utc_now(),
        "workflow": "biomed-analysis-workflow",
        "demo_root": str(demo_root),
        "inputs": {
            "sap": artifact(sap_path),
            "subject_data": artifact(subject_path),
            "efficacy_data": artifact(efficacy_path),
        },
        "decisions": {
            "sap_extraction_status": load_json(paths["sap_contract"]).get("extraction_status"),
            "data_checker_pre_analysis_decision": qc_summary.get("pre_analysis_decision"),
            "ancova_analysis_status": ancova_result.get("analysis_status"),
            "ancova_analysis_executed": ancova_result.get("analysis_executed"),
            "final_release_decision": review.get("release_decision"),
        },
        "artifacts": {
            name: artifact(path)
            for name, path in paths.items()
            if name != "manifest"
        },
        "step_results": step_results,
        "data_handling": {
            "source_data_modified": False,
            "source_data_security_hook_used": True,
            "ancova_gated_by_data_checker": True,
        },
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote workflow manifest: {paths['manifest']}")
    print(json.dumps(manifest["decisions"], indent=2))


if __name__ == "__main__":
    main()
