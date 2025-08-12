import logging
import json
from datetime import datetime
from flask import request, g
from functools import wraps

class SecurityLogger:
    """Logger especializado para eventos de segurança"""
    
    def __init__(self, app=None):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Configurar handler se não existir
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar logging na aplicação"""
        app.before_request(self.log_request)
    
    def log_request(self):
        """Log de requisições para monitoramento"""
        # Log apenas requisições sensíveis
        sensitive_paths = ['/api/auth/', '/api/admin/']
        
        if any(request.path.startswith(path) for path in sensitive_paths):
            self.log_event('request', {
                'method': request.method,
                'path': request.path,
                'ip': self.get_client_ip(),
                'user_agent': request.headers.get('User-Agent', '')[:200]
            })
    
    def log_event(self, event_type, data):
        """Log de evento de segurança"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'ip': self.get_client_ip(),
            'user_id': getattr(g, 'current_user', {}).get('id'),
            'data': data
        }
        
        self.logger.info(json.dumps(log_data))
    
    def get_client_ip(self):
        """Obter IP real do cliente"""
        return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

# Instância global
security_logger = SecurityLogger()

def log_security_event(event_type):
    """Decorator para log automático de eventos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Log de sucesso
                security_logger.log_event(f'{event_type}_success', {
                    'function': f.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                })
                
                return result
                
            except Exception as e:
                # Log de erro
                security_logger.log_event(f'{event_type}_error', {
                    'function': f.__name__,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                raise
        
        return decorated_function
    return decorator