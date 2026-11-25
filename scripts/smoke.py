"""Offline FFmpeg synthetic smoke only; no network or provider calls."""
import json, subprocess
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]

def validate_timeline(ir):
    if (ir['fps'],ir['width'],ir['height']) != (30,1920,1080): raise ValueError('unsupported profile')
    end=0; ids=set()
    for s in ir['scenes']:
        a,b=s['start_frame'],s['end_frame']
        if type(a) is not int or type(b) is not int or a!=end or b<=a or s['id'] in ids: raise ValueError('invalid scene interval or ID')
        ids.add(s['id']); end=b
    if not ids or end!=ir['total_frames']: raise ValueError('incomplete timeline')

def main():
    ir=json.loads((ROOT/'fixtures/video_ir.synthetic.json').read_text())
    validate_timeline(ir)
    if any(s['engine']!='procedural' for s in ir['scenes']): raise ValueError('only synthetic procedural scenes supported')
    out=ROOT/'out'; out.mkdir(exist_ok=True); path=out/'synthetic.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
    colors=['0x18324e','0x335c78','0x874b68']
    for i,s in enumerate(ir['scenes']):
        duration=(s['end_frame']-s['start_frame'])/ir['fps']
        cmd+=['-f','lavfi','-i',f'color=c={colors[i%len(colors)]}:s=1920x1080:r=30:d={duration}']
    count=len(ir['scenes']); total=ir['total_frames']/ir['fps']
    cmd+=['-f','lavfi','-i',f'sine=frequency=440:sample_rate=48000:duration={total}','-filter_complex',''.join(f'[{i}:v]' for i in range(count))+f'concat=n={count}:v=1:a=0[v]','-map','[v]','-map',f'{count}:a','-c:v','libx264','-threads','2','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(path)]
    subprocess.run(cmd,check=True,timeout=120)
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)],text=True,timeout=30))
    v=next(x for x in p['streams'] if x['codec_type']=='video'); a=next(x for x in p['streams'] if x['codec_type']=='audio')
    checks={'V01':v['width']==1920 and v['height']==1080 and Fraction(v['avg_frame_rate'])==30 and int(v['nb_frames'])==ir['total_frames'] and abs(float(v['duration'])-total)<=1/30,'V02':abs(float(v['duration'])-float(a['duration']))<=1/30}
    report={'scope':'synthetic FFmpeg smoke; not Remotion or Windows','checks':{k:'PASS' if val else 'FAIL' for k,val in checks.items()},'video_frames':int(v['nb_frames']),'video_duration_s':float(v['duration']),'audio_duration_s':float(a['duration']),'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2)); return 0 if all(checks.values()) else 1
if __name__=='__main__': raise SystemExit(main())
