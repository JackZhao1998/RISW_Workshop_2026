---
name: data-checker
description: "Validate biomedical analysis datasets against a structured SAP contract JSON. Use when Codex needs deterministic data-readiness QC before analysis, including required variable checks, endpoint availability, analysis population checks, treatment value checks, and population-to-endpoint coverage. This skill must not run statistical models or modify source data."
---

# Data Checker

## Overview

Validate already-loaded or file-backed analysis datasets against a SAP-derived analysis contract. Use deterministic pandas checks and return a detailed term-checking table with pass/fail flags for downstream QC gates.

## Workflow

1. Confirm the SAP extraction step has produced `sap_analysis_contract.json`.
2. Load the subject-level dataset, usually `adsl.csv`, as a pandas DataFrame.
3. Load the efficacy dataset, usually `adeff_results.csv` or `adeff_week24_pass.csv`, as a pandas DataFrame.
4. Call the deterministic helper `check_sap_contract_against_data()` from `data_qc_helpers.py`.
5. Save both table-level output and run-level summary metadata.
6. Report whether every term passed. If any term fails, downstream analysis must be blocked.

## Required Inputs

- SAP contract JSON, produced by the SAP extraction step.
- Subject-level pandas DataFrame or CSV.
- Efficacy-level pandas DataFrame or CSV.

## Function Argument Specifications

Primary helper function:

```python
check_sap_contract_against_data(
    sap_contract_json,
    subject_df,
    efficacy_df,
    *,
    subject_dataset_name="adsl",
    efficacy_dataset_name="adeff",
)
```

Arguments:

| Argument | Type | Required | Meaning | Validation Expectations |
|---|---:|---:|---|---|
| `sap_contract_json` | `str`, `Path`, or `dict` | Yes | Path to `sap_analysis_contract.json` or an already loaded contract object | Must contain top-level `analysis_contract`; expected schema is `sap-analysis-contract-v1` |
| `subject_df` | `pandas.DataFrame` | Yes | Subject-level dataset, usually ADSL | Must include SAP-required subject-level variables such as `USUBJID`, `TRT01P`, and `FASFL` |
| `efficacy_df` | `pandas.DataFrame` | Yes | Efficacy analysis dataset, usually ADEFF | Must include SAP-required efficacy variables such as `USUBJID`, `PARAMCD`, `AVISIT`, `BASE`, `CHG`, and `ANL01FL` |
| `subject_dataset_name` | `str` | No | Label used in output rows for the subject-level dataset | Use the source filename when available, e.g. `adsl.csv` |
| `efficacy_dataset_name` | `str` | No | Label used in output rows for the efficacy dataset | Use the source filename when available, e.g. `adeff_results.csv` |

The helper must not mutate `subject_df`, `efficacy_df`, source CSVs, or the SAP contract.

CLI wrapper:

```text
python scripts/run_data_checker.py \
  --contract <sap_analysis_contract.json> \
  --subject-data <adsl.csv> \
  --efficacy-data <adeff.csv> \
  --output-dir <output-folder>
```

CLI arguments:

| Flag | Required | Expected Value | Output Behavior |
|---|---:|---|---|
| `--contract` | Yes | Path to structured SAP contract JSON | Read only |
| `--subject-data` | Yes | Path to subject-level CSV | Read only; loaded with pandas |
| `--efficacy-data` | Yes | Path to efficacy CSV | Read only; loaded with pandas |
| `--output-dir` | Yes | Directory for generated QC artifacts | Created if missing; receives output files only |

## Checks Performed

- Required subject-level variables are present.
- Required efficacy variables are present.
- `USUBJID` exists and is unique in the subject-level dataset.
- Treatment variable exists and observed values match SAP-allowed treatments.
- SAP population filter can be applied and produces a non-empty population.
- SAP-defined `PARAMCD` exists in efficacy data.
- SAP-defined analysis visit exists in efficacy data.
- Outcome and baseline variables exist.
- Primary endpoint records match `PARAMCD`, `AVISIT`, and `ANL01FL = "Y"`.
- Endpoint subjects are within the analysis population.
- Analysis-population subjects have matching endpoint records.

## Security and Data Handling

- Treat source CSVs as read-only inputs.
- Do not overwrite, edit, impute, or derive replacement source datasets.
- Write outputs only to the requested output directory.
- Do not run ANCOVA or any statistical model in this skill.
- Do not infer missing SAP requirements; rely on the contract JSON.

## Helper Script

Use the wrapper script when file paths are available:

```text
python scripts/run_data_checker.py \
  --contract <sap_analysis_contract.json> \
  --subject-data <adsl.csv> \
  --efficacy-data <adeff.csv> \
  --output-dir <output-folder>
```

The script writes:

- `data_checker_table.csv`
- `data_checker_table.json`
- `data_checker_summary.json`

## Output Table Schema

The helper returns a pandas DataFrame and the wrapper serializes the same rows to CSV and JSON.

| Column | Meaning |
|---|---|
| `task` | QC task group, such as `required_variables`, `endpoint_availability`, or `analysis_population` |
| `term` | Specific term being checked |
| `dataset` | Dataset label used for the check |
| `expected` | SAP-derived expectation |
| `observed` | Value observed in the input data |
| `pass_flag` | Boolean pass/fail flag |
| `status` | `PASS` or `FAIL` |
| `severity` | `INFO`, `WARNING`, or `ERROR` |
| `details` | Human-readable explanation for the term result |
| `source_section` | SAP source section that supplied the expected value |

## Decision Rule

If all checking table rows have `status = PASS`, return:

```text
pre_analysis_decision = ALLOW
```

If any checking table row has `status = FAIL`, return:

```text
pre_analysis_decision = BLOCK
```

The summary must list failed terms so the orchestrator can explain why analysis is blocked.
