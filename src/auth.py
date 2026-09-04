"""
Authentication and Session Security Module for AI Teacher Platform.
Provides PBKDF2-HMAC password hashing, tamper-proof signed JWT-style tokens,
and FastAPI auth dependency. Zero external C/binary dependencies.
"""

import os
import time
import json
import hmac
import base64
import hashlib
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import StudentProfile

AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "ai_teacher_super_secure_auth_secret_key_2026_production")
TOKEN_EXPIRY_SECONDS = 30 * 24 * 60 * 60  # 30 days


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 16-byte random salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored salt:hash string."""
    try:
        if not hashed_password or ":" not in hashed_password:
            return False
        salt_hex, key_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(expected_key, actual_key)
    except Exception:
        return False


def create_access_token(user_id: str, email: str = "") -> str:
    """Create a signed URL-safe authentication token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS
    }
    payload_json = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")
    
    sig = hmac.new(
        AUTH_SECRET_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")
    
    return f"{payload_b64}.{sig_b64}"


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token signature and expiration, return payload dict or None."""
    try:
        if not token or "." not in token:
            return None
        payload_b64, sig_b64 = token.split(".", 1)
        
        # Re-compute expected signature
        expected_sig = hmac.new(
            AUTH_SECRET_KEY.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256
        ).digest()
        
        # Pad base64 strings if needed
        sig_padding = len(sig_b64) % 4
        if sig_padding:
            sig_b64 += "=" * (4 - sig_padding)
        actual_sig = base64.urlsafe_b64decode(sig_b64.encode("utf-8"))
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        # Decode payload
        payload_padding = len(payload_b64) % 4
        if payload_padding:
            payload_b64 += "=" * (4 - payload_padding)
        payload_json = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
        payload = json.loads(payload_json)
        
        # Check expiry
        if payload.get("exp", 0) < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[StudentProfile]:
    """Extract authenticated user if Authorization header is present."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    payload = verify_access_token(token)
    if not payload or "user_id" not in payload:
        return None
    return db.query(StudentProfile).filter(StudentProfile.id == payload["user_id"]).first()


def get_current_user_required(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> StudentProfile:
    """Require valid authentication or raise 401."""
    user = get_current_user_optional(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    return user

