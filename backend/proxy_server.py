#!/usr/bin/env python3
"""
Aplicação Principal 3DBenchy Bros
Backend Flask com SQLite para autenticação e persistência
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database_sqlite import DatabaseManager

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS para produção
cors_origins = ["https://3dbenchybros.com.br", "https://luanmercaldi.github.io"]
if os.environ.get('FLASK_ENV') == 'development':
    cors_origins.append("*")

CORS(app, origins=cors_origins, supports_credentials=True)

# Inicializar gerenciador de banco de dados
try:
    db = DatabaseManager()
    print("✅ Banco de dados inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar banco de dados: {e}")
    db = None

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Endpoint para cadastro de usuários
    """
    if not db:
        return jsonify({"error": "Banco de dados não disponível"}), 500
    
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or not all(k in data for k in ['name', 'email', 'password']):
            return jsonify({
                "error": "Dados obrigatórios: name, email, password"
            }), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validações básicas
        if len(name) < 2:
            return jsonify({"error": "Nome deve ter pelo menos 2 caracteres"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Senha deve ter pelo menos 6 caracteres"}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Email inválido"}), 400
        
        # Criar usuário
        result = db.create_user(name, email, password)
        
        if result['success']:
            return jsonify({
                "message": result['message'],
                "user": result['user']
            }), 201
        else:
            status_code = 409 if result.get('code') == 'EMAIL_EXISTS' else 400
            return jsonify({"error": result['error']}), status_code
            
    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Endpoint para login de usuários
    """
    if not db:
        return jsonify({"error": "Banco de dados não disponível"}), 500
    
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({
                "error": "Dados obrigatórios: email, password"
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Autenticar usuário
        result = db.authenticate_user(email, password)
        
        if result['success']:
            return jsonify({
                "message": result['message'],
                "user": result['user']
            }), 200
        else:
            return jsonify({"error": result['error']}), 401
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Endpoint para buscar usuário por ID
    """
    if not db:
        return jsonify({"error": "Banco de dados não disponível"}), 500
    
    try:
        user = db.get_user_by_id(user_id)
        
        if user:
            return jsonify({"user": user}), 200
        else:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
    except Exception as e:
        print(f"❌ Erro ao buscar usuário: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de saúde da aplicação
    """
    app_health = {
        "status": "ok",
        "message": "3DBenchy Bros Backend is running",
        "version": "2.0.0",
        "features": ["postgresql", "authentication", "cors"]
    }
    
    if db:
        db_health = db.health_check()
        app_health["database"] = db_health
    else:
        app_health["database"] = {"status": "unavailable"}
    
    return jsonify(app_health)

@app.route('/', methods=['GET'])
def index():
    """
    Página inicial da API
    """
    return jsonify({
        "message": "3DBenchy Bros API",
        "version": "2.0.0",
        "endpoints": {
            "/api/auth/register": "POST - Cadastro de usuários",
            "/api/auth/login": "POST - Login de usuários",
            "/api/users/<id>": "GET - Buscar usuário por ID",
            "/health": "GET - Status da aplicação"
        },
        "database": "postgresql" if db else "unavailable"
    })

@app.errorhandler(404)
def not_found(error):
    """
    Handler para rotas não encontradas
    """
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """
    Handler para métodos não permitidos
    """
    return jsonify({"error": "Método não permitido"}), 405

@app.errorhandler(500)
def internal_error(error):
    """
    Handler para erros internos
    """
    return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando 3DBenchy Bros Backend na porta {port}")
    print(f"🗄️ Banco de dados: {'SQLite' if db else 'Não disponível'}")
    print(f"🌐 CORS configurado para: https://3dbenchybros.com.br")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

