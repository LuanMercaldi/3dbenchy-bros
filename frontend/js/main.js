// Arquivo principal que inicializa a aplicação
class App {
    constructor() {
        this.init();
    }

    async init() {
        // Aguardar o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.start());
        } else {
            this.start();
        }
    }

    async start() {
        console.log(`${CONFIG.APP_NAME} v${CONFIG.VERSION} iniciando...`);
        
        try {
            // Inicializar todos os gerenciadores
            await authManager.checkAuthStatus();
            await productManager.loadFeaturedProducts();
            await productManager.loadProducts();
            await cartManager.loadCart();
            
            console.log('Aplicação inicializada com sucesso!');
        } catch (error) {
            console.error('Erro ao inicializar aplicação:', error);
        }
    }
}

// Inicializar aplicação
const app = new App();