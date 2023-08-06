import time
import cgi
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    
    def log_message(self, format, line, return_code, _):
        msg = f'{self.command} {self.client_address} {return_code}'
        t = self.t0 if hasattr(self, 't0') else 0
        self.LOG(2, time.time()-t, label='WSGIServer', label2=self.path, msg=msg)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    def do_GET(self):
        self.send_response(400)
        self.end_headers()

    def do_POST(self):
        self.t0 = time.time()
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype != 'application/json' or self.path not in self.routes:
            self.send_response(400)
            self.end_headers()
            return
        length = int(self.headers.get('content-length'))
        payload = json.loads(self.rfile.read(length))
        cb = self.routes[self.path]
        try:
            res = cb(self.d, payload)
            res = json.dumps(res)
            res = res.encode()
        except Exception as err:
            self.send_response(500)
            self.end_headers()
            return
        self._set_headers()
        self.wfile.write(res)

def HandlerFactory(routes, d):
    class ExtendedHandler(Handler):
        def __init__(self, *args, **kwargs):
            super(ExtendedHandler, self).__init__(*args, **kwargs)
    ExtendedHandler.routes = routes
    ExtendedHandler.d = d
    ExtendedHandler.LOG = d['LOG']
    return ExtendedHandler

class WSGIServer():
    def __init__(self, routes, startup, d={}, secret=None, host='', port=6000):
        self.routes,self.startup = routes,startup
        self.secret,self.host,self.port = secret, host,port
        self.d = d
        self.LOG = d['LOG']
        
    def run(self, host='', port=6000):
        try:
            if self.startup(self.d):
                return True
        except Exception as err:
            self.LOG(4, 0, label='WSGIServer', label2='STARTUP EXCEPTION', msg=str(err))
            raise RuntimeError('MDB STARTUP EXCEPTION')
        Handler = HandlerFactory(self.routes, self.d)
        httpd = HTTPServer((host, port), Handler)
        self.LOG(2, 0, label='WSGIServer', label2='RUN', msg=f'MDB listenning on {self.port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
