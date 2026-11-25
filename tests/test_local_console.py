import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from scripts.local_console import handler

class Fake:
    def __init__(self): self.started=False
    def snapshot(self): return {"status":"IDLE"}
    def start(self):
        if self.started: return False
        self.started=True; return True

class ConsoleTests(unittest.TestCase):
    def test_loopback_routes(self):
        fake=Fake()
        server=ThreadingHTTPServer(("127.0.0.1",0),handler(fake,"secret","local.test"))
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        def request(method,path,headers=None):
            c=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=3)
            try:
                c.request(method,path,headers=headers or {}); r=c.getresponse(); return r.status,r.read()
            finally: c.close()
        try:
            self.assertEqual(request("GET","/status")[0],403)
            self.assertEqual(request("GET","/status",{"Host":"local.test"})[0],200)
            self.assertEqual(request("POST","/run",{"Host":"local.test"})[0],403)
            self.assertEqual(request("POST","/run",{"Host":"local.test","X-Local-Token":"secret","Origin":"http://evil.test"})[0],403)
            self.assertEqual(request("GET","/../private",{"Host":"local.test"})[0],404)
            self.assertEqual(request("POST","/run",{"Host":"local.test","X-Local-Token":"secret"})[0],202)
            self.assertEqual(request("POST","/run",{"Host":"local.test","X-Local-Token":"secret"})[0],409)
        finally: server.shutdown();server.server_close();thread.join()
