from models.database import db
import datetime
import json

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    translation_text = db.Column(db.Text)
    recognized_signs = db.Column(db.Text)  # JSON string of recognized signs
    mode = db.Column(db.String(50), default='standard')  # standard, teacher, kids
    duration_seconds = db.Column(db.Integer, default=0)
    accuracy_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<Session {self.name}>'
    
    def get_recognized_signs_list(self):
        """Parse the JSON string of recognized signs"""
        if self.recognized_signs:
            try:
                return json.loads(self.recognized_signs)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_recognized_signs_list(self, signs_list):
        """Set the recognized signs as JSON string"""
        self.recognized_signs = json.dumps(signs_list, ensure_ascii=False)
    
    def get_word_count(self):
        """Get the number of words in the translation"""
        if self.translation_text:
            return len(self.translation_text.split())
        return 0
    
    def get_sign_count(self):
        """Get the number of recognized signs"""
        return len(self.get_recognized_signs_list())
