"""Exercise pinned upstream implementations, using only generated public-safe fixtures."""
import argparse, json, subprocess, sys
from pathlib import Path
from lyric_preview import make_props, extract_wav, require

ROOT=Path(__file__).resolve().parents[1]
def call(args,cwd=ROOT):
    subprocess.run([sys.executable,*map(str,args)],cwd=cwd,check=True,timeout=60)
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lyric-repo",type=Path,required=True)
    p.add_argument("--mir-repo",type=Path,required=True)
    a=p.parse_args()
    lyric=a.lyric_repo.resolve(); mir=a.mir_repo.resolve()
    call([ROOT/"scripts/lyric_preview_fixture.py"])
    fixture=ROOT/"out/p1-fixture"
    out=ROOT/"out/cross-repo"; out.mkdir(exist_ok=False)
    lines=["朝の光がほどける","青い空へ歩き出す","遠い波の音を聴く","静かな風が通り過ぎる","小さな星が目を覚ます","新しい景色を見つける"]
    text="\n".join(lines)
    (out/"lyrics.txt").write_text(text,encoding="utf-8")
    call([lyric/"scripts/export_handoff.py","--lyrics",out/"lyrics.txt","--song-id","cross-repo-synthetic","--version-id","demo-v1","--output",out/"handoff.json"],lyric)
    call(["-m","mir.analyze",fixture/"source.wav","--output",out/"evidence.json"],mir)
    h=read(out/"handoff.json"); evidence=read(out/"evidence.json")
    digest=extract_wav(fixture/"source.wav",out/"excerpt.wav",0)
    require(evidence["source_sha256"]==digest,"upstream WAV hash mismatch")
    require(h["language"]=="ja" and h["lyrics_text"]==text,"upstream lyric mismatch")
    timing={"schema_version":"0.1.0","master_sha256":digest,"lyrics_sha256":h["lyrics_sha256"],"lyric_version_id":h["lyric_version_id"],"review_status":"SYNTHETIC_FIXTURE","cues":[{"start_ms":i*5000,"end_ms":(i+1)*5000,"line_index":i} for i in range(6)]}
    (out/"timing.json").write_text(json.dumps(timing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    props=make_props(h,timing,digest,0,evidence)
    require([c["text"] for c in props["cues"]]==lines,"caption transfer mismatch")
    require([(c["startFrame"],c["endFrame"]) for c in props["cues"]]==[(i*150,(i+1)*150) for i in range(6)],"frame mapping mismatch")
    require(evidence["pulse"]["status"]=="CANDIDATE" and abs(evidence["pulse"]["pulse_per_minute"]-120)<=3 and len(props["pulses"])>=55,"expected regular synthetic pulse")
    try:
        make_props(h,timing,"0"*64,0,evidence)
    except ValueError:
        pass
    else:
        raise AssertionError("modified master identity accepted")
    report={"scope":"actual upstream Python CLIs to preview props, synthetic fixture only","checks":{"lyric_export":"PASS","mir_analysis":"PASS","master_identity":"PASS","japanese_caption_transfer":"PASS","frame_mapping":"PASS","pulse_candidate_transfer":"PASS","changed_master_rejected":"PASS"},"caption_count":len(props["cues"]),"pulse_candidate_count":len(props["pulses"]),"pulse_per_minute":evidence["pulse"]["pulse_per_minute"],"render":"NOT_RUN","real_song":"NOT_RUN"}
    (out/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
