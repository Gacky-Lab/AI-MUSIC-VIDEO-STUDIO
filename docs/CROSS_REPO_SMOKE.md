# Cross-repository contract smoke — synthetic only
This test uses the real Lyric Handoff exporter and MIR analyzer at pinned commits, not hand-authored substitutes. The consumer is the actual 30-second preview preparation code. It uses an original Japanese text and an original synthetic pulse fixture; no real song, paid provider call or external upload of personal media.

Pinned upstream:
- LYRIC-DESIGN-FRAMEWORK: d13b8e7c2a2b763256b6f234b756951dab872bd9
- AI-MUSIC-INTELLIGENCE-ENGINE: 6337f65ee5fb2c28558cea83c23266e2e0b51206

Seven checks: lyric export, MIR analysis, master identity, exact Japanese caption text, frame mapping, pulse candidate transfer, rejection of changed master identity. Manual timing anchors are synthetic, not a forced-alignment result. The test stops at Remotion input props; visual rendering of Japanese text, real-song BPM, Windows, Suno/VOCALOID and full Video IR remain separate acceptance gates. Existing 30s synthetic render evidence: https://github.com/Gacky-Lab/AI-MUSIC-VIDEO-STUDIO/actions/runs/45542889707 (English fixture, all four checks PASS).

## Local run
Clone the two upstream repos separately and check out the listed commits. From this repository:
```
python scripts/cross_repo_smoke.py --lyric-repo ../LYRIC-DESIGN-FRAMEWORK --mir-repo ../AI-MUSIC-INTELLIGENCE-ENGINE
```
Use a clean output directory on each run. Only report.json is uploaded by CI. Update pins deliberately after upstream compatibility review.
