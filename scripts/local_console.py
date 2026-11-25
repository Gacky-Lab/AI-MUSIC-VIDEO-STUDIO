"""Loopback-only console for the synthetic integration runner; no upload or paid APIs."""
import argparse
import json
import secrets
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML="""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gacky-Lab local console</title>
<style>body{font:17px system-ui;background:#101b2d;color:#e7f2fa;max-width:860px;margin:45px auto;padding:0 20px}button{background:#7ce1c8;color:#101b2d;padding:12px 20px;border:0;border-radius:8px;font-weight:bold}button:disabled{opacity:.45}pre{white-space:pre-wrap;background:#1d3348;padding:18px;border-radius:8px}h1{color:#fff}</style>
<h1>Gacky-Lab / Local integration console</h1><p>Original synthetic fixture only. No account access, uploads, paid generation, or singing synthesis.</p><button id="start">Run synthetic verification</button><p id="status">Idle</p><pre id="evidence">No run yet.</pre>
<script>
const token=__TOKEN__;const start=document.getElementById('start'),status=document.getElementById('status'),evidence=document.getElementById('evidence');
async function refresh(){try{const r=await fetch('/status',{cache:'no-store'});const x=await r.json();status.textContent=x.status;start.disabled=x.status==='RUNNING';evidence.textContent=JSON.stringify(x.report||{run_id:x.run_id||null},null,2)}catch(e){status.textContent='Local server unavailable'}}
start.onclick=async()=>{start.disabled=true;try{await fetch('/run',{method:'POST',headers:{'X-Local-Token':token}})}finally{await refresh()}};
refresh();setInterval(refresh,1500);
</script></html>"""

class Controller:
    def __init__(self,upstream,output_root):
        self.upstream=Path(upstream).resolve()
        self.root=Path(output_root).resolve()
        self.root.mkdir(parents=True,exist_ok=True)
        self.lock=threading.Lock()
        self.status="IDLE"; self.run_id=None
    def snapshot(self):
        with self.lock:
            status,run_id=self.status,self.run_id
        report=None
        if run_id:
            p=self.root/run_id/"report.json"
            try:
                if p.stat().st_size<=1024*1024: report=json.loads(p.read_text(encoding="utf-8"))
            except (OSError,ValueError): pass
        return {"status":status,"run_id":run_id,"report":report}
    def start(self):
        with self.lock:
            if self.status=="RUNNING": return False
            self.run_id=uuid.uuid4().hex; self.status="RUNNING"; run_id=self.run_id
        threading.Thread(target=self._run,args=(run_id,),daemon=True).start()
        return True
    def _run(self,run_id):
        status="FAIL"
        try:
            cmd=[sys.executable,str(ROOT/"scripts/integration_runner.py"),"--upstream",str(self.upstream),"--output",str(self.root/run_id)]
            with (self.root/(run_id+".log")).open("x",encoding="utf-8") as log:
                r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=240,check=False)
            status="PASS" if r.returncode==0 else "FAIL"
        except (OSError,subprocess.SubprocessError): pass
        finally:
            with self.lock: self.status=status

def handler(controller,token,host):
    class Handler(BaseHTTPRequestHandler):
        def respond(self,status,body,kind="application/json; charset=utf-8"):
            self.send_response(status);self.send_header("Content-Type",kind)
            self.send_header("Content-Length",str(len(body)));self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers();self.wfile.write(body)
        def valid_host(self): return self.headers.get("Host")==host
        def do_GET(self):
            if not self.valid_host(): return self.respond(403,b'{}')
            if self.path=="/": return self.respond(200,HTML.replace("__TOKEN__",json.dumps(token)).encode(),"text/html; charset=utf-8")
            if self.path=="/status": return self.respond(200,json.dumps(controller.snapshot(),ensure_ascii=False).encode())
            return self.respond(404,b'{}')
        def do_POST(self):
            if not self.valid_host() or self.headers.get("Origin") not in (None,"http://"+host) or not secrets.compare_digest(self.headers.get("X-Local-Token",""),token):
                return self.respond(403,b'{}')
            if self.path!="/run": return self.respond(404,b'{}')
            if self.headers.get("Content-Length","0")!="0" or self.headers.get("Transfer-Encoding"):
                return self.respond(400,b'{}')
            return self.respond(202 if controller.start() else 409,b'{}')
        def log_message(self,*args): pass
    return Handler

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True);p.add_argument("--output-root",type=Path,required=True);p.add_argument("--port",type=int,default=8765)
    a=p.parse_args()
    if not 1024<=a.port<=65535: p.error("port must be 1024..65535")
    host=f"127.0.0.1:{a.port}"
    with ThreadingHTTPServer(("127.0.0.1",a.port),handler(Controller(a.upstream,a.output_root),secrets.token_hex(32),host)) as server:
        print("Open http://"+host,flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
if __name__=="__main__": main()
