"""Independent stream metadata check, not perceptual or beat alignment QA."""
from pathlib import Path
from fractions import Fraction
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=ROOT/'out/remotion.mp4'
    raw=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)],text=True,timeout=30))
    v=[x for x in raw['streams'] if x['codec_type']=='video']
    a=[x for x in raw['streams'] if x['codec_type']=='audio']
    checks={'streams':len(v)==len(a)==1}
    if checks['streams']:
        v,a=v[0],a[0]
        checks.update(profile=v['width']==1920 and v['height']==1080 and Fraction(v['avg_frame_rate'])==30 and int(v['nb_frames'])==450,
            video_duration=abs(float(v['duration'])-15)<=1/30,
            audio_duration=abs(float(a['duration'])-15)<=1/30,
            duration_delta=abs(float(v['duration'])-float(a['duration']))<=1/30)
    report={'scope':'synthetic Remotion stream metadata only','checks':{k:'PASS' if z else 'FAIL' for k,z in checks.items()}}
    (ROOT/'out/remotion-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if all(checks.values()) else 1
if __name__=='__main__': raise SystemExit(main())
