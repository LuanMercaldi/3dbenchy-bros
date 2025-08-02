// Funções relacionadas ao carrinho
class CartManager {
    constructor() {
        this.cartItems = [];
    }

    getAuthHeaders() {
        const token = localStorage.getItem('access_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    async addToCart(productId) {
        if (!authManager.currentUser) {
            alert('Faça login para adicionar produtos ao carrinho!');
            authManager.showLoginOptions();
            return;
        }

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                alert('Produto adicionado ao carrinho!');
                this.updateCartCount(data.cart_total_items);
            } else {
                alert(data.error || 'Erro ao adicionar produto ao carrinho');
            }
        } catch (error) {
            console.error('Erro ao adicionar ao carrinho:', error);
            alert('Erro ao adicionar produto ao carrinho');
        }
    }

    async loadCart() {
        if (!authManager.currentUser) return;

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/cart`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                this.cartItems = data.items || [];
                this.displayCart();
                this.updateCartCount(data.total_items);
            }
        } catch (error) {
            console.error('Erro ao carregar carrinho:', error);
        }
    }

    async removeFromCart(itemId) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/cart/${itemId}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                this.loadCart(); // Recarregar carrinho
            } else {
                const data = await response.json();
                alert(data.error || 'Erro ao remover item do carrinho');
            }
        } catch (error) {
            console.error('Erro ao remover do carrinho:', error);
        }
    }

    updateCartCount(count) {
        const cartCount = document.getElementById('cartCount');
        if (cartCount) {
            cartCount.textContent = count || 0;
        }
    }

    
}

// Criar instância global
const cartManager = new CartManager();