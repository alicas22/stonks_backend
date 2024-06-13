from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Profile(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fullName = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime, default=db.func.now())
    updatedAt = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<Profile {self.username}>'
class Follow(db.Model):
    follower_id = db.Column(db.String(36), db.ForeignKey('profile.id'), primary_key=True)
    followed_id = db.Column(db.String(36), db.ForeignKey('profile.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('Profile', foreign_keys=[follower_id], backref=db.backref('following', lazy='dynamic'))
    followed = db.relationship('Profile', foreign_keys=[followed_id], backref=db.backref('followers', lazy='dynamic'))

class Channel(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    host_id = db.Column(db.String(36), db.ForeignKey('profile.id'), nullable=False)
    host = db.relationship('Profile', backref=db.backref('channels', lazy=True))
    createdAt = db.Column(db.DateTime, default=db.func.now())
    updatedAt = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class UserStatus(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36), db.ForeignKey('profile.id'), nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    profile = db.relationship('Profile', backref=db.backref('status', uselist=False))

class Role(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    profile_id = db.Column(db.String(36), db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship('Profile', backref=db.backref('roles', lazy=True))
    channel_id = db.Column(db.String(36), db.ForeignKey('channel.id'), nullable=True)
    channel = db.relationship('Channel', backref=db.backref('roles', lazy=True))


class FCMToken(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = db.Column(db.String(255), nullable=False)
    profile_id = db.Column(db.String(36), db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship('Profile', backref=db.backref('fcmtokens', lazy=True))
