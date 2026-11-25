# Local synthetic verification console

After preparing the exact upstream checkouts and installing requirements-integration.txt:

```sh
python scripts/local_console.py --upstream upstream --output-root out/console
```

Open http://127.0.0.1:8765. Click Run synthetic verification. Stage results and the evidence report update while the job runs. The server binds only to loopback, requires a per-process token for POST, checks Host and Origin, rejects file access and arbitrary input, and permits one active run. No remote accounts, file upload, paid generation, or automatic publication. Only run with trusted local checkouts; do not expose or proxy the server to a network. This console runs the contract pipeline, not the full Remotion renderer. Ctrl+C stops the HTTP server; do not terminate it mid-run if you need complete evidence.

The standalone HTML dashboard produced by the runner remains available without starting a server.
