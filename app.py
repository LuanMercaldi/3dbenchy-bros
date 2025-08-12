#!/usr/bin/env python3
"""
3DBenchy Bros - Backend API
Aplicação Flask simples e funcional para o Render.com
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

# Criar aplicação Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, origins=[
    'https://luanmercaldi.github.io',
    'https://3dbenchybros.com.br',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
])

# Configurações básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# Rota principal
@app.route('/')
def index():
    """Página inicial da API"""
    return jsonify({
        'message': '🎮 3DBenchy Bros API',
        'version': '1.0.0',
        'status': 'online',
        'description': 'API para e-commerce de modelos 3D com estética retrô',
        'endpoints': {
            'health': '/health',
            'products': '/api/products',
            'auth': '/api/auth'
        }
    })

# Rota de health check
@app.route('/health')
def health():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'timestamp': '2025-08-12T15:50:00Z',
        'service': '3dbenchy-bros-api'
    })

# Rota de produtos (mock)
@app.route('/api/products')
def products():
    """Lista de produtos 3D"""
    return jsonify({
        'products': [
            {
                'id': 1,
                'name': 'Benchy Clássico',
                'price': 15.99,
                'category': '3D Models',
                'description': 'O famoso modelo de teste para impressoras 3D'
            },
            {
                'id': 2,
                'name': 'Benchy Pixelizado',
                'price': 19.99,
                'category': '3D Models',
                'description': 'Versão retrô do Benchy com estética dos anos 80'
            }
        ],
        'total': 2
    })

# Rota de autenticação (mock)
@app.route('/api/auth/status')
def auth_status():
    """Status de autenticação"""
    return jsonify({
        'authenticated': False,
        'message': 'Sistema de autenticação em desenvolvimento'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Para desenvolvimento local
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

