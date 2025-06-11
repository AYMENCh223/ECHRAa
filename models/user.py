from models.database import db
from flask_login import UserMixin
import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_image_url = db.Column(db.String(255))
    subscription_type = db.Column(db.String(50), default='free')
    subscription_status = db.Column(db.String(50), default='inactive')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def is_premium(self):
        return self.subscription_type in ['premium', 'educational'] and self.subscription_status == 'active'
    
    def can_save_sessions(self):
        if self.subscription_type == 'free':
            return len(self.sessions) < 3  # Free users can save 3 sessions
        elif self.subscription_type == 'basic':
            return len(self.sessions) < 10  # Basic users can save 10 sessions
        else:
            return True  # Premium users have unlimited sessions
