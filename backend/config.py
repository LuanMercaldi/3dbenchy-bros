import os
from datetime import timedelta

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-inproduction'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações do banco de dados
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Configurações CORS - incluir domínio do GitHub Pages
    CORS_ORIGINS = [
    'https://seu-usuario.github.io',
    'https://3dbenchybros.com.br', # se tiver domínio personalizado
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    ]
    
    @staticmethod
    def init_app(app):
        pass
    
class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    FLASK_ENV = 'development'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///3dbenchy.db'
    
class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log para stdout em produção
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
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
