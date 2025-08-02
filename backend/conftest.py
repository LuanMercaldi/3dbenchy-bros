import pytest
import tempfile
import os
from backend.app import create_app
from backend.utils.database import DatabaseManager

@pytest.fixture
def app():
    """Criar aplicação Flask para testes"""
    # Criar banco de dados temporário
    db_fd, db_path = tempfile.mkstemp()
    
    # Configurar aplicação para testes
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{db_path}',
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Inicializar banco de dados de teste
    with app.app_context():
        db = DatabaseManager(db_path)
        app.db = db
    
    yield app
    
    # Limpeza
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Headers de autenticação para testes"""
    # Criar usuário de teste
    response = client.post('/api/auth/register', json={
        'name': 'Usuário Teste',
        'email': 'teste@exemplo.com',
        'password': 'MinhaSenh@123'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    
    return {
        'Authorization': f'Bearer {data["tokens"]["access_token"]}'
    }

@pytest.fixture
def admin_headers(client, app):
    """Headers de admin para testes"""
    # Criar usuário admin
    with app.app_context():
        app.db.create_user(
            name='Admin Teste',
            email='admin@exemplo.com',
            password='AdminSenh@123'
        )
        
        # Tornar usuário admin (seria necessário implementar método no DatabaseManager)
        # Por simplicidade, vamos simular
        
    response = client.post('/api/auth/login', json={
        'email': 'admin@exemplo.com',
        'password': 'AdminSenh@123'
    })
    
    data = response.get_json()
    return {
        'Authorization': f'Bearer {data["tokens"]["access_token"]}'
    }