# simple_app.py - COMPLETE WORKING VERSION
import sqlite3
import hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os

# Simple Fake News Detector
class SimpleFakeNewsDetector:
    def __init__(self):
        self.fake_keywords = [
            'miracle', 'instant', 'secret', 'shocking', 'government hiding',
            'conspiracy', 'cover up', 'they don\'t want you to know',
            'breaking', 'urgent', 'amazing', 'incredible', 'unbelievable',
            'shock', 'scandal', 'exposed', 'revealed', 'truth about'
        ]
        self.real_keywords = [
            'study shows', 'research indicates', 'according to', 'scientists say',
            'evidence suggests', 'peer-reviewed', 'official statement'
        ]
    
    def detect(self, text):
        text_lower = text.lower()
        
        # Check for sensational symbols
        has_exclamation = '!' in text
        has_question = '?' in text
        has_multiple_exclamation = '!!' in text
        has_multiple_question = '??' in text
        
        # Check for ALL CAPS
        words = text.split()
        caps_words = sum(1 for word in words if word.isupper() and len(word) > 2)
        
        # Calculate sensational score
        sensational_score = 0
        if has_exclamation:
            sensational_score += 20
        if has_question:
            sensational_score += 15
        if has_multiple_exclamation:
            sensational_score += 25
        if has_multiple_question:
            sensational_score += 20
        if caps_words > 2:
            sensational_score += min(caps_words * 5, 30)
        
        # Check if factually false
        is_false_claim = False
        false_claims = ['trump is president', 'obama is president', 'biden is not president', 'earth is flat']
        for claim in false_claims:
            if claim in text_lower:
                is_false_claim = True
                break
        
        # Determine prediction
        if is_false_claim and sensational_score > 0:
            prediction = 'Fake (False Claim + Sensational)'
            confidence = 95
        elif is_false_claim:
            prediction = 'Fake (False Claim)'
            confidence = 90
        elif sensational_score >= 40:
            prediction = 'Fake (Sensational Content)'
            confidence = 85
        elif sensational_score >= 20:
            prediction = 'Suspicious - Verify'
            confidence = 60
        elif sensational_score == 0:
            prediction = 'Likely Real'
            confidence = 75
        else:
            prediction = 'Real'
            confidence = 70
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'fake_probability': (100 - confidence) / 100,
            'real_probability': confidence / 100,
            'sensational_score': sensational_score,
            'has_exclamation': has_exclamation,
            'has_question': has_question,
            'caps_words': caps_words
        }

# Database setup
def init_database():
    conn = sqlite3.connect('fake_news.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            news_text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            fake_probability REAL,
            real_probability REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            claim TEXT NOT NULL,
            verdict TEXT NOT NULL,
            confidence REAL NOT NULL,
            sources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Session management
sessions = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
        .header {{ background: #667eea; color: white; padding: 15px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .nav {{ display: flex; justify-content: space-between; align-items: center; }}
        .nav a {{ color: white; text-decoration: none; margin-left: 20px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; }}
        .btn-primary {{ background: #667eea; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        input, textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .result-real {{ background: #d4edda; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .result-fake {{ background: #f8d7da; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .result-warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .alert {{ padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        .alert-success {{ background: #d4edda; color: #155724; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; }}
        footer {{ background: #333; color: white; text-align: center; padding: 15px; margin-top: 50px; }}
        .progress {{ height: 30px; background: #e0e0e0; border-radius: 5px; overflow: hidden; margin: 10px 0; }}
        .progress-bar {{ height: 100%; display: flex; align-items: center; justify-content: center; color: white; }}
        .progress-real {{ background: #28a745; }}
        .progress-fake {{ background: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <div class="nav">
                <h2>🔍 FakeNewsDetector</h2>
                <div>
                    <a href="/">Home</a>
                    {nav_links}
                </div>
            </div>
        </div>
    </div>
    <div class="container">
        {content}
    </div>
    <footer>
        <div class="container">
            <p>&copy; 2024 Fake News Detector</p>
        </div>
    </footer>
</body>
</html>
'''

class RequestHandler(BaseHTTPRequestHandler):
    
    def get_session_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            return sessions.get(session_id)
        return None
    
    def set_session(self, user_id):
        session_id = hashlib.md5(str(user_id).encode()).hexdigest()
        sessions[session_id] = user_id
        self.send_header('Set-Cookie', f'session={session_id}; HttpOnly')
    
    def clear_session(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            if session_id in sessions:
                del sessions[session_id]
        self.send_header('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 UTC')
    
    def send_html(self, content, title="Fake News Detector"):
        user_id = self.get_session_user()
        nav_links = ''
        if user_id:
            nav_links = '<a href="/dashboard">Dashboard</a><a href="/detect">Detect</a><a href="/fact-check">Fact Check</a><a href="/history">History</a><a href="/logout">Logout</a>'
        else:
            nav_links = '<a href="/login">Login</a><a href="/signup">Sign Up</a>'
        
        html = HTML_TEMPLATE.format(title=title, content=content, nav_links=nav_links)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_GET(self):
        if self.path == '/':
            self.show_home()
        elif self.path == '/login':
            self.show_login()
        elif self.path == '/signup':
            self.show_signup()
        elif self.path == '/dashboard':
            self.show_dashboard()
        elif self.path == '/detect':
            self.show_detect()
        elif self.path == '/fact-check':
            self.show_fact_check()
        elif self.path == '/history':
            self.show_history()
        elif self.path == '/logout':
            self.handle_logout()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/login':
            self.handle_login()
        elif self.path == '/signup':
            self.handle_signup()
        elif self.path == '/detect':
            self.handle_detect()
        elif self.path == '/fact-check':
            self.handle_fact_check()
        else:
            self.send_error(404)
    
    def show_home(self):
        content = '''
        <div style="text-align: center; padding: 50px;">
            <h1>Fake News Detection System</h1>
            <p>Detect sensational content and false claims</p>
            <a href="/signup" class="btn btn-primary">Get Started</a>
            <a href="/login" class="btn">Login</a>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 40px;">
            <div class="card">
                <h3>⚠️ Sensational Content</h3>
                <p>Detects excessive ! and ? marks and ALL CAPS text</p>
            </div>
            <div class="card">
                <h3>✅ Fact Checking</h3>
                <p>Verifies claims against known facts</p>
            </div>
            <div class="card">
                <h3>📊 History</h3>
                <p>Track all your detections</p>
            </div>
        </div>
        '''
        self.send_html(content, "Home")
    
    def show_login(self):
        content = '''
        <div class="card" style="max-width: 400px; margin: 50px auto;">
            <h2>Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">No account? <a href="/signup">Sign up</a></p>
        </div>
        '''
        self.send_html(content, "Login")
    
    def show_signup(self):
        content = '''
        <div class="card" style="max-width: 400px; margin: 50px auto;">
            <h2>Sign Up</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <input type="password" name="confirm_password" placeholder="Confirm Password" required>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Create Account</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">Already have an account? <a href="/login">Login</a></p>
        </div>
        '''
        self.send_html(content, "Sign Up")
    
    def show_dashboard(self):
        user_id = self.get_session_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM detections WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()[0]
        conn.close()
        
        content = f'''
        <h1>Welcome, {user[0]}!</h1>
        <div class="card">
            <h3>Statistics</h3>
            <p>Total Detections: {total}</p>
            <a href="/detect" class="btn btn-primary">Detect News</a>
            <a href="/fact-check" class="btn">Fact Check</a>
        </div>
        '''
        self.send_html(content, "Dashboard")
    
    def show_detect(self):
        user_id = self.get_session_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        content = '''
        <div class="card">
            <h2>Fake News Detection</h2>
            <p>Enter text to analyze:</p>
            <form method="POST">
                <textarea name="news_text" rows="6" placeholder="Enter news text here..."></textarea>
                <button type="submit" class="btn btn-primary">Analyze</button>
            </form>
        </div>
        '''
        self.send_html(content, "Detect News")
    
    def handle_detect(self):
        user_id = self.get_session_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(post_data.decode())
        news_text = params.get('news_text', [''])[0]
        
        detector = SimpleFakeNewsDetector()
        result = detector.detect(news_text)
        
        # Save to database
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (user_id, news_text, prediction, confidence, fake_probability, real_probability)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, news_text, result['prediction'], result['confidence'], 
              result['fake_probability'], result['real_probability']))
        conn.commit()
        conn.close()
        
        # Determine result class
        if 'Fake' in result['prediction']:
            result_class = 'result-fake'
        elif 'Suspicious' in result['prediction']:
            result_class = 'result-warning'
        else:
            result_class = 'result-real'
        
        content = f'''
        <div class="card">
            <h2>Detection Result</h2>
            <div class="{result_class}">
                <h3>Prediction: {result['prediction']}</h3>
                <p>Confidence: {result['confidence']:.1f}%</p>
                <div class="progress">
                    <div class="progress-bar progress-real" style="width: {result['confidence']}%">
                        Real: {result['confidence']:.1f}%
                    </div>
                    <div class="progress-bar progress-fake" style="width: {100-result['confidence']}%">
                        Fake: {100-result['confidence']:.1f}%
                    </div>
                </div>
                <h4>Analysis:</h4>
                <ul>
                    <li>Sensational Score: {result['sensational_score']}/100</li>
                    <li>Exclamation Marks: {'Yes' if result['has_exclamation'] else 'No'}</li>
                    <li>Question Marks: {'Yes' if result['has_question'] else 'No'}</li>
                    <li>ALL CAPS Words: {result['caps_words']}</li>
                </ul>
            </div>
            <div style="margin-top: 20px;">
                <a href="/detect" class="btn btn-primary">Analyze Another</a>
                <a href="/dashboard" class="btn">Dashboard</a>
            </div>
        </div>
        '''
        self.send_html(content, "Detection Result")
    
    def show_fact_check(self):
        user_id = self.get_session_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        content = '''
        <div class="card">
            <h2>Fact Check</h2>
            <form method="POST">
                <textarea name="claim" rows="4" placeholder="Enter a claim to fact-check..."></textarea>
                <button type="submit" class="btn btn-primary">Fact Check</button>
            </form>
        </div>
        '''
        self.send_html(content, "Fact Check")
    
    def handle_fact_check(self):
        user_id = self.get_session_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(post_data.decode())
        claim = params.get('claim', [''])[0]
        
        # Simple fact checking
        claim_lower = claim.lower()
        if 'trump is president' in claim_lower:
            verdict = 'False'
            confidence = 95
            explanation = 'Donald Trump was president from 2017-2021. Joe Biden is the current president.'
        elif 'biden is president' in claim_lower:
            verdict = 'True'
            confidence = 95
            explanation = 'Correct! Joe Biden is the current US President.'
        else:
            verdict = 'Unverified'
            confidence = 50
            explanation = 'No specific information available.'
        
        # Save to database
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fact_checks (user_id, claim, verdict, confidence, sources)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, claim, verdict, confidence, '[]'))
        conn.commit()
        conn.close()
        
        alert_class = 'alert-success' if verdict == 'True' else 'alert-danger' if verdict == 'False' else 'alert'
        
        content = f'''
        <div class="card">
            <h2>Fact Check Result</h2>
            <div class="{alert_class}">
                <h3>Verdict: {verdict}</h3>
                <p>Confidence: {confidence}%</p>
                <p>{explanation}</p>
            </div>
            <div style="margin-top: 20px;">
                <a href="/fact-check" class="btn btn-primary">Check Another</a>
                <a href="/dashboard" class="btn">Dashboard</a>
            </div>
        </div>
        '''
        self.send_html(content, "Fact Check Result")
    
    def show_history(self):
        user_id = self.get_session_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM detections WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        detections = cursor.fetchall()
        conn.close()
        
        history_html = ''
        for det in detections:
            history_html += f'''
            <div style="border-bottom: 1px solid #ddd; padding: 10px;">
                <strong>{det[3]}</strong> - {det[2][:100]}...<br>
                <small>{det[7]}</small>
            </div>
            '''
        
        if not history_html:
            history_html = '<p>No history yet.</p>'
        
        content = f'''
        <h1>History</h1>
        <div class="card">
            {history_html}
        </div>
        '''
        self.send_html(content, "History")
    
    def handle_login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(post_data.decode())
        
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[1] == hash_password(password):
            self.set_session(result[0])
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
        else:
            content = '''
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <div class="alert alert-danger">Invalid username or password!</div>
                <a href="/login" class="btn">Try Again</a>
            </div>
            '''
            self.send_html(content, "Login Failed")
    
    def handle_signup(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(post_data.decode())
        
        username = params.get('username', [''])[0]
        email = params.get('email', [''])[0]
        password = params.get('password', [''])[0]
        confirm = params.get('confirm_password', [''])[0]
        
        if password != confirm:
            content = '''
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <div class="alert alert-danger">Passwords do not match!</div>
                <a href="/signup" class="btn">Try Again</a>
            </div>
            '''
            self.send_html(content, "Signup Failed")
            return
        
        try:
            conn = sqlite3.connect('fake_news.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, hash_password(password)))
            conn.commit()
            conn.close()
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
        except sqlite3.IntegrityError:
            content = '''
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <div class="alert alert-danger">Username or email already exists!</div>
                <a href="/signup" class="btn">Try Again</a>
            </div>
            '''
            self.send_html(content, "Signup Failed")
    
    def handle_logout(self):
        self.clear_session()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def run_server():
    init_database()
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("=" * 50)
    print("Server Running!")
    print("=" * 50)
    print("Open: http://localhost:8000")
    print("=" * 50)
    print("\nTest these:")
    print("  'Trump is president!!!' → FAKE")
    print("  'Joe Biden is president' → REAL")
    print("=" * 50)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == '__main__':
    run_server()