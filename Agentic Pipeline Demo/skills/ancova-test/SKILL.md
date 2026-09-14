---
name: ancova-test
description: "Run a deterministic SAP-specified ANCOVA only after the data-checker QC summary returns ALLOW. Use when Codex needs a reproducible primary ANCOVA analysis from a SAP contract JSON, data-checker summary JSON, subject-level CSV/DataFrame, and efficacy CSV/DataFrame. This skill must block execution when QC fails and must not modify source data."
---

# ANCOVA Test

## Overview

Execute the primary ANCOVA analysis as a gated tool step. Treat the data-checker QC summary as a mandatory pre-analysis hook: `ALLOW` runs the model; `BLOCK` returns a blocked result without fitting anything.

## Workflow

1. Confirm `sap_analysis_contract.json` exists from the SAP extraction step.
2. Confirm data-checker has produced `data_checker_summary.json`.
3. Load subject-level and efficacy datasets.
4. Check `pre_analysis_decision` in the QC summary.
5. If the decision is not `ALLOW`, do not fit ANCOVA; return a blocked result with failed QC terms.
6. If the decision is `ALLOW`, construct the analysis dataset using the SAP contract.
7. Fit the SAP-defined model, `CHG = TRT01P + BASE`, with treatment contrast `ABC-201 minus Placebo`.
8. Save JSON with model metadata, N, estimate, CI, p value, inputs, and data-handling flags.

## Function Argument Specifications

Primary helper function:

```python
run_ancova_if_qc_passes(
    sap_contract_json,
    qc_summary_json,
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
| `sap_contract_json` | `str`, `Path`, or `dict` | Yes | Structured SAP contract from the SAP extractor | Must contain `analysis_contract` fields for model, formula, endpoint, treatment, outcome, baseline, contrast, and population |
| `qc_summary_json` | `str`, `Path`, or `dict` | Yes | Summary JSON from `data-checker` | Must contain `pre_analysis_decision`; analysis runs only when value is `ALLOW` |
| `subject_df` | `pandas.DataFrame` | Yes | Subject-level analysis data | Must contain population and treatment variables referenced by SAP contract |
| `efficacy_df` | `pandas.DataFrame` | Yes | Efficacy analysis data | Must contain endpoint, visit, outcome, baseline, and analysis flag variables referenced by SAP contract |
| `subject_dataset_name` | `str` | No | Dataset label recorded in output | Use source filename when available |
| `efficacy_dataset_name` | `str` | No | Dataset label recorded in output | Use source filename when available |

The helper must not mutate DataFrames or source files.

## CLI Wrapper

Use the script when file paths are available:

```text
python scripts/run_ancova_test.py \
  --contract <sap_analysis_contract.json> \
  --qc-summary <data_checker_summary.json> \
  --subject-data <adsl.csv> \
  --efficacy-data <adeff.csv> \
  --output-json <ancova_result.json>
```

CLI arguments:

| Flag | Required | Expected Value | Behavior |
|---|---:|---|---|
| `--contract` | Yes | SAP contract JSON | Read only |
| `--qc-summary` | Yes | Data-checker summary JSON | Read only; determines whether analysis may run |
| `--subject-data` | Yes | Subject-level CSV | Read only; loaded with pandas |
| `--efficacy-data` | Yes | Efficacy CSV | Read only; loaded with pandas |
| `--output-json` | Yes | Output JSON path | Parent folder is created if missing |

## Output Contract

Always write a JSON object with:

- `analysis_status`: `BLOCKED`, `COMPLETED`, or `FAILED`
- `analysis_executed`: boolean
- `qc_gate`: copied QC decision and failed terms
- `analysis_contract`: model, formula, outcome, treatment, baseline, and contrast
- `analysis_dataset`: N and treatment counts when executed
- `result`: estimate, standard error, 95% CI, t statistic, numeric p value, p-value display string, residual df, and model engine when executed
- `data_handling`: source-data mutation flag and QC-gating flag

## Decision Rule

Use this hard gate:

```text
if data_checker_summary.pre_analysis_decision != "ALLOW":
    return BLOCKED without fitting ANCOVA
else:
    fit ANCOVA
```

Do not let the model or user request override this gate.

## Data Handling

- Treat all input files as read-only.
- Do not edit or impute source records.
- Do not run exploratory alternate models in this skill.
- Do not interpret toy results as clinical evidence.
- Include input paths and hashes in the output when the CLI wrapper is used.
