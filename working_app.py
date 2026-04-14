# working_app.py - SIMPLE BUT BEAUTIFUL
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sqlite3
import hashlib

# Database setup
conn = sqlite3.connect('users.db')
conn.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
conn.commit()
conn.close()

# HTML with CSS
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .nav {{
            background: white;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .nav-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
        }}
        .nav a {{
            color: #667eea;
            text-decoration: none;
            margin-left: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        input, textarea {{
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        button {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{
            background: #5a67d8;
        }}
        .result-real {{
            background: #d4edda;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #28a745;
        }}
        .result-fake {{
            background: #f8d7da;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #dc3545;
        }}
        .alert {{
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .alert-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        h1, h2 {{ margin-bottom: 20px; }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <div class="nav-content">
            <h2>🔍 FakeNewsDetector</h2>
            <div>
                <a href="/">Home</a>
                {nav_links}
            </div>
        </div>
    </div>
    <div class="container">
        <div class="card">
            {content}
        </div>
    </div>
</body>
</html>
'''

sessions = {}

class Handler(BaseHTTPRequestHandler):
    
    def get_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            sid = cookie.split('session=')[1].split(';')[0]
            return sessions.get(sid)
        return None
    
    def set_user(self, user_id):
        sid = hashlib.md5(str(user_id).encode()).hexdigest()
        sessions[sid] = user_id
        self.send_header('Set-Cookie', f'session={sid}')
    
    def clear_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            sid = cookie.split('session=')[1].split(';')[0]
            if sid in sessions:
                del sessions[sid]
        self.send_header('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 UTC')
    
    def render(self, content, title="Fake News Detector"):
        user = self.get_user()
        nav = ''
        if user:
            nav = '<a href="/dashboard">Dashboard</a><a href="/detect">Detect</a><a href="/logout">Logout</a>'
        else:
            nav = '<a href="/login">Login</a><a href="/signup">Sign Up</a>'
        
        html = HTML.format(title=title, content=content, nav_links=nav)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_GET(self):
        if self.path == '/':
            self.render('''
                <h1>Fake News Detection System</h1>
                <p>Detect sensational content and false claims</p>
                <a href="/signup" class="btn">Get Started</a>
                <a href="/login" class="btn" style="background:#999">Login</a>
            ''')
        
        elif self.path == '/login':
            self.render('''
                <h2>Login</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <p style="margin-top:20px">No account? <a href="/signup">Sign up</a></p>
            ''', "Login")
        
        elif self.path == '/signup':
            self.render('''
                <h2>Sign Up</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="email" name="email" placeholder="Email" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <input type="password" name="confirm" placeholder="Confirm Password" required>
                    <button type="submit">Sign Up</button>
                </form>
                <p style="margin-top:20px">Have an account? <a href="/login">Login</a></p>
            ''', "Sign Up")
        
        elif self.path == '/dashboard':
            if not self.get_user():
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            self.render('''
                <h2>Dashboard</h2>
                <p>Welcome to your dashboard!</p>
                <a href="/detect" class="btn">Detect News</a>
                <a href="/logout" class="btn" style="background:#dc3545">Logout</a>
            ''', "Dashboard")
        
        elif self.path == '/detect':
            if not self.get_user():
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            self.render('''
                <h2>Detect Fake News</h2>
                <form method="POST">
                    <textarea name="news_text" rows="6" placeholder="Enter news text here..."></textarea>
                    <button type="submit">Analyze</button>
                </form>
            ''', "Detect News")
        
        elif self.path == '/logout':
            self.clear_user()
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        params = urllib.parse.parse_qs(data.decode())
        
        if self.path == '/login':
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            hashed = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username=? AND password=?', (username, hashed))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                self.set_user(user[0])
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
            else:
                self.render('''
                    <div class="alert alert-error">Invalid username or password!</div>
                    <a href="/login" class="btn">Try Again</a>
                ''', "Login Failed")
        
        elif self.path == '/signup':
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            confirm = params.get('confirm', [''])[0]
            
            if password != confirm:
                self.render('<div class="alert alert-error">Passwords do not match!</div><a href="/signup" class="btn">Try Again</a>', "Signup Failed")
                return
            
            hashed = hashlib.sha256(password.encode()).hexdigest()
            
            try:
                conn = sqlite3.connect('users.db')
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
                conn.commit()
                conn.close()
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
            except:
                self.render('<div class="alert alert-error">Username already exists!</div><a href="/signup" class="btn">Try Again</a>', "Signup Failed")
        
        elif self.path == '/detect':
            if not self.get_user():
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            
            news_text = params.get('news_text', [''])[0]
            
            # Simple detection
            has_exclamation = '!' in news_text
            has_question = '?' in news_text
            has_caps = any(w.isupper() and len(w) > 2 for w in news_text.split())
            
            if has_exclamation or has_question or has_caps:
                result_class = 'result-fake'
                result_text = '⚠️ FAKE NEWS - Sensational Content Detected!'
                confidence = 85
            else:
                result_class = 'result-real'
                result_text = '✅ LIKELY REAL NEWS'
                confidence = 75
            
            self.render(f'''
                <h2>Analysis Result</h2>
                <div class="{result_class}">
                    <h3>{result_text}</h3>
                    <p><strong>Confidence:</strong> {confidence}%</p>
                    <p><strong>Text analyzed:</strong> "{news_text[:100]}"</p>
                    <ul>
                        <li>Exclamation marks: {'Yes' if has_exclamation else 'No'}</li>
                        <li>Question marks: {'Yes' if has_question else 'No'}</li>
                        <li>ALL CAPS: {'Yes' if has_caps else 'No'}</li>
                    </ul>
                </div>
                <a href="/detect" class="btn">Analyze Another</a>
                <a href="/dashboard" class="btn" style="background:#999">Dashboard</a>
            ''', "Detection Result")

def run():
    port = 8000
    server = HTTPServer(('', port), Handler)
    print("=" * 50)
    print("✅ SERVER RUNNING!")
    print("=" * 50)
    print(f"Open: http://localhost:{port}")
    print("=" * 50)
    print("\nTest these:")
    print("  'Trump is president!!!' → FAKE")
    print("  'Trump is president' → REAL")
    print("  'BREAKING NEWS!!!' → FAKE")
    print("=" * 50)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == '__main__':
    run()