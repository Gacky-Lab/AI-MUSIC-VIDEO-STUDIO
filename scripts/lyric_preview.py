"""Prepare and render a local 30s lyric preview; never publishes or calls generation APIs."""
import argparse, hashlib, json, math, shutil, subprocess, tempfile, wave
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FPS=30
FRAMES=900
MAX_WAV=128*1024*1024
def require(ok,message):
    if not ok: raise ValueError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def load(path):
    with Path(path).open("rb") as f:
        data=f.read(1024*1024+1)
    require(len(data)<=1024*1024,"JSON too large")
    return json.loads(data)
def frame(ms): return (ms*FPS+500)//1000
def make_props(handoff, timing, wav_hash, start_ms, evidence=None):
    require(handoff.get("contract_version")=="1.0.0","unsupported lyric handoff")
    text=handoff.get("lyrics_text")
    require(isinstance(text,str) and "\r" not in text and sha(text.encode("utf-8"))==handoff.get("lyrics_sha256"),"lyric hash mismatch")
    require(isinstance(handoff.get("lyric_version_id"),str) and handoff["lyric_version_id"],"missing lyric version")
    require(timing.get("schema_version")=="0.1.0" and timing.get("master_sha256")==wav_hash and timing.get("lyrics_sha256")==handoff["lyrics_sha256"] and timing.get("lyric_version_id")==handoff["lyric_version_id"],"timing identity mismatch")
    require(type(start_ms) is int and start_ms>=0,"invalid start")
    require(timing.get("review_status")=="HUMAN_APPROVED_FOR_PREVIEW" or timing.get("review_status")=="SYNTHETIC_FIXTURE","timing not approved")
    lines=text.split("\n")
    cues=[]; previous=0
    for c in timing.get("cues",[]):
        a,b,i=c.get("start_ms"),c.get("end_ms"),c.get("line_index")
        require(all(type(v) is int for v in (a,b,i)) and 0<=a<b and a>=previous and 0<=i<len(lines),"invalid or overlapping cue")
        previous=b
        label=lines[i]
        require(0<len(label)<=80 and bool(label.strip()) and not any(ord(x)<32 for x in label),"invalid caption line")
        lo,hi=max(a,start_ms),min(b,start_ms+30000)
        if lo<hi:
            f,g=frame(lo-start_ms),frame(hi-start_ms)
            require(0<=f<g<=FRAMES,"cue collapses at 30fps")
            cues.append({"startFrame":f,"endFrame":g,"text":label})
    require(cues,"no captions in selected interval")
    pulses=[]
    if evidence is not None:
        require(evidence.get("schema_version")=="0.1.0" and evidence.get("source_sha256")==wav_hash,"MIR identity mismatch")
        p=evidence.get("pulse",{})
        require(p.get("verified_musical_bpm") is False and p.get("status") in ("CANDIDATE","UNKNOWN"),"unsupported MIR evidence")
        if p["status"]=="CANDIDATE":
            values=p.get("energy_onsets_s")
            require(isinstance(values,list) and len(values)<=30000 and all(type(t) in (int,float) and math.isfinite(t) and t>=0 for t in values),"invalid onsets")
            pulses=sorted(set(frame(round(t*1000)-start_ms) for t in values if start_ms<=t*1000<start_ms+30000))
            pulses=[x for x in pulses if 0<=x<FRAMES]
    return {"cues":cues,"pulses":pulses,"synthetic":timing["review_status"]=="SYNTHETIC_FIXTURE"}
def extract_wav(source,dest,start_ms):
    # Hash and read the same bounded snapshot; only PCM16 local WAV is supported.
    import io
    with Path(source).open("rb") as f: data=f.read(MAX_WAV+1)
    require(len(data)<=MAX_WAV,"WAV exceeds 128 MiB")
    with wave.open(io.BytesIO(data),"rb") as w:
        rate,ch=w.getframerate(),w.getnchannels()
        require(w.getsampwidth()==2 and w.getcomptype()=="NONE" and ch in (1,2) and 8000<=rate<=96000,"expected PCM16 WAV")
        offset=(start_ms*rate+500)//1000
        require(offset+30*rate<=w.getnframes(),"30s interval outside audio")
        w.setpos(offset); raw=w.readframes(30*rate)
        require(len(raw)==30*rate*ch*2,"truncated WAV")
        with wave.open(str(dest),"wb") as o:
            o.setnchannels(ch); o.setsampwidth(2); o.setframerate(rate); o.writeframes(raw)
    return sha(data)
def node_cli():
    package=ROOT/"remotion/node_modules/@remotion/cli/package.json"
    spec=load(package)
    binpath=spec["bin"]
    if isinstance(binpath,dict): binpath=binpath["remotion"]
    return ["node",str(package.parent/binpath)]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wav",type=Path,required=True); p.add_argument("--lyrics",type=Path,required=True); p.add_argument("--timing",type=Path,required=True)
    p.add_argument("--mir",type=Path); p.add_argument("--start-ms",type=int,default=0); p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--authorized-local-preview",action="store_true",required=True,help="confirm authorization for local inputs; not publication approval")
    a=p.parse_args()
    require(a.start_ms>=0,"negative start")
    out=a.output_dir.resolve()
    require(not out.exists(),"choose a new output directory")
    with tempfile.TemporaryDirectory(prefix="amvs-preview-") as tmp:
        stage=Path(tmp); public=stage/"public"; public.mkdir()
        digest=extract_wav(a.wav,public/"preview.wav",a.start_ms)
        props=make_props(load(a.lyrics),load(a.timing),digest,a.start_ms,load(a.mir) if a.mir else None)
        (stage/"props.json").write_text(json.dumps(props,ensure_ascii=False),encoding="utf-8")
        out.mkdir(parents=True)
        # Separate public-dir: no other project media is bundled.
        cmd=node_cli()+["render","src/index.jsx","LyricPreview",str(out/"preview.mp4"),"--codec=h264","--concurrency=2","--props",str(stage/"props.json"),"--public-dir",str(public)]
        subprocess.run(cmd,cwd=ROOT/"remotion",check=True,timeout=600)
        from verify_lyric_preview import verify
        report=verify(out/"preview.mp4",public/"preview.wav")
        report.update({"source_sha256":digest,"start_ms":a.start_ms,"caption_count":len(props["cues"]),"onset_cue_count":len(props["pulses"]),"synthetic":props["synthetic"],"human_visual_approval":"NOT_RUN","release_approval":"NOT_RUN"})
        (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 0 if all(v=="PASS" for v in report["checks"].values()) else 1
if __name__=="__main__": raise SystemExit(main())
