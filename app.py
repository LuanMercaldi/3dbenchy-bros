#!/usr/bin/env python3
"""
Aplicação Principal 3DBenchy Bros
Backend Flask completo com todas as funcionalidades
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from backend.config import config
from backend.utils.database import DatabaseManager
from backend.utils.security_headers import SecurityHeaders

def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    # Determinar configuração
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Criar aplicação Flask
    app = Flask(__name__)
    CORS(app, origins=[
        'https://github.com/LuanMercaldi/3dbenchy-bros',
        'https://3dbenchybros.com.br'
    ])
    
    # Carregar configuração
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configurar CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Inicializar banco de dados
    try:
        db = DatabaseManager()
        app.db = db
        print("✅ Banco de dados inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        app.db = None
    
    # Registrar blueprints (rotas)
    from backend.routes.auth import auth_bp
    from backend.routes.products import products_bp
    from backend.routes.cart import cart_bp

    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    
    # Rotas principais
    @app.route('/')
    def index():
        """Página inicial da API"""
        return jsonify({
            "message": "3DBenchy Bros API",
            "version": "2.0.0",
            "status": "running",
            "endpoints": {
                "auth": {
                    "POST /api/auth/register": "Cadastro de usuários",
                    "POST /api/auth/login": "Login de usuários",
                    "GET /api/auth/user": "Dados do usuário logado",
                    "POST /api/auth/logout": "Logout",
                    "POST /api/auth/refresh": "Renovar token",
                    "GET /api/auth/login/github": "Login com GitHub"
                },
                "products": {
                    "GET /api/products": "Listar produtos",
                    "GET /api/products/featured": "Produtos em destaque",
                    "GET /api/products/<id>": "Buscar produto específico",
                    "POST /api/products": "Criar produto (admin)",
                    "GET /api/products/categories": "Listar categorias"
                },
                "cart": {
                    "GET /api/cart": "Ver carrinho",
                    "POST /api/cart": "Adicionar ao carrinho",
                    "DELETE /api/cart/<id>": "Remover do carrinho",
                    "DELETE /api/cart/clear": "Limpar carrinho",
                    "GET /api/cart/count": "Contagem de itens"
                }
            },
            "database": "sqlite" if app.db else "unavailable"
        })
    
    @app.route('/health')
    def health():
        """Endpoint de saúde da aplicação"""
        app_health = {
            "status": "ok",
            "message": "3DBenchy Bros Backend is running",
            "version": "2.0.0",
            "features": ["sqlite", "jwt_authentication", "cors", "oauth_ready"]
        }
        
        if app.db:
            db_health = app.db.health_check()
            app_health["database"] = db_health
        else:
            app_health["database"] = {"status": "unavailable"}
            app_health["status"] = "degraded"
        
        status_code = 200 if app_health["status"] == "ok" else 503
        return jsonify(app_health), status_code
    
    # Handlers de erro
    @app.errorhandler(404)
    def not_found(error):
        """Handler para rotas não encontradas"""
        return jsonify({
            "error": "Endpoint não encontrado",
            "message": "Verifique a documentação da API em /"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handler para métodos não permitidos"""
        return jsonify({
            "error": "Método não permitido",
            "message": "Verifique os métodos HTTP suportados para este endpoint"
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handler para erros internos"""
        return jsonify({
            "error": "Erro interno do servidor",
            "message": "Tente novamente mais tarde"
        }), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handler para erros de autenticação"""
        return jsonify({
            "error": "Não autorizado",
            "message": "Token de acesso requerido ou inválido"
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handler para erros de autorização"""
        return jsonify({
            "error": "Acesso negado",
            "message": "Privilégios insuficientes para esta operação"
        }), 403
    
    # Middleware para logging
    @app.before_request
    def log_request_info():
        """Log de requisições para debug"""
        if app.config.get('DEBUG'):
            print(f"🌐 {request.method} {request.url}")
    
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Iniciando 3DBenchy Bros Backend na porta {port}")
    print(f"🗄️ Banco de dados: {'SQLite' if app.db else 'Não disponível'}")
    print(f"🌐 CORS configurado para: {app.config['CORS_ORIGINS']}")
    print(f"🔧 Modo debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)


