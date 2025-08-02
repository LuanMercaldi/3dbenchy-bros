import pytest

class TestCart:
    """Testes para endpoints de carrinho"""
    
    def test_get_empty_cart(self, client, auth_headers):
        """Teste de carrinho vazio"""
        response = client.get('/api/cart', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'items' in data
        assert 'total_items' in data
        assert 'total_price' in data
        assert data['total_items'] == 0
        assert data['total_price'] == 0
        assert len(data['items']) == 0
    
    def test_add_to_cart(self, client, auth_headers):
        """Teste de adicionar produto ao carrinho"""
        # Primeiro, obter um produto
        products_response = client.get('/api/products')
        products = products_response.get_json()['products']
        
        if products:
            product_id = products[0]['id']
            
            response = client.post('/api/cart',
                headers=auth_headers,
                json={
                    'product_id': product_id,
                    'quantity': 2
                }
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'message' in data
            assert 'cart_total_items' in data
    
    def test_add_nonexistent_product_to_cart(self, client, auth_headers):
        """Teste de adicionar produto inexistente ao carrinho"""
        response = client.post('/api/cart',
            headers=auth_headers,
            json={
                'product_id': 99999,
                'quantity': 1
            }
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_add_to_cart_invalid_quantity(self, client, auth_headers):
        """Teste de adicionar com quantidade inválida"""
        products_response = client.get('/api/products')
        products = products_response.get_json()['products']
        
        if products:
            product_id = products[0]['id']
            
            response = client.post('/api/cart',
                headers=auth_headers,
                json={
                    'product_id': product_id,
                    'quantity': -1  # Quantidade negativa
                }
            )
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_cart_workflow(self, client, auth_headers):
        """Teste de fluxo completo do carrinho"""
        # Obter produto
        products_response = client.get('/api/products')
        products = products_response.get_json()['products']
        
        if not products:
            pytest.skip("Nenhum produto disponível para teste")
        
        product_id = products[0]['id']
        
        # Adicionar ao carrinho
        add_response = client.post('/api/cart',
            headers=auth_headers,
            json={'product_id': product_id, 'quantity': 1}
        )
        assert add_response.status_code == 200
        
        # Verificar carrinho
        cart_response = client.get('/api/cart', headers=auth_headers)
        assert cart_response.status_code == 200
        cart_data = cart_response.get_json()
        
        assert cart_data['total_items'] == 1
        assert len(cart_data['items']) == 1
        assert cart_data['items'][0]['product_id'] == product_id
        
        # Remover do carrinho
        cart_item_id = cart_data['items'][0]['id']
        remove_response = client.delete(f'/api/cart/{cart_item_id}', headers=auth_headers)
        assert remove_response.status_code == 200
        
        # Verificar carrinho vazio
        final_cart_response = client.get('/api/cart', headers=auth_headers)
        final_cart_data = final_cart_response.get_json()
        assert final_cart_data['total_items'] == 0
    
    def test_cart_unauthenticated(self, client):
        """Teste de acesso ao carrinho sem autenticação"""
        response = client.get('/api/cart')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_clear_cart(self, client, auth_headers):
        """Teste de limpar carrinho"""
        # Adicionar item primeiro
        products_response = client.get('/api/products')
        products = products_response.get_json()['products']
        
        if products:
            product_id = products[0]['id']
            client.post('/api/cart',
                headers=auth_headers,
                json={'product_id': product_id, 'quantity': 1}
            )
        
        # Limpar carrinho
        response = client.delete('/api/cart/clear', headers=auth_headers)
        assert response.status_code == 200
        
        # Verificar se está vazio
        cart_response = client.get('/api/cart', headers=auth_headers)
        cart_data = cart_response.get_json()
        assert cart_data['total_items'] == 0