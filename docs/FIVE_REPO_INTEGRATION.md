# Five-repository synthetic integration

One runner invokes four pinned upstream checkouts and the local video implementation. No additional repository. The generated MIDI is passed through the actual VOCALOID studio extractor, then rendered by a deliberately simple sine synthesizer (not VOCALOID). The WAV is analyzed by MIR, including the experimental pitch baseline; lyric handoff and timing are passed to video preparation. The Suno plan and recovery are offline simulations using the mock schema. They do not produce the WAV.

```sh
python -m pip install -r requirements-integration.txt
# Clone each repository into upstream/{lyric,suno,vocaloid,mir} and check out
# the exact SHA in config/integration-pins.json.
python scripts/integration_runner.py --upstream upstream --output out/integration
```

Read out/integration/index.html and report.json. The report records stage status, pinned SHA, artifact hashes, simulated budget, pitch benchmark and NOT_RUN gates. Existing output directories are rejected; a failed stage stops downstream processing.

Docker: build with `docker build -f Dockerfile.integration -t gacky-integration .`, then `docker run --name gacky-run --network none -v "$PWD/upstream:/upstream:ro" gacky-integration`. Git checkout ownership must be trusted explicitly if different from container UID; CI uses an explicit safe-directory list. Copy results using `docker cp gacky-run:/output/run ./integration-result`. The image pins Python and direct/transitive Python versions; OS package/image digests are not locked. Docker covers contracts, not Remotion/browser rendering. No real-song, live Suno, VOCALOID synthesis or automatic lyric alignment claim.

CI separately renders the generated 30-second WAV with the Japanese captions and verifies streams/audio. Human review remains required.
