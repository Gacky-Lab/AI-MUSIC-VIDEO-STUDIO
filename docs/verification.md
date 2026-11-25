# DVP / DVR and implementation plan
Initial thresholds are engineering targets, not measured artistic preferences.

| Test | Acceptance | Initial evidence |
|---|---|---|
| V01 | 1920x1080, 30fps, 450 frames, 15s synthetic | Prior local FFmpeg smoke; rerun CI |
| V02 | Audio/video stream duration difference <=1 frame, both present | Prior local smoke; rerun CI |
| V03 | Gaps, overlaps, duplicate IDs rejected | Prior five unit tests; rerun CI |
| V04 | No unintended black frames/silence, planned fades masked | NOT_RUN |
| V05 | 95% approved lyric boundaries within 200ms of human references | NOT_RUN |
| V06 | No missing/garbled approved captions | NOT_RUN |
| V07 | Decoded AAC content comparison, no unintended edits | NOT_RUN |
| V08 | No overspend; unknown paid task does not replay | NOT_RUN |
| V09 | Equivalent output from pinned environment | NOT_RUN |
| V10 | Identity consistency, creative approval and rights | NOT_RUN |
| V11 | Windows Remotion actual render | NOT_RUN |
| V12 | Suno/VOCALOID final master integration | NOT_RUN |

## Gates
| Phase | Deliverable | Exit gate |
|---|---|---|
| P0a | Synthetic FFmpeg smoke + schema + CI | V01–03 pass on checked commit |
| P0b | Windows preflight, pinned Remotion scaffold, 15s synthetic render | V01–03 and V11 |
| P1 | Authorized real WAV, manual timing, 30s lyric MV | V04–07 plus human review |
| P2 | 3–5min MV, reusable templates, scene cache, vertical variant | V04–07, V09–10 |
| P3 | Optional video adapter: read-only first, then separately approved single 5s clip | V08 incl timeout/recovery; actual cost recorded |
| P4 | VOCALOID/DAW final master and MIR integration | V12; verify timing again |
| P5 | Pre-registered comparison | Report results incl negative/unknown |

P0–P5 must not be implemented in one unverified batch. P1 can use Suno WAV before P4. No external paid calls in P0–P2.

## Research protocol (proposal)
Compare A: fixed image/lyrics; B: beat-aware local animation; C: B plus budget-limited AI video scenes. Same final master, lyric text, aspect ratio, duration and release setting. Predefine rubric and samples, randomize presentation order, blind reviewers where feasible. Record human active time, API cost, elapsed time, retries, QA defects, synchronization, narrative coherence and preference. Report missing and negative results, limitations and distributions; no superiority claim from anecdotes. No paid calls or listener study in Phase 0.

## DVR
Previous local artifact: Linux, FFmpeg 7.1.5, Python 3.13.5; five timeline tests and 15s synthetic output (450 frames, 15.0s audio/video) passed. This is historical evidence for the earlier ZIP version, not evidence for this Git commit or target Windows machine. GitHub Actions must independently rerun the checked commit. No paid calls or real-song acceptance. No Remotion, Windows, live generation, or listener efficacy claimed.
