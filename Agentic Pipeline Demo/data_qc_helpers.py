"""Deterministic SAP-contract data QC helpers for the workshop demo.

The public helper is `check_sap_contract_against_data()`. It loads the SAP
contract JSON, checks pandas DataFrames for required variables, endpoint
availability, and analysis population consistency, then returns a detailed
term-checking table as a pandas DataFrame.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def _load_contract(sap_contract_json: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(sap_contract_json, dict):
        return sap_contract_json
    path = Path(sap_contract_json)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _value(payload: dict[str, Any], key: str, default: Any = None) -> Any:
    field = payload["analysis_contract"].get(key, {})
    return field.get("value", default)


def _source(payload: dict[str, Any], key: str) -> str:
    field = payload["analysis_contract"].get(key, {})
    return field.get("source_section", "")


def _clean_values(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def _unique_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    values = _clean_values(df[column])
    return sorted(value for value in values.unique().tolist() if value)


def _parse_equality_filter(expression: str) -> tuple[str | None, str | None]:
    match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*==\s*['\"](.+?)['\"]\s*$", expression)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def _row(
    task: str,
    term: str,
    dataset: str,
    expected: Any,
    observed: Any,
    passed: bool,
    details: str,
    source_section: str = "",
    severity: str = "ERROR",
) -> dict[str, Any]:
    return {
        "task": task,
        "term": term,
        "dataset": dataset,
        "expected": expected,
        "observed": observed,
        "pass_flag": bool(passed),
        "status": "PASS" if passed else "FAIL",
        "severity": "INFO" if passed else severity,
        "details": details,
        "source_section": source_section,
    }


def check_sap_contract_against_data(
    sap_contract_json: str | Path | dict[str, Any],
    subject_df: pd.DataFrame,
    efficacy_df: pd.DataFrame,
    *,
    subject_dataset_name: str = "adsl",
    efficacy_dataset_name: str = "adeff",
) -> pd.DataFrame:
    """Return a detailed pass/fail table for SAP-contract data readiness terms.

    Parameters
    ----------
    sap_contract_json:
        Path to `sap_analysis_contract.json`, or an already loaded contract dict.
    subject_df:
        Loaded pandas DataFrame for the subject-level dataset.
    efficacy_df:
        Loaded pandas DataFrame for the efficacy analysis dataset.
    subject_dataset_name, efficacy_dataset_name:
        Labels used in the returned checking table.

    Returns
    -------
    pandas.DataFrame
        One row per deterministic check. Important columns are `task`, `term`,
        `expected`, `observed`, `pass_flag`, `status`, and `details`.
    """

    contract = _load_contract(sap_contract_json)
    rows: list[dict[str, Any]] = []

    required = _value(contract, "required_variables", {})
    subject_required = required.get("subject_level", [])
    efficacy_required = required.get("efficacy", [])

    subject_cols = list(subject_df.columns)
    efficacy_cols = list(efficacy_df.columns)
    missing_subject_cols = [column for column in subject_required if column not in subject_cols]
    missing_efficacy_cols = [column for column in efficacy_required if column not in efficacy_cols]

    rows.append(
        _row(
            "required_variables",
            "subject_level_required_variables_present",
            subject_dataset_name,
            subject_required,
            subject_cols,
            not missing_subject_cols,
            "All SAP-required subject-level variables are present."
            if not missing_subject_cols
            else f"Missing subject-level variables: {missing_subject_cols}",
            _source(contract, "required_variables"),
        )
    )
    rows.append(
        _row(
            "required_variables",
            "efficacy_required_variables_present",
            efficacy_dataset_name,
            efficacy_required,
            efficacy_cols,
            not missing_efficacy_cols,
            "All SAP-required efficacy variables are present."
            if not missing_efficacy_cols
            else f"Missing efficacy variables: {missing_efficacy_cols}",
            _source(contract, "required_variables"),
        )
    )

    subject_key = "USUBJID"
    rows.append(
        _row(
            "analysis_population",
            "subject_key_present",
            subject_dataset_name,
            subject_key,
            subject_key in subject_cols,
            subject_key in subject_cols,
            "Subject identifier exists in subject-level data."
            if subject_key in subject_cols
            else "Subject identifier is missing from subject-level data.",
            _source(contract, "required_variables"),
        )
    )
    if subject_key in subject_cols:
        duplicate_n = int(subject_df[subject_key].duplicated().sum())
        rows.append(
            _row(
                "analysis_population",
                "subject_key_unique",
                subject_dataset_name,
                "0 duplicate subject IDs",
                f"{duplicate_n} duplicate subject IDs",
                duplicate_n == 0,
                "Subject-level data have one row per subject."
                if duplicate_n == 0
                else "Subject-level data contain duplicate subject IDs.",
                _source(contract, "required_variables"),
            )
        )

    treatment_var = _value(contract, "treatment_variable")
    allowed_treatments = _value(contract, "allowed_treatments", [])
    treatment_present = treatment_var in subject_cols
    rows.append(
        _row(
            "analysis_population",
            "treatment_variable_present",
            subject_dataset_name,
            treatment_var,
            treatment_present,
            treatment_present,
            "Treatment variable exists in subject-level data."
            if treatment_present
            else "Treatment variable is missing from subject-level data.",
            _source(contract, "treatment_variable"),
        )
    )
    if treatment_present:
        observed_treatments = _unique_values(subject_df, treatment_var)
        unexpected_treatments = [
            value for value in observed_treatments if value not in allowed_treatments
        ]
        rows.append(
            _row(
                "analysis_population",
                "treatment_values_allowed",
                subject_dataset_name,
                allowed_treatments,
                observed_treatments,
                not unexpected_treatments,
                "Observed treatment values match SAP-permitted values."
                if not unexpected_treatments
                else f"Unexpected treatment values: {unexpected_treatments}",
                _source(contract, "allowed_treatments"),
            )
        )

    population_filter = _value(contract, "population_filter", "")
    population_column, population_value = _parse_equality_filter(population_filter)
    population_filter_usable = population_column in subject_cols if population_column else False
    rows.append(
        _row(
            "analysis_population",
            "population_filter_usable",
            subject_dataset_name,
            population_filter,
            f"{population_column} present" if population_filter_usable else "not usable",
            population_filter_usable,
            "Population filter can be applied to subject-level data."
            if population_filter_usable
            else "Population filter cannot be applied to subject-level data.",
            _source(contract, "population_filter"),
        )
    )

    population_subjects: set[str] = set()
    if population_filter_usable and subject_key in subject_cols:
        population_mask = _clean_values(subject_df[population_column]) == population_value
        population_subjects = set(_clean_values(subject_df.loc[population_mask, subject_key]))
        rows.append(
            _row(
                "analysis_population",
                "analysis_population_nonempty",
                subject_dataset_name,
                "population N > 0",
                f"population N = {len(population_subjects)}",
                len(population_subjects) > 0,
                "Analysis population has at least one subject."
                if population_subjects
                else "No subjects match the SAP population filter.",
                _source(contract, "population_filter"),
            )
        )
        if treatment_present:
            treatment_counts = (
                subject_df.loc[population_mask, treatment_var]
                .astype("string")
                .fillna("")
                .value_counts()
                .to_dict()
            )
            missing_treatment_arms = [
                arm for arm in allowed_treatments if int(treatment_counts.get(arm, 0)) == 0
            ]
            rows.append(
                _row(
                    "analysis_population",
                    "analysis_population_treatment_counts",
                    subject_dataset_name,
                    f"nonzero counts for {allowed_treatments}",
                    treatment_counts,
                    not missing_treatment_arms,
                    "Analysis population includes subjects in all SAP-allowed treatment arms."
                    if not missing_treatment_arms
                    else f"Missing treatment arms in analysis population: {missing_treatment_arms}",
                    _source(contract, "treatment_variable"),
                    severity="WARNING",
                )
            )

    parameter_code = _value(contract, "parameter_code")
    analysis_visit = _value(contract, "analysis_visit")
    outcome_var = _value(contract, "outcome_variable")
    baseline_var = _value(contract, "baseline_covariate")

    observed_parameters = _unique_values(efficacy_df, "PARAMCD")
    parameter_present = "PARAMCD" in efficacy_cols and parameter_code in observed_parameters
    rows.append(
        _row(
            "endpoint_availability",
            "parameter_code_present",
            efficacy_dataset_name,
            parameter_code,
            observed_parameters,
            parameter_present,
            "SAP-defined parameter code is present in efficacy data."
            if parameter_present
            else "SAP-defined parameter code is absent from efficacy data.",
            _source(contract, "parameter_code"),
        )
    )

    observed_visits = _unique_values(efficacy_df, "AVISIT")
    visit_present = "AVISIT" in efficacy_cols and analysis_visit in observed_visits
    rows.append(
        _row(
            "endpoint_availability",
            "analysis_visit_present",
            efficacy_dataset_name,
            analysis_visit,
            observed_visits,
            visit_present,
            "SAP-defined analysis visit is present in efficacy data."
            if visit_present
            else "SAP-defined analysis visit is absent from efficacy data.",
            _source(contract, "analysis_visit"),
        )
    )

    for variable, term, source_key in [
        (outcome_var, "outcome_variable_present", "outcome_variable"),
        (baseline_var, "baseline_covariate_present", "baseline_covariate"),
    ]:
        present = variable in efficacy_cols
        rows.append(
            _row(
                "endpoint_availability",
                term,
                efficacy_dataset_name,
                variable,
                present,
                present,
                f"{variable} exists in efficacy data."
                if present
                else f"{variable} is missing from efficacy data.",
                _source(contract, source_key),
            )
        )

    endpoint_subjects: set[str] = set()
    endpoint_record_count = 0
    endpoint_filter_ready = all(
        column in efficacy_cols for column in [subject_key, "PARAMCD", "AVISIT", "ANL01FL"]
    )
    if endpoint_filter_ready:
        endpoint_mask = (
            (_clean_values(efficacy_df["PARAMCD"]) == parameter_code)
            & (_clean_values(efficacy_df["AVISIT"]) == analysis_visit)
            & (_clean_values(efficacy_df["ANL01FL"]) == "Y")
        )
        endpoint_records = efficacy_df.loc[endpoint_mask]
        endpoint_record_count = int(endpoint_records.shape[0])
        endpoint_subjects = set(_clean_values(endpoint_records[subject_key]))

    rows.append(
        _row(
            "endpoint_availability",
            "primary_endpoint_records_present",
            efficacy_dataset_name,
            {
                "PARAMCD": parameter_code,
                "AVISIT": analysis_visit,
                "ANL01FL": "Y",
            },
            f"endpoint records = {endpoint_record_count}",
            endpoint_record_count > 0,
            "Primary endpoint analysis records are available."
            if endpoint_record_count > 0
            else "No primary endpoint analysis records match the SAP contract.",
            _source(contract, "primary_endpoint"),
        )
    )

    if population_subjects and endpoint_filter_ready:
        endpoint_outside_population = sorted(endpoint_subjects - population_subjects)
        missing_endpoint_subjects = sorted(population_subjects - endpoint_subjects)
        rows.append(
            _row(
                "analysis_population",
                "endpoint_subjects_within_analysis_population",
                f"{subject_dataset_name}+{efficacy_dataset_name}",
                "all endpoint subjects in population",
                {
                    "endpoint_subject_count": len(endpoint_subjects),
                    "outside_population": endpoint_outside_population,
                },
                not endpoint_outside_population,
                "All endpoint subjects are in the SAP-defined analysis population."
                if not endpoint_outside_population
                else "Some endpoint subjects are outside the SAP-defined analysis population.",
                _source(contract, "analysis_population"),
            )
        )
        rows.append(
            _row(
                "analysis_population",
                "analysis_population_endpoint_coverage",
                f"{subject_dataset_name}+{efficacy_dataset_name}",
                "all analysis-population subjects have endpoint records",
                {
                    "population_subject_count": len(population_subjects),
                    "endpoint_subject_count": len(endpoint_subjects),
                    "missing_endpoint_subjects": missing_endpoint_subjects,
                },
                not missing_endpoint_subjects,
                "Every analysis-population subject has a matching endpoint record."
                if not missing_endpoint_subjects
                else "Some analysis-population subjects lack matching endpoint records.",
                _source(contract, "missing_data_rule"),
            )
        )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic SAP-contract data QC.")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--subject-data", required=True, type=Path)
    parser.add_argument("--efficacy-data", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    args = parser.parse_args()

    subject_df = pd.read_csv(args.subject_data)
    efficacy_df = pd.read_csv(args.efficacy_data)
    table = check_sap_contract_against_data(
        args.contract,
        subject_df,
        efficacy_df,
        subject_dataset_name=args.subject_data.name,
        efficacy_dataset_name=args.efficacy_data.name,
    )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output_csv, index=False)
    table.to_json(args.output_json, orient="records", indent=2)

    print(f"Wrote checking table CSV: {args.output_csv}")
    print(f"Wrote checking table JSON: {args.output_json}")
    print(table[["task", "term", "dataset", "status", "details"]].to_string(index=False))


if __name__ == "__main__":
    main()
