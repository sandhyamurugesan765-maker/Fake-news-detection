# app.py (corrected version)
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, NewsDetection, FactCheck
from fake_news_detector import FakeNewsDetector
import json
from datetime import datetime
import requests
from textblob import TextBlob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fake_news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize detector
detector = FakeNewsDetector()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()
    # Train the detector if not already trained
    if not detector.is_trained:
        detector.train_with_sample_data()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent activities
    recent_detections = NewsDetection.query.filter_by(user_id=current_user.id)\
        .order_by(NewsDetection.created_at.desc()).limit(5).all()
    
    recent_fact_checks = FactCheck.query.filter_by(user_id=current_user.id)\
        .order_by(FactCheck.created_at.desc()).limit(5).all()
    
    # Statistics
    total_detections = NewsDetection.query.filter_by(user_id=current_user.id).count()
    total_fact_checks = FactCheck.query.filter_by(user_id=current_user.id).count()
    
    # Calculate accuracy (for demo purposes)
    fake_count = NewsDetection.query.filter_by(user_id=current_user.id, prediction='Fake').count()
    real_count = NewsDetection.query.filter_by(user_id=current_user.id, prediction='Real').count()
    
    stats = {
        'total_checks': total_detections + total_fact_checks,
        'total_detections': total_detections,
        'total_fact_checks': total_fact_checks,
        'fake_percentage': (fake_count / total_detections * 100) if total_detections > 0 else 0,
        'real_percentage': (real_count / total_detections * 100) if total_detections > 0 else 0
    }
    
    return render_template('dashboard.html', 
                         recent_detections=recent_detections,
                         recent_fact_checks=recent_fact_checks,
                         stats=stats)

@app.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    if request.method == 'POST':
        news_text = request.form.get('news_text', '')  # Fixed: use get() method
        
        if not news_text.strip():
            flash('Please enter some news text to analyze!', 'warning')
            return redirect(url_for('detect'))
        
        # Get prediction
        result = detector.predict(news_text)
        
        # Save to database
        detection = NewsDetection(
            user_id=current_user.id,
            news_text=news_text,
            prediction=result['prediction'],
            confidence=result['confidence'],
            fake_probability=result['fake_probability'],
            real_probability=result['real_probability']
        )
        db.session.add(detection)
        db.session.commit()
        
        return render_template('detect.html', result=result, news_text=news_text)
    
    return render_template('detect.html', result=None)

@app.route('/fact-check', methods=['GET', 'POST'])
@login_required
def fact_check():
    if request.method == 'POST':
        claim = request.form.get('claim', '')  # Fixed: use get() method
        
        if not claim.strip():
            flash('Please enter a claim to fact-check!', 'warning')
            return redirect(url_for('fact_check'))
        
        # Perform fact-checking (simplified version)
        fact_result = perform_fact_check(claim)
        
        # Save to database
        fact_check = FactCheck(
            user_id=current_user.id,
            claim=claim,
            verdict=fact_result['verdict'],
            confidence=fact_result['confidence'],
            sources=json.dumps(fact_result['sources'])
        )
        db.session.add(fact_check)
        db.session.commit()
        
        return render_template('fact_check.html', result=fact_result, claim=claim)
    
    return render_template('fact_check.html', result=None)

def perform_fact_check(claim):
    """Perform fact-checking using multiple sources"""
    # This is a simplified version - in production, integrate with fact-checking APIs
    
    # Analyze sentiment and language patterns
    blob = TextBlob(claim)
    sentiment = blob.sentiment.polarity
    
    # Simple keyword-based fact checking
    fake_indicators = ['miracle', 'instant', 'secret', 'shocking', 'government hiding',
                       'conspiracy', 'cover up', 'they don\'t want you to know']
    real_indicators = ['study shows', 'research indicates', 'according to', 'scientists say']
    
    claim_lower = claim.lower()
    
    # Calculate scores
    fake_score = sum(1 for word in fake_indicators if word in claim_lower)
    real_score = sum(1 for word in real_indicators if word in claim_lower)
    
    # Determine verdict
    if fake_score > real_score and fake_score >= 2:
        verdict = 'Misleading'
        confidence = 70 + (fake_score * 5)
    elif 'vaccine' in claim_lower and 'cause' in claim_lower:
        verdict = 'False'
        confidence = 85
    elif 'cure' in claim_lower and 'cancer' in claim_lower:
        verdict = 'Misleading'
        confidence = 75
    elif real_score > 0:
        verdict = 'True'
        confidence = 60 + (real_score * 10)
    else:
        verdict = 'Unverified'
        confidence = 50
    
    confidence = min(confidence, 95)
    
    # Mock sources (in production, fetch from APIs)
    sources = [
        {'name': 'FactCheck.org', 'url': 'https://www.factcheck.org', 'verdict': verdict},
        {'name': 'Snopes', 'url': 'https://www.snopes.com', 'verdict': 'Similar claims fact-checked'}
    ]
    
    return {
        'verdict': verdict,
        'confidence': confidence,
        'sources': sources,
        'analysis': {
            'sentiment_score': sentiment,
            'fake_indicators': fake_score,
            'real_indicators': real_score
        }
    }

@app.route('/history')
@login_required
def history():
    # Get all user's detections and fact checks
    detections = NewsDetection.query.filter_by(user_id=current_user.id)\
        .order_by(NewsDetection.created_at.desc()).all()
    
    fact_checks = FactCheck.query.filter_by(user_id=current_user.id)\
        .order_by(FactCheck.created_at.desc()).all()
    
    return render_template('history.html', detections=detections, fact_checks=fact_checks)

@app.route('/api/detect', methods=['POST'])
@login_required
def api_detect():
    """API endpoint for detection"""
    data = request.json
    news_text = data.get('text', '')
    
    if not news_text:
        return jsonify({'error': 'No text provided'}), 400
    
    result = detector.predict(news_text)
    
    # Save to database
    detection = NewsDetection(
        user_id=current_user.id,
        news_text=news_text,
        prediction=result['prediction'],
        confidence=result['confidence'],
        fake_probability=result['fake_probability'],
        real_probability=result['real_probability']
    )
    db.session.add(detection)
    db.session.commit()
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)