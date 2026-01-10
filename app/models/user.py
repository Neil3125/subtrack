"""User model for authentication."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
import hashlib
import secrets


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Password reset fields
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = "subtrack_secret_salt_2024"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return self.password_hash == self.hash_password(password)
    
    def set_password(self, password: str):
        """Set a new password."""
        self.password_hash = self.hash_password(password)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a secure reset token."""
        return secrets.token_urlsafe(32)
