"""Call an extracted Hitokoto Translate Klingon Windows package. Python 3, stdlib only."""
import argparse,json,subprocess,tempfile,wave
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--app',type=Path,required=True,help='Extracted application directory')
p.add_argument('--audio',type=Path,required=True)
p.add_argument('--ui',choices=['en','ja'],default='en')
p.add_argument('--mode',choices=['auto','tlh'],default='tlh')
a=p.parse_args()
exe=a.app.resolve()/'Hitokoto-Klingon.exe'
if not exe.is_file():p.error('Application executable not found')
with wave.open(str(a.audio),'rb') as w:
 if (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())!=(1,2,16000,'NONE'):p.error('Use mono 16-bit PCM WAV at 16 kHz')
 if not 0<w.getnframes()<=160000:p.error('Use an utterance of up to 10 seconds')
with tempfile.TemporaryDirectory(prefix='hitokoto-example-') as folder:
 request=Path(folder)/'request.json'
 request.write_text(json.dumps(dict(audio=str(a.audio.resolve()),ui=a.ui,mode=a.mode,recognitionOnly=True)),encoding='utf-8')
 run=subprocess.run([str(exe),'--engine',str(request)],capture_output=True,encoding='utf-8',timeout=240)
 events=[json.loads(line) for line in run.stdout.splitlines() if line.startswith('{')]
 if run.returncode or not events or events[-1].get('event')!='result':
  raise RuntimeError('Recognition failed: '+(run.stderr[-2000:] or run.stdout[-2000:]))
 print(json.dumps(events[-1],ensure_ascii=True,indent=2))
