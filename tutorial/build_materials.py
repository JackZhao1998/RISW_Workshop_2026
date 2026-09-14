"""Render authored tutorial material. Does not build or execute the pipeline."""
from pathlib import Path
import ast
import hashlib
import html
import json

BASE = Path(__file__).resolve().parent
data = json.loads((BASE / "tutorial.json").read_text(encoding="utf-8"))
chapters = data["chapters"]

def write(name, content):
    path = BASE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

def bullets(items):
    return "\n".join("- " + item for item in items)

guide = """# Build prompts for your coding agent

These are **construction prompts a learner can send to a coding agent**. They ask the agent to create the named skill, helper, hook, or workflow. They are authored teaching material, not a transcript of a real build and not prompts for generating a video.

Open a coding-agent task in your own project folder with the supplied `SAP.md` and `data/`. Send prompt 01 first, then send the later prompts in order after inspecting each result. The filenames refer to that project folder. If starting a new conversation halfway through, provide the project protocol and the artifacts from preceding steps. Do not ask the agent to regenerate the supplied inputs.

The prompts define a suggested rebuild. Requirements extending the reference demo are identified in the component notes. A coding agent may produce a different implementation with the same interfaces and verified behavior.

"""
for i, c in enumerate(chapters, 1):
    write("prompts/" + c["id"] + ".txt", c["prompt"])
    guide += f"## {i:02}. {c['title']}\n\n**Component:** {c['kind']}\n\n{c['purpose']}\n\n**Send this to your coding agent:**\n\n```text\n{c['prompt']}\n```\n\n**Expected deliverables:**\n\n{bullets(c['outputs'])}\n\n**Inspect after generation:** {c['verify']}\n\n"
write("build_prompts.md", guide)

breakdown = """# Biomedical pipeline: project breakdown

The workshop question is: **Is BIO-ABC-101 ready for its primary efficacy analysis? If readiness checks pass, run the specified ANCOVA.** The task is a fictional teaching example using the supplied SAP and CSVs.

## How the pieces fit

```mermaid
flowchart LR
    U[User goal] --> A[Agent / LLM]
    A --> S[SAP extraction skill]
    S --> C[Structured contract]
    C --> D[Data readiness skill]
    D --> Q[Deterministic QC helper]
    Q --> G{Pre-analysis hook}
    G -->|BLOCK| I[Issue report]
    G -->|ALLOW| M[ANCOVA tool]
    M --> R[Post-analysis review]
    R -->|PASS| F[Final report]
    R -->|FAIL| X[Diagnostic report]
```

The harness coordinates the flow. Shared state records the contract, selected inputs, QC evidence, decisions, results, and provenance. A separate pre-tool hook checks protected-file operations before the controlled workflow dispatches them. Reporting includes review of the draft text before release.

| Piece | What it contributes | Example |
| --- | --- | --- |
| User request | The objective and selected inputs | Check readiness, then analyze only if allowed |
| Agent / LLM | Uses the procedures and interprets source evidence | Reads the SAP through the extraction skill |
| Skill | A reusable procedure, input requirements, and output expectations | `skills/data-checker/SKILL.md` |
| Helper / tool | Deterministic computation | `check_sap_contract_against_data()` |
| Hook | An executable check at a controlled boundary | `require_qc_allow()` before fitting |
| State | Evidence carried between stages | Contract, QC table, result, manifest |
| Harness | Calls components in order and handles their decisions | Workflow script and workflow skill |

## Supplied analysis and the two branches

The supplied SAP names HBA1C change at Week 24, FAS subjects with `FASFL = Y`, the model `CHG = TRT01P + BASE`, and the contrast ABC-201 minus Placebo. Its no-imputation rule requires missing endpoint subjects to be counted. Confidence level and some inference settings are not specified; prompt 09 explicitly chooses and labels workshop settings.

The supplied `adsl.csv` has ten FAS subjects. `adeff_results.csv` contains Baseline and Week 12 observations, so it cannot supply the Week 24 endpoint. `adeff_week24_pass.csv` contains Baseline and Week 24 observations for those subjects. These are inspected input properties, not results of a newly executed pipeline. The second file remains a candidate pass case until all checks run.

The tutorial's build prompts require complete usable FAS endpoint coverage as a conservative workshop gate policy. This choice is explicit because the SAP also permits missing-record exclusion and counting. A learner should preserve both the source statement and the policy rather than silently conflate them.

## Existing reference and rebuild additions

The reference project was inspected read-only. The following distinctions keep the breakdown faithful while allowing the prompts to request a stronger, clearer rebuild.

| Topic | Existing reference | What the construction prompts request |
| --- | --- | --- |
| SAP extraction | A deterministic parser tailored to this Markdown excerpt; some values are matched specifically | Explicit supported format, numbered readiness items, ambiguity handling, evidence/schema validation |
| Shared utilities | Hashing, JSON loading, timestamps, and artifact descriptions are repeated across files | Optional consolidation in `state_helpers.py` and explicit per-run state |
| Protected sources | A Python decision hook checks classified operations against `data/`; the workflow invokes it for declared reads | Also protect SAP; reject unrecognized operations, enforce through the dispatcher, test path handling |
| Readiness | Required variables, population, treatments, visit, and endpoint coverage checks | Add explicit duplicate, numeric, and consistency checks with documented tolerances |
| Pre-analysis gate | `require_qc_allow()` primarily checks the summary decision string | Revalidate current inputs and QC; prove the fit function is never called on blocked paths |
| ANCOVA | NumPy OLS with SciPy t inference and a fixed 95% interval | Explicit workshop settings, stable solve, supported-model validation, full-precision state |
| Result review | Contract, gate, file hashes, numerical sanity, and optional report keyword checks | Stronger reconciliation, contextual claim review, exact draft-to-final correspondence |
| Reporting | Reviews an optional supplied narrative; no automatic narrative builder | A new `reporting_helpers.py` with completed, blocked, and diagnostic branches |
| Harness | Calls scripts and records artifact decisions; failures can stop before manifest creation | Reliable failure manifests, explicit semantic gates, report generation and release handling |

These are application-level controls. Merely adding a hook file does not install a provider's global lifecycle hook or create an operating-system sandbox. The inspected Python harness itself does not call a hosted LLM. The agent uses the workflow skill to invoke the deterministic tools.

## Component cards and construction order

"""
for i, c in enumerate(chapters, 1):
    helpers = ", ".join("`" + f + "`" for f in c["functions"]) or "No executable helper in this step."
    breakdown += f"## {i:02}. {c['title']}\n\n{c['purpose']}\n\n- **Role:** {c['kind']}\n- **Inputs:** {'; '.join(c['inputs'])}\n- **Outputs:** {'; '.join(c['outputs'])}\n- **Functions:** {helpers}\n- **Reference / scope:** {c['reference']}\n- **Learner prompt:** [Copy prompt {i:02}](prompts/{c['id']}.txt)\n\n**What to inspect:** {c['verify']}\n\n"
write("project_breakdown.md", breakdown)

storyboard = """# Video storyboard and narration

**Format:** project explanation followed by a build request the learner can give to a coding agent. Use a neutral diagram, file cards, function names, and prompt cards. Show no provider interface, account controls, simulated assistant replies, or invented build logs.

**Opening card:** “Biomedical Agentic Pipeline — Project Breakdown + Build Prompts.” Secondary line: “A guided blueprint using supplied workshop inputs.”

Each chapter explains one component, shows the highlighted construction request, then identifies the artifacts to inspect after a learner builds it. Full copyable prompts accompany the video. The times below are the original editorial plan. For the produced video's actual timings, see [video_chapters.md](video_chapters.md); its full narration is in [video_narration.md](video_narration.md). These timings are not recorded agent-execution durations.

"""
elapsed = 0
def stamp(seconds):
    return f"{seconds // 60:02}:{seconds % 60:02}"
for i, c in enumerate(chapters, 1):
    storyboard += f"## {stamp(elapsed)}–{stamp(elapsed+c['seconds'])} · {i:02}. {c['title']}\n\n**On screen:** {c['screen']}\n\n**Narration:**\n\n{c['narration']}\n\n**Prompt card:** [Full learner construction prompt](prompts/{c['id']}.txt). Show selected sentences while explaining; provide the complete text with the video.\n\n**Hold / annotation:** {c['verify']}\n\n"
    elapsed += c['seconds']
storyboard += "## Closing card\n\n“Choose a component. Give the construction prompt to your coding agent. Inspect its outputs and checks before moving on.”\n\nProvide links to the prompt workbook and component breakdown. Do not label expected behavior as an observed test result.\n"
write("video_storyboard.md", storyboard)

# Reuse the recorded read-only inventory so regeneration is portable after moving.
catalog = "# Reference function index\n\nThis inventory comes from read-only syntax inspection of the existing reference project. Names and signatures describe that source; the prompts may request additional validation or proposed functions. `main()` functions are CLI entry points. Detailed component roles are in [project_breakdown.md](project_breakdown.md).\n\n"
manifest = json.loads((BASE / "reference_inventory.json").read_text(encoding="utf-8"))
for rel, info in manifest["files"].items():
    catalog += "## " + rel + "\n\n"
    for function in info["functions"]:
        catalog += "- `" + function["signature"] + "` — line " + str(function["line"]) + ".\n"
    catalog += "\n"
write("reference_function_index.md", catalog)
write("private/reference-inspection.json", json.dumps(manifest, indent=2))

specs = json.loads((BASE / "function_prompt_specs.json").read_text(encoding="utf-8"))
function_sources = {}
for filename, info in manifest["files"].items():
    for function in info["functions"]:
        function_sources.setdefault(function["name"], []).append(filename)
assert set(function_sources) == set(specs), "Every named reference function needs a construction prompt."
function_guide = "# Function-by-function construction prompts\n\nUse these optional smaller requests when building or discussing one function at a time. The 14 chapter prompts remain the main learning sequence. Provide the preceding component context and agreed schema to the coding agent. Repeated utility names have one reusable prompt with their reference locations listed; each module's `main()` follows that module's interface. These prompts request a rebuild with the safeguards described, not a claim that the existing function already implements every requirement.\n\n"
for name, (purpose, specification) in specs.items():
    prompt = f"Please implement {name}() for the biomedical workshop pipeline. {specification} Keep this step focused on the named function and explain its input/output contract."
    filename = name.lstrip("_")
    if name.startswith("_"):
        filename = "internal-" + filename
    write("function_prompts/" + filename + ".txt", prompt)
    locations = "; ".join("`" + p + "`" for p in function_sources[name])
    function_guide += f"## `{name}()`\n\n**Purpose:** {purpose}\n\n**Reference locations:** {locations}\n\n**Send to your coding agent:**\n\n```text\n{prompt}\n```\n\n"
write("function_build_prompts.md", function_guide)

embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
page = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Biomedical pipeline · Build prompts</title>
<style>
:root{--ink:#172d40;--blue:#135d87;--teal:#167f7e;--muted:#576a78;--line:#d7e1e7;--paper:#fff;--bg:#eef3f5}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}header{padding:22px 4vw 18px;border-bottom:1px solid var(--line);background:#fff;display:flex;justify-content:space-between;gap:20px;align-items:center}.brand{font-weight:750;letter-spacing:.08em;font-size:13px;color:var(--blue)}.sub{font-size:14px;color:var(--muted)}.label{border:1px solid #bdd9d9;border-radius:24px;padding:7px 14px;color:var(--teal);font-size:13px;background:#f2fbfa}main{max-width:1500px;margin:auto;padding:24px 4vw 40px}.chapters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:26px}button{font:inherit;cursor:pointer;border:1px solid var(--line);background:white;color:var(--ink);border-radius:9px;padding:9px 14px}button:hover{border-color:var(--blue)}button:focus-visible{outline:3px solid #80bfdc;outline-offset:2px}.chapters button{font-size:13px;min-width:40px;padding:8px}.chapters button.active{background:var(--blue);color:white;border-color:var(--blue)}.eyebrow{color:var(--teal);font-size:13px;font-weight:700;letter-spacing:.09em;text-transform:uppercase}h1{font-size:clamp(27px,3vw,43px);line-height:1.15;margin:9px 0 24px;font-weight:720;letter-spacing:-.025em}.grid{display:grid;grid-template-columns:minmax(270px,.75fr) minmax(420px,1.25fr);gap:24px}.panel{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:25px}.purpose{font-size:20px;line-height:1.5;margin:0 0 22px}.smalltitle{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:20px 0 9px;font-weight:750}ul{padding-left:21px;margin:8px 0}li{margin:5px 0}.functions{display:flex;flex-wrap:wrap;gap:6px}.functions code{font-size:12px;padding:4px 7px;border-radius:5px;background:#edf5f8;overflow-wrap:anywhere}.prompthead{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:17px}.prompthead h2{font-size:16px;margin:0}.copy{font-size:13px;color:var(--blue);white-space:nowrap}pre{white-space:pre-wrap;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;overflow-wrap:anywhere}.check{border-left:3px solid var(--teal);padding:12px 16px;background:#f1f8f7;margin-top:24px;font-size:14px}.check strong{display:block;color:var(--teal);margin-bottom:4px}.controls{display:flex;justify-content:space-between;align-items:center;gap:16px;margin:22px 0}.controls span{font-size:13px;color:var(--muted)}button:disabled{opacity:.4;cursor:default}details{margin-top:14px;border:1px solid var(--line);border-radius:12px;background:white;padding:16px 20px}summary{cursor:pointer;font-weight:600;font-size:14px}details p{color:var(--muted);font-size:15px}.note{font-size:12px;color:var(--muted);margin-top:24px}a{color:var(--blue)}@media(max-width:850px){.grid{grid-template-columns:1fr}header{align-items:flex-start}.label{display:none}main{padding:20px}h1{font-size:30px}}@media print{header,.chapters,.controls,.copy{display:none}.grid{display:block}.panel{border:0;padding:10px}details{display:block}}
</style></head><body>
<header><div><div class="brand">RISW / BIOMEDICAL PIPELINE</div><div class="sub">Project breakdown &amp; build-from-scratch prompts</div></div><div class="label">Learner construction prompts</div></header>
<main><nav class="chapters" aria-label="Chapters" id="chapters"></nav><div class="eyebrow" id="kind"></div><h1 id="title"></h1>
<div class="grid"><section class="panel"><p class="purpose" id="purpose"></p><div class="smalltitle">Inputs</div><ul id="inputs"></ul><div class="smalltitle">What to build</div><ul id="outputs"></ul><div class="smalltitle">Functions in this component</div><div class="functions" id="functions"></div></section>
<section class="panel"><div class="prompthead"><h2>Send this to your coding agent</h2><button class="copy" id="copy">Copy prompt</button></div><pre id="prompt"></pre></section></div>
<div class="check"><strong>Inspect after generation</strong><span id="verify"></span></div>
<div class="controls"><button id="previous">← Previous</button><span id="position"></span><button id="next">Next →</button></div>
<details><summary>Narration and visual direction</summary><p id="narration"></p><p><strong>On screen: </strong><span id="screen"></span></p><p><strong>Reference / scope: </strong><span id="reference"></span></p></details>
<p class="note">Authored instructions for learners to build the components. No recorded agent replies or execution results. <a href="build_prompts.md">All prompts</a> · <a href="project_breakdown.md">Component guide</a> · <a href="video_storyboard.md">Video script</a></p></main>
<script id="tutorial-data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('tutorial-data').textContent);const rows=data.chapters;let current=0;
const element=id=>document.getElementById(id);
rows.forEach((c,i)=>{const b=document.createElement('button');b.textContent=String(i+1).padStart(2,'0');b.title=c.title;b.setAttribute('aria-label',`${i+1}. ${c.title}`);b.addEventListener('click',()=>render(i));element('chapters').appendChild(b)});
function list(id,items,tag){const parent=element(id);parent.replaceChildren();items.forEach(text=>{const item=document.createElement(tag);item.textContent=text;parent.appendChild(item)})}
function render(i){current=i;const c=rows[i];for(const id of ['title','kind','purpose','prompt','verify','narration','screen','reference'])element(id).textContent=c[id];list('inputs',c.inputs,'li');list('outputs',c.outputs,'li');list('functions',c.functions.length?c.functions:['Procedure / documentation'],'code');[...element('chapters').children].forEach((b,j)=>{b.classList.toggle('active',i===j);b.setAttribute('aria-current',i===j?'step':'false')});element('previous').disabled=i===0;element('next').disabled=i===rows.length-1;element('position').textContent=`${String(i+1).padStart(2,'0')} / ${rows.length} · ${c.kind}`;element('copy').textContent='Copy prompt';history.replaceState(null,'','#'+c.id)}
element('previous').addEventListener('click',()=>render(Math.max(0,current-1)));element('next').addEventListener('click',()=>render(Math.min(rows.length-1,current+1)));
element('copy').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(rows[current].prompt);element('copy').textContent='Copied'}catch{const range=document.createRange();range.selectNodeContents(element('prompt'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);element('copy').textContent='Selected — Ctrl+C'}});
document.addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;if(e.key==='ArrowRight'){e.preventDefault();render(Math.min(rows.length-1,current+1))}if(e.key==='ArrowLeft'){e.preventDefault();render(Math.max(0,current-1))}});
const start=rows.findIndex(c=>'#'+c.id===location.hash);render(start<0?0:start);
</script></body></html>'''
write("walkthrough.html", page.replace("__DATA__", embedded))
write("README.md", """# RISW tutorial: project breakdown and build prompts

Start with **[the tutorial video](RISW_Biomedical_Pipeline_Tutorial.mp4)** or **[the complete prompt workbook](build_prompts.md)**. An [offline chapter viewer](walkthrough.html) is also included.

This package explains the project and supplies prompts a learner can send to a coding agent to **build each function, skill, hook, and workflow component**. These are construction instructions, not video-generation prompts, simulated assistant responses, or a recording of a fresh build.

| File | Purpose |
| --- | --- |
| [RISW_Biomedical_Pipeline_Tutorial.mp4](RISW_Biomedical_Pipeline_Tutorial.mp4) | Narrated 1080p tutorial with visible captions and chapter markers; actual runtime is recorded in video_manifest.json |
| [RISW_Biomedical_Pipeline_Tutorial.srt](RISW_Biomedical_Pipeline_Tutorial.srt) | Separate synchronized subtitles; WebVTT is also included |
| [video_chapters.md](video_chapters.md) | Actual chapter timestamps for the produced video |
| [video_narration.md](video_narration.md) | The complete spoken script |
| [walkthrough.html](walkthrough.html) | Offline chapter viewer with copyable prompts, component cards, and narration |
| [build_prompts.md](build_prompts.md) | All 14 learner construction prompts, expected outputs, and inspection criteria |
| [prompts/](prompts/) | One plain-text prompt per step |
| [project_breakdown.md](project_breakdown.md) | Architecture, component responsibilities, and existing-versus-proposed distinctions |
| [reference_function_index.md](reference_function_index.md) | Function signatures and source locations from read-only inspection |
| [function_build_prompts.md](function_build_prompts.md) | Optional individual construction prompts for all 55 named reference functions |
| [function_prompts/](function_prompts/) | One plain-text construction prompt per named function |
| [video_storyboard.md](video_storyboard.md) | Narration and visual directions; an approximately 14-minute editorial plan |
| [tutorial.json](tutorial.json) | Editable source for chapter text, prompts, and narration |
| [build_materials.py](build_materials.py) | Regenerates the document and HTML package; does not execute the pipeline |

Learners supply their own copy of the workshop SAP/data in their build workspace. No new data or pipeline components were created for this breakdown. The video uses provider-neutral rendered cards and Microsoft Edge's Ava neural English narration. It contains no screen recordings or fabricated coding-agent responses. Production scripts, caption sources, prompts, and the rendered video are kept in this folder.

This repository includes the curated learner materials and final media. Local session records, render intermediates, dependencies, and previous video versions are excluded. The authored prompts do not imply that a coding agent executed them during the video.
""")
print(json.dumps({"chapters": len(chapters), "planned_duration": stamp(elapsed), "prompt_files": len(list((BASE / 'prompts').glob('*.txt'))), "reference_modules": len(manifest['files'])}))
