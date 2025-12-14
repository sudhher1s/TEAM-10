"""
Authentication module with JWT and password hashing
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import bcrypt
import secrets
import os
from .models import User, UserRole, Database


class AuthConfig:
    """Authentication configuration"""
    JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 24
    REFRESH_TOKEN_EXPIRY_DAYS = 7
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15


class PasswordManager:
    """Secure password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        if len(password) < AuthConfig.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {AuthConfig.PASSWORD_MIN_LENGTH} characters")
        
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), hashed.encode())


class JWTManager:
    """JWT token generation and validation"""
    
    @staticmethod
    def create_token(user: User, expires_in_hours: Optional[int] = None) -> str:
        """Create JWT token"""
        payload = user.to_dict()
        
        exp_hours = expires_in_hours or AuthConfig.JWT_EXPIRY_HOURS
        payload["exp"] = datetime.utcnow() + timedelta(hours=exp_hours)
        payload["iat"] = datetime.utcnow()
        payload["token_type"] = "access"
        
        token = jwt.encode(
            payload,
            AuthConfig.JWT_SECRET,
            algorithm=AuthConfig.JWT_ALGORITHM
        )
        return token

    @staticmethod
    def create_refresh_token(user: User) -> str:
        """Create refresh token"""
        payload = {
            "user_id": user.user_id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=AuthConfig.REFRESH_TOKEN_EXPIRY_DAYS),
            "iat": datetime.utcnow(),
            "token_type": "refresh"
        }
        
        token = jwt.encode(
            payload,
            AuthConfig.JWT_SECRET,
            algorithm=AuthConfig.JWT_ALGORITHM
        )
        return token

    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[dict]]:
        """Verify JWT token and extract payload"""
        try:
            payload = jwt.decode(
                token,
                AuthConfig.JWT_SECRET,
                algorithms=[AuthConfig.JWT_ALGORITHM]
            )
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid token"}

    @staticmethod
    def extract_user_from_token(token: str) -> Optional[dict]:
        """Extract user info from token"""
        is_valid, payload = JWTManager.verify_token(token)
        if is_valid:
            return payload
        return None


class AuthManager:
    """Complete authentication management"""
    
    def __init__(self, db: Database):
        self.db = db
        self.failed_attempts = {}  # user_id -> (count, timestamp)

    def register(self, email: str, password: str, full_name: str, 
                role: UserRole = UserRole.DOCTOR) -> Tuple[bool, str, Optional[User]]:
        """Register new user"""
        
        # Validate email format
        if "@" not in email or "." not in email:
            return False, "Invalid email format", None

        # Check if user exists
        existing = self.db.get_user_by_email(email)
        if existing:
            return False, "Email already registered", None

        # Hash password
        try:
            hashed = PasswordManager.hash_password(password)
        except ValueError as e:
            return False, str(e), None

        # Create user
        user = self.db.create_user(email, hashed, full_name, role)
        
        # Log action
        self.db.log_audit(user.user_id, "user_registration", "user", {
            "email": email,
            "role": role.value
        })

        return True, "User registered successfully", user

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """Authenticate user and return JWT tokens"""
        
        # Check for lockout
        if email in self.failed_attempts:
            count, timestamp = self.failed_attempts[email]
            if count >= AuthConfig.MAX_LOGIN_ATTEMPTS:
                elapsed = (datetime.utcnow() - timestamp).total_seconds() / 60
                if elapsed < AuthConfig.LOCKOUT_MINUTES:
                    return False, f"Account locked. Try again in {int(AuthConfig.LOCKOUT_MINUTES - elapsed)} minutes", None
                else:
                    del self.failed_attempts[email]

        # Get user
        user = self.db.get_user_by_email(email)
        if not user:
            self._record_failed_attempt(email)
            return False, "Invalid credentials", None

        # Check if active
        if not user.is_active:
            return False, "Account is disabled", None

        # Verify password
        if not PasswordManager.verify_password(password, user.hashed_password):
            self._record_failed_attempt(email)
            return False, "Invalid credentials", None

        # Clear failed attempts
        if email in self.failed_attempts:
            del self.failed_attempts[email]

        # Create tokens
        access_token = JWTManager.create_token(user)
        refresh_token = JWTManager.create_refresh_token(user)

        # Log action
        self.db.log_audit(user.user_id, "login", "authentication", {
            "email": email,
            "ip": "127.0.0.1"
        })

        return True, "Login successful", {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": user.to_dict()
        }

    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, str, Optional[str]]:
        """Create new access token from refresh token"""
        
        is_valid, payload = JWTManager.verify_token(refresh_token)
        if not is_valid or payload.get("token_type") != "refresh":
            return False, "Invalid refresh token", None

        user = self.db.get_user_by_id(payload["user_id"])
        if not user or not user.is_active:
            return False, "User not found or disabled", None

        new_token = JWTManager.create_token(user)
        return True, "Token refreshed", new_token

    def logout(self, user_id: int) -> None:
        """Log user logout"""
        self.db.log_audit(user_id, "logout", "authentication", {})

    def _record_failed_attempt(self, email: str):
        """Record failed login attempt"""
        if email not in self.failed_attempts:
            self.failed_attempts[email] = (1, datetime.utcnow())
        else:
            count, _ = self.failed_attempts[email]
            self.failed_attempts[email] = (count + 1, datetime.utcnow())


# Global auth manager (initialize after app startup)
auth_manager: Optional[AuthManager] = None


def init_auth(db: Database) -> AuthManager:
    """Initialize authentication manager"""
    global auth_manager
    auth_manager = AuthManager(db)
    return auth_manager


def get_auth_manager() -> AuthManager:
    """Get auth manager"""
    global auth_manager
    if auth_manager is None:
        raise RuntimeError("Auth manager not initialized")
    return auth_manager
