# Pre-Tool Data Security Hook Examples

## Purpose

Protect the source data folder from accidental or agent-initiated mutation before any tool runs.

Protected folder, relative to the demo directory:

```text
data/
```

## Policy

```text
ALLOW read-only inspection of source data.
BLOCK overwrite, deletion, move, rename, append, truncate, patch, or create operations in the data folder.
BLOCK unknown operations targeting the data folder unless explicitly classified as read-only.
```

## Example: Allowed Read

```text
python hooks/pre_tool_data_security_hook.py \
  --tool-name pandas.read_csv \
  --operation read \
  --path data/adsl.csv
```

Decision:

```text
ALLOW
```

## Example: Blocked Overwrite

```text
python hooks/pre_tool_data_security_hook.py \
  --tool-name write_file \
  --operation overwrite \
  --path data/adsl.csv
```

Decision:

```text
BLOCK
```

## Example: Blocked Deletion

```text
python hooks/pre_tool_data_security_hook.py \
  --tool-name shell_command \
  --operation delete \
  --path data/adeff_results.csv
```

Decision:

```text
BLOCK
```

## Agentic Workflow Placement

```text
User/tool intent
  ↓
pre_tool_data_security_hook
  ↓
ALLOW → run read-only data inspection or analysis tool
BLOCK → stop and report protected-data mutation attempt
```
