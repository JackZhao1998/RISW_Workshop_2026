"""Create the tutorial video from authored material and synthesized speech.

No screen capture, coding-agent invocation, or biomedical pipeline execution.
Run: python produce_video.py prepare | assemble | assemble-edge | encode | finish
"""
from __future__ import annotations
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, math, re, subprocess, sys, wave
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
PRIVATE = BASE / "private" / "video-production"
PRIVATE.mkdir(parents=True, exist_ok=True)
ASSETS = PRIVATE / "frames"
AUDIO = PRIVATE / "speech"
CLIPS = PRIVATE / "clips"
for folder in (ASSETS, AUDIO, CLIPS): folder.mkdir(exist_ok=True)
sys.path.insert(0, str(BASE / "private" / "runtime"))
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS = 1920,1080,30
BG = "#F0F5F7"; INK = "#183047"; MUTED = "#536F80"; BLUE = "#165E89"; TEAL = "#137F7B"; LINE = "#D9E4EB"
FONT = Path(r"C:\Windows\Fonts")
def font(size, bold=False, mono=False):
    return ImageFont.truetype(str(FONT / ("consola.ttf" if mono else "segoeuib.ttf" if bold else "segoeui.ttf")),size)

def wrapped(draw, text, f, width):
    lines=[]
    for paragraph in text.split("\n"):
        if not paragraph: lines.append(""); continue
        line=""
        for word in paragraph.split():
            trial=(line+" "+word).strip()
            if draw.textlength(trial,font=f)>width and line: lines.append(line);line=word
            else: line=trial
        if line: lines.append(line)
    return lines

def txt(draw,text,x,y,width,size=30,bold=False,color=INK,gap=1.35,max_bottom=920,mono=False):
    f=font(size,bold,mono); lines=wrapped(draw,text,f,width)
    bottom=y+len(lines)*size*gap
    if bottom>max_bottom: raise ValueError(f"Text overflow: {text[:80]} ({bottom})")
    for line in lines:
        draw.text((x,y),line,font=f,fill=color); y+=size*gap
    return y

def card(draw,box,fill="white"):
    draw.rounded_rectangle(box,radius=22,fill=fill,outline=LINE,width=2)

def base_frame(scene):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,87),fill="white")
    d.text((80,27),"RISW  /  BIOMEDICAL AGENTIC PIPELINE",font=font(24,True),fill=BLUE)
    d.text((1350,29),"PROJECT BREAKDOWN + BUILD PROMPTS",font=font(20),fill=MUTED)
    d.text((82,111),scene["kind"].upper(),font=font(23,True),fill=TEAL)
    size=51
    while len(wrapped(d,scene["title"],font(size,True),1650))>2: size-=1
    txt(d,scene["title"],80,151,1650,size,True,gap=1.15,max_bottom=278)
    if scene.get("chapter"):
        d.rounded_rectangle((1760,124,1840,198),radius=14,fill=BLUE)
        d.text((1779,138),f"{scene['chapter']:02}",font=font(35,True),fill="white")
    d.line((80,891,1840,891),fill=LINE,width=2)
    d.text((82,906),scene.get("footer","Authored construction prompts • Full text accompanies the video"),font=font(22),fill=MUTED)
    return im,d

def bullets(d,items,x,y,width,size=30):
    for value in items:
        d.ellipse((x,y+13,x+8,y+21),fill=TEAL)
        y=txt(d,value,x+25,y,width-25,size,max_bottom=860)+14
    return y

def overview(scene):
    im,d=base_frame(scene)
    card(d,(80,287,900,851)); card(d,(930,287,1840,851))
    y=txt(d,scene["purpose"],116,320,740,36,True,max_bottom=475)
    d.text((116,y+25),"INPUTS",font=font(21,True),fill=TEAL)
    bullets(d,scene["inputs"],116,y+65,735,29)
    d.text((968,320),"WHAT TO BUILD",font=font(21,True),fill=TEAL)
    y=bullets(d,scene["outputs"],968,366,827,29)
    functions=scene["functions"]
    priority={3:["extract_contract","split_sections","field","validate_contract (proposed)","evidence"],7:["check_sap_contract_against_data","make_summary","_row","_parse_equality_filter"],11:["run_final_result_review_hook","check_qc_gate_consistency","check_contract_alignment","check_provenance","check_statistical_result"]}
    functions=priority.get(scene.get("chapter"),functions)
    if functions:
        d.text((968,y+10),"FUNCTIONS / INTERFACES",font=font(21,True),fill=TEAL)
        shown="\n".join(functions[:5])
        if len(functions)>5: shown+="\n+ additional checks in the function guide"
        txt(d,shown,968,y+52,820,24,mono=True,gap=1.3,max_bottom=843)
    return im

def request_frame(scene):
    im,d=base_frame(scene)
    card(d,(80,282,1840,554))
    d.text((118,307),"SEND THIS TO YOUR CODING AGENT  ·  VERBATIM EXCERPT",font=font(21,True),fill=BLUE)
    size=32
    while len(wrapped(d,scene["excerpt"],font(size),1680))*size*1.32>175: size-=1
    txt(d,scene["excerpt"],118,357,1680,size,gap=1.32,max_bottom=547)
    card(d,(80,579,1050,851));card(d,(1080,579,1840,851),"#E6F3F1")
    d.text((116,606),"ALSO REQUIRE",font=font(21,True),fill=TEAL)
    bullets(d,scene["requirements"],116,648,880,28)
    d.text((1116,606),"INSPECT AFTER GENERATION",font=font(21,True),fill=TEAL)
    txt(d,scene["verify"],1116,651,680,28,max_bottom=843)
    return im

def title_frame(scene):
    im,d=base_frame(scene)
    card(d,(80,290,1840,850))
    txt(d,scene["headline"],125,330,1630,58,True,max_bottom=540)
    txt(d,scene["body"],125,530,1560,35,max_bottom=735)
    d.rounded_rectangle((125,768,1150,817),radius=12,fill="#E6F3F1")
    d.text((145,776),scene["tag"],font=font(25,True),fill=TEAL)
    return im

def map_frame(scene):
    im,d=base_frame(scene)
    labels=[("Agent + SAP skill","Interpret the plan"),("Analysis contract","Make requirements explicit"),("Readiness + QC","Check the selected data"),("Pre-analysis gate","Enforce ALLOW or BLOCK")]
    for i,(title,sub) in enumerate(labels):
        x=80+i*446;card(d,(x,306,x+420,441))
        txt(d,title,x+24,331,370,29,True,max_bottom=430)
        txt(d,sub,x+24,380,370,24,color=MUTED,max_bottom=438)
        if i<3:
            d.line((x+421,371,x+443,371),fill=TEAL,width=4)
    d.line((1630,444,1630,517),fill=TEAL,width=4)
    card(d,(1300,520,1840,650),"#E6F3F1")
    txt(d,"ALLOW → ANCOVA",1330,541,480,34,True)
    txt(d,"Fit the authorized model",1330,595,480,26)
    d.line((1300,582,1060,582),fill=TEAL,width=4)
    card(d,(550,520,1060,650))
    txt(d,"Post-analysis review",580,541,450,32,True)
    txt(d,"Check before reporting",580,595,450,26)
    card(d,(80,520,510,650))
    txt(d,"Final report",110,541,370,34,True)
    txt(d,"Release checked findings",110,595,370,26)
    d.line((550,582,510,582),fill=TEAL,width=4)
    d.line((1840,396,1870,396,1870,750,1840,750),fill="#BD683F",width=4)
    d.polygon([(1840,750),(1854,742),(1854,758)],fill="#BD683F")
    d.text((1682,662),"BLOCK",font=font(22,True),fill="#A9532C")
    d.polygon([(1630,519),(1622,505),(1638,505)],fill=TEAL)
    d.polygon([(1061,582),(1075,574),(1075,590)],fill=TEAL)
    d.polygon([(511,582),(525,574),(525,590)],fill=TEAL)
    card(d,(80,701,1840,842))
    txt(d,"BLOCK → stop fitting and explain the issues",114,718,1640,31,True,color="#A9532C")
    txt(d,"Harness = coordination   •   State = evidence   •   Pre-tool hook = protected operations",114,772,1630,29)
    return im

def split_sentences(text):
    # Narration uses prose rather than code paths, so sentence boundaries are explicit.
    return [v.strip() for v in re.split(r"(?<=[.!?])\s+",text) if v.strip()]

def spoken(text):
    for a,b in [("RISW","R I S W"),("SAP","S A P"),("CSV","C S V"),("QC","Q C"),("JSON","J son"),("CLI","C L I"),("LLM","L L M"),("ANCOVA","an co va"),("OLS","O L S"),("FAS","F A S"),("API","A P I")]:
        text=re.sub(r"\b"+a+r"\b",b,text)
    return text.replace("Week-24","Week twenty four").replace("Week 24","Week twenty four").replace("Week 12","Week twelve")

def prepare():
    data=json.loads((BASE/"tutorial.json").read_text(encoding="utf-8"));notes=json.loads((BASE/"video_notes.json").read_text(encoding="utf-8"))
    scenes=[dict(id="00-introduction",type="title",kind="RISW workshop tutorial",title="Build a biomedical agentic pipeline",headline="Understand each component.\nAsk a coding agent to build it.",body="Skills • Helper functions • Hooks • Shared state • Harness\nA step-by-step blueprint using supplied workshop inputs.",tag="Project explanation + learner construction prompts",narration="Welcome. This tutorial breaks a biomedical agentic pipeline into the components you can ask a coding agent to build. We will explain the purpose of each skill, helper, and hook, and show a construction prompt you can adapt. The workshop SAP and datasets are already supplied. This is a project blueprint, not a recording of a fresh build. The full prompts and function guide accompany the video.")]
    scenes.append(dict(id="00-flow",type="map",kind="The complete workflow",title="From an analysis question to a checked report",narration="Begin with the analysis question. The agent extracts requirements from the SAP into a structured contract. A readiness skill calls deterministic data checks. The pre-analysis gate either blocks the analysis or allows the specified ANCOVA. A final review checks the result before reporting. Around these stages, the harness coordinates execution, shared state records the evidence, and a separate pre-tool hook checks protected file operations."))
    for i,(c,note) in enumerate(zip(data["chapters"],notes),1):
        common=dict(chapter=i,kind=c["kind"],title=c["title"])
        scenes.append(dict(**common,id=c["id"]+"-component",type="overview",purpose=c["purpose"],inputs=c["inputs"],outputs=c["outputs"],functions=c["functions"],narration=c["narration"],footer=f"Chapter {i:02} / 14  •  Component responsibilities"))
        scenes.append(dict(**common,id=c["id"]+"-prompt",type="request",excerpt=c["prompt"].split("\n\n")[0],requirements=note["requirements"],verify=c["verify"],narration=note["speech"],footer="Full construction prompt: prompts/"+c["id"]+".txt"))
    scenes.append(dict(id="15-closing",type="title",kind="Your next step",title="Build one component at a time",headline="Choose a component.\nSend its prompt. Inspect the result.",body="14 chapter prompts • Individual function prompts\nComponent guide • Narration script • Captions",tag="Provider-neutral visuals • Synthetic English narration",narration="You now have a component-by-component blueprint. Start with the project protocol, then work through the skills, helpers, hooks, and harness. Send one construction request at a time and inspect the generated artifacts before moving on. The accompanying workbook includes the complete chapter prompts and smaller function-level requests. Use the supplied inputs, keep source documents separate from agent instructions, and report only the outcomes your own checks actually observe."))
    utterances=[]
    for i,s in enumerate(scenes):
        s["number"]=i
        s["frame"]=str((ASSETS/(s["id"]+".png")).relative_to(BASE))
        frame={"title":title_frame,"map":map_frame,"overview":overview,"request":request_frame}[s["type"]](s)
        frame.save(BASE/s["frame"])
        s["utterances"]=[]
        for j,sentence in enumerate(split_sentences(s["narration"])):
            key=f"{i:02}-{j:02}"; s["utterances"].append(key)
            utterances.append(dict(id=key,text=sentence,speech=spoken(sentence),file=str((AUDIO/(key+".wav")).relative_to(BASE))))
    (PRIVATE/"scenes.json").write_text(json.dumps(scenes,indent=2),encoding="utf-8")
    (PRIVATE/"utterances.json").write_text(json.dumps(utterances,indent=2),encoding="utf-8")
    script="# Video narration\n\nAuthored project breakdown. Synthetic English voice; no live agent session recording.\n\n"
    for s in scenes: script+="## "+s["title"]+" — "+s["type"]+"\n\n"+s["narration"]+"\n\n"
    (BASE/"video_narration.md").write_text(script,encoding="utf-8")
    print(json.dumps({"scenes":len(scenes),"utterances":len(utterances),"words":sum(len(s["narration"].split()) for s in scenes)}),flush=True)

def timecode(seconds,ass=False):
    unit=100 if ass else 1000;n=round(seconds*unit);h,n=divmod(n,3600*unit);m,n=divmod(n,60*unit);s,n=divmod(n,unit)
    return f"{h}:{m:02}:{s:02}.{n:02}" if ass else f"{h:02}:{m:02}:{s:02},{n:03}"

def assemble():
    scenes=json.loads((PRIVATE/"scenes.json").read_text()); utterances={u["id"]:u for u in json.loads((PRIVATE/"utterances.json").read_text())}
    cues=[];timeline=0.;params=None
    for s in scenes:
        frames=[];position=.35
        for key in s["utterances"]:
            u=utterances[key]
            with wave.open(str(BASE/u["file"]),'rb') as f:
                if params is None: params=(f.getnchannels(),f.getsampwidth(),f.getframerate())
                assert params==(f.getnchannels(),f.getsampwidth(),f.getframerate())
                pcm=f.readframes(f.getnframes());duration=f.getnframes()/f.getframerate()
            frames.append(pcm);cues.append(dict(start=timeline+position,end=timeline+position+duration,text=u["text"]))
            position+=duration+.10
        rate=params[2];samplebytes=params[0]*params[1]
        def silence(seconds): return b'\x00'*(round(seconds*rate)*samplebytes)
        audio=silence(.35)+silence(.10).join(frames)+silence(.65)
        duration=len(audio)/samplebytes/rate
        duration=math.ceil(duration*FPS)/FPS
        audio+=silence(duration-len(audio)/samplebytes/rate)
        s["start"]=timeline;s["duration"]=duration;s["audio"]=str((AUDIO/(s["id"]+".wav")).relative_to(BASE))
        with wave.open(str(BASE/s["audio"]),'wb') as f:f.setnchannels(params[0]);f.setsampwidth(params[1]);f.setframerate(rate);f.writeframes(audio)
        timeline+=duration
    with wave.open(str(PRIVATE/"narration.wav"),'wb') as f:
        f.setnchannels(params[0]);f.setsampwidth(params[1]);f.setframerate(params[2])
        for s in scenes:
            with wave.open(str(BASE/s["audio"]),'rb') as part:f.writeframes(part.readframes(part.getnframes()))
    write_timeline(scenes,cues,timeline)

def assemble_edge():
    scenes=json.loads((PRIVATE/"scenes.json").read_text());edge=PRIVATE/'edge'
    cues=[];timeline=0.;all_audio=[]
    for s in scenes:
        metadata=json.loads((edge/(s['id']+'.json')).read_text())
        with wave.open(str(edge/(s['id']+'.wav')),'rb') as f:
            assert (f.getnchannels(),f.getsampwidth(),f.getframerate())==(1,2,24000)
            pcm=f.readframes(f.getnframes());original_duration=f.getnframes()/24000
        for cue in metadata['cues']:
            assert 0<=cue['start']<cue['end']<=original_duration+.15
            cues.append(dict(start=timeline+.30+cue['start'],end=timeline+.30+min(cue['end'],original_duration),text=cue['text']))
        audio=b'\x00'*round(.30*24000)*2+pcm+b'\x00'*round(.60*24000)*2
        duration=math.ceil(len(audio)/48000*FPS)/FPS
        audio+=b'\x00'*round((duration-len(audio)/48000)*24000)*2
        s['start']=timeline;s['duration']=duration;s['audio']=str((AUDIO/(s['id']+'.wav')).relative_to(BASE))
        with wave.open(str(BASE/s['audio']),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(audio)
        all_audio.append(audio);timeline+=duration
    with wave.open(str(PRIVATE/'narration.wav'),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000)
        for pcm in all_audio:f.writeframes(pcm)
    write_timeline(scenes,cues,timeline)

def write_timeline(scenes,cues,timeline):
    srt="";vtt="WEBVTT\n\n"
    ass="[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Segoe UI,32,&H00FFFFFF,&H00FFFFFF,&H20473018,&H20473018,0,0,0,0,100,100,0,0,3,9,0,2,100,100,32,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    for i,c in enumerate(cues,1):
        start,end=timecode(c["start"]),timecode(c["end"])
        srt+=f"{i}\n{start} --> {end}\n{c['text']}\n\n";vtt+=f"{start.replace(',','.')} --> {end.replace(',','.')}\n{c['text']}\n\n"
        ass+=f"Dialogue: 0,{timecode(c['start'],True)},{timecode(c['end'],True)},Default,,0,0,0,,{c['text']}\n"
    (BASE/"RISW_Biomedical_Pipeline_Tutorial.srt").write_text(srt,encoding="utf-8")
    (BASE/"RISW_Biomedical_Pipeline_Tutorial.vtt").write_text(vtt,encoding="utf-8")
    (PRIVATE/"captions.ass").write_text(ass,encoding="utf-8")
    metadata=";FFMETADATA1\ntitle=Biomedical Agentic Pipeline - Project Breakdown and Build Prompts\ncomment=Authored tutorial with synthetic narration. No live build recording.\n"
    chapter_scenes=[s for s in scenes if s["type"]!="request"]
    for i,s in enumerate(chapter_scenes):
        end=chapter_scenes[i+1]["start"] if i+1<len(chapter_scenes) else timeline
        metadata+=f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(s['start']*1000)}\nEND={round(end*1000)}\ntitle={s['title']}\n"
    (PRIVATE/"chapters.ffmeta").write_text(metadata,encoding="utf-8")
    (PRIVATE/"timeline.json").write_text(json.dumps(dict(scenes=scenes,cues=cues,duration=timeline),indent=2),encoding="utf-8")
    chapters_md="# Video chapters\n\n"
    for s in chapter_scenes:chapters_md+=f"- {timecode(s['start']).split(',')[0]} — {s['title']}\n"
    (BASE/"video_chapters.md").write_text(chapters_md,encoding="utf-8")
    print(json.dumps({"duration_seconds":timeline,"duration":timecode(timeline),"captions":len(cues)}),flush=True)

def encode():
    scenes=json.loads((PRIVATE/"timeline.json").read_text())["scenes"]
    def one(s):
        path=CLIPS/(s["id"]+".mp4")
        args=[FFMPEG,"-y","-hide_banner","-loglevel","error","-loop","1","-framerate",str(FPS),"-i",str(BASE/s["frame"]),"-t",str(s["duration"]),"-vf",f"fade=t=in:st=0:d=0.22,fade=t=out:st={s['duration']-.20}:d=0.20,format=yuv420p","-c:v","libx264","-preset","veryfast","-tune","stillimage","-crf","19","-threads","3","-an",str(path)]
        subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=(PRIVATE/(s["id"]+"-encode.log")).open('w'),creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        print("Encoded "+s["id"],flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,scenes))
    (CLIPS/"concat.txt").write_text("".join("file '"+s["id"]+".mp4'\n" for s in scenes),encoding="utf-8")

def finish():
    output=BASE/"RISW_Biomedical_Pipeline_Tutorial.mp4"
    staging=PRIVATE/"tutorial-rendering.mp4"
    args=[FFMPEG,"-y","-hide_banner","-loglevel","warning","-f","concat","-safe","0","-i","private/video-production/clips/concat.txt","-i","private/video-production/narration.wav","-i","private/video-production/chapters.ffmeta","-map","0:v:0","-map","1:a:0","-map_metadata","2","-map_chapters","2","-vf","ass=private/video-production/captions.ass","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-preset","veryfast","-crf","19","-threads","4","-c:a","aac","-b:a","192k","-ar","48000","-pix_fmt","yuv420p","-movflags","+faststart","-metadata","artist=RISW Workshop","-metadata","description=Provider-neutral project breakdown and learner construction prompts; synthetic narration.",str(staging)]
    with (PRIVATE/"final-encode.log").open('w') as log:
        subprocess.run(args,cwd=BASE,check=True,stdout=log,stderr=log,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    staging.replace(output)
    print("Created "+str(output),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument('step',choices=['prepare','assemble','assemble-edge','encode','finish']);args=parser.parse_args()
    globals()[args.step.replace('-','_')]()

