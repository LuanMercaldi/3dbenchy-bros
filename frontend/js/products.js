// Funções relacionadas aos produtos
class ProductManager {
    constructor() {
        this.products = [];
    }

    displayProducts(products, containerId) {
        const container = document.getElementById(containerId);
        
        if (products.length === 0) {
            container.innerHTML = '<div class="loading">Nenhum produto encontrado</div>';
            return;
        }

        const getProductIcon = (productId, productName) => {
            const icons = {
                1: { emoji: '🚁', alt: 'Ícone de helicóptero Apache AH-64' },
                2: { emoji: '✈️', alt: 'Ícone de caça F-22 Raptor' },
                3: { emoji: '🚗', alt: 'Ícone de tanque M1A2 Abrams' },
                4: { emoji: '🚢', alt: 'Ícone de porta-aviões USS Enterprise' },
                5: { emoji: '🚀', alt: 'Ícone de nave Millennium Falcon' },
                6: { emoji: '🏎️', alt: 'Ícone de Lamborghini Aventador' }
            };
            const icon = icons[productId] || { emoji: '📦', alt: 'Ícone de produto genérico' };
            return `<span role="img" aria-label="${securityManager.escapeHTML(icon.alt)}">${icon.emoji}</span>`;
        };

        // Usar createElement em vez de innerHTML para segurança
        container.innerHTML = ''; // Limpar container

        products.forEach(product => {
            // Sanitizar todos os dados do produto
            const sanitizedName = securityManager.escapeHTML(product.name);
            const sanitizedDescription = securityManager.escapeHTML(product.description);
            const sanitizedPrice = parseFloat(product.price).toFixed(2).replace('.', ',');

            // Criar elementos de forma segura
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.setAttribute('role', 'article');
            productCard.setAttribute('aria-labelledby', `product-${product.id}-name`);

            const productImage = document.createElement('div');
            productImage.className = 'product-image';
            productImage.innerHTML = getProductIcon(product.id, product.name);

            const productName = document.createElement('h3');
            productName.className = 'product-name';
            productName.id = `product-${product.id}-name`;
            productName.textContent = product.name; // textContent é seguro

            const productPrice = document.createElement('div');
            productPrice.className = 'product-price';
            productPrice.setAttribute('aria-label', `Preço: R$ ${sanitizedPrice}`);
            productPrice.textContent = `R$ ${sanitizedPrice}`;

            const productDescription = document.createElement('p');
            productDescription.className = 'product-description';
            productDescription.textContent = product.description; // textContent é seguro

            const addButton = document.createElement('button');
            addButton.className = 'add-to-cart-btn';
            addButton.setAttribute('aria-label', `Adicionar ${sanitizedName} ao carrinho`);
            addButton.textContent = '🛒 ADICIONAR AO CARRINHO';
            addButton.onclick = () => cartManager.addToCart(product.id);

            // Montar o card
            productCard.appendChild(productImage);
            productCard.appendChild(productName);
            productCard.appendChild(productPrice);
            productCard.appendChild(productDescription);
            productCard.appendChild(addButton);

            container.appendChild(productCard);
        });
    }


}
// Criar instância global
const productManager = new ProductManager();