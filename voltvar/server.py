from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import urlsplit,parse_qs
import json
from .cli import example_names,load_case
from .studies import run
from .model import validate

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,status,payload,kind='application/json'):
        data=json.dumps(payload,allow_nan=False).encode() if kind=='application/json' else payload
        self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(data)
    def do_GET(self):
        path=urlsplit(self.path)
        if path.path=='/api/examples':return self.reply(200,example_names())
        if path.path=='/api/example':
            try:return self.reply(200,load_case('example:'+parse_qs(path.query).get('name',[''])[0]))
            except ValueError as exc:return self.reply(400,{'error':str(exc)})
        assets={'/':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/style.css':('style.css','text/css')}
        if path.path not in assets:return self.reply(404,{'error':'Not found'})
        name,kind=assets[path.path];self.reply(200,files('voltvar').joinpath('web',name).read_bytes(),kind)
    def do_POST(self):
        path=urlsplit(self.path).path
        if path not in ['/api/study','/api/import']:return self.reply(404,{'error':'Not found'})
        if self.headers.get('Origin') and self.headers['Origin']!='http://'+self.headers.get('Host',''):return self.reply(403,{'error':'Cross-origin requests are not accepted'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=2000000:return self.reply(413,{'error':'Request size must be 1..2000000 bytes'})
            if self.headers.get_content_type()!='application/json':return self.reply(415,{'error':'Use application/json'})
            request=json.loads(self.rfile.read(length))
            if not isinstance(request,dict):raise ValueError('Request must be an object')
            if path=='/api/import':
                result=validate(json.loads(request['text']))
            else:result=run(request['network'],request.get('action','analyze'),request.get('options',{}))
            self.reply(200,result)
        except (ValueError,TypeError,KeyError,ArithmeticError,UnicodeError,IndexError) as exc:self.reply(400,{'error':str(exc)})

def serve(port=8772):
    if not 0<=port<=65535:raise ValueError('Invalid port')
    with ThreadingHTTPServer(('127.0.0.1',port),Handler) as server:
        print(f'voltvar workbench: http://127.0.0.1:{server.server_port}',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
