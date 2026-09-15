#!/usr/bin/env python3
"""Run the QC-gated ANCOVA helper for the workshop demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def find_demo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "ancova_helpers.py").exists():
            return candidate
    raise FileNotFoundError("Could not find ancova_helpers.py in this skill's ancestor directories.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ANCOVA only if data-checker QC allows it.")
    parser.add_argument("--contract", required=True, type=Path, help="Path to SAP contract JSON.")
    parser.add_argument("--qc-summary", required=True, type=Path, help="Path to data-checker summary JSON.")
    parser.add_argument("--subject-data", required=True, type=Path, help="Path to subject-level CSV.")
    parser.add_argument("--efficacy-data", required=True, type=Path, help="Path to efficacy CSV.")
    parser.add_argument("--output-json", required=True, type=Path, help="Path for ANCOVA result JSON.")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    demo_root = find_demo_root(script_path)
    sys.path.insert(0, str(demo_root))
    from ancova_helpers import run_ancova_if_qc_passes

    contract_path = args.contract.resolve()
    qc_summary_path = args.qc_summary.resolve()
    subject_path = args.subject_data.resolve()
    efficacy_path = args.efficacy_data.resolve()
    output_path = args.output_json.resolve()

    subject_df = pd.read_csv(subject_path)
    efficacy_df = pd.read_csv(efficacy_path)
    result = run_ancova_if_qc_passes(
        contract_path,
        qc_summary_path,
        subject_df,
        efficacy_df,
        subject_dataset_name=subject_path.name,
        efficacy_dataset_name=efficacy_path.name,
    )
    result["input_datasets"]["subject_data_path"] = str(subject_path)
    result["input_datasets"]["efficacy_data_path"] = str(efficacy_path)
    result["qc_gate"]["qc_summary_path"] = str(qc_summary_path)
    result["analysis_contract"]["contract_path"] = str(contract_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Wrote ANCOVA result JSON: {output_path}")
    print(f"Analysis status: {result['analysis_status']}")
    print(f"Analysis executed: {result['analysis_executed']}")
    if result.get("result"):
        print(json.dumps(result["result"], indent=2))
    elif result.get("block_reason"):
        print(f"Block reason: {result['block_reason']}")


if __name__ == "__main__":
    main()
