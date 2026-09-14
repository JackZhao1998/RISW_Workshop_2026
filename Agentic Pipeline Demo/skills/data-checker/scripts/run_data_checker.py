#!/usr/bin/env python3
"""Run deterministic data-readiness QC using the workshop helper function."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_demo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "data_qc_helpers.py").exists():
            return candidate
    raise FileNotFoundError("Could not find data_qc_helpers.py in this skill's ancestor directories.")


def make_summary(
    table: pd.DataFrame,
    contract_path: Path,
    subject_path: Path,
    efficacy_path: Path,
) -> dict[str, Any]:
    failed = table.loc[table["status"].eq("FAIL")].copy()
    status_counts = table["status"].value_counts().to_dict()
    return {
        "generated_at_utc": utc_now(),
        "skill": "data-checker",
        "decision_rule": "ALLOW only when every checking-table term has status PASS.",
        "pre_analysis_decision": "ALLOW" if failed.empty else "BLOCK",
        "all_terms_passed": bool(failed.empty),
        "status_counts": {str(key): int(value) for key, value in status_counts.items()},
        "failed_terms": failed[
            ["task", "term", "dataset", "expected", "observed", "details", "source_section"]
        ].to_dict(orient="records"),
        "inputs": {
            "contract": {
                "path": str(contract_path),
                "sha256": sha256_file(contract_path),
            },
            "subject_data": {
                "path": str(subject_path),
                "sha256": sha256_file(subject_path),
            },
            "efficacy_data": {
                "path": str(efficacy_path),
                "sha256": sha256_file(efficacy_path),
            },
        },
        "data_handling": {
            "source_files_modified": False,
            "statistical_model_run": False,
            "outputs_written_only_to_output_dir": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate analysis data against a SAP contract JSON.")
    parser.add_argument("--contract", required=True, type=Path, help="Path to SAP contract JSON.")
    parser.add_argument("--subject-data", required=True, type=Path, help="Path to subject-level CSV.")
    parser.add_argument("--efficacy-data", required=True, type=Path, help="Path to efficacy CSV.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for QC outputs.")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    demo_root = find_demo_root(script_path)
    sys.path.insert(0, str(demo_root))
    from data_qc_helpers import check_sap_contract_against_data

    contract_path = args.contract.resolve()
    subject_path = args.subject_data.resolve()
    efficacy_path = args.efficacy_data.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    subject_df = pd.read_csv(subject_path)
    efficacy_df = pd.read_csv(efficacy_path)
    table = check_sap_contract_against_data(
        contract_path,
        subject_df,
        efficacy_df,
        subject_dataset_name=subject_path.name,
        efficacy_dataset_name=efficacy_path.name,
    )

    table_csv = output_dir / "data_checker_table.csv"
    table_json = output_dir / "data_checker_table.json"
    summary_json = output_dir / "data_checker_summary.json"

    table.to_csv(table_csv, index=False)
    table.to_json(table_json, orient="records", indent=2)
    summary = make_summary(table, contract_path, subject_path, efficacy_path)
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote table CSV: {table_csv}")
    print(f"Wrote table JSON: {table_json}")
    print(f"Wrote summary JSON: {summary_json}")
    print(f"Pre-analysis decision: {summary['pre_analysis_decision']}")
    if summary["failed_terms"]:
        print("Failed terms:")
        for item in summary["failed_terms"]:
            print(f"- {item['task']} / {item['term']}: {item['details']}")


if __name__ == "__main__":
    main()
