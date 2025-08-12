import re
from functools import wraps
from flask import request, jsonify

class ValidationError(Exception):
    pass

class DataValidator:
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_email(email):
        if not email or not isinstance(email, str):
            raise ValidationError("Email é obrigatório")
        
        email = email.strip().lower()
        
        if len(email) > 254:
            raise ValidationError("Email muito longo")
        
        if not DataValidator.EMAIL_PATTERN.match(email):
            raise ValidationError("Formato de email inválido")
        
        return email
    
    @staticmethod
    def validate_password(password):
        if not password or not isinstance(password, str):
            raise ValidationError("Senha é obrigatória")
        
        if len(password) < 8:
            raise ValidationError("Senha deve ter pelo menos 8 caracteres")
        
        return password
    
    @staticmethod
    def validate_name(name):
        if not name or not isinstance(name, str):
            raise ValidationError("Nome é obrigatório")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres")
        
        return name

def validate_json(*required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Dados JSON são obrigatórios'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
