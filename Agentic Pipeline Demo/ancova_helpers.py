"""Deterministic ANCOVA helpers gated by data-checker QC output."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    path = Path(value)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def contract_value(contract: dict[str, Any], key: str, default: Any = None) -> Any:
    return contract.get("analysis_contract", {}).get(key, {}).get("value", default)


def clean_values(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def parse_equality_filter(expression: str) -> tuple[str, str]:
    match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*==\s*['\"](.+?)['\"]\s*$", expression)
    if not match:
        raise ValueError(f"Unsupported population filter: {expression}")
    return match.group(1), match.group(2)


def infer_contrast_labels(contract: dict[str, Any]) -> tuple[str, str]:
    contrast = contract_value(contract, "contrast", "")
    allowed = contract_value(contract, "allowed_treatments", [])
    if " minus " in contrast:
        active, reference = [part.strip() for part in contrast.split(" minus ", 1)]
        return active, reference
    if len(allowed) == 2:
        return allowed[1], allowed[0]
    raise ValueError("Could not infer active/reference treatment labels from SAP contract.")


def require_qc_allow(qc_summary: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    decision = qc_summary.get("pre_analysis_decision")
    failed_terms = qc_summary.get("failed_terms", [])
    return decision == "ALLOW", failed_terms


def build_analysis_dataset(
    contract: dict[str, Any],
    subject_df: pd.DataFrame,
    efficacy_df: pd.DataFrame,
    active_label: str,
    reference_label: str,
) -> pd.DataFrame:
    subject_key = "USUBJID"
    treatment_var = contract_value(contract, "treatment_variable")
    population_filter = contract_value(contract, "population_filter")
    parameter_code = contract_value(contract, "parameter_code")
    analysis_visit = contract_value(contract, "analysis_visit")
    outcome = contract_value(contract, "outcome_variable")
    baseline = contract_value(contract, "baseline_covariate")

    pop_col, pop_value = parse_equality_filter(population_filter)
    population = subject_df.loc[clean_values(subject_df[pop_col]) == pop_value].copy()
    endpoint = efficacy_df.loc[
        (clean_values(efficacy_df["PARAMCD"]) == parameter_code)
        & (clean_values(efficacy_df["AVISIT"]) == analysis_visit)
        & (clean_values(efficacy_df["ANL01FL"]) == "Y")
    ].copy()

    merged = population.merge(
        endpoint[[subject_key, outcome, baseline]],
        on=subject_key,
        how="inner",
        validate="one_to_one",
    )
    merged = merged.loc[
        clean_values(merged[treatment_var]).isin([active_label, reference_label])
    ].copy()
    merged["_treatment_indicator"] = (
        clean_values(merged[treatment_var]) == active_label
    ).astype(float)
    merged[outcome] = pd.to_numeric(merged[outcome], errors="coerce")
    merged[baseline] = pd.to_numeric(merged[baseline], errors="coerce")
    merged = merged.dropna(subset=[outcome, baseline, "_treatment_indicator"])
    return merged


def fit_ancova_ols(
    analysis_df: pd.DataFrame,
    *,
    outcome: str,
    baseline: str,
) -> dict[str, Any]:
    y = analysis_df[outcome].to_numpy(dtype=float)
    x = np.column_stack(
        [
            np.ones(len(analysis_df), dtype=float),
            analysis_df["_treatment_indicator"].to_numpy(dtype=float),
            analysis_df[baseline].to_numpy(dtype=float),
        ]
    )
    n, p = x.shape
    if n <= p:
        raise ValueError(f"Not enough analysis rows for ANCOVA: n={n}, parameters={p}")
    xtx_inv = np.linalg.inv(x.T @ x)
    beta = xtx_inv @ x.T @ y
    fitted = x @ beta
    residuals = y - fitted
    df_residual = n - p
    mse = float((residuals.T @ residuals) / df_residual)
    covariance = mse * xtx_inv
    se = np.sqrt(np.diag(covariance))
    treatment_estimate = float(beta[1])
    treatment_se = float(se[1])
    t_stat = treatment_estimate / treatment_se
    p_value = float(2 * stats.t.sf(abs(t_stat), df=df_residual))
    t_crit = float(stats.t.ppf(0.975, df=df_residual))
    ci = [
        float(treatment_estimate - t_crit * treatment_se),
        float(treatment_estimate + t_crit * treatment_se),
    ]
    return {
        "coefficients": {
            "intercept": float(beta[0]),
            "treatment_indicator": treatment_estimate,
            "baseline": float(beta[2]),
        },
        "standard_errors": {
            "intercept": float(se[0]),
            "treatment_indicator": treatment_se,
            "baseline": float(se[2]),
        },
        "estimate": treatment_estimate,
        "standard_error": treatment_se,
        "confidence_interval_95": ci,
        "t_statistic": float(t_stat),
        "p_value": p_value,
        "df_residual": int(df_residual),
        "mse": mse,
    }


def run_ancova_if_qc_passes(
    sap_contract_json: str | Path | dict[str, Any],
    qc_summary_json: str | Path | dict[str, Any],
    subject_df: pd.DataFrame,
    efficacy_df: pd.DataFrame,
    *,
    subject_dataset_name: str = "adsl",
    efficacy_dataset_name: str = "adeff",
) -> dict[str, Any]:
    """Run ANCOVA only when the data-checker QC summary allows analysis."""

    contract = load_json(sap_contract_json)
    qc_summary = load_json(qc_summary_json)
    qc_allowed, failed_terms = require_qc_allow(qc_summary)

    active_label, reference_label = infer_contrast_labels(contract)
    outcome = contract_value(contract, "outcome_variable")
    baseline = contract_value(contract, "baseline_covariate")
    treatment_var = contract_value(contract, "treatment_variable")
    formula = contract_value(contract, "formula")

    result: dict[str, Any] = {
        "schema_version": "ancova-analysis-result-v1",
        "generated_at_utc": utc_now(),
        "analysis_status": "BLOCKED" if not qc_allowed else "PENDING",
        "analysis_executed": False,
        "block_reason": None,
        "qc_gate": {
            "pre_analysis_decision": qc_summary.get("pre_analysis_decision"),
            "all_terms_passed": qc_summary.get("all_terms_passed"),
            "failed_terms": failed_terms,
        },
        "analysis_contract": {
            "study_id": contract_value(contract, "study_id"),
            "model": contract_value(contract, "model"),
            "formula": formula,
            "outcome": outcome,
            "treatment": treatment_var,
            "baseline_covariate": baseline,
            "contrast": f"{active_label} minus {reference_label}",
        },
        "input_datasets": {
            "subject_dataset_name": subject_dataset_name,
            "efficacy_dataset_name": efficacy_dataset_name,
        },
        "data_handling": {
            "source_data_modified": False,
            "analysis_run_only_after_qc_allow": True,
        },
    }

    if not qc_allowed:
        result["block_reason"] = "Data-checker QC summary did not return ALLOW."
        return result

    analysis_df = build_analysis_dataset(
        contract,
        subject_df,
        efficacy_df,
        active_label=active_label,
        reference_label=reference_label,
    )
    if analysis_df.empty:
        result["analysis_status"] = "FAILED"
        result["block_reason"] = "QC allowed analysis, but constructed analysis dataset is empty."
        return result

    fit = fit_ancova_ols(analysis_df, outcome=outcome, baseline=baseline)
    treatment_counts = (
        analysis_df[treatment_var].astype("string").fillna("").value_counts().to_dict()
    )
    result.update(
        {
            "analysis_status": "COMPLETED",
            "analysis_executed": True,
            "analysis_dataset": {
                "n_total": int(analysis_df.shape[0]),
                "n_by_treatment": {str(key): int(value) for key, value in treatment_counts.items()},
                "subjects": analysis_df["USUBJID"].astype("string").tolist(),
            },
            "result": {
                "contrast": f"{active_label} minus {reference_label}",
                "estimate": round(fit["estimate"], 6),
                "standard_error": round(fit["standard_error"], 6),
                "confidence_interval_95": [
                    round(fit["confidence_interval_95"][0], 6),
                    round(fit["confidence_interval_95"][1], 6),
                ],
                "t_statistic": round(fit["t_statistic"], 6),
                "p_value": float(fit["p_value"]),
                "p_value_display": "<0.000001"
                if fit["p_value"] < 0.000001
                else str(round(fit["p_value"], 6)),
                "df_residual": fit["df_residual"],
                "model_engine": "numpy OLS with scipy t distribution",
            },
            "diagnostics": {
                "coefficients": {k: round(v, 6) for k, v in fit["coefficients"].items()},
                "standard_errors": {k: round(v, 6) for k, v in fit["standard_errors"].items()},
                "mse": round(fit["mse"], 6),
            },
        }
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run gated ANCOVA from SAP contract and QC summary.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--qc-summary", required=True, type=Path)
    parser.add_argument("--subject-data", required=True, type=Path)
    parser.add_argument("--efficacy-data", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    args = parser.parse_args()

    subject_df = pd.read_csv(args.subject_data)
    efficacy_df = pd.read_csv(args.efficacy_data)
    result = run_ancova_if_qc_passes(
        args.contract,
        args.qc_summary,
        subject_df,
        efficacy_df,
        subject_dataset_name=args.subject_data.name,
        efficacy_dataset_name=args.efficacy_data.name,
    )

    result["input_datasets"]["subject_data_path"] = str(args.subject_data.resolve())
    result["input_datasets"]["efficacy_data_path"] = str(args.efficacy_data.resolve())
    result["input_datasets"]["subject_data_sha256"] = sha256_file(args.subject_data.resolve())
    result["input_datasets"]["efficacy_data_sha256"] = sha256_file(args.efficacy_data.resolve())

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote ANCOVA result JSON: {args.output_json}")
    print(f"Analysis status: {result['analysis_status']}")
    print(f"Analysis executed: {result['analysis_executed']}")
    if result.get("result"):
        print(json.dumps(result["result"], indent=2))
    elif result.get("block_reason"):
        print(f"Block reason: {result['block_reason']}")


if __name__ == "__main__":
    main()
