from flask import Blueprint, request, jsonify
from utils.database import DatabaseManager
from utils.auth_helpers import require_auth, get_current_user, JWTManager, hash_password, verify_password
from utils.validators import DataValidator, ValidationError, validate_json
from utils.rate_limiter import rate_limit, strict_rate_limit

# DEFINIR O BLUEPRINT PRIMEIRO
auth_bp = Blueprint('auth', __name__)
db = DatabaseManager()

@auth_bp.route('/register', methods=['POST'])
@strict_rate_limit(max_requests=3, window_seconds=300)
@validate_json('name', 'email', 'password')
def register():
    """Endpoint para cadastro de usuários"""
    try:
        data = request.get_json()
        
        # Validar dados
        try:
            name = DataValidator.validate_name(data['name'])
            email = DataValidator.validate_email(data['email'])
            password = DataValidator.validate_password(data['password'])
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        
        # Criar usuário
        result = db.create_user(name, email, password)
        
        if result['success']:
            tokens = JWTManager.generate_tokens(result['user'])
            
            return jsonify({
                "message": result['message'],
                "user": result['user'],
                "tokens": tokens
            }), 201
        else:
            status_code = 409 if result.get('code') == 'EMAIL_EXISTS' else 400
            return jsonify({"error": result['error']}), status_code
            
    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@auth_bp.route('/login', methods=['POST'])
@strict_rate_limit(max_requests=5, window_seconds=300)
@validate_json('email', 'password')
def login():
    """Endpoint para login"""
    try:
        data = request.get_json()
        
        try:
            email = DataValidator.validate_email(data['email'])
            password = data['password']
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        
        result = db.authenticate_user(email, password)
        
        if result['success']:
            tokens = JWTManager.generate_tokens(result['user'])
            
            return jsonify({
                "message": result['message'],
                "user": result['user'],
                "tokens": tokens
            }), 200
        else:
            return jsonify({"error": result['error']}), 401
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@auth_bp.route('/user', methods=['GET'])
@require_auth
def get_current_user_info():
    """Obter dados do usuário logado"""
    try:
        current_user = get_current_user()
        user_data = db.get_user_by_id(current_user['user_id'])
        
        if user_data:
            return jsonify({
                "authenticated": True,
                "user": user_data
            }), 200
        else:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
    except Exception as e:
        print(f"❌ Erro ao obter usuário: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500
