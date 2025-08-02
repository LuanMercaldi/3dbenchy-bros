import pytest

class TestProducts:
    """Testes para endpoints de produtos"""
    
    def test_get_products(self, client):
        """Teste de listagem de produtos"""
        response = client.get('/api/products')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'products' in data
        assert 'total' in data
        assert isinstance(data['products'], list)
        assert data['total'] >= 0
    
    def test_get_featured_products(self, client):
        """Teste de produtos em destaque"""
        response = client.get('/api/products/featured')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, list)
        # Verificar se todos os produtos retornados são featured
        for product in data:
            assert product.get('is_featured') is True
    
    def test_get_product_by_id(self, client):
        """Teste de busca de produto por ID"""
        # Primeiro, obter lista de produtos
        response = client.get('/api/products')
        products = response.get_json()['products']
        
        if products:
            product_id = products[0]['id']
            
            response = client.get(f'/api/products/{product_id}')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['id'] == product_id
    
    def test_get_nonexistent_product(self, client):
        """Teste de busca de produto inexistente"""
        response = client.get('/api/products/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_create_product_admin(self, client, admin_headers):
        """Teste de criação de produto por admin"""
        response = client.post('/api/products', 
            headers=admin_headers,
            json={
                'name': 'Produto Teste',
                'description': 'Descrição do produto teste com mais de 10 caracteres',
                'price': 99.99,
                'category': 'aeronaves',
                'is_featured': True,
                'stock_quantity': 10
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'product' in data
        assert data['product']['name'] == 'Produto Teste'
        assert data['product']['price'] == 99.99
    
    def test_create_product_unauthorized(self, client, auth_headers):
        """Teste de criação de produto sem privilégios de admin"""
        response = client.post('/api/products',
            headers=auth_headers,
            json={
                'name': 'Produto Teste',
                'description': 'Descrição do produto teste',
                'price': 99.99,
                'category': 'aeronaves'
            }
        )
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_create_product_invalid_data(self, client, admin_headers):
        """Teste de criação de produto com dados inválidos"""
        response = client.post('/api/products',
            headers=admin_headers,
            json={
                'name': '',  # Nome vazio
                'description': 'Desc',  # Descrição muito curta
                'price': -10,  # Preço negativo
                'category': 'categoria_inexistente'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_get_categories(self, client):
        """Teste de listagem de categorias"""
        response = client.get('/api/products/categories')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'categories' in data
        assert isinstance(data['categories'], list)
        assert len(data['categories']) > 0
        
        # Verificar estrutura das categorias
        for category in data['categories']:
            assert 'id' in category
            assert 'name' in category
            assert 'description' in category