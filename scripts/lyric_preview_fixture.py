"""Original synthetic 30s fixture; no user data."""
import hashlib,json,math,struct,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=ROOT/"out/p1-fixture"; p.mkdir(parents=True,exist_ok=True)
    rate=16000; data=bytearray()
    for i in range(rate*30):
        t=i/rate; phase=t%0.5
        v=int(12000*min(1,phase/.005)*math.exp(-phase*16)*math.sin(2*math.pi*440*t))
        data.extend(struct.pack("<h",v))
    wav=p/"source.wav"
    with wave.open(str(wav),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(data)
    digest=hashlib.sha256(wav.read_bytes()).hexdigest()
    lines=["The morning opens","A signal in the blue","We follow the horizon","And find a brighter frame","The quiet turns to light","One more step into the sky"]
    text="\n".join(lines); lh=hashlib.sha256(text.encode()).hexdigest()
    items={"lyrics":{"contract_version":"1.0.0","song_id":"synthetic","lyric_version_id":"demo-1","language":"en","lyrics_text":text,"lyrics_sha256":lh},"timing":{"schema_version":"0.1.0","master_sha256":digest,"lyrics_sha256":lh,"lyric_version_id":"demo-1","review_status":"SYNTHETIC_FIXTURE","cues":[{"start_ms":i*5000,"end_ms":(i+1)*5000,"line_index":i} for i in range(6)]},"mir":{"schema_version":"0.1.0","source_sha256":digest,"pulse":{"status":"CANDIDATE","verified_musical_bpm":False,"energy_onsets_s":[i*.5 for i in range(60)]}}}
    for k,v in items.items(): (p/(k+".json")).write_text(json.dumps(v,indent=2)+"\n",encoding="utf-8")
    print(p)
if __name__=="__main__": main()
