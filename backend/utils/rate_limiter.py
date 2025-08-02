import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
    
    def is_rate_limited(self, identifier, max_requests=60, window_seconds=60):
        current_time = time.time()
        user_requests = self.requests[identifier]
        
        # Remover requisições antigas
        while user_requests and user_requests[0] <= current_time - window_seconds:
            user_requests.popleft()
        
        # Verificar limite
        if len(user_requests) >= max_requests:
            return True
        
        # Adicionar nova requisição
        user_requests.append(current_time)
        return False

rate_limiter = RateLimiter()

def rate_limit(max_requests=60, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = request.remote_addr
            
            if rate_limiter.is_rate_limited(identifier, max_requests, window_seconds):
                return jsonify({
                    'error': 'Muitas requisições',
                    'message': f'Limite de {max_requests} requisições por {window_seconds} segundos excedido'
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def strict_rate_limit(max_requests=5, window_seconds=60):
    return rate_limit(max_requests, window_seconds)