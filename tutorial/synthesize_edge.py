"""Render continuous scene narration with Microsoft Edge's online neural voice.

Only the authored, public tutorial narration is sent to the speech service.
Uses edge-tts; saves service-provided sentence boundaries for caption timing.
"""
from pathlib import Path
import argparse,asyncio,hashlib,html,json,re,subprocess,sys,wave

BASE=Path(__file__).resolve().parent
PRIVATE=BASE/'private/video-production'
EDGE=PRIVATE/'edge'
EDGE.mkdir(exist_ok=True)
sys.path.insert(0,str(BASE/'private/edge-runtime'))
sys.path.insert(0,str(BASE/'private/runtime'))
import edge_tts,imageio_ffmpeg

VOICE='en-US-AvaMultilingualNeural'
RATE='-3%'

def speech_text(text):
    replacements={'RISW':'R I S W','SAP':'statistical analysis plan','QC':'quality control',
        'ANCOVA':'analysis of covariance','FAS':'full analysis set','CLI':'command line',
        'CSV':'C S V','OLS':'ordinary least squares','LLM':'language model'}
    for source,target in replacements.items():
        text=re.sub(r'\b'+source+r'\b',target,text)
    return text

def normalized(text):
    return re.sub(r'[^a-z0-9]','',html.unescape(text).lower())

async def synthesize(scene,semaphore):
    text=speech_text(scene['narration'])
    audio_path=EDGE/(scene['id']+'.mp3');metadata_path=EDGE/(scene['id']+'.json')
    fingerprint=hashlib.sha256((VOICE+'|'+RATE+'|'+text).encode()).hexdigest()
    if audio_path.exists() and metadata_path.exists():
        prior=json.loads(metadata_path.read_text())
        if prior.get('fingerprint')==fingerprint:
            print('Cached '+scene['id'],flush=True);return
    async with semaphore:
        for attempt in range(3):
            try:
                chunks=[];audio=bytearray()
                communicate=edge_tts.Communicate(text,VOICE,rate=RATE,boundary='SentenceBoundary',connect_timeout=10,receive_timeout=30)
                async for chunk in communicate.stream():
                    if chunk['type']=='audio':audio.extend(chunk['data'])
                    elif chunk['type']=='SentenceBoundary':chunks.append(chunk)
                original=re.split(r'(?<=[.!?])\s+',scene['narration'].strip())
                if len(original)!=len(chunks):raise ValueError(f"Sentence count differs: {len(original)} / {len(chunks)}")
                cues=[]
                for sentence,boundary in zip(original,chunks):
                    if normalized(speech_text(sentence))!=normalized(boundary['text']):
                        raise ValueError('Sentence text does not align with speech metadata.')
                    cues.append(dict(start=boundary['offset']/10_000_000,end=(boundary['offset']+boundary['duration'])/10_000_000,text=sentence))
                if not audio or not cues:raise ValueError('Empty speech result.')
                audio_path.write_bytes(audio)
                metadata_path.write_text(json.dumps(dict(voice=VOICE,rate=RATE,text=text,fingerprint=fingerprint,cues=cues,boundaries=chunks),indent=2),encoding='utf-8')
                subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-hide_banner','-loglevel','error','-i',str(audio_path),'-c:a','pcm_s16le','-ar','24000','-ac','1',str(EDGE/(scene['id']+'.wav'))],check=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                print('Neural narration ready: '+scene['id'],flush=True);return
            except Exception as error:
                if attempt==2:raise
                print(f"Retry {attempt+1}: {scene['id']} ({type(error).__name__})",flush=True)
                await asyncio.sleep(2*(attempt+1))

async def main(preview):
    scenes=json.loads((PRIVATE/'scenes.json').read_text())
    if preview:scenes=scenes[:1]
    semaphore=asyncio.Semaphore(2)
    await asyncio.gather(*(synthesize(s,semaphore) for s in scenes))
    if not preview:
        (PRIVATE/'voice.json').write_text(json.dumps(dict(engine='Microsoft Edge online text-to-speech',voice=VOICE,language='en-US',rate=RATE,synthetic=True,offline=False,paragraph_synthesis=True,caption_timing='service sentence boundaries',edge_tts_version=edge_tts.__version__),indent=2),encoding='utf-8')
    print(f"Completed {len(scenes)} Edge narration scenes.",flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args()
    asyncio.run(main(args.preview))
