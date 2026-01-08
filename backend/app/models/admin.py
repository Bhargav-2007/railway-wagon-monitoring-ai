"""
Admin User Model with Security
Author: Team Member 4 (Backend Architecture)
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib
import secrets

Base = declarative_base()

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    role = Column(String(20), default="admin")  # admin, superadmin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    def set_password(self, password: str):
        """Hash password with salt"""
        self.salt = secrets.token_hex(16)
        self.password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.salt.encode('utf-8'),
            100000
        ).hex()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.salt.encode('utf-8'),
            100000
        ).hex()
        return password_hash == self.password_hash
    
    def reset_login_attempts(self):
        """Reset failed login attempts"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
    
    def increment_failed_login(self):
        """Increment failed login counter"""
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Lock after 5 failed attempts
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
    
    def is_locked(self) -> bool:
        """Check if admin account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        elif self.locked_until and self.locked_until <= datetime.utcnow():
            self.locked_until = None
            self.login_attempts = 0
        return False

