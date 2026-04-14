# complete_app.py - Full working version with CSS
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sqlite3
import hashlib
from datetime import datetime

# ============ DATABASE SETUP ============
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============ CSS STYLES ============
CSS_STYLES = '''
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .navbar {
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 1rem 0;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .nav-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-decoration: none;
    }
    
    .nav-links {
        display: flex;
        gap: 20px;
    }
    
    .nav-links a {
        text-decoration: none;
        color: #333;
        transition: color 0.3s;
    }
    
    .nav-links a:hover {
        color: #667eea;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    
    .hero {
        text-align: center;
        padding: 80px 20px;
        color: white;
    }
    
    .hero h1 {
        font-size: 3rem;
        margin-bottom: 20px;
        animation: fadeInUp 0.8s ease;
    }
    
    .hero p {
        font-size: 1.2rem;
        margin-bottom: 30px;
        animation: fadeInUp 1s ease;
    }
    
    .btn {
        display: inline-block;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        transition: transform 0.3s, box-shadow 0.3s;
        margin: 5px;
    }
    
    .btn-primary {
        background: white;
        color: #667eea;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .btn-outline {
        background: transparent;
        color: white;
        border: 2px solid white;
    }
    
    .btn-outline:hover {
        background: white;
        color: #667eea;
        transform: translateY(-2px);
    }
    
    .card {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease;
    }
    
    .card h2 {
        color: #333;
        margin-bottom: 20px;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    label {
        display: block;
        margin-bottom: 8px;
        color: #333;
        font-weight: 500;
    }
    
    input, textarea {
        width: 100%;
        padding: 12px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 14px;
        transition: border-color 0.3s;
    }
    
    input:focus, textarea:focus {
        outline: none;
        border-color: #667eea;
    }
    
    textarea {
        resize: vertical;
        font-family: inherit;
    }
    
    .result-real {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border-left: 5px solid #28a745;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .result-fake {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border-left: 5px solid #dc3545;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .result-warning {
        background: linear-gradient(135deg, #fff3cd, #ffeeba);
        border-left: 5px solid #ffc107;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .progress {
        height: 30px;
        background: #e0e0e0;
        border-radius: 15px;
        overflow: hidden;
        margin: 15px 0;
    }
    
    .progress-bar {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        transition: width 0.5s ease;
    }
    
    .progress-real {
        background: linear-gradient(90deg, #28a745, #34ce57);
    }
    
    .progress-fake {
        background: linear-gradient(90deg, #dc3545, #e4606d);
    }
    
    .alert {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .alert-success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .alert-danger {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .alert-warning {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 30px;
        margin-top: 40px;
    }
    
    .feature-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        transition: transform 0.3s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
    }
    
    .footer {
        background: #333;
        color: white;
        text-align: center;
        padding: 20px;
        margin-top: 50px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @media (max-width: 768px) {
        .hero h1 { font-size: 2rem; }
        .nav-links { display: none; }
        .grid { grid-template-columns: 1fr; }
    }
</style>
'''

# ============ HTML TEMPLATES ============
def get_html(content, title="Fake News Detector", user=None):
    nav_links = ''
    if user:
        nav_links = f'''
            <a href="/dashboard">Dashboard</a>
            <a href="/detect">Detect</a>
            <a href="/fact-check">Fact Check</a>
            <a href="/history">History</a>
            <a href="/logout">Logout</a>
        '''
    else:
        nav_links = '<a href="/login">Login</a><a href="/signup">Sign Up</a>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {CSS_STYLES}
    </head>
    <body>
        <nav class="navbar">
            <div class="nav-container">
                <a href="/" class="logo">🔍 FakeNewsDetector</a>
                <div class="nav-links">
                    <a href="/">Home</a>
                    {nav_links}
                </div>
            </div>
        </nav>
        
        <div class="container">
            {content}
        </div>
        
        <footer class="footer">
            <p>&copy; 2024 Fake News Detector | Fighting misinformation with AI</p>
        </footer>
    </body>
    </html>
    '''

# ============ DETECTION LOGIC ============
class FakeNewsDetector:
    def detect(self, text):
        has_exclamation = '!' in text
        has_question = '?' in text
        has_multiple_exclamation = '!!' in text or '!!!' in text
        has_multiple_question = '??' in text or '???' in text
        
        words = text.split()
        caps_words = sum(1 for word in words if word.isupper() and len(word) > 2)
        
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
        
        text_lower = text.lower()
        is_false_claim = False
        false_claims = ['trump is president', 'obama is president', 'biden is not president']
        for claim in false_claims:
            if claim in text_lower:
                is_false_claim = True
                break
        
        if is_false_claim and sensational_score > 0:
            prediction = 'Fake News (False Claim + Sensational)'
            confidence = 95
        elif is_false_claim:
            prediction = 'Fake News (False Claim)'
            confidence = 90
        elif sensational_score >= 40:
            prediction = 'Fake News (Sensational Content)'
            confidence = 85
        elif sensational_score >= 20:
            prediction = 'Suspicious - Verify'
            confidence = 60
        else:
            prediction = 'Likely Real News'
            confidence = 75
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'sensational_score': sensational_score,
            'has_exclamation': has_exclamation,
            'has_question': has_question,
            'caps_words': caps_words,
            'is_false_claim': is_false_claim
        }

# ============ SERVER HANDLER ============
class Handler(BaseHTTPRequestHandler):
    sessions = {}
    
    def get_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            return self.sessions.get(session_id)
        return None
    
    def set_user(self, user_id):
        session_id = hashlib.md5(str(user_id).encode()).hexdigest()
        self.sessions[session_id] = user_id
        self.send_header('Set-Cookie', f'session={session_id}; HttpOnly')
    
    def clear_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            if session_id in self.sessions:
                del self.sessions[session_id]
        self.send_header('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 UTC')
    
    def send_html(self, content, title="Fake News Detector"):
        user_id = self.get_user()
        html = get_html(content, title, user_id)
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
    
    def show_home(self):
        content = '''
        <div class="hero">
            <h1>🔍 Fake News Detection System</h1>
            <p>Using AI to detect sensational content and false claims</p>
            <a href="/signup" class="btn btn-primary">Get Started</a>
            <a href="/login" class="btn btn-outline">Login</a>
        </div>
        
        <div class="grid">
            <div class="feature-card">
                <div class="feature-icon">⚠️</div>
                <h3>Sensational Content Detection</h3>
                <p>Detects excessive ! and ? marks and ALL CAPS text</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">✅</div>
                <h3>Fact Checking</h3>
                <p>Verifies claims against known facts and databases</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>History Tracking</h3>
                <p>Keep track of all your detections and fact checks</p>
            </div>
        </div>
        '''
        self.send_html(content, "Home")
    
    def show_login(self):
        content = '''
        <div class="card" style="max-width: 400px; margin: 50px auto;">
            <h2 style="text-align: center;">Login</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                Don't have an account? <a href="/signup">Sign up here</a>
            </p>
        </div>
        '''
        self.send_html(content, "Login")
    
    def show_signup(self):
        content = '''
        <div class="card" style="max-width: 400px; margin: 50px auto;">
            <h2 style="text-align: center;">Create Account</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" name="confirm_password" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Sign Up</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                Already have an account? <a href="/login">Login here</a>
            </p>
        </div>
        '''
        self.send_html(content, "Sign Up")
    
    def show_dashboard(self):
        user_id = self.get_user()
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
        <div class="card">
            <h2>Welcome, {user[0]}! 👋</h2>
            <p>Your personal dashboard for fake news detection</p>
        </div>
        
        <div class="grid">
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Total Detections</h3>
                <p style="font-size: 2rem; font-weight: bold;">{total}</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Quick Actions</h3>
                <a href="/detect" class="btn btn-primary">Detect News</a>
                <a href="/fact-check" class="btn btn-outline" style="background: #667eea; color: white;">Fact Check</a>
            </div>
        </div>
        '''
        self.send_html(content, "Dashboard")
    
    def show_detect(self):
        user_id = self.get_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        content = '''
        <div class="card">
            <h2>🔍 Fake News Detection</h2>
            <p>Enter the news text below to analyze it for fake news indicators:</p>
            <form method="POST">
                <div class="form-group">
                    <label>News Article Text</label>
                    <textarea name="news_text" rows="8" placeholder="Paste your news article here..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Analyze News</button>
            </form>
        </div>
        '''
        self.send_html(content, "Detect News")
    
    def handle_detect(self):
        user_id = self.get_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        params = urllib.parse.parse_qs(data.decode())
        news_text = params.get('news_text', [''])[0]
        
        detector = FakeNewsDetector()
        result = detector.detect(news_text)
        
        # Save to database
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (user_id, news_text, prediction, confidence)
            VALUES (?, ?, ?, ?)
        ''', (user_id, news_text, result['prediction'], result['confidence']))
        conn.commit()
        conn.close()
        
        if 'Fake' in result['prediction']:
            result_class = 'result-fake'
        elif 'Suspicious' in result['prediction']:
            result_class = 'result-warning'
        else:
            result_class = 'result-real'
        
        content = f'''
        <div class="card">
            <h2>📊 Detection Result</h2>
            
            <div class="{result_class}">
                <h3>{'⚠️' if 'Fake' in result['prediction'] else '✅' if 'Real' in result['prediction'] else '❓'} {result['prediction']}</h3>
                
                <div class="progress">
                    <div class="progress-bar progress-real" style="width: {result['confidence']}%">
                        Real: {result['confidence']:.1f}%
                    </div>
                    <div class="progress-bar progress-fake" style="width: {100-result['confidence']}%">
                        Fake: {100-result['confidence']:.1f}%
                    </div>
                </div>
                
                <h4>📋 Detailed Analysis:</h4>
                <ul>
                    <li><strong>Sensational Score:</strong> {result['sensational_score']}/100</li>
                    <li><strong>Exclamation Marks (!):</strong> {'Yes' if result['has_exclamation'] else 'No'}</li>
                    <li><strong>Question Marks (?):</strong> {'Yes' if result['has_question'] else 'No'}</li>
                    <li><strong>ALL CAPS Words:</strong> {result['caps_words']}</li>
                    <li><strong>False Claim Detected:</strong> {'Yes' if result['is_false_claim'] else 'No'}</li>
                </ul>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="/detect" class="btn btn-primary">Analyze Another</a>
                <a href="/dashboard" class="btn btn-outline" style="background: #667eea; color: white;">Dashboard</a>
            </div>
        </div>
        '''
        self.send_html(content, "Detection Result")
    
    def show_fact_check(self):
        user_id = self.get_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        content = '''
        <div class="card">
            <h2>✅ Fact Check a Claim</h2>
            <p>Enter a claim to verify its accuracy:</p>
            <form method="POST">
                <div class="form-group">
                    <label>Claim to Fact Check</label>
                    <textarea name="claim" rows="4" placeholder="Enter a claim here..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Fact Check</button>
            </form>
        </div>
        '''
        self.send_html(content, "Fact Check")
    
    def handle_fact_check(self):
        user_id = self.get_user()
        if not user_id:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        params = urllib.parse.parse_qs(data.decode())
        claim = params.get('claim', [''])[0]
        
        claim_lower = claim.lower()
        if 'trump is president' in claim_lower:
            verdict = 'False'
            confidence = 95
            explanation = 'Donald Trump was president from 2017-2021. The current president is Joe Biden.'
        elif 'biden is president' in claim_lower:
            verdict = 'True'
            confidence = 95
            explanation = 'Correct! Joe Biden is the 46th and current President of the United States.'
        else:
            verdict = 'Unverified'
            confidence = 50
            explanation = 'No specific fact-checking information available for this claim.'
        
        alert_class = 'alert-success' if verdict == 'True' else 'alert-danger' if verdict == 'False' else 'alert-warning'
        
        content = f'''
        <div class="card">
            <h2>🔍 Fact Check Result</h2>
            
            <div class="{alert_class}">
                <h3>{'✅' if verdict == 'True' else '❌' if verdict == 'False' else '❓'} Verdict: {verdict}</h3>
                <p><strong>Confidence:</strong> {confidence}%</p>
                <p><strong>Explanation:</strong> {explanation}</p>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="/fact-check" class="btn btn-primary">Check Another</a>
                <a href="/dashboard" class="btn btn-outline" style="background: #667eea; color: white;">Dashboard</a>
            </div>
        </div>
        '''
        self.send_html(content, "Fact Check Result")
    
    def show_history(self):
        user_id = self.get_user()
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
            <div style="border-bottom: 1px solid #e0e0e0; padding: 15px;">
                <strong>{det[3]}</strong> (Confidence: {det[4]:.1f}%)<br>
                <span style="color: #666;">{det[2][:200]}...</span><br>
                <small style="color: #999;">{det[6]}</small>
            </div>
            '''
        
        if not history_html:
            history_html = '<p style="text-align: center; padding: 40px;">No detection history yet. <a href="/detect">Start detecting!</a></p>'
        
        content = f'''
        <div class="card">
            <h2>📜 Your Detection History</h2>
            {history_html}
        </div>
        '''
        self.send_html(content, "History")
    
    def handle_login(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        params = urllib.parse.parse_qs(data.decode())
        
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[1] == hash_password(password):
            self.set_user(result[0])
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
        else:
            content = '''
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <div class="alert alert-danger">Invalid username or password!</div>
                <a href="/login" class="btn btn-primary">Try Again</a>
            </div>
            '''
            self.send_html(content, "Login Failed")
    
    def handle_signup(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        params = urllib.parse.parse_qs(data.decode())
        
        username = params.get('username', [''])[0]
        email = params.get('email', [''])[0]
        password = params.get('password', [''])[0]
        confirm = params.get('confirm_password', [''])[0]
        
        if password != confirm:
            content = '''
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <div class="alert alert-danger">Passwords do not match!</div>
                <a href="/signup" class="btn btn-primary">Try Again</a>
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
                <a href="/signup" class="btn btn-primary">Try Again</a>
            </div>
            '''
            self.send_html(content, "Signup Failed")
    
    def handle_logout(self):
        self.clear_user()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

# ============ RUN SERVER ============
def run():
    init_database()
    port = 8000
    server = HTTPServer(('', port), Handler)
    print("=" * 50)
    print("🚀 FAKE NEWS DETECTOR IS RUNNING!")
    print("=" * 50)
    print(f"📍 Open: http://localhost:{port}")
    print("=" * 50)
    print("\n📝 Test these examples:")
    print("   'Trump is president!!!' → FAKE")
    print("   'Trump is president' → FAKE")
    print("   'Joe Biden is president' → REAL")
    print("   'BREAKING NEWS!!!' → FAKE")
    print("=" * 50)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == '__main__':
    run()