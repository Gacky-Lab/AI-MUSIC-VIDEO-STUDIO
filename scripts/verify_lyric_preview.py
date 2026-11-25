"""Independent metadata and decoded-audio similarity check. No artistic acceptance."""
import json, math, subprocess, struct
from fractions import Fraction
def decode(path):
    data=subprocess.check_output(["ffmpeg","-v","error","-i",str(path),"-map","0:a:0","-ac","2","-ar","8000","-f","s16le","-"],timeout=60)
    return [x[0] for x in struct.iter_unpack("<h",data)]
def verify(video,reference):
    raw=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(video)],text=True,timeout=30))
    v=[s for s in raw["streams"] if s["codec_type"]=="video"]; a=[s for s in raw["streams"] if s["codec_type"]=="audio"]
    checks={"streams":"PASS" if len(v)==len(a)==1 else "FAIL"}
    report={"scope":"30s preview stream metadata and zero-lag decoded-audio similarity; not caption timing or artistic validation","checks":checks}
    if checks["streams"]!="PASS": return report
    v,a=v[0],a[0]
    checks["profile"]="PASS" if (v["width"],v["height"],Fraction(v["avg_frame_rate"]),int(v["nb_frames"]))==(1920,1080,30,900) else "FAIL"
    checks["duration"]="PASS" if max(abs(float(v["duration"])-30),abs(float(a["duration"])-30),abs(float(v["duration"])-float(a["duration"])))<=1/30 else "FAIL"
    x,y=decode(reference),decode(video); n=min(len(x),len(y))
    x,y=x[:n],y[:n]
    xx=sum(t*t for t in x); yy=sum(t*t for t in y)
    corr=sum(i*j for i,j in zip(x,y))/math.sqrt(xx*yy) if xx and yy else None
    ratio=math.sqrt(yy/xx) if xx else None
    report.update({"audio_correlation_zero_lag":corr,"audio_rms_ratio":ratio})
    checks["audio_similarity"]="UNKNOWN" if corr is None else "PASS" if corr>=.95 and .85<=ratio<=1.15 else "FAIL"
    return report
