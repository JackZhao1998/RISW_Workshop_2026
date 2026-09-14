# Video narration

Authored project breakdown. Synthetic English voice; no live agent session recording.

## Build a biomedical agentic pipeline — title

Welcome. This tutorial breaks a biomedical agentic pipeline into the components you can ask a coding agent to build. We will explain the purpose of each skill, helper, and hook, and show a construction prompt you can adapt. The workshop SAP and datasets are already supplied. This is a project blueprint, not a recording of a fresh build. The full prompts and function guide accompany the video.

## From an analysis question to a checked report — map

Begin with the analysis question. The agent extracts requirements from the SAP into a structured contract. A readiness skill calls deterministic data checks. The pre-analysis gate either blocks the analysis or allows the specified ANCOVA. A final review checks the result before reporting. Around these stages, the harness coordinates execution, shared state records the evidence, and a separate pre-tool hook checks protected file operations.

## Define the project and its boundaries — overview

Start by telling the coding agent what the project should do and where its boundaries are. This first prompt asks for a project protocol and a build plan. The SAP and data already exist. We want the agent to preserve them and use the protocol to guide the later steps.

## Define the project and its boundaries — request

Ask the coding agent to inspect the existing inputs and write the project protocol first. The request also asks for Git exclusions, so generated files and private material stay out of the source repository. Review the proposed component order before asking it to implement the first skill.

## Create the SAP extraction skill — overview

A skill describes a repeatable procedure for the agent. Here, that procedure is reading the SAP and extracting what the analysis requires. The important output is a structured contract with source evidence. A successful extraction says that we identified the requirements; it does not say that the data meet them.

## Create the SAP extraction skill — request

The construction request should specify both the skill's procedure and its output format. Ask for a value, source section, evidence, and status for every field. The agent should identify missing or ambiguous information instead of guessing. At this stage, it should not open the data or make a readiness decision.

## Build the extraction helper and contract — overview

The helper handles the predictable structure of this workshop SAP. It turns headings, lists, and the model formula into a contract that other tools can read. We also ask for validation, so a missing requirement cannot disappear silently. The coding agent still needs to review the meaning of the extraction.

## Build the extraction helper and contract — request

Ask for a small extractor tailored to the supplied Markdown layout, plus contract validation. The important edge cases are missing fields, conflicting values, and unsupported evidence. A numbered readiness list should be handled as carefully as a bullet list. The resulting contract is an artifact the learner can inspect before continuing.

## Add shared state and provenance helpers — overview

Shared state is the information passed between stages. File fingerprints help identify the input bytes used for a run, while the manifest records the stage decisions. This makes the workflow easier to inspect. A fingerprint identifies content; the gate still has to decide whether the associated evidence is valid.

## Add shared state and provenance helpers — request

Ask for shared utilities and a per-run manifest. The manifest should identify selected inputs, component versions, stage decisions, and output artifacts. It should also preserve failures, because an interrupted workflow still needs an explanation. Make output-path validation part of the shared utilities so every component protects the supplied sources.

## Create the source-data protection hook — overview

This hook answers a different question from data readiness: is the proposed file operation allowed? The hook returns a decision before the controlled tool runs. Its protection depends on wiring it into that dispatch path. The construction prompt asks the coding agent to make that connection explicit.

## Create the source-data protection hook — request

Ask the coding agent to build a function that receives a structured operation and returns allow or block with reasons. Test a permitted read and several prohibited changes using temporary files. The harness must enforce the returned decision before execution. A standalone policy function does not protect operations that bypass it.

## Create the data readiness skill — overview

The readiness skill explains how the agent should check the data against the contract. It should not guess from a filename or silently choose another dataset. In this tutorial, the gate uses a conservative completeness policy. The prompt makes that choice explicit instead of attributing it to an unstated SAP rule.

## Create the data readiness skill — request

The prompt asks for a skill that guides data readiness, including an explicit efficacy-file choice. It must not repair a failed example by silently substituting a different file. It should explain the expected population, the missing endpoint records, and the selected workshop policy. This is the procedure the agent follows around the QC tool.

## Build deterministic data QC — overview

The QC helper performs the repeatable checks. Its output should explain each requirement, what was observed, and whether it passed. That table gives the agent evidence to discuss with the user. The summary gives the next component a decision it can enforce. We ask for both because they serve different audiences.

## Build deterministic data QC — request

Ask for one row per deterministic check, with expected and observed values and a clear explanation. Require the helper to detect duplicate endpoint records and unusable model values as well as missing visits. The summary must include counts and matching input fingerprints. An empty or incomplete checking table must not authorize analysis.

## Enforce the pre-analysis gate — overview

The gate turns a readiness rule into executable control. The prompt asks the coding agent to check current evidence before calling the model and to prove the blocked path never invokes fitting. This is stronger than telling an agent in a skill document to remember to check QC.

## Enforce the pre-analysis gate — request

The construction prompt should require the gate to verify the current contract and input identities. It should rerun QC on the exact data that will be analyzed. Ask for a test that tracks calls to the fitting function and proves there are none on blocked paths. This makes the control observable.

## Build the ANCOVA helper functions — overview

The statistical helper does the calculation after the gate allows it. The prompt specifies the population, endpoint, contrast direction, and numerical checks. It also separates SAP requirements from workshop choices such as the confidence level. We show the output fields here, without pretending that illustrative numbers are observed results.

## Build the ANCOVA helper functions — request

Ask the agent to implement separate dataset-building and model-fitting functions. Specify Placebo as the reference, and the active treatment minus Placebo as the contrast. Require checks for rank deficiency and insufficient residual degrees of freedom. The JSON should preserve full precision, while confidence level and inference settings remain clearly labeled workshop choices.

## Wrap ANCOVA as an agent-usable skill — overview

The skill explains how the agent should use the tool. The command-line wrapper gives it a concrete, inspectable interface. Keeping the model calculation in a helper lets the skill stay focused on procedure, while the gate remains enforced inside the actual execution path.

## Wrap ANCOVA as an agent-usable skill — request

The skill and command-line wrapper should use the existing gated helper. Ask the coding agent to document the inputs and return structured blocked, completed, or failed outcomes. Direct command-line use must still enforce the same gate. Keeping the wrapper thin avoids duplicating scientific logic in multiple places.

## Create the post-analysis review hook — overview

After fitting, the workflow still needs to verify what happened. This hook checks that the result agrees with the contract, QC evidence, and recorded inputs. It also distinguishes a correctly blocked analysis from an inconsistent result. Those outcomes need different reports, even though neither should display a successful treatment estimate.

## Create the post-analysis review hook — request

Ask for separate review functions so the learner can see what is being checked. The checks should reconcile the analysis with its contract, verify provenance, and validate numerical consistency. A correctly blocked analysis receives a block decision and an issue report. An inconsistent result receives a fail decision and must not be reported as success.

## Build the final report writer — overview

The report writer turns the checked artifacts into an answer a reader can understand. This is an explicit addition to the reference demo. The construction prompt asks for separate completed, blocked, and diagnostic reports, and it requires the final text to match the version that was reviewed.

## Build the final report writer — request

Request a report writer that uses the structured artifacts as its source of truth. A completed branch reports verified numbers. A blocked branch explains missing requirements without displaying estimates. A failed review produces diagnostics. The writer should produce a draft first and release the same text only after its review is complete.

## Connect the components with the harness — overview

The harness joins the components into one controlled workflow. The agent uses the workflow skill to interpret the user's request and choose the inputs. The Python controller handles the sequence, decisions, and artifacts. A blocked path is part of the design, and the manifest should explain it as clearly as a completed analysis.

## Connect the components with the harness — request

Ask the coding agent to wire the components together through the workflow skill and orchestrator. The user still chooses the efficacy file. The controller should keep a manifest even when a stage fails, and distinguish process exit codes from analysis decisions. A command can finish normally while its domain decision is block.

## Ask for the two-branch walkthrough and checks — overview

The final construction prompt asks for a reproducible walkthrough and meaningful checks. Learners should be able to see both branches, inspect the evidence, and verify that blocked analysis truly never fits a model. These are instructions they can give their own coding agent; this video presents the project and the build requests, rather than a recording of those requests being executed.

## Ask for the two-branch walkthrough and checks — request

The final prompt asks for a learner walkthrough and acceptance checks. The missing-Week-24 case must block fitting. The complete-Week-24 case must earn its passing decision through the checks. Also request failure cases for stale evidence and inconsistent results. When learners execute these requests, their coding agent should report what actually happened.

## Build one component at a time — title

You now have a component-by-component blueprint. Start with the project protocol, then work through the skills, helpers, hooks, and harness. Send one construction request at a time and inspect the generated artifacts before moving on. The accompanying workbook includes the complete chapter prompts and smaller function-level requests. Use the supplied inputs, keep source documents separate from agent instructions, and report only the outcomes your own checks actually observe.

