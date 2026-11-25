"""Synthetic visual/audio regression gates. Not OCR or human quality approval."""
import argparse, json, math, re, subprocess, struct
from pathlib import Path

def cmd(args):
    return subprocess.run(args,check=True,capture_output=True,timeout=90)
def frame_luma(video, sec):
    r=cmd(["ffmpeg","-v","error","-ss",str(sec),"-i",str(video),"-frames:v","1","-vf","crop=1620:330:150:370,format=gray","-f","rawvideo","-"])
    data=r.stdout
    if len(data)!=1620*330: raise ValueError("missing frame")
    return sum(v>=180 for v in data)
def decode(path):
    r=cmd(["ffmpeg","-v","error","-i",str(path),"-map","0:a:0","-ac","2","-ar","8000","-f","s16le","-"])
    return [v[0] for v in struct.iter_unpack("<h",r.stdout)]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--video",type=Path,required=True)
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    black=cmd(["ffmpeg","-hide_banner","-i",str(a.video),"-vf","blackdetect=d=0.10:pix_th=0.10:pic_th=0.98","-an","-f","null","-"]).stderr.decode("utf-8",errors="replace")
    black_events=re.findall(r"black_start:([0-9.]+)",black)
    bright=[frame_luma(a.video,i*5+2.5) for i in range(6)]
    x,y=decode(a.reference),decode(a.video)
    block=16000
    stats=[]
    for offset in range(0,30*block,block):
        u,v=x[offset:offset+block],y[offset:offset+block]
        if len(u)!=block or len(v)!=block: stats.append(None); continue
        uu=sum(z*z for z in u); vv=sum(z*z for z in v)
        stats.append(sum(i*j for i,j in zip(u,v))/math.sqrt(uu*vv) if uu and vv else None)
    checks={"no_detected_black_segment":"PASS" if not black_events else "FAIL",
            "bright_caption_region_all_six_samples":"PASS" if all(v>=150 for v in bright) else "FAIL",
            "one_second_audio_similarity":"PASS" if all(v is not None and v>=.95 for v in stats) else "FAIL"}
    report={"scope":"synthetic regression only; brightness proxy does not verify glyph correctness or lyric timing","checks":checks,
            "black_events":black_events,"bright_pixel_counts":bright,"audio_blocks":len(stats),
            "min_audio_correlation":min((v for v in stats if v is not None),default=None),
            "human_visual_review":"NOT_RUN","real_song":"NOT_RUN"}
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0 if all(v=="PASS" for v in checks.values()) else 1
if __name__=="__main__": raise SystemExit(main())
