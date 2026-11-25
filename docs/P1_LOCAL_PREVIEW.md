# P1 candidate — local 30s lyric preview
A local, data-driven 1080p30 preview from an authorized final PCM16 WAV, Lyric Handoff v1, manually reviewed lyric line anchors and optional Analysis Evidence v0.1. Uses only a procedural visual theme; no image/video generation API, no automatic release. Source audio and lyrics are private and must never be placed in CI. The preview path is a narrow local contract, not the full Video IR renderer or Music Handoff implementation.

## Prepare
Install Node 22, Python 3.11+, FFmpeg/FFprobe; confirm Remotion license eligibility. Run npm install in remotion/ first. Use your own authorized local WAV (PCM16 mono/stereo, 8–96kHz, <=128MiB), exported Lyric Handoff JSON and timing JSON. Timing values are absolute milliseconds from final master time zero, line_index is zero-based in lyrics_text split by LF, cues are sorted and non-overlapping. Copy fixtures from the synthetic generator as a template; replace hashes with the actual master/lyric hashes and manually confirm every anchor. Set review_status=HUMAN_APPROVED_FOR_PREVIEW only after review. This is an operator assertion, not independent accuracy evidence. Optional MIR JSON must match the final WAV SHA-256. Only candidate energy onsets affect decoration, never lyric timing.

```powershell
python scripts/lyric_preview_fixture.py
cd remotion
npm install
cd ..
python scripts/lyric_preview.py --wav out/p1-fixture/source.wav --lyrics out/p1-fixture/lyrics.json --timing out/p1-fixture/timing.json --mir out/p1-fixture/mir.json --output-dir out/p1-preview --authorized-local-preview
```
For real audio, change paths and optionally --start-ms (default 0). Choose a fresh output directory outside tracked content; only synthetic fixture outputs may be uploaded to CI. Do not upload real inputs or outputs. Inspect preview.mp4 and report.json. Captions are derived from exact lyric lines; timing is rounded to 30fps. The renderer uses a temporary public directory and only a 30s WAV excerpt. Do not use for concurrent production before dependency lock and security review.

## Verification boundary
CI checks synthetic 30s render, profile, stream duration, zero-lag decoded audio similarity, and eight input/identity tests. The audio check is a provisional global metric; it can miss localized defects. No independent lyric timing, font readability, black-frame, real song, Windows, or subjective quality acceptance. MIR fixture is contract-shaped synthetic input, not a live cross-repository execution. Actual MIR adapter integration still pending. All release gates remain blocked until evidence and human approval.
Official CLI docs: https://www.remotion.dev/docs/cli/render and https://www.remotion.dev/docs/options/props.
