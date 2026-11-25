# Interface selection and provenance — 2026-11-25
| Layer | Primary | Fallback / scope |
|---|---|---|
| Dev | VS Code + Codex | Copilot optional; no subscription credentials in repo |
| Render | Remotion CLI + pinned Node/dependencies | FFmpeg smoke only; WebMCP optional Studio interaction |
| QA | FFprobe/FFmpeg, Python | Independent of renderer |
| Images | ChatGPT UI manual export | Optional separately billed API |
| Video | Runway API adapter, optional | Dev MCP distinct from generation MCP; verify capability and price first |
| 3D | Blender Python/CLI | Optional; no unofficial MCP dependency |
| Audio | final WAV + lyric timing | librosa/Whisper candidates, manual corrections |

## Official references (recheck at implementation)
- https://www.remotion.dev/docs/agents/
- https://www.remotion.dev/docs/agents/webmcp
- https://www.remotion.dev/docs/render
- https://www.remotion.dev/docs/license/pricing
- https://docs.dev.runwayml.com/guides/mcp/
- https://docs.dev.runwayml.com/api/
- https://docs.dev.runwayml.com/guides/pricing/
- https://ffmpeg.org/ffprobe.html
- https://ffmpeg.org/ffmpeg-filters.html
- https://developers.openai.com/api/docs/pricing
No live connector or licensing acceptance is inferred from documentation links.

## Upstream audit
- Lyric Handoff v1: upstream docs/handoff_interface.md blob f95fa6a6f670bca87d34eaecd06e395c6c777ea1. Actual keys contract_version, song_id, lyric_version_id, language, lyrics_text, lyrics_sha256. SHA-256 of UTF-8 text after LF normalization, not JSON file hash. Preserve spaces/final newline. Verify before mapping.
- SUNO-GENERATION-OPTIMIZER: provider feedback not independent acceptance; private WAV transfer requires explicit approval; no automatic generation assumed.
- AI-VOCALOID-STUDIO: docs/INTERFACES_VERIFIED_2026-11-24.md blob 50ecdfea1b418dd5ca57e53c47f53da21b74ca9f. MIDI note candidates are not aligned lyrics or actual singing boundaries; V6 unofficial MCP not assumed compatible with V7. Use final authorized exported WAV, not intermediate synthesis.
- AI-MUSIC-INTELLIGENCE-ENGINE: README blob 16be95e37418771a5f950a731b8b3bb6626ab0fd; only conceptual interface assumed.

## Contracts
Music Handoff v0.1 is a new adapter proposal, not an existing upstream interface. Source, final WAV relative path/hash, duration_ms, lyric version/hash and provenance required. Timed lyrics, rights manifest and master-specific alignment are future extensions; absence cannot pass subtitle/release acceptance. Video IR v0.1 uses integer half-open frame ranges [start,end), fps=30, contiguous primary scenes; captions are a separate future track. Convert ms to frames by nearest rounding, ties upward; retain raw timestamps for QA. Asset registry must record hashes and rights; reject absolute paths, traversal, credentials and remote URLs in production manifests. Schema alone does not enforce continuity, path containment or hashes. Synthetic fixture uses procedural backgrounds only. Render runtime must reject unapproved or missing assets.

## Windows bring-up
Check node --version, npm --version, python --version, ffmpeg -version, ffprobe -version. Confirm Remotion license eligibility, then scaffold with npx create-video@latest in a dedicated subfolder; pin versions and lockfile. Follow official Codex Agent Skills/WebMCP docs. Use local CLI as production path even if browser bridge fails. No live Runway call until actual model, cost estimate, cap, rights, authentication and explicit approval are recorded. Keep API keys outside repo; no private inputs in CI. Plus does not imply external API credits.
