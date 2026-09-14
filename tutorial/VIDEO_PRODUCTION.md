# Video production

The tutorial is a provider-neutral project breakdown with construction prompts learners can send to a coding agent. Visuals are rendered from the authored chapter data. Narration uses Microsoft Edge's online Ava neural English voice (`en-US-AvaMultilingualNeural`) at a slightly relaxed rate of -3%. It does not imitate a person. There is no screen capture or pipeline execution.

The video includes an introduction, workflow map, two scenes for each of 14 chapters, and a closing scene. Prompt cards show a labeled verbatim excerpt, a concise summary of further requirements, and an inspection criterion. The accompanying prompt files contain the full instructions. Each scene is synthesized as a continuous paragraph. Sentence-level subtitle timing comes from the service's returned boundaries. Spoken expansions of abbreviations such as SAP and QC preserve their meaning; captions retain the written acronyms.

## Editable inputs

- `tutorial.json`: component descriptions and complete chapter prompts.
- `video_notes.json`: visual requirement summaries and additional spoken explanation.
- `produce_video.py`: scene rendering, timing, subtitles, encoding, and chapter metadata.
- `synthesize_edge.py`: current online Edge neural narration and timing metadata.
- `synthesize_narration.ps1`: retained original desktop-voice generation script; not used for the current video.
- `video_narration.md`: complete script actually used in the produced video.

## Reproduction

Use Windows with Python and Pillow for the current scene renderer. If recreating dependencies, install `imageio-ffmpeg==0.6.0` into `private/runtime` and `edge-tts==7.2.8` into `private/edge-runtime`. The speech script sends only authored tutorial narration to the online service. It uses the [edge-tts project](https://github.com/rany2/edge-tts) and its streaming sentence-boundary interface.

```powershell
python produce_video.py prepare
python synthesize_edge.py
python produce_video.py assemble-edge
python produce_video.py encode
python produce_video.py finish
```

Generated scene audio and service timing metadata are written to `private/video-production/edge/`. Images, intermediate clips, and logs are written under `private/video-production/`. These generated directories are ignored by Git. The final MP4, narration audio, subtitles, chapter list, and learner materials live at the tutorial root. The original editorial storyboard remains available; `video_chapters.md` gives the final video's actual timing.

The repository video uses only the authored chapter material. Raw session records and previous production versions are not included.
