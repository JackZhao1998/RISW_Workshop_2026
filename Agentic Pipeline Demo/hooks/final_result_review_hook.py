#!/usr/bin/env python3
"""Final result review and QC hook for the biomedical agent demo.

This hook checks whether an ANCOVA result can be released into the final
answer/report. It does not rerun data QC or ANCOVA. It verifies that the
existing artifacts are internally consistent, source-grounded, and reproducible.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
from pathlib import Path
from typing import Any


EXPECTED_CONTRACT_MAP = {
    "study_id": "study_id",
    "model": "model",
    "formula": "formula",
    "outcome_variable": "outcome",
    "treatment_variable": "treatment",
    "baseline_covariate": "baseline_covariate",
    "contrast": "contrast",
}

OVERCLAIM_PATTERNS = [
    r"\bclinically\s+proven\b",
    r"\bclinical\s+benefit\b",
    r"\befficacious\b",
    r"\beffective\s+treatment\b",
    r"\bsafe\s+and\s+effective\b",
    r"\bregulatory\s+ready\b",
    r"\bapproved\b",
]


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def field_value(contract: dict[str, Any], key: str) -> Any:
    return contract.get("analysis_contract", {}).get(key, {}).get("value")


def add_check(
    checks: list[dict[str, Any]],
    *,
    hook: str,
    term: str,
    passed: bool,
    expected: Any,
    observed: Any,
    details: str,
    severity: str = "ERROR",
) -> None:
    checks.append(
        {
            "hook": hook,
            "term": term,
            "status": "PASS" if passed else "FAIL",
            "pass_flag": bool(passed),
            "severity": "INFO" if passed else severity,
            "expected": expected,
            "observed": observed,
            "details": details,
        }
    )


def check_qc_gate_consistency(result: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    qc_gate = result.get("qc_gate", {})
    decision = qc_gate.get("pre_analysis_decision")
    all_terms_passed = qc_gate.get("all_terms_passed")
    failed_terms = qc_gate.get("failed_terms", [])
    analysis_executed = bool(result.get("analysis_executed"))
    analysis_status = result.get("analysis_status")

    if decision == "ALLOW":
        passed = analysis_executed and analysis_status == "COMPLETED" and all_terms_passed is True and not failed_terms
        details = (
            "QC allowed analysis and the analysis completed."
            if passed
            else "QC allowed analysis, but result execution state is inconsistent."
        )
    elif decision == "BLOCK":
        passed = (not analysis_executed) and analysis_status == "BLOCKED" and all_terms_passed is False and bool(failed_terms)
        details = (
            "QC blocked analysis and ANCOVA was not executed."
            if passed
            else "QC blocked analysis, but ANCOVA execution state is inconsistent."
        )
    else:
        passed = False
        details = "QC decision must be ALLOW or BLOCK."

    add_check(
        checks,
        hook="qc_gate_consistency_hook",
        term="analysis_execution_matches_qc_decision",
        passed=passed,
        expected="ALLOW -> COMPLETED; BLOCK -> BLOCKED",
        observed={
            "pre_analysis_decision": decision,
            "all_terms_passed": all_terms_passed,
            "failed_terms_n": len(failed_terms),
            "analysis_status": analysis_status,
            "analysis_executed": analysis_executed,
        },
        details=details,
    )


def check_contract_alignment(
    result: dict[str, Any],
    contract: dict[str, Any] | None,
    checks: list[dict[str, Any]],
) -> None:
    if contract is None:
        add_check(
            checks,
            hook="sap_contract_alignment_hook",
            term="contract_available_for_review",
            passed=False,
            expected="SAP contract JSON available",
            observed="not provided and embedded path unavailable",
            details="Cannot independently verify analysis contract fields.",
        )
        return

    result_contract = result.get("analysis_contract", {})
    mismatches = []
    for contract_key, result_key in EXPECTED_CONTRACT_MAP.items():
        expected = field_value(contract, contract_key)
        observed = result_contract.get(result_key)
        if expected != observed:
            mismatches.append(
                {
                    "contract_field": contract_key,
                    "result_field": result_key,
                    "expected": expected,
                    "observed": observed,
                }
            )

    add_check(
        checks,
        hook="sap_contract_alignment_hook",
        term="analysis_contract_fields_match_sap",
        passed=not mismatches,
        expected="ANCOVA result contract fields match extracted SAP contract",
        observed=mismatches if mismatches else "all compared fields match",
        details=(
            "Analysis result uses the SAP-derived model, endpoint variables, and contrast."
            if not mismatches
            else "Analysis result has fields that do not match the extracted SAP contract."
        ),
    )


def check_source_data_handling(result: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    handling = result.get("data_handling", {})
    add_check(
        checks,
        hook="source_data_security_hook",
        term="source_data_not_modified",
        passed=handling.get("source_data_modified") is False,
        expected=False,
        observed=handling.get("source_data_modified"),
        details=(
            "ANCOVA result declares source data were not modified."
            if handling.get("source_data_modified") is False
            else "ANCOVA result does not confirm source data immutability."
        ),
    )
    add_check(
        checks,
        hook="source_data_security_hook",
        term="analysis_gated_by_qc",
        passed=handling.get("analysis_run_only_after_qc_allow") is True,
        expected=True,
        observed=handling.get("analysis_run_only_after_qc_allow"),
        details=(
            "Analysis result declares execution was gated by QC ALLOW."
            if handling.get("analysis_run_only_after_qc_allow") is True
            else "Analysis result does not confirm QC-gated execution."
        ),
    )


def check_statistical_result(result: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    if not result.get("analysis_executed"):
        add_check(
            checks,
            hook="statistical_result_sanity_hook",
            term="statistical_result_required_when_executed",
            passed=True,
            expected="no result required when analysis is blocked",
            observed=result.get("analysis_status"),
            details="Analysis was not executed, so no statistical result is required.",
        )
        return

    analysis_result = result.get("result", {})
    dataset = result.get("analysis_dataset", {})
    required_fields = [
        "contrast",
        "estimate",
        "standard_error",
        "confidence_interval_95",
        "t_statistic",
        "p_value",
        "df_residual",
        "model_engine",
    ]
    missing_fields = [field for field in required_fields if field not in analysis_result]
    add_check(
        checks,
        hook="statistical_result_sanity_hook",
        term="required_result_fields_present",
        passed=not missing_fields,
        expected=required_fields,
        observed=missing_fields if missing_fields else "all required result fields present",
        details=(
            "ANCOVA result contains all required result fields."
            if not missing_fields
            else "ANCOVA result is missing required fields."
        ),
    )
    if missing_fields:
        return

    estimate = analysis_result.get("estimate")
    se = analysis_result.get("standard_error")
    ci = analysis_result.get("confidence_interval_95")
    p_value = analysis_result.get("p_value")
    df = analysis_result.get("df_residual")
    n_total = dataset.get("n_total")
    n_by_treatment = dataset.get("n_by_treatment", {})

    numeric_checks_pass = (
        isinstance(estimate, (int, float))
        and isinstance(se, (int, float))
        and se > 0
        and isinstance(ci, list)
        and len(ci) == 2
        and all(isinstance(x, (int, float)) and math.isfinite(x) for x in ci)
        and ci[0] <= estimate <= ci[1]
        and isinstance(p_value, (int, float))
        and 0 <= p_value <= 1
        and isinstance(df, int)
        and df > 0
    )
    add_check(
        checks,
        hook="statistical_result_sanity_hook",
        term="numeric_result_values_valid",
        passed=numeric_checks_pass,
        expected="finite estimate, SE > 0, CI contains estimate, 0 <= p <= 1, df > 0",
        observed={
            "estimate": estimate,
            "standard_error": se,
            "confidence_interval_95": ci,
            "p_value": p_value,
            "df_residual": df,
        },
        details=(
            "Numeric ANCOVA result values pass basic sanity checks."
            if numeric_checks_pass
            else "Numeric ANCOVA result values failed one or more sanity checks."
        ),
    )

    n_check_pass = (
        isinstance(n_total, int)
        and n_total > 0
        and isinstance(n_by_treatment, dict)
        and sum(int(v) for v in n_by_treatment.values()) == n_total
    )
    add_check(
        checks,
        hook="statistical_result_sanity_hook",
        term="analysis_n_matches_treatment_counts",
        passed=n_check_pass,
        expected="n_total equals sum of treatment counts",
        observed={"n_total": n_total, "n_by_treatment": n_by_treatment},
        details=(
            "Analysis N matches treatment counts."
            if n_check_pass
            else "Analysis N does not match treatment counts."
        ),
    )


def check_final_report_text(report_text: str | None, checks: list[dict[str, Any]]) -> None:
    if report_text is None:
        add_check(
            checks,
            hook="final_response_safety_hook",
            term="optional_report_text_overclaim_scan",
            passed=True,
            expected="no optional report text supplied",
            observed="not scanned",
            details="No final report text was supplied; overclaim scan skipped.",
        )
        return
    hits = [
        pattern
        for pattern in OVERCLAIM_PATTERNS
        if re.search(pattern, report_text, flags=re.IGNORECASE)
    ]
    add_check(
        checks,
        hook="final_response_safety_hook",
        term="report_text_avoids_clinical_or_regulatory_overclaim",
        passed=not hits,
        expected="no unsupported clinical/regulatory overclaims",
        observed=hits if hits else "no overclaim patterns detected",
        details=(
            "Final report text does not contain configured overclaim patterns."
            if not hits
            else "Final report text contains unsupported clinical or regulatory claim language."
        ),
    )


def resolve_embedded_contract(result: dict[str, Any], explicit_path: Path | None) -> dict[str, Any] | None:
    path = explicit_path
    if path is None:
        embedded = result.get("analysis_contract", {}).get("contract_path")
        path = Path(embedded) if embedded else None
    if path is None or not path.exists():
        return None
    return load_json(path)


def decide_release(checks: list[dict[str, Any]], result: dict[str, Any]) -> str:
    if any(check["status"] == "FAIL" for check in checks):
        return "FAIL"
    if result.get("analysis_status") == "BLOCKED":
        return "BLOCK"
    return "PASS"


def run_final_result_review_hook(
    ancova_result_path: Path,
    *,
    contract_path: Path | None = None,
    final_report_path: Path | None = None,
) -> dict[str, Any]:
    result = load_json(ancova_result_path)
    contract = resolve_embedded_contract(result, contract_path)
    report_text = final_report_path.read_text(encoding="utf-8") if final_report_path else None

    checks: list[dict[str, Any]] = []
    check_qc_gate_consistency(result, checks)
    check_contract_alignment(result, contract, checks)
    check_source_data_handling(result, checks)
    check_statistical_result(result, checks)
    check_final_report_text(report_text, checks)

    release_decision = decide_release(checks, result)
    return {
        "schema_version": "final-result-review-hook-v1",
        "generated_at_utc": utc_now(),
        "hook_name": "final_result_review_hook",
        "ancova_result_path": str(ancova_result_path.resolve()),
        "release_decision": release_decision,
        "release_meaning": {
            "PASS": "Result is internally consistent and may be used in the final demo report.",
            "BLOCK": "Analysis was correctly blocked; final report may describe the blocking reason, not ANCOVA results.",
            "FAIL": "Do not release final result until failed hook checks are resolved.",
        }[release_decision],
        "analysis_status": result.get("analysis_status"),
        "analysis_executed": result.get("analysis_executed"),
        "check_counts": {
            "PASS": sum(1 for check in checks if check["status"] == "PASS"),
            "FAIL": sum(1 for check in checks if check["status"] == "FAIL"),
        },
        "failed_checks": [check for check in checks if check["status"] == "FAIL"],
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run final result review and quality hook.")
    parser.add_argument("--ancova-result", required=True, type=Path, help="Path to ANCOVA result JSON.")
    parser.add_argument("--contract", type=Path, default=None, help="Optional SAP contract JSON override.")
    parser.add_argument("--final-report", type=Path, default=None, help="Optional final report text/markdown to scan.")
    parser.add_argument("--output-json", required=True, type=Path, help="Path for hook review JSON.")
    args = parser.parse_args()

    review = run_final_result_review_hook(
        args.ancova_result.resolve(),
        contract_path=args.contract.resolve() if args.contract else None,
        final_report_path=args.final_report.resolve() if args.final_report else None,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(review, indent=2), encoding="utf-8")

    print(f"Wrote final result review hook JSON: {args.output_json}")
    print(f"Release decision: {review['release_decision']}")
    print(f"Analysis status: {review['analysis_status']}")
    print(f"Check counts: {review['check_counts']}")
    if review["failed_checks"]:
        print("Failed checks:")
        for item in review["failed_checks"]:
            print(f"- {item['hook']} / {item['term']}: {item['details']}")


if __name__ == "__main__":
    main()

