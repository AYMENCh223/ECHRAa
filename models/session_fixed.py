import datetime
import json
from .database import db

class Session(db.Model):
    """
    Model for storing user translation sessions
    """
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(100), default="Untitled Session")
    content = db.Column(db.Text, nullable=False)
    recognized_signs = db.Column(db.Text)  # Stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __init__(self, content, user_id=None, title=None, recognized_signs=None):
        """
        Initialize a new session
        
        Args:
            content: The content of the session (translated text)
            user_id: ID of the user who owns this session (optional)
            title: Title of the session (optional)
            recognized_signs: List of recognized signs (optional)
        """
        self.content = content
        self.user_id = user_id
        
        if title:
            self.title = title
            
        if recognized_signs:
            if isinstance(recognized_signs, list):
                self.recognized_signs = json.dumps(recognized_signs)
            else:
                self.recognized_signs = recognized_signs
    
    def get_recognized_signs(self):
        """
        Get the list of recognized signs
        
        Returns:
            list: List of recognized signs, or empty list if none
        """
        if self.recognized_signs:
            try:
                return json.loads(self.recognized_signs)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_recognized_signs(self, signs):
        """
        Set the list of recognized signs
        
        Args:
            signs: List of recognized signs
        """
        if isinstance(signs, list):
            self.recognized_signs = json.dumps(signs)
        else:
            raise ValueError("Recognized signs must be a list")
    
    def to_dict(self):
        """
        Convert session object to dictionary
        
        Returns:
            dict: Session data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'recognized_signs': self.get_recognized_signs(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of the session"""
        return f'<Session {self.id}: {self.title}>'

class TestSession(db.Model):
    """
    Model for storing teacher mode test sessions
    """
    __tablename__ = 'test_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=True)
    student_name = db.Column(db.String(100), nullable=True)
    test_type = db.Column(db.String(50), nullable=False)  # e.g., 'letters', 'phrases', 'mixed'
    difficulty = db.Column(db.String(20), default='medium')  # 'easy', 'medium', 'hard'
    total_signs = db.Column(db.Integer, default=0)
    correct_signs = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    time_spent = db.Column(db.Integer, default=0)  # in seconds
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Store test details as JSON
    test_details = db.Column(db.Text)  # JSON string with test items and results
    
    def __init__(self, test_type, user_id=None, student_name=None, difficulty='medium'):
        """
        Initialize a new test session
        
        Args:
            test_type: Type of test ('letters', 'phrases', 'mixed')
            user_id: ID of the teacher (optional)
            student_name: Name of the student (optional)
            difficulty: Difficulty level ('easy', 'medium', 'hard')
        """
        self.test_type = test_type
        self.user_id = user_id
        self.student_name = student_name
        self.difficulty = difficulty
        self.test_details = json.dumps([])
    
    def add_test_item(self, sign, correct, time_taken):
        """
        Add a test item result
        
        Args:
            sign: The sign that was tested
            correct: Whether the recognition was correct
            time_taken: Time taken to recognize the sign (seconds)
        """
        details = self.get_test_details()
        
        details.append({
            'sign': sign,
            'correct': correct,
            'time_taken': time_taken,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        
        self.test_details = json.dumps(details)
        
        # Update summary stats
        self.total_signs += 1
        if correct:
            self.correct_signs += 1
        
        if self.total_signs > 0:
            self.accuracy = (self.correct_signs / self.total_signs) * 100
        
        self.time_spent += time_taken
    
    def complete_test(self):
        """Mark the test as completed"""
        self.completed = True
        self.completed_at = datetime.datetime.utcnow()
    
    def get_test_details(self):
        """
        Get test details as a list
        
        Returns:
            list: Test details
        """
        if self.test_details:
            try:
                return json.loads(self.test_details)
            except json.JSONDecodeError:
                return []
        return []
    
    def to_dict(self):
        """
        Convert test session object to dictionary
        
        Returns:
            dict: Test session data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_name': self.student_name,
            'test_type': self.test_type,
            'difficulty': self.difficulty,
            'total_signs': self.total_signs,
            'correct_signs': self.correct_signs,
            'accuracy': self.accuracy,
            'time_spent': self.time_spent,
            'completed': self.completed,
            'test_details': self.get_test_details(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        """String representation of the test session"""
        return f'<TestSession {self.id}: {self.test_type} ({self.difficulty})>'