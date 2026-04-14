# fake_news_detector_fixed.py - Complete working version with fixed HTTP responses

import sqlite3
import hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import re

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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============ FAKE NEWS DETECTOR ============
class FakeNewsDetector:
    def __init__(self):
        self.false_claims = [
            'trump is president', 'obama is president', 'bush is president',
            'biden is not president', 'earth is flat', 'vaccines cause autism',
            '5g causes covid', 'government hiding aliens', 'election was stolen',
            'moon landing fake', 'climate change hoax'
        ]
    
    def detect(self, text):
        if not text or not text.strip():
            return {
                'prediction': 'Error - Empty Input',
                'confidence': 0,
                'fake_probability': 0.5,
                'real_probability': 0.5,
                'sensational_score': 0
            }
        
        text_lower = text.lower()
        
        # Check for sensational symbols
        has_exclamation = '!' in text
        has_question = '?' in text
        has_multiple_exclamation = '!!' in text or '!!!' in text
        has_multiple_question = '??' in text or '???' in text
        
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
        for claim in self.false_claims:
            if claim in text_lower:
                is_false_claim = True
                break
        
        # Determine prediction
        if is_false_claim and sensational_score >= 20:
            prediction = 'Fake News (False Claim + Sensational)'
            confidence = 95
            fake_prob = 0.95
            real_prob = 0.05
        elif is_false_claim:
            prediction = 'Fake News (False Claim)'
            confidence = 90
            fake_prob = 0.90
            real_prob = 0.10
        elif sensational_score >= 40:
            prediction = 'Fake News (Sensational Content)'
            confidence = min(70 + sensational_score/2, 95)
            fake_prob = confidence / 100
            real_prob = 1 - fake_prob
        elif sensational_score >= 20:
            prediction = 'Suspicious - Verify'
            confidence = 55
            fake_prob = 0.55
            real_prob = 0.45
        else:
            prediction = 'Likely Real News'
            confidence = 75
            fake_prob = 0.25
            real_prob = 0.75
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'fake_probability': fake_prob,
            'real_probability': real_prob,
            'sensational_score': sensational_score,
            'has_exclamation': has_exclamation,
            'has_question': has_question,
            'caps_words': caps_words,
            'is_false_claim': is_false_claim
        }

# ============ HTML/CSS ============
CSS_STYLES = '''
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
    .navbar { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1rem 0; position: sticky; top: 0; z-index: 100; }
    .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 1.5rem; font-weight: bold; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-decoration: none; }
    .nav-links { display: flex; gap: 20px; }
    .nav-links a { text-decoration: none; color: #333; transition: color 0.3s; }
    .nav-links a:hover { color: #667eea; }
    .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
    .hero { text-align: center; padding: 80px 20px; color: white; }
    .hero h1 { font-size: 3rem; margin-bottom: 20px; animation: fadeInUp 0.8s ease; }
    .hero p { font-size: 1.2rem; margin-bottom: 30px; animation: fadeInUp 1s ease; }
    .btn { display: inline-block; padding: 12px 30px; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: transform 0.3s, box-shadow 0.3s; margin: 5px; }
    .btn-primary { background: white; color: #667eea; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    .btn-outline { background: transparent; color: white; border: 2px solid white; }
    .btn-outline:hover { background: white; color: #667eea; transform: translateY(-2px); }
    .card { background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); animation: fadeIn 0.5s ease; }
    .card h2 { color: #333; margin-bottom: 20px; }
    .form-group { margin-bottom: 20px; }
    label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
    input, textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
    input:focus, textarea:focus { outline: none; border-color: #667eea; }
    textarea { resize: vertical; font-family: inherit; }
    .result-real { background: linear-gradient(135deg, #d4edda, #c3e6cb); border-left: 5px solid #28a745; padding: 20px; border-radius: 10px; margin-top: 20px; }
    .result-fake { background: linear-gradient(135deg, #f8d7da, #f5c6cb); border-left: 5px solid #dc3545; padding: 20px; border-radius: 10px; margin-top: 20px; }
    .result-warning { background: linear-gradient(135deg, #fff3cd, #ffeeba); border-left: 5px solid #ffc107; padding: 20px; border-radius: 10px; margin-top: 20px; }
    .progress { height: 30px; background: #e0e0e0; border-radius: 15px; overflow: hidden; margin: 15px 0; }
    .progress-bar { height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; transition: width 0.5s ease; }
    .progress-real { background: linear-gradient(90deg, #28a745, #34ce57); }
    .progress-fake { background: linear-gradient(90deg, #dc3545, #e4606d); }
    .alert { padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 40px; }
    .feature-card { background: white; padding: 30px; border-radius: 15px; text-align: center; transition: transform 0.3s; }
    .feature-card:hover { transform: translateY(-5px); }
    .feature-icon { font-size: 3rem; margin-bottom: 15px; }
    .footer { background: #333; color: white; text-align: center; padding: 20px; margin-top: 50px; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    @media (max-width: 768px) { .hero h1 { font-size: 2rem; } .nav-links { display: none; } .grid { grid-template-columns: 1fr; } }
</style>
'''

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

# ============ SERVER HANDLER ============
sessions = {}

class Handler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Override to suppress default logging (optional)
        print(f"{self.address_string()} - {format % args}")
    
    def get_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            return sessions.get(session_id)
        return None
    
    def set_user(self, user_id):
        session_id = hashlib.md5(str(user_id).encode()).hexdigest()
        sessions[session_id] = user_id
        self.send_header('Set-Cookie', f'session={session_id}; HttpOnly')
    
    def clear_user(self):
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            if session_id in sessions:
                del sessions[session_id]
        self.send_header('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 UTC')
    
    def send_html(self, content, title="Fake News Detector"):
        user_id = self.get_user()
        html = get_html(content, title, user_id)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def redirect(self, location):
        """Helper method for redirects - FIXED version"""
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()  # IMPORTANT: No extra headers after this
    
    def do_GET(self):
        print(f"GET request: {self.path}")
        
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
        print(f"POST request: {self.path}")
        
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
            <form method="POST" action="/login">
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
            <form method="POST" action="/signup">
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
            self.redirect('/login')
            return
        
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM detections WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM detections WHERE user_id = ? AND prediction LIKE "%Fake%"', (user_id,))
        fake_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM fact_checks WHERE user_id = ?', (user_id,))
        fact_count = cursor.fetchone()[0]
        conn.close()
        
        fake_percent = (fake_count / total * 100) if total > 0 else 0
        
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
                <div class="feature-icon">⚠️</div>
                <h3>Fake News Found</h3>
                <p style="font-size: 2rem; font-weight: bold;">{fake_percent:.0f}%</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">✅</div>
                <h3>Fact Checks</h3>
                <p style="font-size: 2rem; font-weight: bold;">{fact_count}</p>
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
            self.redirect('/login')
            return
        
        content = '''
        <div class="card">
            <h2>🔍 Fake News Detection</h2>
            <p>Enter the news text below to analyze it for fake news indicators:</p>
            <form method="POST" action="/detect">
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
            self.redirect('/login')
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
            INSERT INTO detections (user_id, news_text, prediction, confidence, fake_probability, real_probability)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, news_text, result['prediction'], result['confidence'],
              result['fake_probability'], result['real_probability']))
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
            self.redirect('/login')
            return
        
        content = '''
        <div class="card">
            <h2>✅ Fact Check a Claim</h2>
            <p>Enter a claim to verify its accuracy:</p>
            <form method="POST" action="/fact-check">
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
            self.redirect('/login')
            return
        
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        params = urllib.parse.parse_qs(data.decode())
        claim = params.get('claim', [''])[0]
        
        claim_lower = claim.lower()
        
        # Fact checking database
        fact_db = {
            'trump is president': {'verdict': 'False', 'confidence': 95, 'explanation': 'Donald Trump was president from 2017-2021. The current president is Joe Biden.'},
            'obama is president': {'verdict': 'False', 'confidence': 95, 'explanation': 'Barack Obama was president from 2009-2017. The current president is Joe Biden.'},
            'biden is president': {'verdict': 'True', 'confidence': 95, 'explanation': 'Correct! Joe Biden is the 46th and current President of the United States.'},
            'earth is flat': {'verdict': 'False', 'confidence': 99, 'explanation': 'Scientific consensus confirms Earth is an oblate spheroid.'},
            'vaccines cause autism': {'verdict': 'False', 'confidence': 98, 'explanation': 'Numerous studies have debunked this claim. Vaccines do not cause autism.'},
            'climate change is hoax': {'verdict': 'False', 'confidence': 97, 'explanation': '97% of climate scientists agree that climate change is real and human-caused.'}
        }
        
        found = False
        for key, value in fact_db.items():
            if key in claim_lower:
                verdict = value['verdict']
                confidence = value['confidence']
                explanation = value['explanation']
                found = True
                break
        
        if not found:
            verdict = 'Unverified'
            confidence = 50
            explanation = 'No specific fact-checking information available for this claim. Please consult reliable sources.'
        
        # Save to database
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fact_checks (user_id, claim, verdict, confidence, sources)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, claim, verdict, confidence, '[]'))
        conn.commit()
        conn.close()
        
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
            self.redirect('/login')
            return
        
        conn = sqlite3.connect('fake_news.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM detections WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        detections = cursor.fetchall()
        conn.close()
        
        history_html = ''
        for det in detections:
            prediction_class = 'result-fake' if 'Fake' in det[3] else 'result-real'
            history_html += f'''
            <div style="border-bottom: 1px solid #e0e0e0; padding: 15px;">
                <div class="{prediction_class}" style="padding: 10px; margin-bottom: 5px;">
                    <strong>{det[3]}</strong> (Confidence: {det[4]:.1f}%)
                </div>
                <div style="padding: 10px;">
                    <span style="color: #666;">{det[2][:200]}...</span>
                </div>
                <small style="color: #999; display: block; padding: 5px 10px;">{det[7]}</small>
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
            # Set session and redirect - FIXED: Use redirect method
            session_id = hashlib.md5(str(result[0]).encode()).hexdigest()
            sessions[session_id] = result[0]
            
            self.send_response(302)
            self.send_header('Set-Cookie', f'session={session_id}; HttpOnly')
            self.send_header('Location', '/dashboard')
            self.end_headers()  # IMPORTANT: Only call end_headers once
        else:
            # Show error page
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
        # Clear session
        cookie = self.headers.get('Cookie', '')
        if 'session=' in cookie:
            session_id = cookie.split('session=')[1].split(';')[0]
            if session_id in sessions:
                del sessions[session_id]
        
        self.send_response(302)
        self.send_header('Set-Cookie', 'session=; expires=Thu, 01 Jan 1970 00:00:00 UTC')
        self.send_header('Location', '/')
        self.end_headers()

# ============ RUN SERVER ============
def run():
    init_database()
    port = 8000
    server = HTTPServer(('', port), Handler)
    print("=" * 60)
    print("🚀 FAKE NEWS DETECTOR IS RUNNING!")
    print("=" * 60)
    print(f"📍 Open: http://localhost:{port}")
    print("=" * 60)
    print("\n📝 Test these examples:")
    print("   'Trump is president!!!' → FAKE NEWS")
    print("   'Trump is president' → FAKE NEWS")
    print("   'Joe Biden is president' → REAL NEWS")
    print("   'BREAKING NEWS!!!' → FAKE NEWS")
    print("   'BREAKING NEWS' → REAL NEWS")
    print("=" * 60)
    print("\n✅ Sign up with any email/password")
    print("✅ Login and start detecting")
    print("✅ Press Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
        server.server_close()

if __name__ == '__main__':
    run()