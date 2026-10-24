import unittest,threading,json,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from voltvar.server import Handler
from voltvar.cli import load_case
class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.url='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,path,payload,headers=None):return urllib.request.urlopen(urllib.request.Request(self.url+path,payload,headers or {'Content-Type':'application/json'}))
    def test_static_assets(self):
        for path in ['/','/app.js','/style.css']:
            with urllib.request.urlopen(self.url+path) as r:self.assertEqual(r.status,200);self.assertIn("default-src 'self'",r.headers['Content-Security-Policy'])
    def test_example_list(self):
        with urllib.request.urlopen(self.url+'/api/examples') as r:self.assertIn('industrial',json.load(r))
    def test_study_roundtrip(self):
        with self.request('/api/study',json.dumps({'network':load_case('example:industrial')}).encode()) as r:self.assertIn('provenance',json.load(r))
    def test_import(self):
        with self.request('/api/import',json.dumps({'text':json.dumps(load_case('example:industrial'))}).encode()) as r:self.assertIsInstance(json.load(r),dict)
    def test_origin_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/study',b'{}',{'Content-Type':'application/json','Origin':'https://elsewhere.invalid'})
        self.assertEqual(e.exception.code,403)
    def test_bad_json(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/study',b'{')
        self.assertEqual(e.exception.code,400)
    def test_unknown_asset(self):
        with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(self.url+'/missing')
        self.assertEqual(e.exception.code,404)
    def test_wrong_content_type(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/study',b'{}',{'Content-Type':'text/plain'})
        self.assertEqual(e.exception.code,415)
