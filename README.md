# AI-MUSIC-VIDEO-STUDIO

[![Offline CI](https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/actions/workflows/offline.yml/badge.svg?branch=main)](https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/actions/workflows/offline.yml) · [Gacky-Lab research portfolio](https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/blob/main/docs/profile/README.md)

AI音楽映像制作・自動編集・品質保証基盤 / Reproducible AI music video production framework.

**Status: Phase 0 — synthetic FFmpeg and Remotion rendering verified in CI.** Windows runtime, real-song alignment, subjective video quality and paid generation remain NOT_RUN. Independent research, not affiliated with providers.

```mermaid
flowchart LR
 L[Lyric Handoff] --> M[Music Handoff]
 S[Suno WAV] --> M
 V[VOCALOID / DAW WAV] --> M
 I[MIR evidence] --> M
 M --> T[Storyboard / Video IR]
 T --> R[Remotion / local assets]
 R --> Q[Independent QA]
 Q -->|Fail| T
 Q -->|Pass and human approval| E[MV export]
```

## Documents
- [Requirements and architecture](docs/requirements.md)
- [Interface decisions and sources](docs/interfaces.md)
- [Implementation plan and DVP/DVR](docs/verification.md)
- [Music Handoff schema](schemas/music_handoff.schema.json)
- [Video IR schema](schemas/video_ir.schema.json)

## Offline quick start
Python 3.11+ and FFmpeg/FFprobe on PATH. No network or paid calls by the scripts.
```sh
python -m unittest discover -s tests -v
python scripts/smoke.py
```
Synthetic 15-second MP4 and report are written to ignored out/. This is a simple three-scene technical smoke test, not the Remotion production renderer or an artistic-quality test.

## Related projects
- [LYRIC-DESIGN-FRAMEWORK](https://github.com/Gacky-Lab/LYRIC-DESIGN-FRAMEWORK): Lyric Handoff v1.
- [SUNO-GENERATION-OPTIMIZER](https://github.com/Gacky-Lab/SUNO-GENERATION-OPTIMIZER): source audio candidates and evidence.
- [AI-MUSIC-INTELLIGENCE-ENGINE](https://github.com/Gacky-Lab/AI-MUSIC-INTELLIGENCE-ENGINE): future MIR and singing analysis; no existing API assumed.
- [AI-VOCALOID-STUDIO](https://github.com/Gacky-Lab/AI-VOCALOID-STUDIO): proposed Song IR and mastered audio.

No private music, credentials, signed URLs, proprietary assets or voicebanks. License undecided. Human approval required for paid calls and release.

## Portfolio and next milestone
- [Gacky-Lab portfolio README draft](docs/profile/README.md)
- [Conceptual portfolio architecture](docs/profile/architecture.svg)
- [P0b Remotion candidate / Windows bring-up](docs/P0B_REMOTION.md): synthetic motion graphic; Linux CI render and metadata checks passed. Windows repeat and visual inspection remain pending.

### Verified Remotion preview (Linux CI)

- [CI run and downloadable artifact](https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/actions/runs/45542015749): 15 s, 1920×1080, 30 fps, 450 frames; all five independent stream checks passed. Synthetic test tone only.
- No paid generation API was used. This is not a real-song MV or an artistic-quality assessment. The generated package lock is in the CI artifact; dependency lock review and Windows verification remain open.
