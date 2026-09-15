---
name: biomed-analysis-workflow
description: "Run the governed biomedical SAP-to-analysis workflow that integrates SAP extraction, pre-tool data security, deterministic data QC, QC-gated ANCOVA, and final result review. Use when Codex needs to check whether a study is ready for primary efficacy analysis and run ANCOVA only if all QC gates pass. This skill coordinates existing local skills/hooks and writes reproducible artifacts; it must not modify source data."
---

# Biomed Analysis Workflow

## Overview

Coordinate the complete demo workflow from SAP and source datasets to a final release decision. This skill is the orchestrator layer; it does not replace the specialized skills or hooks.

## Workflow

1. Run SAP extraction to create `sap_analysis_contract.json`.
2. Run pre-tool data security hooks before reading source datasets.
3. Run data-checker to validate required variables, endpoint availability, and analysis population.
4. Run ANCOVA-test only if data-checker returns `ALLOW`.
5. Run final result review hook to decide whether the result can be released.
6. Write a manifest that records input paths, stage decisions, and output artifacts.

## Component Responsibilities

| Component | Role |
|---|---|
| `sap-extractor` | Extract SAP prose into a structured analysis contract |
| `pre_tool_data_security_hook.py` | Prevent mutation of the protected `data/` folder |
| `data-checker` | Validate SAP-required data terms and emit `ALLOW` or `BLOCK` |
| `ancova-test` | Run ANCOVA only when QC returns `ALLOW` |
| `final_result_review_hook.py` | Verify contract alignment, result sanity, and release decision |

## Function/CLI Argument Specifications

Use the orchestrator script:

```text
python scripts/run_biomed_analysis_workflow.py \
  --sap <SAP.md> \
  --subject-data <adsl.csv> \
  --efficacy-data <adeff.csv> \
  --output-dir <workflow-output-folder>
```

Arguments:

| Flag | Required | Expected Value | Behavior |
|---|---:|---|---|
| `--sap` | Yes | SAP markdown/text file | Read only; passed to SAP extractor |
| `--subject-data` | Yes | Subject-level CSV | Read only; protected by security hook |
| `--efficacy-data` | Yes | Efficacy CSV | Read only; protected by security hook |
| `--output-dir` | Yes | Output directory | Created if missing; receives generated artifacts |

Optional flags:

| Flag | Meaning |
|---|---|
| `--final-report` | Optional text/markdown report to scan for overclaiming in final review |
| `--python` | Optional Python executable; defaults to current interpreter |

## Output Artifacts

The workflow writes:

```text
sap_analysis_contract.json
data_checker_table.csv
data_checker_table.json
data_checker_summary.json
ancova_result.json
final_result_review.json
workflow_manifest.json
```

## Decision Semantics

| Decision | Meaning |
|---|---|
| `ALLOW` | Data QC passed; ANCOVA may run |
| `BLOCK` | Analysis must not run; final report should explain QC failure |
| `PASS` | Final completed result passed release review |
| `FAIL` | Workflow artifact is inconsistent; do not release |

## Hard Rules

- Never edit files under the source `data/` folder.
- Never run ANCOVA when data-checker returns `BLOCK`.
- Never report ANCOVA estimates for a blocked branch.
- Always include the selected input paths and generated artifact paths.
- Treat output as a synthetic workshop demonstration, not clinical evidence.

