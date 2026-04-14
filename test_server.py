from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Server is working!</h1>')

print("Starting server on http://localhost:8888")
HTTPServer(('', 8888), TestHandler).serve_forever()