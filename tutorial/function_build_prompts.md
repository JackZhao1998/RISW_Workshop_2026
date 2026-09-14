# Function-by-function construction prompts

Use these optional smaller requests when building or discussing one function at a time. The 14 chapter prompts remain the main learning sequence. Provide the preceding component context and agreed schema to the coding agent. Repeated utility names have one reusable prompt with their reference locations listed; each module's `main()` follows that module's interface. These prompts request a rebuild with the safeguards described, not a claim that the existing function already implements every requirement.

## `_clean_values()`

**Purpose:** Normalize text for QC.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _clean_values() for the biomedical workshop pipeline. Return a cleaned string Series with whitespace removed and an explicit missing-value policy. Preserve the original Series; this function must not edit the source DataFrame. Keep this step focused on the named function and explain its input/output contract.
```

## `_load_contract()`

**Purpose:** Load the QC contract.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _load_contract() for the biomedical workshop pipeline. Accept a dictionary or JSON path, validate the expected top-level contract structure, and report malformed or missing content clearly. Do not treat arbitrary document strings as executable expressions. Keep this step focused on the named function and explain its input/output contract.
```

## `_parse_equality_filter()`

**Purpose:** Parse the QC population rule.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _parse_equality_filter() for the biomedical workshop pipeline. Support only a documented column-equals-quoted-value grammar and return the column and value. Reject unsupported syntax instead of using eval or guessing a filter. Keep this step focused on the named function and explain its input/output contract.
```

## `_row()`

**Purpose:** Construct one QC finding.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _row() for the biomedical workshop pipeline. Return a dictionary with task, term, dataset, expected, observed, pass_flag, status, severity, details, and source_section. Keep status and pass_flag consistent and preserve meaningful observed values. Keep this step focused on the named function and explain its input/output contract.
```

## `_source()`

**Purpose:** Read the source anchor for a contract field.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _source() for the biomedical workshop pipeline. Return the source section for the requested field and handle missing field metadata explicitly. Do not fabricate a section when none was extracted. Keep this step focused on the named function and explain its input/output contract.
```

## `_unique_values()`

**Purpose:** Inspect categorical values.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _unique_values() for the biomedical workshop pipeline. Return deterministic unique nonempty cleaned values for a requested DataFrame column. Define the behavior for an absent column and avoid modifying the DataFrame. Keep this step focused on the named function and explain its input/output contract.
```

## `_value()`

**Purpose:** Read a contract value for QC.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement _value() for the biomedical workshop pipeline. Read a named field from analysis_contract while distinguishing an absent value from valid false, zero, or empty values. Require callers to handle missing mandatory fields rather than silently assuming readiness. Keep this step focused on the named function and explain its input/output contract.
```

## `add_check()`

**Purpose:** Accumulate a review finding.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement add_check() for the biomedical workshop pipeline. Append a structured review finding with expected and observed evidence, PASS/FAIL, severity, and explanation. Keep the decision fields consistent; do not convert a skipped mandatory check into PASS. Keep this step focused on the named function and explain its input/output contract.
```

## `all_bullets()`

**Purpose:** Read list entries from a SAP section.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement all_bullets() for the biomedical workshop pipeline. Extract list entries in source order without inventing text. Document support for bullet and numbered lists, and preserve enough source location information for later evidence checks. Keep this step focused on the named function and explain its input/output contract.
```

## `artifact()`

**Purpose:** Describe an input or output artifact.

**Reference locations:** `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`

**Send to your coding agent:**

```text
Please implement artifact() for the biomedical workshop pipeline. Return its relative path, existence, and SHA-256 fingerprint. Report missing artifacts explicitly and never describe a missing file as verified. Keep this step focused on the named function and explain its input/output contract.
```

## `build_analysis_dataset()`

**Purpose:** Select and join the analysis records.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement build_analysis_dataset() for the biomedical workshop pipeline. Apply the validated population and endpoint rules, including ANL01FL = Y, and join by USUBJID with one-to-one validation. Preserve source DataFrames, account for exclusions, and reject nonfinite model inputs or unrecognized treatments. Return the selected rows and the information needed to reconcile counts with QC. Keep this step focused on the named function and explain its input/output contract.
```

## `bullet_value()`

**Purpose:** Extract a labeled SAP item.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement bullet_value() for the biomedical workshop pipeline. Read the value following a specific label in a Markdown list. Escape the label when matching text and expose absent or repeated conflicting labels for review instead of selecting a value silently. Keep this step focused on the named function and explain its input/output contract.
```

## `bullets_after_phrase()`

**Purpose:** Extract a required-variable list.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement bullets_after_phrase() for the biomedical workshop pipeline. Find the designated introductory phrase and collect only its following list, stopping at the next section or unrelated text. Preserve order and detect absence explicitly. Keep this step focused on the named function and explain its input/output contract.
```

## `check_contract_alignment()`

**Purpose:** Compare the result with the authorized contract.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement check_contract_alignment() for the biomedical workshop pipeline. Check study, model, formula, outcome, treatment, baseline, and contrast against the independently loaded contract. List mismatches and missing mandatory values; two absent values must not count as agreement. Keep this step focused on the named function and explain its input/output contract.
```

## `check_final_report_text()`

**Purpose:** Review the draft's claims.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement check_final_report_text() for the biomedical workshop pipeline. Flag unsupported clinical or regulatory claims while retaining context, including negation and quoted examples. Record whether text was actually reviewed; describe keyword matches as review flags rather than complete scientific validation. Keep this step focused on the named function and explain its input/output contract.
```

## `check_provenance()`

**Purpose:** Review the result's input identities.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement check_provenance() for the biomedical workshop pipeline. Check the recorded contract, QC summary, subject-data, and efficacy-data paths and hashes against current files. Also reconcile them with the QC input identities; self-reported flags alone are insufficient. Keep this step focused on the named function and explain its input/output contract.
```

## `check_qc_gate_consistency()`

**Purpose:** Reconcile the gate and execution state.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement check_qc_gate_consistency() for the biomedical workshop pipeline. Verify that BLOCK never produced a fitted result and that COMPLETED required a valid ALLOW. Recognize FAILED explicitly, and reject contradictory counts, failed checks, or result fields. Keep this step focused on the named function and explain its input/output contract.
```

## `check_sap_contract_against_data()`

**Purpose:** Evaluate data readiness deterministically.

**Reference locations:** `data_qc_helpers.py`

**Send to your coding agent:**

```text
Please implement check_sap_contract_against_data() for the biomedical workshop pipeline. Accept a validated contract and read-only subject/efficacy DataFrames. Return a term-level QC table covering required fields, population, treatments, endpoint availability, duplicates, joins, numeric inputs, and documented consistency tolerances. Use explicit failures for unsupported or incomplete checks and keep all source data unchanged. Keep this step focused on the named function and explain its input/output contract.
```

## `check_source_data_handling()`

**Purpose:** Verify input preservation.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement check_source_data_handling() for the biomedical workshop pipeline. Compare source fingerprints before and after the workflow and report any mismatch. Keep declared mutation flags as supplementary metadata rather than accepting them as proof that files were untouched. Keep this step focused on the named function and explain its input/output contract.
```

## `check_statistical_result()`

**Purpose:** Check numerical result consistency.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement check_statistical_result() for the biomedical workshop pipeline. For completed analysis, validate finite estimates and standard errors, confidence interval bounds, p-value range, positive residual degrees of freedom, and agreement of N with both arm counts and QC. Check internal estimate/SE/t/p consistency using the recorded inference settings. Blocked analysis must contain no fitted estimates. Keep this step focused on the named function and explain its input/output contract.
```

## `clean_values()`

**Purpose:** Normalize text for analysis selection.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement clean_values() for the biomedical workshop pipeline. Return trimmed string values with a documented missing-value representation, without changing the caller's Series. Keep normalization consistent with the QC helper. Keep this step focused on the named function and explain its input/output contract.
```

## `code_or_text_formula()`

**Purpose:** Extract the stated model formula.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement code_or_text_formula() for the biomedical workshop pipeline. Read a supported fenced formula or explicit model line and preserve it as text. Expose missing or conflicting formulas for review; never execute a formula extracted from a document. Keep this step focused on the named function and explain its input/output contract.
```

## `collect_path_candidates()`

**Purpose:** Collect declared file-operation targets.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement collect_path_candidates() for the biomedical workshop pipeline. Traverse the structured tool event and return all relevant input and output path fields, including nested lists and objects. Document the accepted event structure and reject ambiguous events at the policy layer. Keep this step focused on the named function and explain its input/output contract.
```

## `command_has_mutating_pattern()`

**Purpose:** Flag suspicious shell operations.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement command_has_mutating_pattern() for the biomedical workshop pipeline. Detect common mutation operators for diagnostic purposes. Document false positives and bypass limits, and keep this heuristic supplementary to structured operation validation rather than treating it as a shell sandbox. Keep this step focused on the named function and explain its input/output contract.
```

## `command_mentions_data_dir()`

**Purpose:** Identify shell references to protected data.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement command_mentions_data_dir() for the biomedical workshop pipeline. Recognize supported path spellings for the protected directory and return a diagnostic match. Document that substring matching cannot prove a command's safety or resolve every shell expansion. Keep this step focused on the named function and explain its input/output contract.
```

## `contract_value()`

**Purpose:** Read a contract value for analysis.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement contract_value() for the biomedical workshop pipeline. Retrieve the named value from a validated contract and report missing required values explicitly. Do not supply an unstated model, contrast, or population default. Keep this step focused on the named function and explain its input/output contract.
```

## `decide_release()`

**Purpose:** Choose the final review outcome.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement decide_release() for the biomedical workshop pipeline. Return FAIL for failed mandatory checks or inconsistent artifacts, BLOCK for a correctly blocked analysis, and PASS only for a completed result with all required reviews satisfied. Do not equate ALLOW with successful completion. Keep this step focused on the named function and explain its input/output contract.
```

## `evidence()`

**Purpose:** Preserve a source evidence snippet.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement evidence() for the biomedical workshop pipeline. Create a readable source snippet without changing its meaning. Retain an anchor to the original text, indicate truncation, and avoid cutting off a qualification that is needed to support the extracted claim. Keep this step focused on the named function and explain its input/output contract.
```

## `extract_contract()`

**Purpose:** Coordinate deterministic SAP extraction.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement extract_contract() for the biomedical workshop pipeline. Read the supported Markdown SAP, call the section and field helpers, and construct the agreed contract schema with evidence, extraction status, unresolved fields, and source fingerprint. Validate the result and do not inspect CSVs or infer data readiness. Keep this step focused on the named function and explain its input/output contract.
```

## `field()`

**Purpose:** Construct one source-supported contract field.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement field() for the biomedical workshop pipeline. Return value, source_section, evidence, and FOUND/NOT_FOUND/AMBIGUOUS status. Preserve valid falsy values and explicitly represent missing or conflicting information without inventing evidence. Keep this step focused on the named function and explain its input/output contract.
```

## `field_value()`

**Purpose:** Read a contract value during final review.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement field_value() for the biomedical workshop pipeline. Retrieve a named field for comparison with the result. Expose missing or malformed fields so the alignment check can fail explicitly rather than treating absence as agreement. Keep this step focused on the named function and explain its input/output contract.
```

## `find_demo_root()`

**Purpose:** Locate the project from a script path.

**Reference locations:** `skills/ancova-test/scripts/run_ancova_test.py`; `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`; `skills/data-checker/scripts/run_data_checker.py`

**Send to your coding agent:**

```text
Please implement find_demo_root() for the biomedical workshop pipeline. Search the script directory and its ancestors for the component's required project markers. Return the verified project root or a clear error without hard-coding a user's local path. Keep this step focused on the named function and explain its input/output contract.
```

## `find_section()`

**Purpose:** Look up a SAP section.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement find_section() for the biomedical workshop pipeline. Find a named section using a documented heading-normalization rule. Preserve section identity for evidence and handle absent or duplicate ambiguous headings explicitly. Keep this step focused on the named function and explain its input/output contract.
```

## `fit_ancova_ols()`

**Purpose:** Fit the authorized toy ANCOVA.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement fit_ancova_ols() for the biomedical workshop pipeline. Fit an intercept, explicit treatment indicator, and baseline covariate using stable linear algebra. Validate finite data, full rank, both treatment arms, and positive residual degrees of freedom. Return full-precision coefficients, uncertainty, t inference, and diagnostics with recorded workshop settings. Treat this as an internal numerical function behind the gated public entry point. Keep this step focused on the named function and explain its input/output contract.
```

## `infer_contrast_labels()`

**Purpose:** Resolve active and reference treatments.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement infer_contrast_labels() for the biomedical workshop pipeline. Parse the explicit contract contrast and check both labels against permitted treatments. Return active and reference labels in the stated direction; reject ambiguity rather than using alphabetical order or list position as an unstated default. Keep this step focused on the named function and explain its input/output contract.
```

## `is_inside_or_equal()`

**Purpose:** Check protected-path containment.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement is_inside_or_equal() for the biomedical workshop pipeline. Compare resolved paths using platform-appropriate path semantics, accepting the directory itself as inside. Handle '..' and resolved links where supported, and ensure a sibling with a similar prefix is not misclassified as a child. Keep this step focused on the named function and explain its input/output contract.
```

## `load_event()`

**Purpose:** Read a proposed tool event.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement load_event() for the biomedical workshop pipeline. Read JSON from an explicit file or standard input and validate its required tool-operation fields. Return a structured error for missing or malformed events so the hook can fail closed. Keep this step focused on the named function and explain its input/output contract.
```

## `load_json()`

**Purpose:** Load structured pipeline artifacts.

**Reference locations:** `ancova_helpers.py`; `hooks/final_result_review_hook.py`; `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`

**Send to your coding agent:**

```text
Please implement load_json() for the biomedical workshop pipeline. Accept the documented path/object input forms, return a JSON object, and reject malformed or unsupported content clearly. Keep loading separate from artifact-specific schema validation. Keep this step focused on the named function and explain its input/output contract.
```

## `looks_like_path()`

**Purpose:** Recognize a possible path token.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement looks_like_path() for the biomedical workshop pipeline. Implement this only as a candidate-detection heuristic for the documented event format. Avoid treating a negative heuristic result as authorization to execute an otherwise unclassified operation. Keep this step focused on the named function and explain its input/output contract.
```

## `main()`

**Purpose:** Expose the component's CLI.

**Reference locations:** `ancova_helpers.py`; `data_qc_helpers.py`; `hooks/final_result_review_hook.py`; `hooks/pre_tool_data_security_hook.py`; `skills/ancova-test/scripts/run_ancova_test.py`; `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`; `skills/data-checker/scripts/run_data_checker.py`; `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement main() for the biomedical workshop pipeline. Use argparse for the component's documented input/output flags, validate paths and schemas, call its public helper, and write structured status and useful exit behavior. Preserve the analysis gate in analysis entry points, reject protected output locations, and avoid embedding scientific logic in the CLI. Keep this step focused on the named function and explain its input/output contract.
```

## `make_summary()`

**Purpose:** Summarize the QC table.

**Reference locations:** `skills/data-checker/scripts/run_data_checker.py`

**Send to your coding agent:**

```text
Please implement make_summary() for the biomedical workshop pipeline. Validate that all required checks exist, then summarize status counts, failed terms, endpoint/population counts, and matching contract/input fingerprints. ALLOW only a complete passing set of required checks; an empty or malformed table must BLOCK. Keep this step focused on the named function and explain its input/output contract.
```

## `norm()`

**Purpose:** Normalize a path for policy checks.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement norm() for the biomedical workshop pipeline. Resolve the path and apply platform-appropriate case handling without changing the actual filesystem. Document unresolved-link behavior and use this consistently with the containment checker. Keep this step focused on the named function and explain its input/output contract.
```

## `parse_equality_filter()`

**Purpose:** Parse the analysis population rule.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement parse_equality_filter() for the biomedical workshop pipeline. Support the same explicit equality grammar as QC, return the column and value, and raise a clear error for unsupported syntax. Do not evaluate arbitrary source strings. Keep this step focused on the named function and explain its input/output contract.
```

## `require_qc_allow()`

**Purpose:** Enforce the pre-analysis decision.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement require_qc_allow() for the biomedical workshop pipeline. Validate complete QC evidence, current contract/data identities, and required checks. Recheck deterministic QC on the exact selected inputs in the controlled workflow. Return allowed status and reasons, failing closed for missing, stale, edited, or contradictory evidence. Expand the interface if needed to perform these checks. Keep this step focused on the named function and explain its input/output contract.
```

## `require_success()`

**Purpose:** Validate a subprocess stage outcome.

**Reference locations:** `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`

**Send to your coding agent:**

```text
Please implement require_success() for the biomedical workshop pipeline. Raise or return a structured failure for nonzero process status and retain the command's useful error output. Keep domain decisions such as BLOCK or FAIL separate: a zero exit status does not mean analysis was allowed or the result passed review. Keep this step focused on the named function and explain its input/output contract.
```

## `resolve_candidate()`

**Purpose:** Resolve an event path.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement resolve_candidate() for the biomedical workshop pipeline. Resolve relative paths against an explicit project base directory, preserving absolute paths appropriately. Return a canonical candidate for containment checking; do not use the current working directory implicitly. Keep this step focused on the named function and explain its input/output contract.
```

## `resolve_embedded_contract()`

**Purpose:** Locate the contract used for review.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement resolve_embedded_contract() for the biomedical workshop pipeline. Prefer an explicit contract path when supplied, otherwise use a validated recorded path. Check existence, schema, and the expected fingerprint before trusting it. Report mismatched explicit and recorded identities. Keep this step focused on the named function and explain its input/output contract.
```

## `run_ancova_if_qc_passes()`

**Purpose:** Provide the gated analysis entry point.

**Reference locations:** `ancova_helpers.py`

**Send to your coding agent:**

```text
Please implement run_ancova_if_qc_passes() for the biomedical workshop pipeline. Validate the contract and QC evidence, invoke the pre-analysis gate, and return BLOCKED without constructing or fitting the model when disallowed. On ALLOW, use the exact verified inputs, call the dataset builder and numerical fitter, and return a structured COMPLETED or FAILED record with provenance and no fabricated results. Keep this step focused on the named function and explain its input/output contract.
```

## `run_command()`

**Purpose:** Run one known pipeline stage.

**Reference locations:** `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`

**Send to your coding agent:**

```text
Please implement run_command() for the biomedical workshop pipeline. Execute a list of arguments without shell string interpolation, using an explicit working directory. Capture status, stdout, and stderr, and return structured evidence for the manifest. Limit the dispatcher to approved component calls and perform the relevant hook checks before dispatch. Keep this step focused on the named function and explain its input/output contract.
```

## `run_final_result_review_hook()`

**Purpose:** Coordinate final result review.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement run_final_result_review_hook() for the biomedical workshop pipeline. Load and validate the contract, QC evidence, result, and optional draft report, call each review function, and return checks plus PASS/BLOCK/FAIL. Preserve malformed-input failures as review artifacts and record exactly which draft text was reviewed. Keep this step focused on the named function and explain its input/output contract.
```

## `run_pre_tool_data_security_hook()`

**Purpose:** Decide whether a file operation may run.

**Reference locations:** `hooks/pre_tool_data_security_hook.py`

**Send to your coding agent:**

```text
Please implement run_pre_tool_data_security_hook() for the biomedical workshop pipeline. Validate a structured tool event, resolve every target, and allow only classified reads against protected SAP/data sources. Block mutations and unknown operations with reasons. Return a JSON decision for the controlled dispatcher and document that callers must enforce it. Keep this step focused on the named function and explain its input/output contract.
```

## `sha256_file()`

**Purpose:** Fingerprint a file's bytes.

**Reference locations:** `ancova_helpers.py`; `hooks/final_result_review_hook.py`; `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`; `skills/data-checker/scripts/run_data_checker.py`; `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement sha256_file() for the biomedical workshop pipeline. Read the file in binary chunks and return a SHA-256 hex digest without modifying it. Report missing or unreadable files explicitly; describe the hash as content identity, not a signature or proof of who produced it. Keep this step focused on the named function and explain its input/output contract.
```

## `split_sections()`

**Purpose:** Split a Markdown SAP into sections.

**Reference locations:** `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement split_sections() for the biomedical workshop pipeline. Preserve headings, body text, and source locations under a documented heading convention. Detect duplicate headings that would otherwise overwrite content and return an explicit ambiguity for review. Keep this step focused on the named function and explain its input/output contract.
```

## `utc_now()`

**Purpose:** Record a portable timestamp.

**Reference locations:** `ancova_helpers.py`; `hooks/final_result_review_hook.py`; `hooks/pre_tool_data_security_hook.py`; `skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py`; `skills/data-checker/scripts/run_data_checker.py`; `skills/sap-extractor/scripts/extract_sap_contract.py`

**Send to your coding agent:**

```text
Please implement utc_now() for the biomedical workshop pipeline. Return a timezone-aware UTC timestamp in a consistent ISO 8601 format. Keep it free of local account or machine metadata. Keep this step focused on the named function and explain its input/output contract.
```

## `verify_hash_from_result()`

**Purpose:** Verify one recorded file fingerprint.

**Reference locations:** `hooks/final_result_review_hook.py`

**Send to your coding agent:**

```text
Please implement verify_hash_from_result() for the biomedical workshop pipeline. Require a valid path and expected SHA-256, hash the current file, and append a clear PASS/FAIL finding. Missing, unreadable, or changed files must produce explicit failed provenance checks. Keep this step focused on the named function and explain its input/output contract.
```
