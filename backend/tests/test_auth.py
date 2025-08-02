import pytest
import json

class TestAuth:
    """Testes para endpoints de autenticação"""
    
    def test_register_success(self, client):
        """Teste de cadastro bem-sucedido"""
        response = client.post('/api/auth/register', json={
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': 'MinhaSenh@123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'user' in data
        assert 'tokens' in data
        assert data['user']['email'] == 'joao@exemplo.com'
        assert data['user']['name'] == 'João Silva'
        assert 'access_token' in data['tokens']
        assert 'refresh_token' in data['tokens']
    
    def test_register_invalid_email(self, client):
        """Teste de cadastro com email inválido"""
        response = client.post('/api/auth/register', json={
            'name': 'João Silva',
            'email': 'email-invalido',
            'password': 'MinhaSenh@123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'email' in data['error'].lower()
    
    def test_register_weak_password(self, client):
        """Teste de cadastro com senha fraca"""
        response = client.post('/api/auth/register', json={
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': '123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'senha' in data['error'].lower()
    
    def test_register_duplicate_email(self, client):
        """Teste de cadastro com email duplicado"""
        # Primeiro cadastro
        client.post('/api/auth/register', json={
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': 'MinhaSenh@123'
        })
        
        # Segundo cadastro com mesmo email
        response = client.post('/api/auth/register', json={
            'name': 'Maria Silva',
            'email': 'joao@exemplo.com',
            'password': 'OutraSenh@123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'já cadastrado' in data['error'].lower()
    
    def test_login_success(self, client):
        """Teste de login bem-sucedido"""
        # Cadastrar usuário primeiro
        client.post('/api/auth/register', json={
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': 'MinhaSenh@123'
        })
        
        # Fazer login
        response = client.post('/api/auth/login', json={
            'email': 'joao@exemplo.com',
            'password': 'MinhaSenh@123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'user' in data
        assert 'tokens' in data
        assert data['user']['email'] == 'joao@exemplo.com'
    
    def test_login_invalid_credentials(self, client):
        """Teste de login com credenciais inválidas"""
        response = client.post('/api/auth/login', json={
            'email': 'inexistente@exemplo.com',
            'password': 'senhaerrada'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_get_user_info_authenticated(self, client, auth_headers):
        """Teste de obter informações do usuário autenticado"""
        response = client.get('/api/auth/user', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['authenticated'] is True
        assert 'user' in data
        assert data['user']['email'] == 'teste@exemplo.com'
    
    def test_get_user_info_unauthenticated(self, client):
        """Teste de obter informações sem autenticação"""
        response = client.get('/api/auth/user')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_logout(self, client, auth_headers):
        """Teste de logout"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Tentar usar token após logout (deve falhar)
        response = client.get('/api/auth/user', headers=auth_headers)
        assert response.status_code == 401
    
    def test_rate_limiting_register(self, client):
        """Teste de rate limiting no cadastro"""
        # Fazer múltiplas tentativas rapidamente
        for i in range(5):
            response = client.post('/api/auth/register', json={
                'name': f'Usuário {i}',
                'email': f'usuario{i}@exemplo.com',
                'password': 'MinhaSenh@123'
            })
            
            if i < 3:
                assert response.status_code in [201, 409]  # Sucesso ou email duplicado
            else:
                # Deve ser bloqueado por rate limiting
                assert response.status_code == 429