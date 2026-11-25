"""Five-repository synthetic integration, no paid calls, no GUI or private inputs."""
import argparse
import hashlib
import html
import json
import math
import os
import struct
import subprocess
import sys
import uuid
import wave
from pathlib import Path

try:
    from .lyric_preview import make_props
except ImportError:
    from lyric_preview import make_props

ROOT=Path(__file__).resolve().parents[1]
PINS=json.loads((ROOT/"config/integration-pins.json").read_text())
LINES=["朝の光がほどける","青い空へ歩き出す","遠い波の音を聴く","静かな風が通り過ぎる","小さな星が目を覚ます","新しい景色を見つける"]
STAGES=["provenance","lyric","suno_proposal","vocaloid_midi","synthetic_audio","mir","pitch","note_candidates","alignment_candidates","video_props","negative_gates"]
def require(ok,msg):
    if not ok: raise ValueError(msg)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def write(path,value):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    os.replace(tmp,path)
def run(cmd,cwd):
    return subprocess.run([str(x) for x in cmd],cwd=cwd,check=True,capture_output=True,text=True,encoding="utf-8",timeout=120).stdout
def py(repo,*args):
    return run([sys.executable,*args],repo)
def verify_pins(upstream):
    paths={}
    for key,pin in PINS.items():
        p=upstream/key
        require(run(["git","rev-parse","HEAD"],p).strip()==pin["sha"],"upstream revision mismatch: "+key)
        require(not run(["git","status","--porcelain","--untracked-files=no"],p).strip(),"modified upstream: "+key)
        paths[key]=p.resolve()
    return paths
def make_midi(path):
    import mido
    m=mido.MidiFile(type=1,ticks_per_beat=480)
    m.tracks.append(mido.MidiTrack([mido.MetaMessage("set_tempo",tempo=500000,time=0),mido.MetaMessage("end_of_track",time=28800)]))
    tr=mido.MidiTrack()
    for i in range(60):
        pitch=(60,64,67,69)[i%4]
        tr.append(mido.Message("note_on",note=pitch,velocity=90,time=0))
        tr.append(mido.Message("note_off",note=pitch,velocity=0,time=480))
    m.tracks.append(tr); m.save(str(path))
def synthesize(notes,path):
    rate=16000; raw=bytearray()
    for i,n in enumerate(notes):
        require(n["start_sample"]==i*24000 and n["end_sample"]==(i+1)*24000,"MIDI timing mismatch")
        hz=440*2**((n["pitch_midi"]-69)/12)
        for j in range(rate//2):
            t=j/rate
            v=int(12000*min(1,t/.005)*math.exp(-t*16)*math.sin(2*math.pi*hz*t))
            raw.extend(struct.pack("<h",v))
    with wave.open(str(path),"wb") as w:
        w.setparams((1,2,rate,0,"NONE","not compressed")); w.writeframes(raw)
def reject(fn):
    try: fn()
    except (ValueError,subprocess.CalledProcessError): return
    raise AssertionError("invalid input unexpectedly accepted")
def dashboard(out,report):
    esc=lambda v:html.escape(str(v))
    rows="".join("<tr><td>"+esc(k)+"</td><td>"+esc(v)+"</td></tr>" for k,v in report["stages"].items())
    body="<h1>Gacky-Lab | Integration evidence</h1><p>Synthetic only · no paid generation · no singing synthesis</p><p>Run "+esc(report["run_id"])+" / "+esc(report["status"])+"</p><table><tr><th>Stage</th><th>Status</th></tr>"+rows+"</table><p>Real song, vocal synthesis, lyric alignment and artistic acceptance: NOT_RUN</p><p><a href='report.json'>JSON evidence</a></p>"
    (out/"index.html").write_text("<!doctype html><meta charset='utf-8'><title>Integration evidence</title><style>body{font:17px system-ui;background:#101b2d;color:#e7f2fa;padding:40px;max-width:850px;margin:auto}table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #53677b;text-align:left}a{color:#81d7c3}</style>"+body,encoding="utf-8")
def execute(upstream,out):
    out=out.resolve(); out.mkdir(parents=True,exist_ok=False)
    report={"version":"0.1.0","run_id":uuid.uuid4().hex,"mode":"SYNTHETIC_OFFLINE","status":"RUNNING","stages":dict.fromkeys(STAGES,"NOT_RUN"),"upstream":PINS,"artifacts":{},"live_suno":"NOT_RUN","vocal_synthesis":"NOT_RUN","automatic_lyric_alignment":"NOT_RUN","real_song":"NOT_RUN","render":"NOT_RUN","artistic_acceptance":"NOT_RUN"}
    def stage(name,fn):
        report["stages"][name]="RUNNING"; write(out/"report.json",report)
        try: val=fn()
        except Exception:
            report["stages"][name]="FAIL"; raise
        report["stages"][name]="PASS"; write(out/"report.json",report)
        return val
    try:
        repos=stage("provenance",lambda:verify_pins(upstream))
        def lyric():
            (out/"lyrics.txt").write_text("\n".join(LINES),encoding="utf-8")
            py(repos["lyric"],"scripts/export_handoff.py","--lyrics",out/"lyrics.txt","--song-id","integration-synthetic","--version-id","v1","--output",out/"handoff.json")
            h=read(out/"handoff.json")
            require(h["lyrics_text"]=="\n".join(LINES),"lyric transfer")
            return h
        h=stage("lyric",lyric)
        def suno():
            args=["suno_optimizer.py","plan","fixtures/mcp_observed_subset.mock.json",out/"handoff.json","--style","synthetic electronic","--bpm","120","--duration","30","--attempt-id","integration-fixture","--approved-credits","20","--estimated-upper","10","--remaining","30","--max-candidates","2"]
            p=json.loads(py(repos["suno"],*args))
            require(p["execution"]=="PROPOSAL_ONLY" and p["requires_live_reconfirmation"] is True and p["lyric_sha256"]==h["lyrics_sha256"],"unsafe proposal")
            write(out/"suno-proposal.json",p)
            # Simulate an uncertain submission; no remote execution. Exercise actual upstream recovery.
            code="import json,sys; from pathlib import Path; from verification import new_run,reserve,reconcile,save_checkpoint,load_checkpoint,totals; p=json.load(open(sys.argv[1])); f=p['approval_fingerprint']; r=reserve(new_run(20,2,4,60),'synthetic',f,f,10,2,0,30); save_checkpoint(sys.argv[2],r); r=load_checkpoint(sys.argv[2]); assert totals(r)['pending']==1; r=reconcile(r,'synthetic',['fixture-a','fixture-b'],10,True); assert totals(r)['pending']==0; print(json.dumps(totals(r)))"
            state=json.loads(py(repos["suno"],"-c",code,out/"suno-proposal.json",out/"simulated-checkpoint.json"))
            require(state["spent"]==10 and state["pending"]==0,"simulated state")
            write(out/"simulated-state.json",state)
            return args
        args=stage("suno_proposal",suno)
        def midi():
            make_midi(out/"source.mid")
            py(repos["vocaloid"],"tools/midi_candidates.py","--midi",out/"source.mid","--song-id",h["song_id"],"--track-index","1","--lyric-handoff",out/"handoff.json","--output",out/"midi-candidates.json")
            m=read(out/"midi-candidates.json")
            require(m["source_midi_sha256"]==digest(out/"source.mid") and m["lyric_reference"]["lyrics_sha256"]==h["lyrics_sha256"] and m["alignment_status"]=="needs_lyric_and_voice_review" and len(m["notes"])==60,"MIDI contract mismatch")
            return m
        m=stage("vocaloid_midi",midi)
        stage("synthetic_audio",lambda:synthesize(m["notes"],out/"source.wav"))
        master=digest(out/"source.wav")
        def mir():
            py(repos["mir"],"-m","mir.analyze",out/"source.wav","--output",out/"evidence.json")
            ev=read(out/"evidence.json")
            require(ev["source_sha256"]==master and ev["duration_s"]==30 and ev["pitch_status"]=="NOT_RUN","audio identity mismatch")
            return ev
        ev=stage("mir",mir)
        def pitch():
            py(repos["mir"],"-m","mir.pitch",out/"source.wav","--output",out/"pitch.json")
            p=read(out/"pitch.json")
            require(p["source_sha256"]==master,"pitch identity")
            errors=[]; eligible=0
            for f in p["frames"]:
                t=f["center_s"]; phase=t%.5
                if .07<=phase<=.22:
                    eligible+=1
                    if f["candidate"] is not None:
                        expected=m["notes"][int(t/.5)]["pitch_midi"]
                        errors.append(abs(f["candidate"]["midi_candidate"]-expected)*100)
            correct=sum(e<=35 for e in errors)
            require(eligible>=240 and correct/eligible>=.95,"synthetic pitch threshold")
            report["pitch_benchmark"]={"eligible_frames":eligible,"voiced_frames":len(errors),"correct_frames":correct,"within_35_cents_fraction":correct/eligible,"real_song_accuracy":"NOT_RUN"}
        stage("pitch",pitch)
        def notes():
            py(repos["mir"],"-m","mir.notes",out/"pitch.json","--output",out/"note-candidates.json")
            result=read(out/"note-candidates.json")
            require(result["source_sha256"]==master and result["status"]=="REVIEW_ONLY","note evidence identity")
            expected=[n["pitch_midi"] for n in m["notes"]]
            actual=[n["pitch_midi"] for n in result["notes"]]
            require(actual==expected,"synthetic note sequence mismatch")
            onset_errors=[abs(n["start_s"]-i*.5) for i,n in enumerate(result["notes"])]
            require(max(onset_errors)<=.12,"synthetic onset threshold")
            report["note_benchmark"]={"expected":len(expected),"matched_pitch_sequence":len(actual),"max_onset_error_s":max(onset_errors),"real_song_accuracy":"NOT_RUN"}
        stage("note_candidates",notes)
        def alignment():
            transcript={"schema_version":"0.1.0","master_sha256":master,"source":"SYNTHETIC_FIXTURE","segments":[{"start_ms":i*5000,"end_ms":(i+1)*5000,"text":line} for i,line in enumerate(LINES)]}
            write(out/"transcript.json",transcript)
            py(repos["lyric"],"scripts/align_transcript.py","--lyrics",out/"handoff.json","--transcript",out/"transcript.json","--output",out/"alignment-candidates.json")
            candidate=read(out/"alignment-candidates.json")
            require(candidate["review_status"]=="CANDIDATE_REVIEW_REQUIRED" and candidate["master_sha256"]==master,"alignment identity")
            reject(lambda:make_props(h,candidate,master,0,ev))
            return candidate
        candidate=stage("alignment_candidates",alignment)
        timing={"schema_version":"0.1.0","master_sha256":master,"lyrics_sha256":h["lyrics_sha256"],"lyric_version_id":h["lyric_version_id"],"review_status":"SYNTHETIC_FIXTURE","cues":candidate["cues"]}
        require(timing["cues"]==[{"start_ms":i*5000,"end_ms":(i+1)*5000,"line_index":i} for i in range(6)],"synthetic ground truth mismatch")
        write(out/"timing.json",timing)
        def video():
            props=make_props(h,timing,master,0,ev)
            require([c["text"] for c in props["cues"]]==LINES and props["synthetic"],"video cue contract")
            write(out/"props.json",props)
        stage("video_props",video)
        def negative():
            reject(lambda:make_props(h,timing,"0"*64,0,ev))
            reject(lambda:make_props(h,{**timing,"review_status":"UNKNOWN"},master,0,ev))
            bad=args.copy(); bad[bad.index("--remaining")+1]="0"
            reject(lambda:py(repos["suno"],*bad))
            reject(lambda:py(repos["vocaloid"],"tools/midi_candidates.py","--midi",out/"source.mid","--song-id","wrong","--track-index","1","--lyric-handoff",out/"handoff.json","--output",out/"invalid.json"))
            require(not (out/"invalid.json").exists(),"invalid output created")
        stage("negative_gates",negative)
        report["status"]="PASS"
    except Exception as e:
        report["status"]="FAIL"; report["error_type"]=type(e).__name__
        print("Integration stopped:",str(e),file=sys.stderr)
        if isinstance(e,subprocess.CalledProcessError): print(e.stderr,file=sys.stderr)
    finally:
        report["artifacts"]={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ("report.json","index.html")}
        write(out/"report.json",report); dashboard(out,report)
    return 0 if report["status"]=="PASS" else 1
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(); return execute(a.upstream.resolve(),a.output)
if __name__=="__main__": raise SystemExit(main())
