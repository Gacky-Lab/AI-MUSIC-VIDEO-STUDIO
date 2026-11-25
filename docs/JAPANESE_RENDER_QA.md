# Japanese synthetic render quality gate
## Scope
Extend the verified cross-repository preparation test through the actual renderer. The prior verified commit tested only Remotion props. Use the actual pinned upstream lyric exporter and MIR analyzer, generated Japanese captions, 30s pulse train and manual synthetic time anchors. No real lyrics or audio.
## Acceptance
| Gate | Target |
|---|---|
| Existing contract test | 7/7 PASS |
| Render | 1920x1080, 30fps, 900 frames, 30s, stream checks |
| Font | Noto Sans CJK JP available in Linux runner |
| Black detection | No >=0.10s black segment at 98% dark pixels, pixel threshold 0.10 |
| Caption presence proxy | >=150 bright pixels in designated caption region at six cue midpoints |
| Audio local integrity | Zero-lag correlation >=0.95 in each of 30 one-second blocks at 8kHz stereo |
| Human visual/lyric review | NOT_RUN; required separately |
Thresholds apply only to this fixture and procedural visual template. Brightness is not OCR, does not prove correct glyphs, line wrapping or timing, and can give false positives. Audio similarity cannot establish perceptual quality or absence of all local defects. No auto release.
## Reproducibility
Pinned upstream commits are recorded in the workflow. Node packages have pinned direct versions; CI emits lockfile for later review. Font version and transitive dependencies not locked yet. Windows repeat pending.
## Evidence
Earlier contract test: https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/actions/runs/45543144307.
Earlier 30s render: https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/actions/runs/45542889707.
New integrated CI and sample frame pending at authoring. Record outcome after execution.
