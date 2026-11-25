# P0b Remotion bring-up — candidate, NOT_RUN at authoring
A 15-second, 1080p30 synthetic motion graphic. Three five-second scenes, procedural typography and deterministic 120 BPM tone, no real lyrics, provider calls or private assets. Visual pulse uses the known fixture beat grid rather than audio analysis. The bars are procedural decoration, not a measured spectrum. No claim of actual lyric alignment, artistic quality, visual beat synchronization or reproducible byte equality.

## Windows 11 / PowerShell from repository root
Confirm individual-use license eligibility: https://www.remotion.dev/docs/license/pricing
```powershell
node --version
npm --version
python --version
ffmpeg -version
ffprobe -version
python scripts/remotion_fixture.py
cd remotion
npm install
npm run studio
# close Studio before rendering in a separate terminal if needed
npm run render
cd ..
python scripts/verify_remotion.py
```
Node 22 is the candidate runtime. All direct Remotion packages are pinned to 4.0.545. Transitive dependencies are **not yet locked**; generate and review package-lock.json after successful install, then switch to npm ci. npm/Chromium installation needs internet; rendering does not call a paid generation API. Developer runtime npm DNS failed, so actual Remotion rendering must be verified in CI or Windows. Do not mark V11 PASS from Linux CI. Record OS, exact dependencies, render report and human inspection.

## Official sources
https://www.remotion.dev/docs/render
https://www.remotion.dev/docs/composition
https://www.remotion.dev/docs/agents/webmcp
https://www.remotion.dev/docs/upgrading

## Next gates
P0b: CI render/metadata and human preview, then Windows repeat. P1: authorized final WAV, approved lyrics, manual time anchors, real-song 30-second MV. P2: Video IR driven rendering (current demo is fixed), asset manifest, full song. P3: paid adapter only with explicit cost approval.
