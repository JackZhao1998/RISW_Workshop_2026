# Video storyboard and narration

**Format:** project explanation followed by a build request the learner can give to a coding agent. Use a neutral diagram, file cards, function names, and prompt cards. Show no provider interface, account controls, simulated assistant replies, or invented build logs.

**Opening card:** “Biomedical Agentic Pipeline — Project Breakdown + Build Prompts.” Secondary line: “A guided blueprint using supplied workshop inputs.”

Each chapter explains one component, shows the highlighted construction request, then identifies the artifacts to inspect after a learner builds it. Full copyable prompts accompany the video. The times below are the original editorial plan. For the produced video's actual timings, see [video_chapters.md](video_chapters.md); its full narration is in [video_narration.md](video_narration.md). These timings are not recorded agent-execution durations.

## 00:00–00:50 · 01. Define the project and its boundaries

**On screen:** Show the full flow, then highlight project setup and the supplied SAP/data folder.

**Narration:**

Start by telling the coding agent what the project should do and where its boundaries are. This first prompt asks for a project protocol and a build plan. The SAP and data already exist. We want the agent to preserve them and use the protocol to guide the later steps.

**Prompt card:** [Full learner construction prompt](prompts/01-project-protocol.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The plan follows the diagram; source files are unchanged; the protocol is ignored; no pipeline components have been built by this prompt yet.

## 00:50–01:45 · 02. Create the SAP extraction skill

**On screen:** Highlight SAP extraction. Show a skill card: when to use → procedure → output.

**Narration:**

A skill describes a repeatable procedure for the agent. Here, that procedure is reading the SAP and extracting what the analysis requires. The important output is a structured contract with source evidence. A successful extraction says that we identified the requirements; it does not say that the data meet them.

**Prompt card:** [Full learner construction prompt](prompts/02-sap-skill.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The skill separates extraction from readiness and defines how unknowns and source evidence are represented.

## 01:45–02:50 · 03. Build the extraction helper and contract

**On screen:** Animate SAP fields into a JSON contract. Label displayed JSON as an illustrative schema excerpt.

**Narration:**

The helper handles the predictable structure of this workshop SAP. It turns headings, lists, and the model formula into a contract that other tools can read. We also ask for validation, so a missing requirement cannot disappear silently. The coding agent still needs to review the meaning of the extraction.

**Prompt card:** [Full learner construction prompt](prompts/03-contract-helper.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The contract identifies Week 24, HBA1C, FASFL = Y, CHG = TRT01P + BASE, and ABC-201 minus Placebo; unsupported extraction cannot silently pass.

## 02:50–03:40 · 04. Add shared state and provenance helpers

**On screen:** Show contract → QC → result connected by a small run manifest.

**Narration:**

Shared state is the information passed between stages. File fingerprints help identify the input bytes used for a run, while the manifest records the stage decisions. This makes the workflow easier to inspect. A fingerprint identifies content; the gate still has to decide whether the associated evidence is valid.

**Prompt card:** [Full learner construction prompt](prompts/04-shared-state.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** A changed input produces a different fingerprint; source destinations are rejected; hashes are not described as signatures or proof of trust.

## 03:40–04:40 · 05. Create the source-data protection hook

**On screen:** Show proposed operation → hook → allowed read or blocked write. Use illustrative decision cards, not terminal recordings.

**Narration:**

This hook answers a different question from data readiness: is the proposed file operation allowed? The hook returns a decision before the controlled tool runs. Its protection depends on wiring it into that dispatch path. The construction prompt asks the coding agent to make that connection explicit.

**Prompt card:** [Full learner construction prompt](prompts/05-data-protection-hook.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The controlled dispatcher can reject a protected-source mutation before execution; declaring a policy in prose alone is insufficient.

## 04:40–05:30 · 06. Create the data readiness skill

**On screen:** Show the contract beside the two supplied efficacy filenames; highlight explicit selection.

**Narration:**

The readiness skill explains how the agent should check the data against the contract. It should not guess from a filename or silently choose another dataset. In this tutorial, the gate uses a conservative completeness policy. The prompt makes that choice explicit instead of attributing it to an unstated SAP rule.

**Prompt card:** [Full learner construction prompt](prompts/06-readiness-skill.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The skill requires an explicit dataset choice and explains failure without trying to repair the source files.

## 05:30–06:40 · 07. Build deterministic data QC

**On screen:** Show the checking-table columns and highlight the endpoint availability row.

**Narration:**

The QC helper performs the repeatable checks. Its output should explain each requirement, what was observed, and whether it passed. That table gives the agent evidence to discuss with the user. The summary gives the next component a decision it can enforce. We ask for both because they serve different audiences.

**Prompt card:** [Full learner construction prompt](prompts/07-qc-helper.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The Week 12 file has zero qualifying Week 24 records and ten missing FAS endpoints; a candidate pass file must earn its decision through checks.

## 06:40–07:45 · 08. Enforce the pre-analysis gate

**On screen:** Zoom in on the decision diamond. BLOCK goes directly to an issue record; ALLOW continues toward the model.

**Narration:**

The gate turns a readiness rule into executable control. The prompt asks the coding agent to check current evidence before calling the model and to prove the blocked path never invokes fitting. This is stronger than telling an agent in a skill document to remember to check QC.

**Prompt card:** [Full learner construction prompt](prompts/08-pre-analysis-gate.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** A blocked or fabricated ALLOW summary cannot trigger fitting through the supported entry point; the no-fit assertion is behavioral.

## 07:45–09:00 · 09. Build the ANCOVA helper functions

**On screen:** Show the model formula, reference treatment, selected records, and output field names. Display no invented estimates.

**Narration:**

The statistical helper does the calculation after the gate allows it. The prompt specifies the population, endpoint, contrast direction, and numerical checks. It also separates SAP requirements from workshop choices such as the confidence level. We show the output fields here, without pretending that illustrative numbers are observed results.

**Prompt card:** [Full learner construction prompt](prompts/09-ancova-helper.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** Treatment coding and contrast direction match the contract; numerical failure produces FAILED rather than a plausible-looking result.

## 09:00–09:50 · 10. Wrap ANCOVA as an agent-usable skill

**On screen:** Show skill guidance above a compact CLI argument card, connected to the existing helper.

**Narration:**

The skill explains how the agent should use the tool. The command-line wrapper gives it a concrete, inspectable interface. Keeping the model calculation in a helper lets the skill stay focused on procedure, while the gate remains enforced inside the actual execution path.

**Prompt card:** [Full learner construction prompt](prompts/10-ancova-skill.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** Calling the CLI directly cannot skip readiness enforcement; blocked output contains reasons and no model estimates.

## 09:50–11:00 · 11. Create the post-analysis review hook

**On screen:** Show six review checks converging on PASS, BLOCK, or FAIL.

**Narration:**

After fitting, the workflow still needs to verify what happened. This hook checks that the result agrees with the contract, QC evidence, and recorded inputs. It also distinguishes a correctly blocked analysis from an inconsistent result. Those outcomes need different reports, even though neither should display a successful treatment estimate.

**Prompt card:** [Full learner construction prompt](prompts/11-final-review-hook.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** A review decision means artifact consistency for this demo; it is not clinical validation. Inconsistent results cannot be released as success.

## 11:00–12:00 · 12. Build the final report writer

**On screen:** Show a report outline and the three report branches. Label the report writer as an addition to the reference project.

**Narration:**

The report writer turns the checked artifacts into an answer a reader can understand. This is an explicit addition to the reference demo. The construction prompt asks for separate completed, blocked, and diagnostic reports, and it requires the final text to match the version that was reviewed.

**Prompt card:** [Full learner construction prompt](prompts/12-report-helper.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The report's branch and numbers agree with the reviewed artifacts; unreviewed draft text is not labeled final.

## 12:00–13:15 · 13. Connect the components with the harness

**On screen:** Reassemble the complete flow. Highlight state records below the skill, tool, and hook layers.

**Narration:**

The harness joins the components into one controlled workflow. The agent uses the workflow skill to interpret the user's request and choose the inputs. The Python controller handles the sequence, decisions, and artifacts. A blocked path is part of the design, and the manifest should explain it as clearly as a completed analysis.

**Prompt card:** [Full learner construction prompt](prompts/13-harness.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** The harness coordinates real controls and artifacts; a normal process exit is not mistaken for a passing domain decision.

## 13:15–14:20 · 14. Ask for the two-branch walkthrough and checks

**On screen:** End with the two branches and a checklist of artifacts to inspect. Keep prompts visible as learner instructions.

**Narration:**

The final construction prompt asks for a reproducible walkthrough and meaningful checks. Learners should be able to see both branches, inspect the evidence, and verify that blocked analysis truly never fits a model. These are instructions they can give their own coding agent; this video presents the project and the build requests, rather than a recording of those requests being executed.

**Prompt card:** [Full learner construction prompt](prompts/14-walkthrough-checks.txt). Show selected sentences while explaining; provide the complete text with the video.

**Hold / annotation:** Learners can reproduce both branches, inspect the artifacts, and distinguish expected behavior from an observed test result.

## Closing card

“Choose a component. Give the construction prompt to your coding agent. Inspect its outputs and checks before moving on.”

Provide links to the prompt workbook and component breakdown. Do not label expected behavior as an observed test result.
