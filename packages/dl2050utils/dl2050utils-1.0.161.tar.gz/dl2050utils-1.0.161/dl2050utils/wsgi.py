import time
import datetime
import cgi
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class ServiceLog():
    def __init__(self, server_name='WSGI'):
        self.LEVELS = {1:'DEBUG', 2:'INFO', 2:'WARNING', 2:'ERROR', 2:'CRITICAL'}
        self.server_name = server_name
    def __call__(self, level, t, label='', label2='', msg=''):
        print(f'{self.server_name} - {datetime.datetime.now().isoformat()} - {self.LEVELS[level]} - {label} - {label2} - {t} - {msg}')

class Handler(BaseHTTPRequestHandler):
    
    def log_message(self, format, line, return_code, _):
        msg = f'{self.command} {self.client_address} {return_code}'
        self.LOG(2, time.time()-self.t0, label='WSGIServer', label2=self.path, msg=msg)

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
            res = cb(payload)
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
    def __init__(self, server_name, routes, startup, d={}, secret=None, host='', port=6000):
        self.routes,self.startup = routes,startup
        self.secret,self.host,self.port = secret, host,port
        self.LOG = ServiceLog(server_name)
        self.d = d
        d['LOG'] = self.LOG
        
    def run(self, host='', port=6000):
        try:
            if self.startup(self.d):
                return True
        except Exception as err:
            self.LOG(4, 0, label='WSGIServer', label2='STARTUP EXCEPTION', msg=str(err))
        Handler = HandlerFactory(self.routes, self.d)
        httpd = HTTPServer((host, port), Handler)
        self.LOG(2, 0, label='WSGIServer', label2='RUN', msg=f'MDB listenning on {self.port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
