import os
from datetime import timedelta

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações do banco de dados
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///3dbenchy.db'
    
    # Configurações CORS
    CORS_ORIGINS = [
        'https://3dbenchybros.com.br',
        'https://luanmercaldi.github.io',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        '*'  # Para desenvolvimento
    ]
    
    @staticmethod
    def init_app(app ):
        pass

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
