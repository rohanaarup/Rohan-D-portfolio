"""Serves ONLY the customised portfolio (../Portfolio) with caching disabled.

    python dev/serve.py            -> http://localhost:5000
    python dev/serve.py 5001       -> another port

Safety checks (this is what stops the original template from ever being served):
  * the folder is resolved from this file's location, never from the current directory;
  * index.html must contain the marker <meta name="site-source" content="rohan-portfolio-custom">;
  * the port must be free; otherwise it says what is already using it instead of silently
    letting an old server keep answering.
"""
import http.server, pathlib, socket, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "Portfolio"
MARKER = 'name="site-source" content="rohan-portfolio-custom"'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

index = ROOT / "index.html"
if not index.exists() or MARKER not in index.read_text(encoding="utf-8", errors="ignore"):
    sys.exit(f"REFUSING TO START: {index} is missing or is not the customised portfolio (marker not found).")

with socket.socket() as s:
    if s.connect_ex(("127.0.0.1", PORT)) == 0:
        who = ""
        try:
            who = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-NetTCPConnection -LocalPort {PORT} -State Listen | ForEach-Object {{ (Get-CimInstance Win32_Process -Filter \"ProcessId=$($_.OwningProcess)\").CommandLine }}) -join \"`n\""],
                capture_output=True, text=True, timeout=15).stdout.strip()
        except Exception:
            pass
        sys.exit(f"PORT {PORT} IS ALREADY IN USE by another server, which may be serving an old copy.\n{who}\nStop it, or run: python dev/serve.py {PORT + 1}")


class NoCache(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("X-Site-Source", "rohan-portfolio-custom")
        super().end_headers()


print(f"Serving {ROOT}\n  -> http://localhost:{PORT}   (Ctrl+C to stop)")
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), NoCache).serve_forever()
