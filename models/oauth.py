from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy import UniqueConstraint
from models.database import db
from models.user import User

class OAuth(OAuthConsumerMixin, db.Model):
    """
    Model for storing OAuth tokens for users
    Used by Replit authentication system
    """
    __tablename__ = 'oauth'
    
    user_id = db.Column(db.String(64), db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String(255), nullable=False)
    user = db.relationship(User)

    # Ensure uniqueness of user-browser-provider combination
    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)