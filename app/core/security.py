import hashlib
import os
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "your_secret_key_here"  # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password with a random salt using SHA-256."""
    salt = os.urandom(16)
    salted_password = salt + password.encode('utf-8')
    hashed = hashlib.sha256(salted_password).hexdigest()
    # Store salt and hash together (hex encoded)
    return salt.hex() + hashed

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify a password against the stored hash."""
    salt = bytes.fromhex(stored_hash[:32])
    stored_password_hash = stored_hash[32:]
    salted_password = salt + password.encode('utf-8')
    hashed = hashlib.sha256(salted_password).hexdigest()
    return hashed == stored_password_hash

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.

    :param data: Dictionary containing the data to encode in the token.
    :param expires_delta: Optional timedelta for token expiration.
    :return: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
