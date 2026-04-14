# minimal_app.py - SUPER SIMPLE VERSION
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Simple HTML pages
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h1>Login</h1>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Login</button>
    </form>
    <a href="/signup">Sign Up</a>
</body>
</html>
'''

SIGNUP_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Sign Up</title></head>
<body>
    <h1>Sign Up</h1>
    <form method="POST" action="/signup">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="email" name="email" placeholder="Email" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <input type="password" name="confirm" placeholder="Confirm Password" required><br><br>
        <button type="submit">Sign Up</button>
    </form>
    <a href="/login">Login</a>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <h1>Welcome to Dashboard!</h1>
    <p>You are logged in!</p>
    <a href="/detect">Detect News</a><br><br>
    <a href="/logout">Logout</a>
</body>
</html>
'''

DETECT_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Detect News</title></head>
<body>
    <h1>Fake News Detection</h1>
    <form method="POST" action="/detect">
        <textarea name="news_text" rows="5" cols="50" placeholder="Enter news text..."></textarea><br><br>
        <button type="submit">Analyze</button>
    </form>
    <a href="/dashboard">Back to Dashboard</a>
</body>
</html>
'''

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"GET request: {self.path}")
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Home</h1><a href="/login">Login</a> | <a href="/signup">Sign Up</a>')
            
        elif self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(LOGIN_PAGE.encode())
            
        elif self.path == '/signup':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(SIGNUP_PAGE.encode())
            
        elif self.path == '/dashboard':
            # Check if user is logged in (simplified - just check cookie)
            cookie = self.headers.get('Cookie', '')
            if 'logged_in' in cookie:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(DASHBOARD_PAGE.encode())
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                
        elif self.path == '/detect':
            cookie = self.headers.get('Cookie', '')
            if 'logged_in' in cookie:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(DETECT_PAGE.encode())
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                
        elif self.path == '/logout':
            self.send_response(302)
            self.send_header('Location', '/')
            self.send_header('Set-Cookie', 'logged_in=; expires=Thu, 01 Jan 1970 00:00:00 UTC')
            self.end_headers()
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def do_POST(self):
        print(f"POST request: {self.path}")
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(post_data.decode())
        
        if self.path == '/login':
            username = params.get('username', [''])[0]
            # Simple login - any username/password works
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.send_header('Set-Cookie', 'logged_in=true; HttpOnly')
            self.end_headers()
            
        elif self.path == '/signup':
            username = params.get('username', [''])[0]
            email = params.get('email', [''])[0]
            password = params.get('password', [''])[0]
            confirm = params.get('confirm', [''])[0]
            
            if password != confirm:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Error</h1><p>Passwords do not match!</p><a href="/signup">Try Again</a>')
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                
        elif self.path == '/detect':
            news_text = params.get('news_text', [''])[0]
            
            # Simple detection logic
            has_exclamation = '!' in news_text
            has_question = '?' in news_text
            has_caps = any(word.isupper() and len(word) > 2 for word in news_text.split())
            
            if has_exclamation or has_question or has_caps:
                result = "FAKE NEWS (Sensational Content Detected!)"
                confidence = 85
            else:
                result = "LIKELY REAL NEWS"
                confidence = 70
            
            # Show result
            html = f'''
            <!DOCTYPE html>
            <html>
            <head><title>Detection Result</title></head>
            <body>
                <h1>Detection Result</h1>
                <p><strong>Text analyzed:</strong> {news_text}</p>
                <p><strong>Result:</strong> {result}</p>
                <p><strong>Confidence:</strong> {confidence}%</p>
                <h3>Analysis:</h3>
                <ul>
                    <li>Exclamation marks: {'Yes' if has_exclamation else 'No'}</li>
                    <li>Question marks: {'Yes' if has_question else 'No'}</li>
                    <li>ALL CAPS words: {'Yes' if has_caps else 'No'}</li>
                </ul>
                <a href="/detect">Analyze Another</a><br>
                <a href="/dashboard">Back to Dashboard</a>
            </body>
            </html>
            '''
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHandler)
    print("=" * 50)
    print("SERVER IS RUNNING!")
    print("=" * 50)
    print(f"Open your browser and go to: http://localhost:{port}")
    print("=" * 50)
    print("\nWhat to do:")
    print("1. Click 'Sign Up' and create an account")
    print("2. Login with your account")
    print("3. Go to 'Detect News'")
    print("4. Test these examples:")
    print("   - 'Trump is president!!!' → FAKE")
    print("   - 'Trump is president' → REAL")
    print("   - 'Joe Biden is president' → REAL")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()