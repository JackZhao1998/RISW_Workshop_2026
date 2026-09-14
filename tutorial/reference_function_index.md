# Reference function index

This inventory comes from read-only syntax inspection of the existing reference project. Names and signatures describe that source; the prompts may request additional validation or proposed functions. `main()` functions are CLI entry points. Detailed component roles are in [project_breakdown.md](project_breakdown.md).

## ancova_helpers.py

- `utc_now()` — line 18.
- `sha256_file(path: Path)` — line 22.
- `load_json(value: str | Path | dict[str, Any])` — line 30.
- `contract_value(contract: dict[str, Any], key: str, default: Any=None)` — line 38.
- `clean_values(series: pd.Series)` — line 42.
- `parse_equality_filter(expression: str)` — line 46.
- `infer_contrast_labels(contract: dict[str, Any])` — line 53.
- `require_qc_allow(qc_summary: dict[str, Any])` — line 64.
- `build_analysis_dataset(contract: dict[str, Any], subject_df: pd.DataFrame, efficacy_df: pd.DataFrame, active_label: str, reference_label: str)` — line 70.
- `fit_ancova_ols(analysis_df: pd.DataFrame, *, outcome: str, baseline: str)` — line 111.
- `run_ancova_if_qc_passes(sap_contract_json: str | Path | dict[str, Any], qc_summary_json: str | Path | dict[str, Any], subject_df: pd.DataFrame, efficacy_df: pd.DataFrame, *, subject_dataset_name: str='adsl', efficacy_dataset_name: str='adeff')` — line 166.
- `main()` — line 272.

## data_qc_helpers.py

- `_load_contract(sap_contract_json: str | Path | dict[str, Any])` — line 20.
- `_value(payload: dict[str, Any], key: str, default: Any=None)` — line 28.
- `_source(payload: dict[str, Any], key: str)` — line 33.
- `_clean_values(series: pd.Series)` — line 38.
- `_unique_values(df: pd.DataFrame, column: str)` — line 42.
- `_parse_equality_filter(expression: str)` — line 49.
- `_row(task: str, term: str, dataset: str, expected: Any, observed: Any, passed: bool, details: str, source_section: str='', severity: str='ERROR')` — line 56.
- `check_sap_contract_against_data(sap_contract_json: str | Path | dict[str, Any], subject_df: pd.DataFrame, efficacy_df: pd.DataFrame, *, subject_dataset_name: str='adsl', efficacy_dataset_name: str='adeff')` — line 81.
- `main()` — line 417.

## hooks/final_result_review_hook.py

- `utc_now()` — line 42.
- `load_json(path: Path)` — line 46.
- `sha256_file(path: Path)` — line 51.
- `field_value(contract: dict[str, Any], key: str)` — line 59.
- `add_check(checks: list[dict[str, Any]], *, hook: str, term: str, passed: bool, expected: Any, observed: Any, details: str, severity: str='ERROR')` — line 63.
- `check_qc_gate_consistency(result: dict[str, Any], checks: list[dict[str, Any]])` — line 88.
- `check_contract_alignment(result: dict[str, Any], contract: dict[str, Any] | None, checks: list[dict[str, Any]])` — line 131.
- `verify_hash_from_result(checks: list[dict[str, Any]], *, hook: str, term: str, path_value: str | None, expected_hash: str | None)` — line 178.
- `check_provenance(result: dict[str, Any], checks: list[dict[str, Any]])` — line 225.
- `check_source_data_handling(result: dict[str, Any], checks: list[dict[str, Any]])` — line 260.
- `check_statistical_result(result: dict[str, Any], checks: list[dict[str, Any]])` — line 290.
- `check_final_report_text(report_text: str | None, checks: list[dict[str, Any]])` — line 394.
- `resolve_embedded_contract(result: dict[str, Any], explicit_path: Path | None)` — line 426.
- `decide_release(checks: list[dict[str, Any]], result: dict[str, Any])` — line 436.
- `run_final_result_review_hook(ancova_result_path: Path, *, contract_path: Path | None=None, final_report_path: Path | None=None)` — line 444.
- `main()` — line 485.

## hooks/pre_tool_data_security_hook.py

- `utc_now()` — line 82.
- `norm(path: Path)` — line 86.
- `is_inside_or_equal(path: Path, directory: Path)` — line 90.
- `looks_like_path(value: str)` — line 96.
- `collect_path_candidates(value: Any)` — line 105.
- `resolve_candidate(candidate: str, base_dir: Path)` — line 125.
- `command_has_mutating_pattern(command: str)` — line 132.
- `command_mentions_data_dir(command: str, protected_data_dir: Path)` — line 136.
- `run_pre_tool_data_security_hook(*, tool_name: str, operation: str | None=None, tool_arguments: dict[str, Any] | None=None, paths: list[str] | None=None, protected_data_dir: str | Path=DEFAULT_PROTECTED_DATA_DIR, base_dir: str | Path | None=None)` — line 146.
- `load_event(path: Path | None)` — line 228.
- `main()` — line 238.

## skills/ancova-test/scripts/run_ancova_test.py

- `find_demo_root(start: Path)` — line 14.
- `main()` — line 21.

## skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py

- `utc_now()` — line 16.
- `sha256_file(path: Path)` — line 20.
- `find_demo_root(start: Path)` — line 28.
- `run_command(command: list[str], *, cwd: Path)` — line 35.
- `require_success(step: dict[str, Any])` — line 51.
- `load_json(path: Path)` — line 62.
- `artifact(path: Path)` — line 67.
- `main()` — line 75.

## skills/data-checker/scripts/run_data_checker.py

- `utc_now()` — line 17.
- `sha256_file(path: Path)` — line 21.
- `find_demo_root(start: Path)` — line 29.
- `make_summary(table: pd.DataFrame, contract_path: Path, subject_path: Path, efficacy_path: Path)` — line 36.
- `main()` — line 76.

## skills/sap-extractor/scripts/extract_sap_contract.py

- `sha256_file(path: Path)` — line 35.
- `utc_now()` — line 43.
- `split_sections(markdown: str)` — line 47.
- `find_section(sections: dict[str, str], name: str)` — line 61.
- `evidence(text: str, fallback: str='')` — line 68.
- `field(value: Any, section: str, evidence_text: str, status: str | None=None)` — line 75.
- `bullet_value(section_text: str, label: str)` — line 91.
- `code_or_text_formula(section_text: str)` — line 97.
- `bullets_after_phrase(section_text: str, phrase: str)` — line 105.
- `all_bullets(section_text: str)` — line 119.
- `extract_contract(sap_path: Path)` — line 123.
- `main()` — line 216.
