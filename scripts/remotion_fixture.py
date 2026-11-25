"""Generate a deterministic, original 120 BPM test tone, not a song."""
from pathlib import Path
import math, struct, wave
ROOT=Path(__file__).resolve().parents[1]
def main():
    path=ROOT/'remotion/public/synthetic.wav'
    path.parent.mkdir(parents=True, exist_ok=True)
    rate=48000
    samples=bytearray()
    for i in range(rate*15):
        t=i/rate
        phase=t%0.5
        env=min(1,phase/0.005)*math.exp(-phase*18)
        value=int(12000*env*math.sin(2*math.pi*440*t))
        samples.extend(struct.pack('<h',value))
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(samples)
    print(path)
if __name__=='__main__': main()
