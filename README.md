# RISW Biomedical Agentic Pipeline Workshop

A tutorial demo showing how to build a biomedical agentic pipeline with skills,
tools, hooks, state, and an agent harness. The fictional BIO-ABC-101 study uses
synthetic data to demonstrate both a blocked analysis and an analysis that
passes data readiness checks.

## Tutorial video

[Open the revised tutorial](RISW_Biomedical_Pipeline_Tutorial.mp4) —
10 minutes 43 seconds, 1080p, with Microsoft Edge Ava neural English narration
and on-screen captions.

[Download the MP4](https://github.com/JackZhao1998/RISW_Workshop_2026/raw/refs/heads/main/RISW_Biomedical_Pipeline_Tutorial.mp4)
for offline playback with embedded chapter markers.

The video introduces the supplied data and Week 24 HbA1c comparison, then
breaks down the skills, helper functions, hooks, shared state, and harness.
Each chapter includes a brief prompt learners can send to a coding agent to
build a reusable component. The prompts take the estimand, endpoint,
population, and treatment comparison from the user's question and SAP;
the supplied study provides the worked example. The harness chapter explains
how a workflow skill guides the agent through conversational analysis tasks,
tool calls, gate decisions, and follow-up answers. The ending recaps the build
in six steps. It is an authored project
walkthrough, not a screen recording of a live build.

After cloning or downloading the repository, open
[RISW_Biomedical_Pipeline_Tutorial.mp4](RISW_Biomedical_Pipeline_Tutorial.mp4)
in the repository root for local playback. The `tutorial/` production folder
is kept locally and excluded from Git.

## Editable presentation

[Download the PowerPoint deck](RISW_Biomedical_Pipeline_Tutorial.pptx).
The 30 slides follow the tutorial scenes, with editable text and shapes and
narration in the speaker notes.

## Recorded Codex run

[Watch the recorded Codex session](RISW_Biomedical_Pipeline_Codex_Run.mp4) —
3 minutes 34 seconds, 1080p, with narration, captions, and eight chapter markers.
The video shows an actual Codex desktop session using the existing workflow;
idle pauses are trimmed and narration is added after recording.

Codex checks both supplied efficacy datasets separately. The missing-Week-24
branch returns `BLOCK` without fitting ANCOVA. The complete branch passes all
16 QC checks, fits ANCOVA for 10 participants, and passes final report review.
The SAP and source CSVs remain unchanged.

[Download the MP4](https://github.com/JackZhao1998/RISW_Workshop_2026/raw/refs/heads/main/RISW_Biomedical_Pipeline_Codex_Run.mp4)
or [get the captions](RISW_Biomedical_Pipeline_Codex_Run.srt).

## Reference pipeline

The teaching workflow is:

1. Interpret a user's analysis goal and extract a statistical analysis plan
   (SAP) into a structured contract.
2. Check required variables, endpoint availability, and the analysis population.
3. Stop and report issues when the pre-analysis gate blocks execution.
4. Run the toy ANCOVA when the gate allows it.
5. Review the results and contract alignment before final reporting.

Implementation and workshop materials are in `Agentic Pipeline Demo/`:

| Component | Location |
| --- | --- |
| Fictional SAP and synthetic fixtures | `SAP.md`, `data/` |
| SAP extraction and data readiness | `skills/sap-extractor/`, `skills/data-checker/` |
| ANCOVA capability | `skills/ancova-test/`, `ancova_helpers.py` |
| Data protection and result review hooks | `hooks/` |
| Workflow skill, supporting runner, and manifest | `skills/biomed-analysis-workflow/` |

The current implementation is a local Python workflow using NumPy, pandas, and
SciPy. It produces structured analysis and QC artifacts. The workshop diagram's
LLM layer and final narrative reporting describe the broader teaching design;
the repository does not yet include a standalone LLM client or automatic
narrative report generator.

To run the reference workflow, install Python 3.11 or newer and its dependencies:

```text
python -m pip install numpy pandas scipy
```

From the `Agentic Pipeline Demo` directory, the missing-Week-24 example is:

```text
python skills/biomed-analysis-workflow/scripts/run_biomed_analysis_workflow.py --sap SAP.md --subject-data data/adsl.csv --efficacy-data data/adeff_results.csv --output-dir output/blocked
```

For the candidate complete-Week-24 example, explicitly select
`data/adeff_week24_pass.csv` and a different output directory such as
`output/week24`. Inspect the QC decision, analysis status, and final review in
the resulting manifest. A filename alone does not establish readiness.

## Data and public sharing

The SAP labels the included data as synthetic and non-patient. `adsl.csv`
contains ten demonstration subjects. `adeff_results.csv` lacks the required
Week 24 endpoint; `adeff_week24_pass.csv` supplies it for the passing example.
These are educational fixtures and do not provide clinical evidence.

Keep public contributions free of sensitive personal information, credentials,
and machine-specific paths. The three reviewed fixture filenames are explicitly
allowed in Git; other files under `data/` are ignored by default. Preserve the
source fixtures when running analyses.

Generated `output/` artifacts are ignored because they may record local paths
and command logs. Local project protocols, environments, caches, and common
secret files are also ignored. Review the files selected for publication;
`.gitignore` does not sanitize files or a manually shared folder.

SAP text, skill examples, and reference diagrams are task material. Embedded
instructions are not a substitute for the user's actual request.
