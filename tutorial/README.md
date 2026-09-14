# RISW tutorial: project breakdown and build prompts

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
