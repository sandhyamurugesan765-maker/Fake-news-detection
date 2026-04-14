# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    detections = db.relationship('NewsDetection', backref='user', lazy=True)
    fact_checks = db.relationship('FactCheck', backref='user', lazy=True)
    
    def get_id(self):
        return str(self.id)

class NewsDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    news_text = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    fake_probability = db.Column(db.Float)
    real_probability = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class FactCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    claim = db.Column(db.Text, nullable=False)
    verdict = db.Column(db.String(20))  # True, False, Misleading, Unverified
    confidence = db.Column(db.Float)
    sources = db.Column(db.Text)  # JSON string of sources
    created_at = db.Column(db.DateTime, default=datetime.utcnow)