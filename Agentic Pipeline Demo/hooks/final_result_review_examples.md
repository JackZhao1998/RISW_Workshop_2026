# Final Result Review Hook Examples

## Hook Examples

Use these as discussion examples before final reporting.

### 1. QC Gate Consistency Hook

Question:

```text
Did the analysis execution state match the QC decision?
```

Expected behavior:

```text
QC = BLOCK  -> ANCOVA must not run.
QC = ALLOW  -> ANCOVA may run.
```

### 2. SAP Contract Alignment Hook

Question:

```text
Did the final result use the SAP-derived model and variables?
```

Checks:

```text
study_id, model, formula, outcome, treatment, baseline covariate, contrast
```

### 3. Statistical Result Sanity Hook

Question:

```text
Are the reported ANCOVA values structurally valid?
```

Checks:

```text
estimate is finite
standard error > 0
95% CI contains estimate
0 <= p value <= 1
residual df > 0
N equals sum of treatment counts
```

### 4. Final Response Safety Hook

Question:

```text
Does the final report avoid unsupported clinical or regulatory claims?
```

Examples to block:

```text
"clinically proven"
"safe and effective"
"regulatory ready"
"approved"
```

## Release Decisions

```text
PASS  = completed result is internally consistent and reportable for the demo
BLOCK = analysis was correctly blocked; report the QC failure, not ANCOVA results
FAIL  = do not release; fix contract, QC, or result inconsistencies
```

