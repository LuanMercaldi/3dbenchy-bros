import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
import hashlib
import secrets

class JWTManager:
    @staticmethod
    def generate_tokens(user):
        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        
        access_token = jwt.encode(payload, 'dev-jwt-secret', algorithm='HS256')
        
        refresh_payload = {
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(days=30)
        }
        
        refresh_token = jwt.encode(refresh_payload, 'dev-jwt-secret', algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600
        }
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, 'dev-jwt-secret', algorithms=['HS256'])
            return payload
        except:
            return None

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token de acesso requerido'}), 401
        
        payload = JWTManager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        g.current_user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    return getattr(g, 'current_user', None)

def hash_password(password):
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def verify_password(stored_password, provided_password):
    salt = stored_password[:32]
    stored_hash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_hash
